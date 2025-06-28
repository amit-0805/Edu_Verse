from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Form
from app.models import TutorRequest, StudyPlanRequest, ResourceRequest, ExamRequest, ExamSubmission, SyllabusUploadRequest
from app.agents.tutor_agent import tutor_agent
from app.agents.planner_agent import planner_agent
from app.agents.curator_agent import curator_agent
from app.agents.exam_agent import exam_agent
from app.agents.syllabus_agent import syllabus_agent
from typing import Dict, Any
import io
import PyPDF2
import docx

router = APIRouter(prefix="/agents", tags=["agents"])

async def _extract_file_content(file: UploadFile) -> str:
    """Extract text content from uploaded file"""
    try:
        content = await file.read()
        
        # Handle PDF files
        if file.content_type == "application/pdf" or file.filename.lower().endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        
        # Handle Word documents
        elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document" or file.filename.lower().endswith('.docx'):
            doc = docx.Document(io.BytesIO(content))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        
        # Handle plain text files
        elif file.content_type == "text/plain" or file.filename.lower().endswith('.txt'):
            return content.decode('utf-8').strip()
        
        # Handle other text-based files (try UTF-8 decoding)
        else:
            try:
                return content.decode('utf-8').strip()
            except UnicodeDecodeError:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Unsupported file type: {file.content_type}. Please upload PDF, DOCX, or TXT files."
                )
                
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error processing file: {str(e)}"
        )

@router.post("/tutor/{user_id}", response_model=Dict[str, Any])
async def get_tutoring(user_id: str, request: TutorRequest):
    """Get personalized tutoring explanation"""
    try:
        # Format the tutoring request
        user_input = f"Explain {request.topic}"
        if request.subject:
            user_input += f" in {request.subject}"
        if request.difficulty_level:
            user_input += f" at {request.difficulty_level} level"
        
        # Run the tutor agent
        result = await tutor_agent.invoke(
            user_id=user_id,
            user_input=user_input,
            subject=request.subject,
            difficulty_level=request.difficulty_level
        )
        
        return {
            "success": True,
            "agent": "tutor",
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/planner/{user_id}", response_model=Dict[str, Any])
async def create_study_plan(user_id: str, request: StudyPlanRequest):
    """Generate personalized study plan"""
    try:
        # Format the planning request
        user_input = f"Create a study plan for {', '.join(request.subjects)}"
        user_input += f" for {request.days_ahead} days"
        user_input += f" with {request.daily_hours} hours of daily study"
        
        # Run the planner agent
        result = await planner_agent.invoke(
            user_id=user_id,
            user_input=user_input,
            subjects=request.subjects,
            days_ahead=request.days_ahead,
            daily_hours=request.daily_hours
        )
        
        return {
            "success": True,
            "agent": "study_planner",
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/curator/{user_id}", response_model=Dict[str, Any])
async def curate_resources(user_id: str, request: ResourceRequest):
    """Find and curate educational resources"""
    try:
        # Format the resource request
        user_input = f"Find {', '.join(request.resource_types)} resources for {request.topic} in {request.subject}"
        
        # Run the curator agent
        result = await curator_agent.invoke(
            user_id=user_id,
            user_input=user_input,
            topic=request.topic,
            subject=request.subject,
            resource_types=request.resource_types
        )
        
        return {
            "success": True,
            "agent": "resource_curator",
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/exam/create/{user_id}", response_model=Dict[str, Any])
async def create_exam(user_id: str, request: ExamRequest):
    """Generate practice exam"""
    try:
        # Format the exam request
        user_input = f"Create a {request.difficulty} exam on {request.topic} in {request.subject}"
        user_input += f" with {request.question_count} questions"
        user_input += f" of types: {', '.join(request.question_types)}"
        
        # Run the exam agent
        result = await exam_agent.invoke(
            user_id=user_id,
            user_input=user_input,
            topic=request.topic,
            subject=request.subject,
            question_count=request.question_count,
            difficulty=request.difficulty,
            question_types=request.question_types
        )
        
        return {
            "success": True,
            "agent": "exam_coach",
            "action": "exam_created",
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/exam/evaluate/{user_id}", response_model=Dict[str, Any])
async def evaluate_exam(user_id: str, submission: ExamSubmission):
    """Evaluate exam answers"""
    try:
        # Format the evaluation request
        answers_dict = {answer.question_id: answer.user_answer for answer in submission.answers}
        user_input = f"Evaluate exam {submission.exam_id} with answers: {answers_dict}"
        
        # Run the exam agent with evaluation
        result = await exam_agent.invoke(
            user_id=user_id,
            user_input=user_input,
            exam_id=submission.exam_id,
            answers_provided=answers_dict,
            action_type="evaluate"
        )
        
        return {
            "success": True,
            "agent": "exam_coach",
            "action": "answers_evaluated",
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status", response_model=Dict[str, Any])
async def get_agent_status():
    """Get status of all agents"""
    try:
        return {
            "success": True,
            "agents": {
                "tutor": "online",
                "study_planner": "online", 
                "resource_curator": "online",
                "exam_coach": "online",
                "syllabus_analyzer": "online"
            },
            "message": "All agents are operational"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# NEW ROUTES FOR SYLLABUS AGENT
@router.post("/syllabus/analyze/{user_id}", response_model=Dict[str, Any])
async def analyze_syllabus(
    user_id: str,
    syllabus_file: UploadFile = File(...),
    subject: str = Form(...),
    course_name: str = Form(None),
    semester: str = Form(None),
    difficulty_level: str = Form("medium")
):
    """Analyze syllabus file and generate learning path with resources"""
    try:
        # Extract text content from uploaded file
        syllabus_content = await _extract_file_content(syllabus_file)
        
        # Format the syllabus request
        user_input = f"Analyze syllabus for {course_name or 'course'} in {subject}"
        
        # Run the syllabus agent
        result = await syllabus_agent.invoke(
            user_id=user_id,
            user_input=user_input,
            syllabus_content=syllabus_content,
            subject=subject,
            course_name=course_name,
            semester=semester,
            difficulty_level=difficulty_level
        )
        
        return {
            "success": True,
            "agent": "syllabus_analyzer",
            "result": result,
            "file_info": {
                "filename": syllabus_file.filename,
                "content_type": syllabus_file.content_type,
                "size_bytes": len(syllabus_content.encode('utf-8'))
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Alternative endpoint for direct text input (for testing)
@router.post("/syllabus/analyze-text/{user_id}", response_model=Dict[str, Any])
async def analyze_syllabus_text(user_id: str, request: SyllabusUploadRequest):
    """Analyze syllabus text and generate learning path with resources"""
    try:
        # Format the syllabus request
        user_input = f"Analyze syllabus for {request.course_name or 'course'} in {request.subject}"
        
        # Run the syllabus agent
        result = await syllabus_agent.invoke(
            user_id=user_id,
            user_input=user_input,
            syllabus_content=request.syllabus_content,
            subject=request.subject,
            course_name=request.course_name,
            semester=request.semester,
            difficulty_level=request.difficulty_level
        )
        
        return {
            "success": True,
            "agent": "syllabus_analyzer",
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/syllabus/paths/{user_id}", response_model=Dict[str, Any])
async def get_user_learning_paths(user_id: str):
    """Get all learning paths for a user"""
    try:
        from app.services.appwrite_service import appwrite_service
        paths = await appwrite_service.get_user_learning_paths(user_id)
        
        return {
            "success": True,
            "learning_paths": paths,
            "total_paths": len(paths)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/syllabus/resources/{path_id}", response_model=Dict[str, Any])
async def get_learning_path_resources(path_id: str):
    """Get all resources for a specific learning path"""
    try:
        from app.services.appwrite_service import appwrite_service
        resources = await appwrite_service.get_learning_path_resources(path_id)
        
        return {
            "success": True,
            "resources": resources,
            "total_resources": len(resources)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 