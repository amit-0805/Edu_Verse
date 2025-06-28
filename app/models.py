from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class LearningStyle(str, Enum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING_WRITING = "reading_writing"

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserProfile(BaseModel):
    user_id: str
    name: str
    email: str
    grade: Optional[str] = None
    subjects: List[str] = []
    learning_style: Optional[LearningStyle] = None

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    grade: Optional[str] = None
    subjects: Optional[List[str]] = None
    learning_style: Optional[LearningStyle] = None

class TutorRequest(BaseModel):
    topic: str
    subject: Optional[str] = None
    difficulty_level: Optional[str] = "medium"

class TutorResponse(BaseModel):
    explanation: str
    examples: List[str]
    additional_resources: List[str]
    session_id: str

class StudyPlanRequest(BaseModel):
    subjects: List[str]
    days_ahead: int = 7
    daily_hours: int = 2

class StudyTask(BaseModel):
    topic: str
    subject: str
    duration_minutes: int
    priority: str
    resources: List[str]

class StudyPlan(BaseModel):
    plan_id: str
    start_date: datetime
    end_date: datetime
    daily_tasks: Dict[str, List[StudyTask]]
    total_hours: int

class ResourceRequest(BaseModel):
    topic: str
    subject: str
    resource_types: List[str] = ["video", "article", "course"]

class Resource(BaseModel):
    title: str
    url: str
    type: str
    description: str
    rating: Optional[float] = None
    source: str

class ResourceResponse(BaseModel):
    resources: List[Resource]
    search_query: str
    total_found: int

class ExamRequest(BaseModel):
    topic: str
    subject: str
    question_count: int = 10
    difficulty: str = "medium"
    question_types: List[str] = ["mcq", "short_answer"]

class Question(BaseModel):
    id: str
    question: str
    type: str
    options: Optional[List[str]] = None
    correct_answer: str
    explanation: str

class ExamSession(BaseModel):
    exam_id: str
    questions: List[Question]
    time_limit_minutes: int
    topic: str
    subject: str

class Answer(BaseModel):
    question_id: str
    user_answer: str

class ExamSubmission(BaseModel):
    exam_id: str
    answers: List[Answer]

class ExamResult(BaseModel):
    exam_id: str
    score: float
    total_questions: int
    correct_answers: int
    feedback: str
    weak_areas: List[str]
    question_results: List[Dict[str, Any]]

# NEW MODELS FOR SYLLABUS AGENT
class SyllabusUploadRequest(BaseModel):
    syllabus_content: str
    subject: str
    course_name: Optional[str] = None
    semester: Optional[str] = None
    difficulty_level: Optional[str] = "medium"

class LearningPathTopic(BaseModel):
    topic_id: str
    title: str
    description: str
    week_number: int
    estimated_hours: int
    prerequisites: List[str] = []
    learning_objectives: List[str] = []
    resources_found: int = 0

class LearningPath(BaseModel):
    path_id: str
    course_name: str
    subject: str
    total_weeks: int
    total_hours: int
    topics: List[LearningPathTopic]
    created_at: datetime

class SyllabusResource(BaseModel):
    resource_id: str
    topic_id: str
    title: str
    url: str
    type: str  # video, article, course, documentation
    description: str
    difficulty_level: str
    estimated_time_minutes: int
    source: str
    relevance_score: float

class SyllabusAnalysisResult(BaseModel):
    syllabus_id: str
    learning_path: LearningPath
    all_resources: List[SyllabusResource]
    total_resources_found: int
    coverage_analysis: Dict[str, Any]
    recommendations: List[str] 