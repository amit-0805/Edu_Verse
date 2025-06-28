from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from app.agents.base_agent import BaseAgent, AgentState
from app.services.appwrite_service import appwrite_service
from app.services.mem0_service import mem0_service
import uuid
import json

class TutorAgent(BaseAgent):
    def __init__(self):
        super().__init__()
    
    def _build_graph(self):
        """Build the tutor agent workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_request", self.analyze_request_node)
        workflow.add_node("retrieve_context", self.retrieve_context_node)
        workflow.add_node("generate_explanation", self.generate_explanation_node)
        workflow.add_node("save_session", self.save_session_node)
        
        # Add edges
        workflow.add_edge("analyze_request", "retrieve_context")
        workflow.add_edge("retrieve_context", "generate_explanation")
        workflow.add_edge("generate_explanation", "save_session")
        workflow.add_edge("save_session", END)
        
        # Set entry point
        workflow.set_entry_point("analyze_request")
        
        self.graph = workflow.compile()
    
    async def analyze_request_node(self, state: AgentState) -> AgentState:
        """Analyze the user's request to extract topic and subject"""
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
        Analyze this learning request and extract the key information:
        Request: "{user_message}"
        
        Extract:
        1. Main topic
        2. Subject area
        3. Difficulty level (if mentioned)
        4. Specific questions or concepts
        
        Return as JSON with keys: topic, subject, difficulty, concepts
        """
        
        try:
            response = await self.llm.ainvoke([HumanMessage(content=analysis_prompt)])
            
            # Try to parse JSON response
            try:
                analysis = json.loads(response.content)
            except:
                # Fallback if JSON parsing fails
                analysis = {
                    "topic": user_message,
                    "subject": "general",
                    "difficulty": "medium",
                    "concepts": [user_message]
                }
            
            state["context"]["analysis"] = analysis
            
        except Exception as e:
            state["context"]["analysis"] = {
                "topic": user_message,
                "subject": "general", 
                "difficulty": "medium",
                "concepts": [user_message],
                "error": str(e)
            }
        
        return state
    
    async def retrieve_context_node(self, state: AgentState) -> AgentState:
        """Retrieve relevant context from user's learning history"""
        user_id = state["user_id"]
        analysis = state["context"]["analysis"]
        topic = analysis.get("topic", "")
        
        try:
            # Get learning history for this topic
            learning_history = await mem0_service.get_learning_history(user_id, topic)
            
            # Get user's weak areas
            weak_areas = await mem0_service.get_weak_areas(user_id)
            
            # Search for related memories
            related_memories = await mem0_service.search_memory(user_id, topic, limit=5)
            
            state["context"]["learning_history"] = learning_history
            state["context"]["weak_areas"] = weak_areas
            state["context"]["related_memories"] = related_memories
            
        except Exception as e:
            state["context"]["retrieval_error"] = str(e)
        
        return state
    
    async def generate_explanation_node(self, state: AgentState) -> AgentState:
        """Generate personalized explanation based on context"""
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
        user_profile = state["context"].get("profile", {})
        analysis = state["context"]["analysis"]
        learning_history = state["context"].get("learning_history", [])
        weak_areas = state["context"].get("weak_areas", [])
        
        # Build context for the explanation
        learning_style = user_profile.get("learning_style", "visual")
        grade = user_profile.get("grade", "")
        
        # Create personalized prompt
        explanation_prompt = f"""
        You are an expert AI tutor. Create a personalized explanation for this student.
        
        Student Request: "{user_message}"
        Topic: {analysis.get('topic', '')}
        Subject: {analysis.get('subject', '')}
        
        Student Profile:
        - Learning Style: {learning_style}
        - Grade Level: {grade}
        - Known Weak Areas: {', '.join(weak_areas) if weak_areas else 'None identified'}
        
        Previous Learning History (if any):
        {self._format_learning_history(learning_history)}
        
        Instructions:
        1. Provide a clear, personalized explanation adapted to their learning style
        2. If this is a topic they've struggled with before, acknowledge it and provide additional support
        3. Include 2-3 concrete examples
        4. Suggest 2-3 additional learning resources
        5. Use appropriate language for their grade level
        6. If they're visual learners, suggest diagrams/visuals
        7. If they're auditory learners, suggest verbal techniques
        8. If they're kinesthetic learners, suggest hands-on activities
        
        Format your response as JSON with:
        - explanation: main explanation text
        - examples: list of examples
        - additional_resources: list of suggested resources
        - learning_tips: personalized study tips
        - difficulty_addressed: boolean if this addresses a known weak area
        """
        
        try:
            response = await self.llm.ainvoke([HumanMessage(content=explanation_prompt)])
            
            # Try to parse JSON response
            try:
                explanation_data = json.loads(response.content)
            except:
                # Fallback format
                explanation_data = {
                    "explanation": response.content,
                    "examples": [],
                    "additional_resources": [],
                    "learning_tips": [],
                    "difficulty_addressed": any(topic in weak_areas for topic in [analysis.get('topic', '')])
                }
            
            # Generate session ID
            session_id = str(uuid.uuid4())
            
            state["result"] = {
                "session_id": session_id,
                "topic": analysis.get('topic', ''),
                "subject": analysis.get('subject', ''),
                **explanation_data
            }
            
        except Exception as e:
            state["result"] = {
                "error": f"Failed to generate explanation: {str(e)}",
                "session_id": str(uuid.uuid4())
            }
        
        return state
    
    async def save_session_node(self, state: AgentState) -> AgentState:
        """Save the tutoring session to Appwrite"""
        user_id = state["user_id"]
        result = state["result"]
        
        try:
            # Prepare session data for Appwrite
            session_data = {
                "topic": result.get("topic", ""),
                "subject": result.get("subject", ""),
                "explanation": result.get("explanation", ""),
                "examples": result.get("examples", []),
                "additional_resources": result.get("additional_resources", []),
                "learning_tips": result.get("learning_tips", []),
                "difficulty_addressed": result.get("difficulty_addressed", False)
            }
            
            # Save to Appwrite
            saved_session = await appwrite_service.save_tutoring_session(user_id, session_data)
            
            # Update Mem0 with learning context
            performance = "good" if not result.get("difficulty_addressed") else "improving"
            await mem0_service.add_learning_context(
                user_id=user_id,
                topic=result.get("topic", ""),
                context=result.get("explanation", ""),
                performance=performance
            )
            
            state["result"]["saved"] = True
            state["result"]["appwrite_id"] = saved_session.get("$id")
            
        except Exception as e:
            state["result"]["save_error"] = str(e)
        
        return state
    
    def _format_learning_history(self, history: List[Dict[str, Any]]) -> str:
        """Format learning history for prompt"""
        if not history:
            return "No previous learning history for this topic."
        
        formatted = []
        for item in history[:3]:  # Limit to most recent 3
            metadata = item.get('metadata', {})
            formatted.append(f"- {metadata.get('timestamp', '')}: {metadata.get('performance', 'neutral')} performance")
        
        return "\n".join(formatted)

# Singleton instance
tutor_agent = TutorAgent() 