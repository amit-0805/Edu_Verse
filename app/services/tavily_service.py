from tavily import TavilyClient
from app.config import settings
from typing import List, Dict, Any

class TavilyService:
    def __init__(self):
        self.client = TavilyClient(api_key=settings.TAVILY_API_KEY)
    
    async def search_educational_resources(self, topic: str, subject: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search for educational resources on a specific topic"""
        try:
            # Construct search query
            query = f"{topic} {subject} education tutorial learn"
            
            # Search with educational domains
            search_results = self.client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results,
                include_domains=[
                    "youtube.com",
                    "khanacademy.org", 
                    "coursera.org",
                    "edx.org",
                    "mit.edu",
                    "stanford.edu",
                    "harvard.edu",
                    "codecademy.com",
                    "udemy.com",
                    "pluralsight.com",
                    "wikipedia.org",
                    "britannica.com"
                ]
            )
            
            # Process and format results
            formatted_results = []
            for result in search_results.get('results', []):
                formatted_result = {
                    "title": result.get('title', ''),
                    "url": result.get('url', ''),
                    "description": result.get('content', ''),
                    "source": self._extract_domain(result.get('url', '')),
                    "type": self._determine_resource_type(result.get('url', '')),
                    "relevance_score": result.get('score', 0.0)
                }
                formatted_results.append(formatted_result)
            
            return formatted_results
            
        except Exception as e:
            raise Exception(f"Failed to search educational resources: {str(e)}")
    
    async def search_videos(self, topic: str, subject: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search specifically for video content"""
        try:
            query = f"{topic} {subject} video tutorial explanation"
            
            search_results = self.client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results,
                include_domains=[
                    "youtube.com",
                    "vimeo.com",
                    "khanacademy.org",
                    "coursera.org",
                    "edx.org"
                ]
            )
            
            video_results = []
            for result in search_results.get('results', []):
                if self._is_video_content(result.get('url', '')):
                    video_results.append({
                        "title": result.get('title', ''),
                        "url": result.get('url', ''),
                        "description": result.get('content', ''),
                        "source": self._extract_domain(result.get('url', '')),
                        "type": "video",
                        "relevance_score": result.get('score', 0.0)
                    })
            
            return video_results
            
        except Exception as e:
            raise Exception(f"Failed to search videos: {str(e)}")
    
    async def search_articles(self, topic: str, subject: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search specifically for articles and written content"""
        try:
            query = f"{topic} {subject} article guide explanation"
            
            search_results = self.client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results,
                include_domains=[
                    "wikipedia.org",
                    "britannica.com",
                    "khanacademy.org",
                    "mit.edu",
                    "stanford.edu",
                    "harvard.edu"
                ]
            )
            
            article_results = []
            for result in search_results.get('results', []):
                if not self._is_video_content(result.get('url', '')):
                    article_results.append({
                        "title": result.get('title', ''),
                        "url": result.get('url', ''),
                        "description": result.get('content', ''),
                        "source": self._extract_domain(result.get('url', '')),
                        "type": "article",
                        "relevance_score": result.get('score', 0.0)
                    })
            
            return article_results
            
        except Exception as e:
            raise Exception(f"Failed to search articles: {str(e)}")
    
    async def search_courses(self, topic: str, subject: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search specifically for online courses"""
        try:
            query = f"{topic} {subject} course online learning"
            
            search_results = self.client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results,
                include_domains=[
                    "coursera.org",
                    "edx.org",
                    "udemy.com",
                    "pluralsight.com",
                    "codecademy.com",
                    "khanacademy.org"
                ]
            )
            
            course_results = []
            for result in search_results.get('results', []):
                course_results.append({
                    "title": result.get('title', ''),
                    "url": result.get('url', ''),
                    "description": result.get('content', ''),
                    "source": self._extract_domain(result.get('url', '')),
                    "type": "course",
                    "relevance_score": result.get('score', 0.0)
                })
            
            return course_results
            
        except Exception as e:
            raise Exception(f"Failed to search courses: {str(e)}")
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.replace('www.', '')
        except:
            return "unknown"
    
    def _determine_resource_type(self, url: str) -> str:
        """Determine resource type based on URL"""
        url_lower = url.lower()
        
        if 'youtube.com' in url_lower or 'vimeo.com' in url_lower:
            return 'video'
        elif any(domain in url_lower for domain in ['coursera.org', 'edx.org', 'udemy.com']):
            return 'course'
        elif any(domain in url_lower for domain in ['wikipedia.org', 'britannica.com']):
            return 'article'
        else:
            return 'resource'
    
    def _is_video_content(self, url: str) -> bool:
        """Check if URL contains video content"""
        video_indicators = ['youtube.com', 'vimeo.com', 'video', 'watch']
        return any(indicator in url.lower() for indicator in video_indicators)

# Singleton instance
tavily_service = TavilyService() 