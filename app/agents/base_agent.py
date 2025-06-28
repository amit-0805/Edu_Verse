from abc import ABC, abstractmethod
from typing import Dict, Any, List, TypedDict
import uuid
from datetime import datetime
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import settings
from app.services.appwrite_service import appwrite_service
from app.services.mem0_service import mem0_service

class AgentState(TypedDict):
    """Base state class for all agents"""
    messages: List[Dict[str, Any]]
    user_id: str
    user_input: str
    context: Dict[str, Any]
    result: Dict[str, Any]

class BaseAgent(ABC):
    """Base class for all EduVerse agents"""
    
    def __init__(self):
        # Initialize Google Gemini LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",  # You can change this model here!
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.7,
            convert_system_message_to_human=True
        )
        self.graph = None
        self._build_graph()
    
    @abstractmethod
    def _build_graph(self):
        """Build the LangGraph workflow for this agent"""
        pass
    
    async def invoke(self, user_id: str, user_input: str, **kwargs) -> Dict[str, Any]:
        """Main entry point for agent invocation"""
        try:
            # Initialize state
            state: AgentState = {
                "user_id": user_id,
                "messages": [{"role": "user", "content": user_input}],
                "user_input": user_input,
                "context": kwargs,
                "result": {}
            }
            
            # Get user profile
            user_profile = await appwrite_service.get_user_profile(user_id)
            if user_profile:
                state["context"]["profile"] = user_profile
            
            # Run the agent workflow
            result = await self.graph.ainvoke(state)
            
            # Save interaction to memory
            await self._save_interaction(user_id, user_input, result["result"])
            
            return result["result"]
            
        except Exception as e:
            print(f"Agent error details: {str(e)}")
            print(f"State keys: {list(state.keys()) if 'state' in locals() else 'No state'}")
            import traceback
            traceback.print_exc()
            return {
                "error": f"Agent failed: {str(e)}",
                "agent": self.__class__.__name__,
                "debug_info": {
                    "state_keys": list(state.keys()) if 'state' in locals() else None,
                    "user_id": user_id,
                    "user_input": user_input[:100] if user_input else None
                }
            }
    
    async def _save_interaction(self, user_id: str, user_input: str, agent_response: Dict[str, Any]):
        """Save interaction to memory"""
        try:
            # Prepare memory data
            messages = [
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": str(agent_response)}
            ]
            
            # Add to Mem0
            await mem0_service.add_memory(
                user_id=user_id,
                messages=messages,
                metadata={
                    "agent": self.__class__.__name__,
                    "timestamp": self._get_current_timestamp(),
                    "response_type": agent_response.get("action", "response")
                }
            )
            
        except Exception as e:
            print(f"Failed to save interaction: {e}")
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        return datetime.utcnow().isoformat() 