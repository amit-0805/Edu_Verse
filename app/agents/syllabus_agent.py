from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from app.agents.base_agent import BaseAgent, AgentState
from app.services.appwrite_service import appwrite_service
from app.services.tavily_service import tavily_service
from app.services.mem0_service import mem0_service
import uuid
import json
import re

class SyllabusAgent(BaseAgent):
    def __init__(self):
        super().__init__()
    
    def _build_graph(self):
        """Build the syllabus agent workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("parse_syllabus", self.parse_syllabus_node)
        workflow.add_node("generate_learning_path", self.generate_learning_path_node)
        workflow.add_node("find_resources", self.find_resources_node)
        workflow.add_node("analyze_coverage", self.analyze_coverage_node)
        workflow.add_node("save_analysis", self.save_analysis_node)
        
        # Add edges
        workflow.add_edge("parse_syllabus", "generate_learning_path")
        workflow.add_edge("generate_learning_path", "find_resources")
        workflow.add_edge("find_resources", "analyze_coverage")
        workflow.add_edge("analyze_coverage", "save_analysis")
        workflow.add_edge("save_analysis", END)
        
        # Set entry point
        workflow.set_entry_point("parse_syllabus")
        
        self.graph = workflow.compile()
    
    async def parse_syllabus_node(self, state: AgentState) -> AgentState:
        """Parse and analyze the syllabus content"""
        syllabus_content = state["context"].get("syllabus_content", "")
        subject = state["context"].get("subject", "General")
        course_name = state["context"].get("course_name", "")
        
        if not syllabus_content:
            state["context"]["parse_error"] = "No syllabus content provided"
            return state
        
        parsing_prompt = f"""
        Analyze this syllabus content and extract structured information:
        
        SYLLABUS CONTENT:
        {syllabus_content}
        
        Subject: {subject}
        Course: {course_name}
        
        Extract and organize:
        1. Course overview and objectives
        2. Main topics/chapters with descriptions
        3. Weekly or module breakdown if available
        4. Prerequisites mentioned
        5. Learning objectives for each topic
        6. Estimated time/duration for each topic
        7. Assessment methods mentioned
        
        Return as JSON with:
        - course_overview: string description
        - main_topics: array of objects with {{title, description, week_number, estimated_hours, prerequisites, learning_objectives}}
        - total_duration_weeks: number
        - assessment_methods: array of strings
        - overall_difficulty: string (beginner/intermediate/advanced)
        - key_skills: array of skills students will gain
        """
        
        try:
            response = await self.llm.ainvoke([HumanMessage(content=parsing_prompt)])
            
            try:
                parsed_data = json.loads(response.content)
            except:
                # Fallback parsing
                parsed_data = {
                    "course_overview": "Course analysis available",
                    "main_topics": self._extract_topics_fallback(syllabus_content),
                    "total_duration_weeks": 12,
                    "assessment_methods": ["assignments", "exams"],
                    "overall_difficulty": "intermediate",
                    "key_skills": []
                }
            
            state["context"]["parsed_syllabus"] = parsed_data
            
        except Exception as e:
            state["context"]["parse_error"] = str(e)
            # Provide minimal fallback
            state["context"]["parsed_syllabus"] = {
                "course_overview": "Error parsing syllabus",
                "main_topics": [],
                "total_duration_weeks": 12,
                "assessment_methods": [],
                "overall_difficulty": "intermediate",
                "key_skills": []
            }
        
        return state
    
    async def generate_learning_path_node(self, state: AgentState) -> AgentState:
        """Generate a structured learning path from parsed syllabus"""
        parsed_data = state["context"].get("parsed_syllabus", {})
        user_profile = state["context"].get("profile", {})
        subject = state["context"].get("subject", "General")
        course_name = state["context"].get("course_name", "Course")
        
        learning_style = user_profile.get("learning_style", "visual")
        grade = user_profile.get("grade", "")
        
        path_prompt = f"""
        Create a detailed learning path based on this syllabus analysis:
        
        Course: {course_name}
        Subject: {subject}
        Overview: {parsed_data.get('course_overview', '')}
        Topics: {json.dumps(parsed_data.get('main_topics', []), indent=2)}
        Duration: {parsed_data.get('total_duration_weeks', 12)} weeks
        Difficulty: {parsed_data.get('overall_difficulty', 'intermediate')}
        
        Student Profile:
        - Learning Style: {learning_style}
        - Grade Level: {grade}
        
        Create an optimized learning path with:
        1. Logical topic sequencing based on prerequisites
        2. Realistic time estimates for each topic
        3. Learning objectives for each topic
        4. Suggested learning activities for their learning style
        5. Milestone checkpoints
        6. Review and assessment points
        
        Return as JSON with:
        - path_id: unique identifier
        - course_name: string
        - subject: string
        - total_weeks: number
        - total_estimated_hours: number
        - learning_path: array of topics with {{topic_id, title, description, week_number, estimated_hours, prerequisites, learning_objectives, activities}}
        - milestones: array of checkpoint weeks
        - recommended_pace: string description
        """
        
        try:
            response = await self.llm.ainvoke([HumanMessage(content=path_prompt)])
            
            try:
                learning_path = json.loads(response.content)
                
                # Ensure we have required fields
                learning_path["path_id"] = str(uuid.uuid4())
                learning_path["course_name"] = course_name
                learning_path["subject"] = subject
                
            except:
                # Fallback learning path
                learning_path = self._create_fallback_learning_path(
                    parsed_data, course_name, subject
                )
            
            state["context"]["learning_path"] = learning_path
            
        except Exception as e:
            state["context"]["path_generation_error"] = str(e)
            # Create minimal fallback
            state["context"]["learning_path"] = self._create_fallback_learning_path(
                parsed_data, course_name, subject
            )
        
        return state
    
    async def find_resources_node(self, state: AgentState) -> AgentState:
        """Find educational resources for each topic using Tavily"""
        learning_path = state["context"].get("learning_path", {})
        subject = state["context"].get("subject", "General")
        
        all_resources = []
        topics = learning_path.get("learning_path", [])
        
        if not topics:
            state["context"]["resource_error"] = "No topics found in learning path"
            state["context"]["all_resources"] = []
            return state
        
        try:
            for topic in topics[:10]:  # Limit to first 10 topics to avoid rate limits
                topic_title = topic.get("title", "")
                topic_id = topic.get("topic_id", str(uuid.uuid4()))
                
                if not topic_title:
                    continue
                
                # Search for various types of resources
                try:
                    # Get videos
                    videos = await tavily_service.search_videos(topic_title, subject, max_results=3)
                    for video in videos:
                        all_resources.append({
                            "resource_id": str(uuid.uuid4()),
                            "topic_id": topic_id,
                            "path_id": learning_path.get("path_id"),
                            "title": video.get("title", ""),
                            "url": video.get("url", ""),
                            "type": "video",
                            "description": video.get("description", ""),
                            "source": video.get("source", ""),
                            "relevance_score": video.get("relevance_score", 0.8),
                            "difficulty_level": topic.get("difficulty", "medium"),
                            "estimated_time_minutes": 30
                        })
                    
                    # Get articles
                    articles = await tavily_service.search_articles(topic_title, subject, max_results=2)
                    for article in articles:
                        all_resources.append({
                            "resource_id": str(uuid.uuid4()),
                            "topic_id": topic_id,
                            "path_id": learning_path.get("path_id"),
                            "title": article.get("title", ""),
                            "url": article.get("url", ""),
                            "type": "article",
                            "description": article.get("description", ""),
                            "source": article.get("source", ""),
                            "relevance_score": article.get("relevance_score", 0.7),
                            "difficulty_level": topic.get("difficulty", "medium"),
                            "estimated_time_minutes": 15
                        })
                    
                    # Get courses
                    courses = await tavily_service.search_courses(topic_title, subject, max_results=1)
                    for course in courses:
                        all_resources.append({
                            "resource_id": str(uuid.uuid4()),
                            "topic_id": topic_id,
                            "path_id": learning_path.get("path_id"),
                            "title": course.get("title", ""),
                            "url": course.get("url", ""),
                            "type": "course",
                            "description": course.get("description", ""),
                            "source": course.get("source", ""),
                            "relevance_score": course.get("relevance_score", 0.9),
                            "difficulty_level": topic.get("difficulty", "medium"),
                            "estimated_time_minutes": 120
                        })
                        
                except Exception as topic_error:
                    print(f"Error finding resources for topic {topic_title}: {topic_error}")
                    continue
            
            state["context"]["all_resources"] = all_resources
            
        except Exception as e:
            state["context"]["resource_error"] = str(e)
            state["context"]["all_resources"] = []
        
        return state
    
    async def analyze_coverage_node(self, state: AgentState) -> AgentState:
        """Analyze resource coverage and provide recommendations"""
        learning_path = state["context"].get("learning_path", {})
        all_resources = state["context"].get("all_resources", [])
        
        topics = learning_path.get("learning_path", [])
        
        coverage_analysis = {
            "total_topics": len(topics),
            "topics_with_resources": 0,
            "total_resources": len(all_resources),
            "resource_distribution": {"video": 0, "article": 0, "course": 0},
            "average_resources_per_topic": 0,
            "well_covered_topics": [],
            "under_covered_topics": []
        }
        
        # Analyze coverage
        topic_resource_count = {}
        for resource in all_resources:
            topic_id = resource.get("topic_id")
            resource_type = resource.get("type", "unknown")
            
            if topic_id not in topic_resource_count:
                topic_resource_count[topic_id] = 0
            topic_resource_count[topic_id] += 1
            
            if resource_type in coverage_analysis["resource_distribution"]:
                coverage_analysis["resource_distribution"][resource_type] += 1
        
        coverage_analysis["topics_with_resources"] = len(topic_resource_count)
        
        if topics:
            coverage_analysis["average_resources_per_topic"] = len(all_resources) / len(topics)
        
        # Categorize topics by coverage
        for topic in topics:
            topic_id = topic.get("topic_id")
            resource_count = topic_resource_count.get(topic_id, 0)
            
            if resource_count >= 3:
                coverage_analysis["well_covered_topics"].append(topic.get("title", ""))
            elif resource_count < 2:
                coverage_analysis["under_covered_topics"].append(topic.get("title", ""))
        
        # Generate recommendations
        recommendations = []
        
        if coverage_analysis["under_covered_topics"]:
            recommendations.append(f"Need more resources for: {', '.join(coverage_analysis['under_covered_topics'][:3])}")
        
        if coverage_analysis["resource_distribution"]["video"] < coverage_analysis["total_resources"] * 0.3:
            recommendations.append("Consider adding more video content for visual learners")
        
        if coverage_analysis["average_resources_per_topic"] < 2:
            recommendations.append("Each topic should have at least 2-3 different resource types")
        
        if not recommendations:
            recommendations.append("Excellent resource coverage! Ready to start learning.")
        
        state["context"]["coverage_analysis"] = coverage_analysis
        state["context"]["recommendations"] = recommendations
        
        return state
    
    async def save_analysis_node(self, state: AgentState) -> AgentState:
        """Save the complete syllabus analysis to database"""
        user_id = state["user_id"]
        learning_path = state["context"].get("learning_path", {})
        all_resources = state["context"].get("all_resources", [])
        coverage_analysis = state["context"].get("coverage_analysis", {})
        recommendations = state["context"].get("recommendations", [])
        parsed_syllabus = state["context"].get("parsed_syllabus", {})
        
        try:
            # Generate analysis ID
            analysis_id = str(uuid.uuid4())
            
            # Save learning path - convert arrays to JSON strings for Appwrite
            path_data = {
                "path_id": learning_path.get("path_id"),
                "course_name": learning_path.get("course_name", ""),
                "subject": learning_path.get("subject", ""),
                "total_weeks": learning_path.get("total_weeks", 12),
                "total_estimated_hours": learning_path.get("total_estimated_hours", 0),
                "learning_path_topics": json.dumps(learning_path.get("learning_path", [])),
                "milestones": json.dumps(learning_path.get("milestones", [])),
                "recommended_pace": learning_path.get("recommended_pace", "")
            }
            
            saved_path = await appwrite_service.save_learning_path(user_id, path_data)
            
            # Save resources
            saved_resources = []
            if all_resources:
                saved_resources = await appwrite_service.save_syllabus_resources(user_id, all_resources)
            
            # Save complete analysis - convert complex data to JSON strings for Appwrite
            analysis_data = {
                "syllabus_id": analysis_id,
                "path_id": learning_path.get("path_id"),
                "course_overview": parsed_syllabus.get("course_overview", ""),
                "total_resources_found": len(all_resources),
                "coverage_analysis": json.dumps(coverage_analysis) if coverage_analysis else "{}",
                "recommendations": json.dumps(recommendations) if recommendations else "[]",
                "assessment_methods": json.dumps(parsed_syllabus.get("assessment_methods", [])),
                "key_skills": json.dumps(parsed_syllabus.get("key_skills", [])),
                "overall_difficulty": parsed_syllabus.get("overall_difficulty", "intermediate")
            }
            
            saved_analysis = await appwrite_service.save_syllabus_analysis(user_id, analysis_data)
            
            # Add to Mem0
            await mem0_service.add_memory(
                user_id=user_id,
                messages=[
                    {"role": "user", "content": f"Analyze syllabus for {learning_path.get('course_name', 'course')}"},
                    {"role": "assistant", "content": f"Created learning path with {len(learning_path.get('learning_path', []))} topics and found {len(all_resources)} resources"}
                ],
                metadata={
                    "type": "syllabus_analysis",
                    "analysis_id": analysis_id,
                    "path_id": learning_path.get("path_id"),
                    "course_name": learning_path.get("course_name", ""),
                    "subject": learning_path.get("subject", ""),
                    "topics_count": len(learning_path.get("learning_path", [])),
                    "resources_found": len(all_resources),
                    "timestamp": self._get_current_timestamp()
                }
            )
            
            # Prepare final result
            state["result"] = {
                "analysis_id": analysis_id,
                "learning_path": learning_path,
                "resources": all_resources,
                "coverage_analysis": coverage_analysis,
                "recommendations": recommendations,
                "total_resources_found": len(all_resources),
                "saved": True,
                "appwrite_path_id": saved_path.get("$id"),
                "appwrite_analysis_id": saved_analysis.get("$id")
            }
            
        except Exception as e:
            state["result"] = {
                "error": f"Failed to save analysis: {str(e)}",
                "analysis_id": str(uuid.uuid4()),
                "learning_path": learning_path,
                "resources": all_resources,
                "saved": False
            }
        
        return state
    
    def _extract_topics_fallback(self, content: str) -> List[Dict[str, Any]]:
        """Fallback method to extract topics from syllabus content"""
        topics = []
        lines = content.split('\n')
        
        topic_patterns = [
            r'chapter\s+\d+[:\-]\s*(.+)',
            r'week\s+\d+[:\-]\s*(.+)',
            r'module\s+\d+[:\-]\s*(.+)',
            r'unit\s+\d+[:\-]\s*(.+)',
            r'topic\s+\d+[:\-]\s*(.+)',
            r'^\d+\.\s*(.+)',
            r'^[IVX]+\.\s*(.+)'
        ]
        
        week_number = 1
        for line in lines:
            line = line.strip()
            if len(line) > 10:  # Reasonable topic length
                for pattern in topic_patterns:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        topics.append({
                            "topic_id": str(uuid.uuid4()),
                            "title": match.group(1).strip(),
                            "description": f"Topic covering {match.group(1).strip()}",
                            "week_number": week_number,
                            "estimated_hours": 3,
                            "prerequisites": [],
                            "learning_objectives": []
                        })
                        week_number += 1
                        break
        
        return topics[:15]  # Limit to 15 topics
    
    def _create_fallback_learning_path(self, parsed_data: Dict[str, Any], course_name: str, subject: str) -> Dict[str, Any]:
        """Create a fallback learning path"""
        topics = parsed_data.get("main_topics", [])
        
        if not topics:
            topics = [{
                "topic_id": str(uuid.uuid4()),
                "title": "Course Introduction",
                "description": "Introduction to the course content",
                "week_number": 1,
                "estimated_hours": 2,
                "prerequisites": [],
                "learning_objectives": []
            }]
        
        return {
            "path_id": str(uuid.uuid4()),
            "course_name": course_name,
            "subject": subject,
            "total_weeks": len(topics),
            "total_estimated_hours": sum(t.get("estimated_hours", 3) for t in topics),
            "learning_path": topics,
            "milestones": [i for i in range(1, len(topics) + 1, 3)],
            "recommended_pace": "Follow weekly schedule with regular review"
        }

# Singleton instance
syllabus_agent = SyllabusAgent() 