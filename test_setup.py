#!/usr/bin/env python3
"""
EduVerse Setup Test
Test script to verify all imports and basic functionality
"""

import sys
import importlib

def test_import(module_name):
    """Test if a module can be imported"""
    try:
        importlib.import_module(module_name)
        print(f"✅ {module_name}")
        return True
    except ImportError as e:
        print(f"❌ {module_name} - {e}")
        return False

def test_basic_imports():
    """Test basic Python imports"""
    print("🔍 Testing Basic Imports:")
    modules = [
        'fastapi',
        'uvicorn', 
        'pydantic',
        'appwrite',
        'mem0',
        'tavily',
        'langgraph',
        'langchain_google_genai',
        'httpx',
        'python_dotenv'
    ]
    
    success_count = 0
    for module in modules:
        if test_import(module):
            success_count += 1
    
    print(f"\n📊 Import Results: {success_count}/{len(modules)} successful")
    return success_count == len(modules)

def test_app_imports():
    """Test application imports"""
    print("\n🔍 Testing Application Imports:")
    modules = [
        'app.config',
        'app.models',
        'app.services.appwrite_service',
        'app.services.mem0_service',
        'app.services.tavily_service',
        'app.agents.base_agent',
        'app.agents.tutor_agent',
        'app.agents.planner_agent',
        'app.agents.curator_agent',
        'app.agents.exam_agent',
        'app.routes.auth',
        'app.routes.agents'
    ]
    
    success_count = 0
    for module in modules:
        if test_import(module):
            success_count += 1
    
    print(f"\n📊 App Import Results: {success_count}/{len(modules)} successful")
    return success_count == len(modules)

def test_environment():
    """Test environment setup"""
    print("\n🔍 Testing Environment:")
    import os
    
    # Check for .env file
    if os.path.exists('.env'):
        print("✅ .env file found")
        env_exists = True
    else:
        print("❌ .env file not found")
        print("📝 Copy .env.example to .env and configure your API keys")
        env_exists = False
    
    # Test loading config
    try:
        from app.config import settings
        print("✅ Configuration loaded")
        
        # Check if API keys are configured
        if settings.GOOGLE_API_KEY and settings.GOOGLE_API_KEY != "your_gemini_api_key":
            print("✅ Google Gemini API key configured")
        else:
            print("⚠️  Google Gemini API key not configured")
            
        if settings.APPWRITE_PROJECT_ID and settings.APPWRITE_PROJECT_ID != "your_project_id":
            print("✅ Appwrite project configured")
        else:
            print("⚠️  Appwrite project not configured")
            
        config_loaded = True
    except Exception as e:
        print(f"❌ Configuration failed: {e}")
        config_loaded = False
    
    return env_exists and config_loaded

def test_agents():
    """Test agent initialization"""
    print("\n🔍 Testing Agent Initialization:")
    agents = {
        'tutor': 'app.agents.tutor_agent.tutor_agent',
        'planner': 'app.agents.planner_agent.planner_agent', 
        'curator': 'app.agents.curator_agent.curator_agent',
        'exam': 'app.agents.exam_agent.exam_agent',
        'syllabus': 'app.agents.syllabus_agent.syllabus_agent'
    }
    
    success_count = 0
    for name, module_path in agents.items():
        try:
            module_parts = module_path.split('.')
            module_name = '.'.join(module_parts[:-1])
            object_name = module_parts[-1]
            
            module = importlib.import_module(module_name)
            agent = getattr(module, object_name)
            print(f"✅ {name.title()} Agent initialized")
            success_count += 1
        except Exception as e:
            print(f"❌ {name.title()} Agent failed: {e}")
    
    print(f"\n📊 Agent Results: {success_count}/{len(agents)} successful")
    return success_count == len(agents)

def main():
    """Main test function"""
    print("🎓 EduVerse Setup Test")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Run tests
    all_tests_passed &= test_basic_imports()
    all_tests_passed &= test_app_imports()
    all_tests_passed &= test_environment()
    all_tests_passed &= test_agents()
    
    # Final result
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("🎉 All tests passed! EduVerse is ready to run.")
        print("🚀 Start the server with: python run.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("📝 Make sure to:")
        print("   1. Install all dependencies: pip install -r requirements.txt")
        print("   2. Copy .env.example to .env")
        print("   3. Configure your API keys in .env file")
        print("   4. Check API_KEYS_GUIDE.md for detailed setup instructions")

if __name__ == "__main__":
    main() 