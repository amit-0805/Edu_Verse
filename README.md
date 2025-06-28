# 🎓 EduVerse - AI-Powered Learning Backend

A comprehensive multi-agent educational system built with FastAPI, featuring personalized learning powered by LangGraph agents, Appwrite, Mem0, Tavily, and Keywords AI.

## 🌟 Features

### 🤖 AI Agents
- **🧑‍🏫 AI Tutor Agent**: Provides personalized explanations adapted to learning styles
- **📅 Study Planner Agent**: Generates customized study schedules based on performance
- **🌐 Resource Curator Agent**: Finds and ranks educational content from the web
- **🧪 Exam Coach Agent**: Creates practice tests and evaluates performance

### 🔧 Technology Stack
- **FastAPI**: Modern web framework for building APIs
- **LangGraph**: Agent workflow orchestration
- **Google Gemini**: Large language model for AI capabilities
- **Appwrite**: Authentication, database, and storage
- **Mem0**: Long-term memory for agents
- **Tavily**: Web search for educational resources
- **Keywords AI**: Prompt monitoring and analytics

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- API keys for all services (see setup guide below)

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd eduverse-backend
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
Copy the example environment file and fill in your API keys:

```bash
cp .env.example .env
```

📖 **See [API_KEYS_GUIDE.md](API_KEYS_GUIDE.md) for detailed instructions on obtaining all required API keys**

Your `.env` file should contain:
```env
# Appwrite Configuration
APPWRITE_ENDPOINT=https://nyc.cloud.appwrite.io/v1
APPWRITE_PROJECT_ID=your_actual_project_id
APPWRITE_API_KEY=your_actual_api_key

# Google Gemini API
GOOGLE_API_KEY=your_actual_gemini_api_key

# Tavily API
TAVILY_API_KEY=your_actual_tavily_api_key

# Keywords AI
KEYWORDS_AI_API_KEY=your_actual_keywords_ai_key

# Mem0 Configuration
MEM0_API_KEY=your_actual_mem0_api_key
```

4. **Test your setup**
```bash
python test_setup.py
```

5. **Run the application**
```bash
python run.py
```

The API will be available at `http://localhost:8000`

## 📖 API Documentation

### Authentication Endpoints
- `POST /auth/register` - Register a new user
- `POST /auth/login` - User login
- `GET /auth/profile/{user_id}` - Get user profile
- `PUT /auth/profile/{user_id}` - Update user profile

### Agent Endpoints
- `POST /agents/tutor/{user_id}` - Get personalized tutoring
- `POST /agents/planner/{user_id}` - Create study plan
- `POST /agents/curator/{user_id}` - Find educational resources
- `POST /agents/exam/create/{user_id}` - Generate practice exam
- `POST /agents/exam/evaluate/{user_id}` - Evaluate exam answers
- `GET /agents/status` - Check agent status

### System Endpoints
- `GET /` - API information
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation
- `GET /redoc` - Alternative API documentation

## 🔄 Agent Workflows

### 🧑‍🏫 AI Tutor Agent Flow
1. **Analyze Request**: Extract topic, subject, and difficulty
2. **Retrieve Context**: Get learning history from Mem0
3. **Generate Explanation**: Create personalized content
4. **Save Session**: Store in Appwrite and update Mem0

### 📅 Study Planner Agent Flow
1. **Analyze Requirements**: Parse study goals and constraints
2. **Gather Context**: Retrieve weak areas and exam history
3. **Generate Plan**: Create day-by-day study schedule
4. **Save Plan**: Store plan and update memory

### 🌐 Resource Curator Agent Flow
1. **Analyze Request**: Understand resource needs
2. **Search Resources**: Use Tavily for web search
3. **Curate and Rank**: LLM-powered quality assessment
4. **Save Resources**: Store curated collection

### 🧪 Exam Coach Agent Flow
1. **Analyze Request**: Determine exam parameters
2. **Gather Context**: Get learning history and weak areas
3. **Generate Questions**: Create personalized exam
4. **Evaluate Answers**: Grade and provide feedback
5. **Save Results**: Store performance data

## 🎯 Usage Examples

### Register a User
```python
import requests

response = requests.post("http://localhost:8000/auth/register", json={
    "name": "John Doe",
    "email": "john@example.com", 
    "password": "secure_password"
})
```

### Get Tutoring Help
```python
response = requests.post("http://localhost:8000/agents/tutor/user_id", json={
    "topic": "quadratic equations",
    "subject": "mathematics",
    "difficulty_level": "intermediate"
})
```

### Create Study Plan
```python
response = requests.post("http://localhost:8000/agents/planner/user_id", json={
    "subjects": ["mathematics", "physics"],
    "days_ahead": 7,
    "daily_hours": 3
})
```

### Find Resources
```python
response = requests.post("http://localhost:8000/agents/curator/user_id", json={
    "topic": "machine learning",
    "subject": "computer science",
    "resource_types": ["video", "article", "course"]
})
```

### Generate Practice Exam
```python
response = requests.post("http://localhost:8000/agents/exam/create/user_id", json={
    "topic": "calculus",
    "subject": "mathematics", 
    "question_count": 10,
    "difficulty": "medium",
    "question_types": ["multiple_choice", "short_answer"]
})
```

## 🏗️ Architecture

The system follows a multi-agent architecture where each agent is responsible for a specific educational task:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │   LangGraph      │    │   External APIs │
│                 │    │   Agents         │    │                 │
│  ┌───────────┐  │    │  ┌─────────────┐ │    │  ┌───────────┐  │
│  │  Auth     │  │◄──►│  │ Tutor Agent │ │◄──►│  │  Gemini   │  │
│  │  Routes   │  │    │  └─────────────┘ │    │  └───────────┘  │
│  └───────────┘  │    │  ┌─────────────┐ │    │  ┌───────────┐  │
│  ┌───────────┐  │    │  │ Planner     │ │    │  │ Appwrite  │  │
│  │  Agent    │  │    │  │ Agent       │ │◄──►│  │           │  │
│  │  Routes   │  │    │  └─────────────┘ │    │  └───────────┘  │
│  └───────────┘  │    │  ┌─────────────┐ │    │  ┌───────────┐  │
└─────────────────┘    │  │ Curator     │ │    │  │   Mem0    │  │
                       │  │ Agent       │ │◄──►│  │           │  │
                       │  └─────────────┘ │    │  └───────────┘  │
                       │  ┌─────────────┐ │    │  ┌───────────┐  │
                       │  │ Exam Agent  │ │    │  │  Tavily   │  │
                       │  └─────────────┘ │◄──►│  └───────────┘  │
                       └──────────────────┘    │  ┌───────────┐  │
                                               │  │Keywords AI│  │
                                               │  └───────────┘  │
                                               └─────────────────┘
```

## 🛠️ Development

### Project Structure
```
eduverse-backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── models.py            # Pydantic models
│   ├── agents/              # LangGraph agents
│   │   ├── __init__.py
│   │   ├── base_agent.py    # Base agent class
│   │   ├── tutor_agent.py   # AI tutor agent
│   │   ├── planner_agent.py # Study planner agent
│   │   ├── curator_agent.py # Resource curator agent
│   │   └── exam_agent.py    # Exam coach agent
│   ├── routes/              # API routes
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication routes
│   │   └── agents.py        # Agent interaction routes
│   └── services/            # External service integrations
│       ├── __init__.py
│       ├── appwrite_service.py
│       ├── mem0_service.py
│       ├── tavily_service.py
│       └── keywords_ai_service.py
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── API_KEYS_GUIDE.md       # Complete API setup guide
├── run.py                  # Easy startup script
├── test_setup.py          # Setup verification
└── README.md              # This file
```

### Adding New Agents

1. Create a new agent class in `app/agents/` inheriting from `BaseAgent`
2. Implement the LangGraph workflow in `_build_graph()`
3. Add agent routes in `app/routes/agents.py`
4. Import and use the agent in your routes

### Testing

The API includes interactive documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🔒 Security

- User authentication through Appwrite (no JWT needed)
- API key management for external services
- Input validation with Pydantic models
- CORS configuration for frontend integration

## 📊 Monitoring

- Keywords AI integration for prompt monitoring
- Agent performance tracking
- Error logging and handling
- Health check endpoints

## 🔑 API Keys Required

The system requires API keys from several services. See **[API_KEYS_GUIDE.md](API_KEYS_GUIDE.md)** for detailed instructions on:

- 🧠 **Google Gemini API** - Free tier available
- 🚀 **Appwrite** - 75K requests/month free
- 🌐 **Tavily API** - Free tier available  
- 📊 **Keywords AI** - Check pricing page
- 🧠 **Mem0 API** - Free tier available

**Total estimated cost for development: $0-10/month**

## 🎯 Future Enhancements

- [ ] Frontend integration with CopilotKit
- [ ] Advanced analytics dashboard
- [ ] Real-time collaboration features
- [ ] Mobile app support
- [ ] Multi-language support
- [ ] Advanced recommendation algorithms

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Check **[API_KEYS_GUIDE.md](API_KEYS_GUIDE.md)** for setup help
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review the health check at `/health`

---

**EduVerse** - Empowering education through AI-driven personalization 🎓✨ 