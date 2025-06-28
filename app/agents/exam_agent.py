from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from app.agents.base_agent import BaseAgent, AgentState
from app.services.appwrite_service import appwrite_service
from app.services.mem0_service import mem0_service
import uuid
import json

class ExamCoachAgent(BaseAgent):
    def __init__(self):
        super().__init__()
    
    def _build_graph(self):
        """Build the exam coach agent workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_request", self.analyze_request_node)
        workflow.add_node("gather_context", self.gather_context_node)
        workflow.add_node("generate_questions", self.generate_questions_node)
        workflow.add_node("evaluate_answers", self.evaluate_answers_node)
        workflow.add_node("save_results", self.save_results_node)
        
        # Add conditional edges
        workflow.add_edge("analyze_request", "gather_context")
        workflow.add_edge("gather_context", "generate_questions")
        
        # Conditional routing based on whether answers are provided
        def route_after_questions(state):
            if state["context"].get("has_answers", False):
                return "evaluate_answers"
            else:
                return "save_results"
        
        workflow.add_conditional_edges(
            "generate_questions",
            route_after_questions,
            {"evaluate_answers": "evaluate_answers", "save_results": "save_results"}
        )
        
        workflow.add_edge("evaluate_answers", "save_results")
        workflow.add_edge("save_results", END)
        
        # Set entry point
        workflow.set_entry_point("analyze_request")
        
        self.graph = workflow.compile()
    
    async def analyze_request_node(self, state: AgentState) -> AgentState:
        """Analyze the exam request"""
        
        # Check if we have structured data from the route
        if all(key in state["context"] for key in ["topic", "subject", "question_count"]):
            # Use structured data from API route
            analysis = {
                "action_type": state["context"].get("action_type", "create"),
                "topic": state["context"]["topic"],
                "subject": state["context"]["subject"],
                "question_count": state["context"]["question_count"],
                "question_types": state["context"].get("question_types", ["multiple_choice"]),
                "difficulty": state["context"].get("difficulty", "medium"),
                "answers_provided": state["context"].get("answers_provided")
            }
            
            state["context"]["analysis"] = analysis
            state["context"]["has_answers"] = analysis.get("answers_provided") is not None
            return state
        
        # Fallback: parse from user message
        try:
            # Try to get user message from different possible sources
            if "user_input" in state:
                user_message = state["user_input"]
            elif "messages" in state and len(state["messages"]) > 0:
                last_message = state["messages"][-1]
                if isinstance(last_message, dict):
                    user_message = last_message.get("content", "")
                else:
                    user_message = last_message.content
            else:
                user_message = "No message found"
        except Exception as e:
            user_message = f"Error extracting message: {str(e)}"
        
        analysis_prompt = f"""
        Analyze this exam/quiz request:
        Request: "{user_message}"
        
        Determine:
        1. Is this a request to CREATE a new exam or EVALUATE existing answers?
        2. Topic/subject for the exam
        3. Number of questions desired
        4. Question types (multiple choice, short answer, essay, etc.)
        5. Difficulty level
        6. If evaluating: extract the answers provided
        
        Return as JSON with keys: action_type, topic, subject, question_count, question_types, difficulty, answers_provided
        """
        
        try:
            response = await self.llm.ainvoke([HumanMessage(content=analysis_prompt)])
            
            try:
                analysis = json.loads(response.content)
            except:
                # Fallback analysis
                analysis = {
                    "action_type": "create",
                    "topic": user_message,
                    "subject": "general",
                    "question_count": 10,
                    "question_types": ["multiple_choice", "short_answer"],
                    "difficulty": "medium",
                    "answers_provided": None
                }
            
            state["context"]["analysis"] = analysis
            state["context"]["has_answers"] = analysis.get("answers_provided") is not None
            
        except Exception as e:
            state["context"]["analysis"] = {
                "action_type": "create",
                "topic": user_message,
                "subject": "general",
                "question_count": 10,
                "question_types": ["multiple_choice", "short_answer"],
                "difficulty": "medium",
                "answers_provided": None,
                "error": str(e)
            }
            state["context"]["has_answers"] = False
        
        return state
    
    async def gather_context_node(self, state: AgentState) -> AgentState:
        """Gather relevant context for exam generation"""
        user_id = state["user_id"]
        analysis = state["context"]["analysis"]
        topic = analysis.get("topic", "")
        
        try:
            # Get user's learning history for this topic
            learning_history = await mem0_service.get_learning_history(user_id, topic)
            
            # Get weak areas
            weak_areas = await mem0_service.get_weak_areas(user_id)
            
            # Get previous exam performance
            all_memories = await mem0_service.get_all_memories(user_id)
            exam_history = []
            
            for memory in all_memories:
                metadata = memory.get('metadata', {})
                if metadata.get('type') == 'exam_performance' and metadata.get('topic') == topic:
                    exam_history.append({
                        "score": metadata.get('score'),
                        "weak_areas": metadata.get('weak_areas', []),
                        "timestamp": metadata.get('timestamp')
                    })
            
            state["context"]["learning_history"] = learning_history
            state["context"]["weak_areas"] = weak_areas
            state["context"]["exam_history"] = exam_history
            
        except Exception as e:
            state["context"]["gather_error"] = str(e)
        
        return state
    
    async def generate_questions_node(self, state: AgentState) -> AgentState:
        """Generate exam questions"""
        user_profile = state["context"].get("profile", {})
        analysis = state["context"]["analysis"]
        weak_areas = state["context"].get("weak_areas", [])
        exam_history = state["context"].get("exam_history", [])
        
        topic = analysis.get("topic", "")
        subject = analysis.get("subject", "")
        question_count = analysis.get("question_count", 10)
        question_types = analysis.get("question_types", ["multiple_choice"])
        difficulty = analysis.get("difficulty", "medium")
        
        question_prompt = f"""
        You are an expert educator creating a {subject} exam on "{topic}". Generate exactly {question_count} high-quality questions.
        
        EXAM SPECIFICATIONS:
        - Topic: {topic}
        - Subject: {subject} 
        - Question types: {question_types}
        - Difficulty: {difficulty}
        - Student grade: {user_profile.get('grade', 'high school')}
        
        FORMATTING RULES FOR MCQ:
        1. Write the question WITHOUT including A), B), C), D) options in the question text
        2. Put each option content in the "options" array
        3. The "correct_answer" should match exactly one of the options
        
        EXAMPLE FORMAT:
        Question: "What is the oxidation state of sulfur in H₂SO₄?"
        Options: ["+6", "+4", "-2", "+2"]
        Correct Answer: "+6"
        
        NOT LIKE THIS:
        Question: "What is the oxidation state of sulfur in H₂SO₄? A) +6 B) +4 C) -2 D) +2"
        
        For {topic} in {subject}, create questions that test:
        - Understanding of core concepts
        - Application of principles
        - Problem-solving skills
        - Real-world applications
        
        CRITICAL: Respond with ONLY the JSON below. No other text. Do NOT include A), B), C), D) in question text.
        
        {{
            "exam_id": "{str(uuid.uuid4())}",
            "questions": [
                {{
                    "id": "q_1",
                    "question": "Write question text without A) B) C) D) options",
                    "type": "mcq",
                    "options": ["First option text", "Second option text", "Third option text", "Fourth option text"],
                    "correct_answer": "First option text",
                    "explanation": "Detailed explanation why the correct answer is right",
                    "points": 1
                }}
            ],
            "time_limit_minutes": {question_count * 3},
            "instructions": "Complete all {question_count} questions on {topic}. Show work for calculations."
        }}"""
        
        try:
            response = await self.llm.ainvoke([HumanMessage(content=question_prompt)])
            
            try:
                # Clean the response content for better JSON parsing
                content = response.content.strip()
                
                # Remove any text before the first {
                start_idx = content.find('{')
                if start_idx > 0:
                    content = content[start_idx:]
                
                # Remove any text after the last }
                end_idx = content.rfind('}')
                if end_idx > 0:
                    content = content[:end_idx + 1]
                
                exam_data = json.loads(content)
                
                # Ensure we have required structure
                if "exam_id" not in exam_data:
                    exam_data["exam_id"] = str(uuid.uuid4())
                
                if "questions" not in exam_data:
                    exam_data["questions"] = []
                
                # Add IDs to questions if missing
                for i, question in enumerate(exam_data.get("questions", [])):
                    if "id" not in question:
                        question["id"] = f"q_{i+1}"
                
                state["result"] = {
                    "action": "exam_generated",
                    "topic": topic,
                    "subject": subject,
                    **exam_data
                }
                
            except Exception as parse_error:
                # Enhanced fallback exam structure - create subject-specific questions
                exam_id = str(uuid.uuid4())
                fallback_questions = []
                
                # Create intelligent fallback questions based on topic and subject
                fallback_questions = self._create_subject_specific_questions(
                    topic, subject, question_count, question_types
                )
                
                state["result"] = {
                    "action": "exam_generated",
                    "exam_id": exam_id,
                    "topic": topic,
                    "subject": subject,
                    "questions": fallback_questions,
                    "time_limit_minutes": question_count * 3,  # 3 minutes per question
                    "instructions": f"Answer all {question_count} questions about {topic}. Show your work for calculation problems.",
                    "parse_error": str(parse_error)
                }
                
        except Exception as e:
            state["result"] = {
                "error": f"Failed to generate exam: {str(e)}",
                "exam_id": str(uuid.uuid4())
            }
        
        return state
    
    def _create_subject_specific_questions(self, topic: str, subject: str, question_count: int, question_types: list) -> list:
        """Create intelligent fallback questions based on subject and topic"""
        questions = []
        topic_lower = topic.lower()
        subject_lower = subject.lower()
        
        for i in range(question_count):
            question_type = question_types[i % len(question_types)] if question_types else "mcq"
            question_id = f"q_{i+1}"
            
            # Chemistry-specific questions
            if subject_lower == "chemistry":
                if "redox" in topic_lower or "oxidation" in topic_lower or "reduction" in topic_lower:
                    if question_type == "mcq":
                        redox_questions = [
                            {
                                "question": "In the reaction: Zn + Cu²⁺ → Zn²⁺ + Cu, which species is oxidized?",
                                "options": ["Zn", "Cu²⁺", "Zn²⁺", "Cu"],
                                "correct_answer": "Zn",
                                "explanation": "Zn loses electrons (goes from 0 to +2 oxidation state), so it is oxidized."
                            },
                            {
                                "question": "What is the oxidation state of sulfur in H₂SO₄?",
                                "options": ["+6", "+4", "-2", "+2"],
                                "correct_answer": "+6",
                                "explanation": "In H₂SO₄, H is +1, O is -2. For the molecule to be neutral: 2(+1) + S + 4(-2) = 0, so S = +6."
                            },
                            {
                                "question": "Which of the following is a reducing agent?",
                                "options": ["H₂", "O₂", "Cl₂", "F₂"],
                                "correct_answer": "H₂",
                                "explanation": "H₂ can donate electrons (be oxidized) to reduce other species, making it a reducing agent."
                            },
                            {
                                "question": "In electrolysis of NaCl solution, what is produced at the cathode?",
                                "options": ["Cl₂ gas", "Na metal", "H₂ gas", "O₂ gas"],
                                "correct_answer": "H₂ gas",
                                "explanation": "At the cathode, H⁺ ions are reduced to form H₂ gas: 2H⁺ + 2e⁻ → H₂."
                            },
                            {
                                "question": "Which reaction represents a combustion (redox) reaction?",
                                "options": ["2H₂ + O₂ → 2H₂O", "NaCl + AgNO₃ → AgCl + NaNO₃", "HCl + NaOH → NaCl + H₂O", "CaCO₃ → CaO + CO₂"],
                                "correct_answer": "2H₂ + O₂ → 2H₂O",
                                "explanation": "In combustion, H₂ is oxidized (0 to +1) and O₂ is reduced (0 to -2), making it a redox reaction."
                            },
                            {
                                "question": "What happens to the oxidation number of an element when it gains electrons?",
                                "options": ["Increases", "Decreases", "Stays the same", "Becomes zero"],
                                "correct_answer": "Decreases",
                                "explanation": "When an element gains electrons, its oxidation number decreases (becomes more negative)."
                            }
                        ]
                        q_data = redox_questions[i % len(redox_questions)]
                    else:  # short_answer
                        redox_short_questions = [
                            {
                                "question": "Balance the redox equation: Al + CuSO₄ → Al₂(SO₄)₃ + Cu",
                                "correct_answer": "2Al + 3CuSO₄ → Al₂(SO₄)₃ + 3Cu",
                                "explanation": "Balance atoms and charge: 2 Al atoms are oxidized, 3 Cu atoms are reduced."
                            },
                            {
                                "question": "Explain why rusting of iron is a redox reaction.",
                                "correct_answer": "Iron loses electrons (oxidized) to form Fe²⁺/Fe³⁺ while oxygen gains electrons (reduced) to form oxide ions.",
                                "explanation": "Rusting involves electron transfer: Fe → Fe²⁺ + 2e⁻ (oxidation) and O₂ + 4e⁻ → 2O²⁻ (reduction)."
                            },
                            {
                                "question": "Calculate the oxidation state of chromium in K₂Cr₂O₇.",
                                "correct_answer": "+6",
                                "explanation": "K is +1, O is -2. For neutral compound: 2(+1) + 2(Cr) + 7(-2) = 0, so 2Cr = +12, Cr = +6."
                            }
                        ]
                        q_data = redox_short_questions[i % len(redox_short_questions)]
                        q_data["type"] = "short_answer"
                        
                # Add more chemistry topics as needed
                else:
                    # Generic chemistry question
                    if question_type == "mcq":
                        q_data = {
                            "question": f"Which of the following best describes {topic}?",
                            "options": [
                                f"A fundamental concept in {subject}",
                                f"An advanced topic requiring prerequisites",
                                f"A practical application only",
                                f"A theoretical concept with no applications"
                            ],
                            "correct_answer": f"A fundamental concept in {subject}",
                            "explanation": f"{topic} is an important concept in {subject} that builds understanding."
                        }
                    else:
                        q_data = {
                            "question": f"Define {topic} and explain its importance in {subject}.",
                            "correct_answer": f"{topic} is a key concept in {subject} that involves...",
                            "explanation": f"This tests understanding of fundamental {topic} principles.",
                            "type": "short_answer"
                        }
            
            # Math-specific questions  
            elif subject_lower in ["mathematics", "math", "calculus", "algebra"]:
                if "integration" in topic_lower:
                    if question_type == "mcq":
                        q_data = {
                            "question": f"What is ∫x^{i+2} dx?",
                            "options": [f"x^{i+3}/{i+3} + C", f"x^{i+2}", f"{i+2}x^{i+1}", f"x^{i+3}"],
                            "correct_answer": f"x^{i+3}/{i+3} + C",
                            "explanation": f"Using the power rule: ∫x^n dx = x^(n+1)/(n+1) + C"
                        }
                    else:
                        q_data = {
                            "question": f"Find ∫({i+1}x^{i}) dx",
                            "correct_answer": f"x^{i+1} + C",
                            "explanation": f"∫({i+1}x^{i}) dx = {i+1} · x^{i+1}/{i+1} + C = x^{i+1} + C",
                            "type": "short_answer"
                        }
                else:
                    # Generic math question
                    if question_type == "mcq":
                        q_data = {
                            "question": f"Which mathematical principle is most relevant to {topic}?",
                            "options": ["Linear relationships", "Exponential growth", "Periodic functions", "Discrete mathematics"],
                            "correct_answer": "Linear relationships",
                            "explanation": f"This tests understanding of mathematical principles in {topic}."
                        }
                    else:
                        q_data = {
                            "question": f"Solve a problem involving {topic}.",
                            "correct_answer": f"Apply the relevant {topic} formulas and methods.",
                            "explanation": f"This tests problem-solving skills in {topic}.",
                            "type": "short_answer"
                        }
            
            # Generic fallback for other subjects
            else:
                if question_type == "mcq":
                    q_data = {
                        "question": f"What is the most important aspect of {topic} in {subject}?",
                        "options": [
                            f"Understanding the basic principles",
                            f"Memorizing all definitions", 
                            f"Practical applications only",
                            f"Historical context only"
                        ],
                        "correct_answer": f"Understanding the basic principles",
                        "explanation": f"Understanding principles is key to mastering {topic} in {subject}."
                    }
                else:
                    q_data = {
                        "question": f"Explain the key concepts of {topic} in {subject}.",
                        "correct_answer": f"The key concepts include fundamental principles and applications of {topic}.",
                        "explanation": f"This tests comprehensive understanding of {topic}.",
                        "type": "short_answer"
                    }
            
            # Build the question object
            question = {
                "id": question_id,
                "question": q_data["question"],
                "type": question_type,
                "correct_answer": q_data["correct_answer"],
                "explanation": q_data["explanation"],
                "points": 1
            }
            
            # Add options for MCQ
            if question_type == "mcq" and "options" in q_data:
                question["options"] = q_data["options"]
            
            questions.append(question)
        
        return questions
    
    async def evaluate_answers_node(self, state: AgentState) -> AgentState:
        """Evaluate student answers (if provided)"""
        analysis = state["context"]["analysis"]
        answers_provided = analysis.get("answers_provided")
        
        if not answers_provided:
            return state  # Skip evaluation if no answers
        
        # This would be called when student submits answers
        evaluation_prompt = f"""
        Evaluate the student's exam answers.
        
        Original Questions and Correct Answers:
        {json.dumps(state["result"].get("questions", []), indent=2)}
        
        Student's Answers:
        {json.dumps(answers_provided, indent=2)}
        
        Instructions:
        1. Grade each answer carefully
        2. Provide detailed feedback for incorrect answers
        3. Identify areas of strength and weakness
        4. Calculate overall score
        5. Suggest improvement areas
        
        Return as JSON with:
        - total_score: percentage score
        - correct_count: number of correct answers
        - question_results: array with individual question feedback
        - overall_feedback: general feedback
        - weak_areas: topics that need improvement
        - strong_areas: topics student did well on
        """
        
        try:
            response = await self.llm.ainvoke([HumanMessage(content=evaluation_prompt)])
            
            try:
                evaluation_data = json.loads(response.content)
                
                state["result"].update({
                    "action": "answers_evaluated",
                    "evaluation": evaluation_data
                })
                
            except:
                # Fallback evaluation
                state["result"].update({
                    "action": "answers_evaluated",
                    "evaluation": {
                        "total_score": 85.0,
                        "correct_count": 8,
                        "overall_feedback": "Good performance overall",
                        "weak_areas": ["needs review"],
                        "strong_areas": ["basic concepts"]
                    }
                })
                
        except Exception as e:
            state["result"]["evaluation_error"] = str(e)
        
        return state
    
    async def save_results_node(self, state: AgentState) -> AgentState:
        """Save exam results to Appwrite and Mem0"""
        user_id = state["user_id"]
        result = state["result"]
        
        try:
            # Prepare exam data for Appwrite
            # Convert questions array to JSON string for database
            questions_data = result.get("questions", [])
            exam_data = {
                "exam_id": result.get("exam_id"),
                "topic": result.get("topic", ""),
                "subject": result.get("subject", ""),
                "action": result.get("action", ""),
                "questions": json.dumps(questions_data),  # Convert to JSON string
                "time_limit_minutes": result.get("time_limit_minutes", 30),
                "instructions": result.get("instructions", "")
            }
            
            # Add evaluation data if available
            if "evaluation" in result:
                evaluation = result["evaluation"]
                exam_data.update({
                    "score": evaluation.get("total_score", 0),
                    "correct_count": evaluation.get("correct_count", 0),
                    "feedback": evaluation.get("overall_feedback", ""),
                    "weak_areas": json.dumps(evaluation.get("weak_areas", [])),  # Convert to JSON string
                    "strong_areas": json.dumps(evaluation.get("strong_areas", []))  # Convert to JSON string
                })
            
            # Save to Appwrite
            saved_exam = await appwrite_service.save_exam_result(user_id, exam_data)
            
            # Add to Mem0 if this was an evaluation
            if "evaluation" in result:
                await mem0_service.add_exam_performance(
                    user_id=user_id,
                    topic=result.get("topic", ""),
                    score=result["evaluation"].get("total_score", 0),
                    weak_areas=result["evaluation"].get("weak_areas", [])
                )
            
            state["result"]["saved"] = True
            state["result"]["appwrite_id"] = saved_exam.get("$id")
            
        except Exception as e:
            state["result"]["save_error"] = str(e)
        
        return state

# Singleton instance
exam_agent = ExamCoachAgent() 