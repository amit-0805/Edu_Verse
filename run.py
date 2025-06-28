#!/usr/bin/env python3
"""
EduVerse Backend Runner
Simple script to start the EduVerse multi-agent learning system
"""

import os
import sys
import subprocess

def check_env_file():
    """Check if .env file exists"""
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("📝 Please copy .env.example to .env and fill in your API keys")
        print("📖 Check API_KEYS_GUIDE.md for detailed instructions on obtaining API keys")
        print("\nQuick setup:")
        print("1. cp .env.example .env")
        print("2. Edit .env with your actual API keys")
        print("3. Run python test_setup.py to verify")
        return False
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting EduVerse backend...")
    print("📚 AI-Powered Learning System")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔄 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        subprocess.run([sys.executable, "-m", "app.main"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Server failed to start: {e}")

def main():
    """Main function"""
    print("🎓 EduVerse - AI-Powered Learning Backend")
    print("=" * 50)
    
    # Check environment file
    if not check_env_file():
        return
    
    # Ask user if they want to install dependencies
    install_deps = input("📦 Install/Update dependencies? (y/n): ").lower().strip()
    if install_deps in ['y', 'yes']:
        if not install_dependencies():
            return
    
    # Start the server
    start_server()

if __name__ == "__main__":
    main() 