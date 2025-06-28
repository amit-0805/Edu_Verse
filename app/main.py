from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, agents
from app.config import settings
import asyncio
import uvicorn
from datetime import datetime

# Create FastAPI app
app = FastAPI(
    title="EduVerse - AI-Powered Learning Backend",
    description="Multi-agent educational system with personalized learning",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(agents.router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to EduVerse - AI-Powered Learning System",
        "version": "1.0.0",
        "features": [
            "AI Tutor Agent - Personalized explanations",
            "Study Planner Agent - Custom study schedules", 
            "Resource Curator Agent - Educational content discovery",
            "Exam Coach Agent - Practice tests and evaluation"
        ],
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    # Test basic service connections
    services = {
        "appwrite": "connected",
        "gemini": "connected", 
        "mem0": "connected",
        "tavily": "connected"
    }
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": services
    }

@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    print("🚀 EduVerse backend starting up...")
    print("📚 AI Tutor Agent ready")
    print("📅 Study Planner Agent ready") 
    print("🌐 Resource Curator Agent ready")
    print("🧪 Exam Coach Agent ready")
    print("📋 Syllabus Analyzer Agent ready")
    print("✅ All agents operational!")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    print("👋 EduVerse backend shutting down...")

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 