from mem0 import Memory
from app.config import settings
from typing import List, Dict, Any, Optional

class Mem0Service:
    def __init__(self):
        # Simplified config - let Mem0 handle defaults
        config = {
            "vector_store": {
                "provider": "chroma",
                "config": {
                    "collection_name": "eduverse_memory",
                    "path": "./chroma_db"
                }
            },
            "embedder": {
                "provider": "openai",
                "config": {
                    "api_key": settings.OPENAI_API_KEY,
                    "model": "text-embedding-3-small"
                }
            }
        }
        self.memory = Memory.from_config(config)
    
    async def add_memory(self, user_id: str, messages: List[Dict[str, str]], metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a new memory for a user"""
        try:
            result = self.memory.add(
                messages=messages,
                user_id=user_id,
                metadata=metadata or {}
            )
            return result
        except Exception as e:
            raise Exception(f"Failed to add memory: {str(e)}")
    
    async def search_memory(self, user_id: str, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for memories related to a query"""
        try:
            results = self.memory.search(
                query=query,
                user_id=user_id,
                limit=limit
            )
            return results
        except Exception as e:
            raise Exception(f"Failed to search memory: {str(e)}")
    
    async def get_all_memories(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all memories for a user"""
        try:
            memories = self.memory.get_all(user_id=user_id)
            return memories
        except Exception as e:
            raise Exception(f"Failed to get memories: {str(e)}")
    
    async def update_memory(self, memory_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing memory"""
        try:
            result = self.memory.update(memory_id=memory_id, data=data)
            return result
        except Exception as e:
            raise Exception(f"Failed to update memory: {str(e)}")
    
    async def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory"""
        try:
            self.memory.delete(memory_id=memory_id)
            return True
        except Exception as e:
            raise Exception(f"Failed to delete memory: {str(e)}")
    
    async def add_learning_context(self, user_id: str, topic: str, context: str, performance: str = "neutral"):
        """Add learning context for a specific topic"""
        messages = [
            {"role": "user", "content": f"Learning about: {topic}"},
            {"role": "assistant", "content": context}
        ]
        
        metadata = {
            "type": "learning_context",
            "topic": topic,
            "performance": performance,  # good, poor, neutral
            "timestamp": self._get_current_timestamp()
        }
        
        return await self.add_memory(user_id, messages, metadata)
    
    async def add_difficulty_context(self, user_id: str, topic: str, difficulty: str, details: str):
        """Add context about user's difficulty with a topic"""
        messages = [
            {"role": "user", "content": f"Having difficulty with: {topic}"},
            {"role": "assistant", "content": f"Difficulty level: {difficulty}. Details: {details}"}
        ]
        
        metadata = {
            "type": "difficulty",
            "topic": topic,
            "difficulty_level": difficulty,
            "timestamp": self._get_current_timestamp()
        }
        
        return await self.add_memory(user_id, messages, metadata)
    
    async def add_exam_performance(self, user_id: str, topic: str, score: float, weak_areas: List[str]):
        """Add exam performance context"""
        messages = [
            {"role": "user", "content": f"Exam completed for: {topic}"},
            {"role": "assistant", "content": f"Score: {score}%. Weak areas: {', '.join(weak_areas)}"}
        ]
        
        metadata = {
            "type": "exam_performance",
            "topic": topic,
            "score": score,
            "weak_areas": weak_areas,
            "timestamp": self._get_current_timestamp()
        }
        
        return await self.add_memory(user_id, messages, metadata)
    
    async def get_learning_history(self, user_id: str, topic: str) -> List[Dict[str, Any]]:
        """Get learning history for a specific topic"""
        try:
            results = await self.search_memory(user_id, f"topic:{topic}")
            return [r for r in results if r.get('metadata', {}).get('topic') == topic]
        except Exception as e:
            raise Exception(f"Failed to get learning history: {str(e)}")
    
    async def get_weak_areas(self, user_id: str) -> List[str]:
        """Get user's weak areas based on memory"""
        try:
            memories = await self.get_all_memories(user_id)
            weak_areas = []
            
            for memory in memories:
                metadata = memory.get('metadata', {})
                if metadata.get('type') == 'difficulty':
                    weak_areas.append(metadata.get('topic'))
                elif metadata.get('type') == 'exam_performance':
                    weak_areas.extend(metadata.get('weak_areas', []))
            
            return list(set(weak_areas))  # Remove duplicates
        except Exception as e:
            raise Exception(f"Failed to get weak areas: {str(e)}")
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

# Singleton instance
mem0_service = Mem0Service() 