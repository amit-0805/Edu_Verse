from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from app.agents.base_agent import BaseAgent, AgentState
from app.services.appwrite_service import appwrite_service
from app.services.tavily_service import tavily_service
from app.services.mem0_service import mem0_service
import uuid
import json

class ResourceCuratorAgent(BaseAgent):
    def __init__(self):
        super().__init__()
    
    def _build_graph(self):
        """Build the resource curator agent workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_request", self.analyze_request_node)
        workflow.add_node("search_resources", self.search_resources_node)
        workflow.add_node("curate_and_rank", self.curate_and_rank_node)
        workflow.add_node("save_resources", self.save_resources_node)
        
        # Add edges
        workflow.add_edge("analyze_request", "search_resources")
        workflow.add_edge("search_resources", "curate_and_rank")
        workflow.add_edge("curate_and_rank", "save_resources")
        workflow.add_edge("save_resources", END)
        
        # Set entry point
        workflow.set_entry_point("analyze_request")
        
        self.graph = workflow.compile()
    
    async def analyze_request_node(self, state: AgentState) -> AgentState:
        """Analyze the resource request"""
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
        Analyze this resource request:
        Request: "{user_message}"
        
        Extract:
        1. Topic/subject to find resources for
        2. Preferred resource types (video, article, course, etc.)
        3. Difficulty level
        4. Specific requirements or preferences
        
        Return as JSON with keys: topic, subject, resource_types, difficulty, requirements
        """
        
        try:
            response = await self.llm.ainvoke([HumanMessage(content=analysis_prompt)])
            
            try:
                analysis = json.loads(response.content)
            except:
                # Fallback analysis
                analysis = {
                    "topic": user_message,
                    "subject": "general",
                    "resource_types": ["video", "article", "course"],
                    "difficulty": "medium",
                    "requirements": []
                }
            
            state["context"]["analysis"] = analysis
            
        except Exception as e:
            state["context"]["analysis"] = {
                "topic": user_message,
                "subject": "general",
                "resource_types": ["video", "article", "course"],
                "difficulty": "medium",
                "requirements": [],
                "error": str(e)
            }
        
        return state
    
    async def search_resources_node(self, state: AgentState) -> AgentState:
        """Search for resources using Tavily"""
        analysis = state["context"]["analysis"]
        topic = analysis.get("topic", "")
        subject = analysis.get("subject", "general")
        resource_types = analysis.get("resource_types", ["video", "article", "course"])
        
        all_resources = []
        
        try:
            # Search for different types of resources
            if "video" in resource_types:
                videos = await tavily_service.search_videos(topic, subject, max_results=5)
                all_resources.extend(videos)
            
            if "article" in resource_types:
                articles = await tavily_service.search_articles(topic, subject, max_results=5)
                all_resources.extend(articles)
            
            if "course" in resource_types:
                courses = await tavily_service.search_courses(topic, subject, max_results=3)
                all_resources.extend(courses)
            
            # If no specific types requested, search for all
            if not any(rt in resource_types for rt in ["video", "article", "course"]):
                general_resources = await tavily_service.search_educational_resources(topic, subject, max_results=10)
                all_resources.extend(general_resources)
            
            state["context"]["raw_resources"] = all_resources
            
        except Exception as e:
            state["context"]["search_error"] = str(e)
            state["context"]["raw_resources"] = []
        
        return state
    
    async def curate_and_rank_node(self, state: AgentState) -> AgentState:
        """Curate and rank the found resources using LLM"""
        user_profile = state["context"].get("profile", {})
        analysis = state["context"]["analysis"]
        raw_resources = state["context"].get("raw_resources", [])
        weak_areas = state["context"].get("weak_areas", [])
        
        if not raw_resources:
            state["result"] = {
                "error": "No resources found",
                "resources": [],
                "total_found": 0
            }
            return state
        
        # Build curation prompt
        curation_prompt = f"""
        You are an expert educational content curator. Review and rank these resources for a student.
        
        Student Request: {analysis.get('topic', '')} in {analysis.get('subject', '')}
        Student Profile:
        - Learning Style: {user_profile.get('learning_style', 'visual')}
        - Grade: {user_profile.get('grade', '')}
        - Weak Areas: {weak_areas}
        - Difficulty Level: {analysis.get('difficulty', 'medium')}
        
        Resources to evaluate:
        {json.dumps(raw_resources[:15], indent=2)}
        
        Instructions:
        1. Rank resources by educational quality and relevance
        2. Filter out low-quality or irrelevant content
        3. Prioritize resources that match the student's learning style
        4. Include a brief explanation of why each resource is valuable
        5. Ensure variety in resource types and sources
        6. Consider the student's grade level and weak areas
        
        Return as JSON with:
        - curated_resources: array of top resources with enhanced descriptions
        - total_found: number of resources found
        - search_summary: brief summary of what was found
        - recommendations: specific recommendations based on student profile
        
        Each resource should have: title, url, type, description, rating (1-5), source, why_recommended
        """
        
        try:
            response = await self.llm.ainvoke([HumanMessage(content=curation_prompt)])
            
            try:
                curation_data = json.loads(response.content)
                
                # Ensure we have the required structure
                if "curated_resources" not in curation_data:
                    curation_data["curated_resources"] = raw_resources[:8]  # Fallback
                
                # Generate resource collection ID
                collection_id = str(uuid.uuid4())
                
                state["result"] = {
                    "collection_id": collection_id,
                    "topic": analysis.get('topic', ''),
                    "subject": analysis.get('subject', ''),
                    **curation_data
                }
                
            except Exception as parse_error:
                # Fallback curation
                curated = []
                for i, resource in enumerate(raw_resources[:8]):
                    curated.append({
                        **resource,
                        "rating": 4.0,  # Default rating
                        "why_recommended": "Quality educational content from trusted source"
                    })
                
                state["result"] = {
                    "collection_id": str(uuid.uuid4()),
                    "topic": analysis.get('topic', ''),
                    "subject": analysis.get('subject', ''),
                    "curated_resources": curated,
                    "total_found": len(raw_resources),
                    "search_summary": f"Found {len(raw_resources)} resources for {analysis.get('topic', '')}",
                    "recommendations": ["Review multiple sources", "Start with videos for visual learning"],
                    "parse_error": str(parse_error)
                }
                
        except Exception as e:
            state["result"] = {
                "error": f"Failed to curate resources: {str(e)}",
                "collection_id": str(uuid.uuid4()),
                "curated_resources": raw_resources[:5],  # Return some resources anyway
                "total_found": len(raw_resources)
            }
        
        return state
    
    async def save_resources_node(self, state: AgentState) -> AgentState:
        """Save the curated resources to Appwrite and Mem0"""
        user_id = state["user_id"]
        result = state["result"]
        
        try:
            # Prepare resource data for Appwrite
            # Note: curated_resources needs to be JSON string, but recommendations should be array
            curated_resources = result.get("curated_resources", [])
            recommendations = result.get("recommendations", [])
            
            resource_data = {
                "collection_id": result.get("collection_id"),
                "topic": result.get("topic", ""),
                "subject": result.get("subject", ""),
                "curated_resources": json.dumps(curated_resources) if curated_resources else "[]",
                "total_found": result.get("total_found", 0),
                "search_summary": result.get("search_summary", ""),
                "recommendations": recommendations  # Keep as array for Appwrite
            }
            
            # Save to Appwrite
            saved_resources = await appwrite_service.save_curated_resources(user_id, resource_data)
            
            # Add resource summary to Mem0
            resource_summary = f"Found {result.get('total_found', 0)} resources for {result.get('topic', '')} in {result.get('subject', '')}"
            await mem0_service.add_memory(
                user_id=user_id,
                messages=[
                    {"role": "user", "content": f"Find resources for {result.get('topic', '')}"},
                    {"role": "assistant", "content": resource_summary}
                ],
                metadata={
                    "type": "resource_search",
                    "collection_id": result.get("collection_id"),
                    "topic": result.get("topic", ""),
                    "subject": result.get("subject", ""),
                    "resource_count": result.get("total_found", 0),
                    "timestamp": self._get_current_timestamp()
                }
            )
            
            state["result"]["saved"] = True
            state["result"]["appwrite_id"] = saved_resources.get("$id")
            
        except Exception as e:
            state["result"]["save_error"] = str(e)
        
        return state

# Singleton instance
curator_agent = ResourceCuratorAgent() 