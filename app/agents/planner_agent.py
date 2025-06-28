from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from app.agents.base_agent import BaseAgent, AgentState
from app.services.appwrite_service import appwrite_service
from app.services.mem0_service import mem0_service
from datetime import datetime, timedelta
import uuid
import json

class StudyPlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__()
    
    def _build_graph(self):
        """Build the study planner agent workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_requirements", self.analyze_requirements_node)
        workflow.add_node("gather_context", self.gather_context_node)
        workflow.add_node("generate_plan", self.generate_plan_node)
        workflow.add_node("save_plan", self.save_plan_node)
        
        # Add edges
        workflow.add_edge("analyze_requirements", "gather_context")
        workflow.add_edge("gather_context", "generate_plan")
        workflow.add_edge("generate_plan", "save_plan")
        workflow.add_edge("save_plan", END)
        
        # Set entry point
        workflow.set_entry_point("analyze_requirements")
        
        self.graph = workflow.compile()
    
    async def analyze_requirements_node(self, state: AgentState) -> AgentState:
        """Analyze the study planning requirements"""
        
        # Check if we already have structured requirements from the route
        if "requirements" in state["context"] and state["context"]["requirements"]:
            return state
        
        # Check if we have structured data from kwargs
        if "subjects" in state["context"] and state["context"]["subjects"]:
            state["context"]["requirements"] = {
                "subjects": state["context"]["subjects"],
                "duration_days": state["context"].get("days_ahead", 7),
                "daily_hours": state["context"].get("daily_hours", 2),
                "goals": ["improve understanding"],
                "priorities": []
            }
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
        Analyze this study planning request:
        Request: "{user_message}"
        
        Extract:
        1. Subjects to study
        2. Time duration (days/weeks)
        3. Daily study hours available
        4. Specific goals or deadlines
        5. Priority topics
        
        Return as JSON with keys: subjects, duration_days, daily_hours, goals, priorities
        If not specified, use reasonable defaults.
        """
        
        try:
            response = await self.llm.ainvoke([HumanMessage(content=analysis_prompt)])
            
            try:
                analysis = json.loads(response.content)
            except:
                # Fallback defaults
                analysis = {
                    "subjects": ["general"],
                    "duration_days": 7,
                    "daily_hours": 2,
                    "goals": ["improve understanding"],
                    "priorities": []
                }
            
            state["context"]["requirements"] = analysis
            
        except Exception as e:
            state["context"]["requirements"] = {
                "subjects": ["general"],
                "duration_days": 7,
                "daily_hours": 2,
                "goals": ["improve understanding"],
                "priorities": [],
                "error": str(e)
            }
        
        return state
    
    async def gather_context_node(self, state: AgentState) -> AgentState:
        """Gather user's learning context and history"""
        user_id = state["user_id"]
        requirements = state["context"]["requirements"]
        
        try:
            # Get weak areas
            weak_areas = await mem0_service.get_weak_areas(user_id)
            
            # Get recent learning history
            all_memories = await mem0_service.get_all_memories(user_id)
            
            # Filter for exam performance and difficulties
            exam_history = []
            difficulty_areas = []
            
            for memory in all_memories[-10:]:  # Recent 10 memories
                metadata = memory.get('metadata', {})
                if metadata.get('type') == 'exam_performance':
                    exam_history.append({
                        "topic": metadata.get('topic'),
                        "score": metadata.get('score'),
                        "weak_areas": metadata.get('weak_areas', [])
                    })
                elif metadata.get('type') == 'difficulty':
                    difficulty_areas.append({
                        "topic": metadata.get('topic'),
                        "difficulty_level": metadata.get('difficulty_level')
                    })
            
            state["context"]["weak_areas"] = weak_areas
            state["context"]["exam_history"] = exam_history
            state["context"]["difficulty_areas"] = difficulty_areas
            
        except Exception as e:
            state["context"]["gather_error"] = str(e)
        
        return state
    
    async def generate_plan_node(self, state: AgentState) -> AgentState:
        """Generate the personalized study plan"""
        user_profile = state["context"].get("profile", {})
        requirements = state["context"]["requirements"]
        weak_areas = state["context"].get("weak_areas", [])
        exam_history = state["context"].get("exam_history", [])
        difficulty_areas = state["context"].get("difficulty_areas", [])
        
        # Calculate plan dates
        start_date = datetime.now()
        duration_days = requirements.get("duration_days", 7)
        end_date = start_date + timedelta(days=duration_days)
        
        planning_prompt = f"""
        Create a personalized study plan for this student.
        
        Requirements:
        - Subjects: {requirements.get('subjects', [])}
        - Duration: {duration_days} days
        - Daily hours available: {requirements.get('daily_hours', 2)} hours
        - Goals: {requirements.get('goals', [])}
        
        Student Context:
        - Learning Style: {user_profile.get('learning_style', 'visual')}
        - Grade: {user_profile.get('grade', '')}
        - Weak Areas: {weak_areas}
        - Recent Difficulties: {[area['topic'] for area in difficulty_areas]}
        - Recent Exam Performance: {exam_history}
        
        Instructions:
        1. Prioritize weak areas and recent difficulties
        2. Balance time across all subjects
        3. Include varied learning activities
        4. Adapt to their learning style
        5. Include review and practice sessions
        6. Set realistic daily goals
        
        Create a day-by-day plan with:
        - Daily topics and tasks
        - Time allocation for each task
        - Learning activities (reading, practice, review)
        - Progress milestones
        
        Return as JSON with:
        - daily_schedule: object with date keys and task arrays
        - weekly_goals: array of goals
        - total_hours: daily study hours (0-24)
        - focus_areas: prioritized topics
        - learning_tips: personalized study tips
        """
        
        try:
            response = await self.llm.ainvoke([HumanMessage(content=planning_prompt)])
            
            try:
                plan_data = json.loads(response.content)
            except:
                # Fallback plan structure
                plan_data = {
                    "daily_schedule": self._create_fallback_schedule(requirements, duration_days),
                    "weekly_goals": requirements.get('goals', []),
                    "total_hours": requirements.get('daily_hours', 2),  # Daily hours, not total
                    "focus_areas": weak_areas[:3],
                    "learning_tips": ["Stay consistent", "Take breaks", "Review regularly"]
                }
            
            # Generate plan ID
            plan_id = str(uuid.uuid4())
            
            state["result"] = {
                "plan_id": plan_id,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "duration_days": duration_days,
                **plan_data
            }
            
        except Exception as e:
            state["result"] = {
                "error": f"Failed to generate study plan: {str(e)}",
                "plan_id": str(uuid.uuid4())
            }
        
        return state
    
    async def save_plan_node(self, state: AgentState) -> AgentState:
        """Save the study plan to Appwrite and Mem0"""
        user_id = state["user_id"]
        result = state["result"]
        
        try:
            # Prepare plan data for Appwrite - only include supported fields
            # Convert only complex objects to strings, keep arrays as arrays
            daily_schedule = result.get("daily_schedule", {})
            plan_data = {
                "plan_id": result.get("plan_id"),
                "start_date": result.get("start_date"),
                "end_date": result.get("end_date"),
                "duration_days": result.get("duration_days"),
                "daily_schedule": json.dumps(daily_schedule),  # Complex object -> string
                "weekly_goals": result.get("weekly_goals", []),  # Keep as array
                "total_hours": result.get("total_hours", 0),
                "learning_tips": result.get("learning_tips", [])  # Keep as array
                # Note: Removed "focus_areas" as it's not supported by the database schema
            }
            
            # Save to Appwrite
            saved_plan = await appwrite_service.save_study_plan(user_id, plan_data)
            
            # Add plan summary to Mem0
            plan_summary = f"Study plan created for {result.get('duration_days')} days focusing on: {', '.join(result.get('focus_areas', []))}"
            await mem0_service.add_memory(
                user_id=user_id,
                messages=[
                    {"role": "user", "content": "Create study plan"},
                    {"role": "assistant", "content": plan_summary}
                ],
                metadata={
                    "type": "study_plan",
                    "plan_id": result.get("plan_id"),
                    "duration_days": result.get("duration_days"),
                    "focus_areas": result.get("focus_areas", []),
                    "timestamp": self._get_current_timestamp()
                }
            )
            
            state["result"]["saved"] = True
            state["result"]["appwrite_id"] = saved_plan.get("$id")
            
        except Exception as e:
            state["result"]["save_error"] = str(e)
        
        return state
    
    def _create_fallback_schedule(self, requirements: Dict[str, Any], duration_days: int) -> Dict[str, List[Dict[str, Any]]]:
        """Create a basic fallback schedule"""
        subjects = requirements.get('subjects', ['general'])
        daily_hours = requirements.get('daily_hours', 2)
        
        schedule = {}
        
        for day in range(duration_days):
            date = (datetime.now() + timedelta(days=day)).strftime('%Y-%m-%d')
            daily_tasks = []
            
            # Distribute subjects across days
            subject = subjects[day % len(subjects)]
            
            daily_tasks.append({
                "topic": f"{subject} review",
                "subject": subject,
                "duration_minutes": int(daily_hours * 60 * 0.6),
                "priority": "high",
                "activity": "study"
            })
            
            daily_tasks.append({
                "topic": f"{subject} practice",
                "subject": subject,
                "duration_minutes": int(daily_hours * 60 * 0.4),
                "priority": "medium",
                "activity": "practice"
            })
            
            schedule[date] = daily_tasks
        
        return schedule

# Singleton instance
planner_agent = StudyPlannerAgent() 