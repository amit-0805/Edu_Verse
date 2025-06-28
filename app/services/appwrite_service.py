from appwrite.client import Client
from appwrite.services.account import Account
from appwrite.services.databases import Databases
from appwrite.services.storage import Storage
from appwrite.exception import AppwriteException
from app.config import settings
import uuid
from typing import Dict, Any, Optional, List

class AppwriteService:
    def __init__(self):
        self.client = Client()
        self.client.set_endpoint(settings.APPWRITE_ENDPOINT)
        self.client.set_project(settings.APPWRITE_PROJECT_ID)
        self.client.set_key(settings.APPWRITE_API_KEY)
        
        self.account = Account(self.client)
        self.databases = Databases(self.client)
        self.storage = Storage(self.client)
        
        # Database and Collection IDs
        self.database_id = "eduverse_db"
        self.collections = {
            "users": "users",
            "tutoring_sessions": "tutoring_sessions",
            "study_schedules": "study_schedules",
            "curated_resources": "curated_resources",
            "exam_results": "exam_results",
            # NEW COLLECTIONS FOR SYLLABUS AGENT
            "syllabus_analysis": "syllabus_analysis",
            "learning_paths": "learning_paths",
            "syllabus_resources": "syllabus_resources"
        }
    
    async def create_user(self, name: str, email: str, password: str) -> Dict[str, Any]:
        """Create a new user account"""
        try:
            user_id = str(uuid.uuid4())
            user = self.account.create(
                user_id=user_id,
                email=email,
                password=password,
                name=name
            )
            
            # Create user profile in database
            profile = await self.create_user_profile(user_id, name, email)
            
            return {
                "user_id": user_id,
                "name": name,
                "email": email,
                "profile": profile
            }
        except AppwriteException as e:
            raise Exception(f"Failed to create user: {str(e)}")
    
    async def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user and return session"""
        try:
            session = self.account.create_email_password_session(email, password)
            return session
        except AppwriteException as e:
            raise Exception(f"Authentication failed: {str(e)}")
    
    async def create_user_profile(self, user_id: str, name: str, email: str) -> Dict[str, Any]:
        """Create user profile in database"""
        try:
            profile_data = {
                "user_id": user_id,
                "name": name,
                "email": email,
                "grade": None,
                "subjects": "",  # Store as empty string instead of empty list
                "learning_style": None,
                "created_at": self._get_current_timestamp()
            }
            
            document = self.databases.create_document(
                database_id=self.database_id,
                collection_id=self.collections["users"],
                document_id=user_id,
                data=profile_data
            )
            return document
        except AppwriteException as e:
            raise Exception(f"Failed to create user profile: {str(e)}")
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile from database"""
        try:
            document = self.databases.get_document(
                database_id=self.database_id,
                collection_id=self.collections["users"],
                document_id=user_id
            )
            # Convert subjects string back to list for consistency with models
            if document and "subjects" in document:
                subjects_str = document["subjects"]
                document["subjects"] = subjects_str.split(",") if subjects_str else []
            
            return document
        except AppwriteException:
            return None
    
    async def update_user_profile(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile"""
        try:
            # Convert subjects list to string if present
            if "subjects" in data and isinstance(data["subjects"], list):
                data["subjects"] = ",".join(data["subjects"]) if data["subjects"] else ""
            
            document = self.databases.update_document(
                database_id=self.database_id,
                collection_id=self.collections["users"],
                document_id=user_id,
                data=data
            )
            return document
        except AppwriteException as e:
            raise Exception(f"Failed to update user profile: {str(e)}")
    
    async def save_tutoring_session(self, user_id: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save tutoring session to database"""
        try:
            session_id = str(uuid.uuid4())
            data = {
                **session_data,
                "user_id": user_id,
                "session_id": session_id,
                "timestamp": self._get_current_timestamp()
            }
            
            document = self.databases.create_document(
                database_id=self.database_id,
                collection_id=self.collections["tutoring_sessions"],
                document_id=session_id,
                data=data
            )
            return document
        except AppwriteException as e:
            raise Exception(f"Failed to save tutoring session: {str(e)}")
    
    async def save_study_plan(self, user_id: str, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save study plan to database"""
        try:
            plan_id = str(uuid.uuid4())
            data = {
                **plan_data,
                "user_id": user_id,
                "plan_id": plan_id,
                "created_at": self._get_current_timestamp()
            }
            
            document = self.databases.create_document(
                database_id=self.database_id,
                collection_id=self.collections["study_schedules"],
                document_id=plan_id,
                data=data
            )
            return document
        except AppwriteException as e:
            raise Exception(f"Failed to save study plan: {str(e)}")
    
    async def save_curated_resources(self, user_id: str, resources_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save curated resources to database"""
        try:
            resource_id = str(uuid.uuid4())
            data = {
                **resources_data,
                "user_id": user_id,
                "resource_id": resource_id,
                "created_at": self._get_current_timestamp()
            }
            
            document = self.databases.create_document(
                database_id=self.database_id,
                collection_id=self.collections["curated_resources"],
                document_id=resource_id,
                data=data
            )
            return document
        except AppwriteException as e:
            raise Exception(f"Failed to save curated resources: {str(e)}")
    
    async def save_exam_result(self, user_id: str, exam_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save exam result to database"""
        try:
            result_id = str(uuid.uuid4())
            data = {
                **exam_data,
                "user_id": user_id,
                "result_id": result_id,
                "timestamp": self._get_current_timestamp()
            }
            
            document = self.databases.create_document(
                database_id=self.database_id,
                collection_id=self.collections["exam_results"],
                document_id=result_id,
                data=data
            )
            return document
        except AppwriteException as e:
            raise Exception(f"Failed to save exam result: {str(e)}")
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

    # NEW METHODS FOR SYLLABUS AGENT
    async def save_syllabus_analysis(self, user_id: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save syllabus analysis to database"""
        try:
            analysis_id = str(uuid.uuid4())
            data = {
                **analysis_data,
                "user_id": user_id,
                "analysis_id": analysis_id,
                "created_at": self._get_current_timestamp()
            }
            
            document = self.databases.create_document(
                database_id=self.database_id,
                collection_id=self.collections["syllabus_analysis"],
                document_id=analysis_id,
                data=data
            )
            return document
        except AppwriteException as e:
            raise Exception(f"Failed to save syllabus analysis: {str(e)}")

    async def save_learning_path(self, user_id: str, path_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save learning path to database"""
        try:
            path_id = str(uuid.uuid4())
            data = {
                **path_data,
                "user_id": user_id,
                "path_id": path_id,
                "created_at": self._get_current_timestamp()
            }
            
            document = self.databases.create_document(
                database_id=self.database_id,
                collection_id=self.collections["learning_paths"],
                document_id=path_id,
                data=data
            )
            return document
        except AppwriteException as e:
            raise Exception(f"Failed to save learning path: {str(e)}")

    async def save_syllabus_resources(self, user_id: str, resources_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Save syllabus resources to database"""
        try:
            saved_resources = []
            for resource in resources_data:
                resource_id = str(uuid.uuid4())
                data = {
                    **resource,
                    "user_id": user_id,
                    "resource_id": resource_id,
                    "created_at": self._get_current_timestamp()
                }
                
                document = self.databases.create_document(
                    database_id=self.database_id,
                    collection_id=self.collections["syllabus_resources"],
                    document_id=resource_id,
                    data=data
                )
                saved_resources.append(document)
            
            return saved_resources
        except AppwriteException as e:
            raise Exception(f"Failed to save syllabus resources: {str(e)}")

    async def get_user_learning_paths(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all learning paths for a user"""
        try:
            from appwrite.query import Query
            result = self.databases.list_documents(
                database_id=self.database_id,
                collection_id=self.collections["learning_paths"],
                queries=[Query.equal("user_id", user_id)]
            )
            return result["documents"]
        except AppwriteException as e:
            raise Exception(f"Failed to get learning paths: {str(e)}")

    async def get_learning_path_resources(self, path_id: str) -> List[Dict[str, Any]]:
        """Get all resources for a specific learning path"""
        try:
            from appwrite.query import Query
            result = self.databases.list_documents(
                database_id=self.database_id,
                collection_id=self.collections["syllabus_resources"],
                queries=[Query.equal("path_id", path_id)]
            )
            return result["documents"]
        except AppwriteException as e:
            raise Exception(f"Failed to get learning path resources: {str(e)}")

# Singleton instance
appwrite_service = AppwriteService() 