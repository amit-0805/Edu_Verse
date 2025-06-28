import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import Optional

load_dotenv()

class Settings(BaseSettings):
    # Google Gemini API (for main agents)
    GOOGLE_API_KEY: str
    
    # OpenAI API (for Mem0 embeddings)
    OPENAI_API_KEY: str
    
    # Appwrite Configuration
    APPWRITE_PROJECT_ID: str
    APPWRITE_API_KEY: str
    APPWRITE_ENDPOINT: str = "https://nyc.cloud.appwrite.io/v1"
    
    # Tavily Search API
    TAVILY_API_KEY: str
    
    # Mem0 API
    MEM0_API_KEY: str
    
    class Config:
        env_file = ".env"

settings = Settings() 