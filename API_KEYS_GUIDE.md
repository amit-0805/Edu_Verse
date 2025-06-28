# 🔑 API Keys Setup Guide for EduVerse

This guide will help you obtain all the necessary API keys to run the EduVerse backend system.

## 📋 Required API Keys

1. **Google Gemini API** - For AI language model capabilities
2. **Appwrite** - For authentication, database, and storage
3. **Tavily API** - For educational web search
4. **Mem0 API** - For agent memory management

---

## 🧠 1. Google Gemini API

### How to get it:
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click "Get API Key" in the left sidebar
4. Create a new API key or use an existing one
5. Copy the API key

### Add to .env:
```env
GOOGLE_API_KEY=your_actual_gemini_api_key_here
```

### Notes:
- Free tier available with generous limits
- Required for all AI agent functionality

---

## 🚀 2. Appwrite

### How to get it:
1. Go to [Appwrite Cloud](https://cloud.appwrite.io/)
2. Sign up for a free account
3. Create a new project
4. Go to "Settings" → "View API Keys"
5. Copy the Project ID and create a new API key with appropriate permissions

### Add to .env:
```env
APPWRITE_ENDPOINT=https://nyc.cloud.appwrite.io/v1
APPWRITE_PROJECT_ID=your_actual_project_id_here
APPWRITE_API_KEY=your_actual_api_key_here
```

### Database Setup Required:
First, create a database called `eduverse_db` in your Appwrite console. Then create these 5 collections with the exact attributes shown below:

---

## 1. Create Collection: `users`

**Attribute Name:** `user_id`
- **Type:** String
- **Size:** 36
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `name`
- **Type:** String
- **Size:** 255
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `email`
- **Type:** String
- **Size:** 255
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `grade`
- **Type:** String
- **Size:** 50
- **Required:** ❌ No
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `subjects`
- **Type:** String
- **Size:** 100
- **Required:** ❌ No
- **Array:** ✅ Yes
- **Default:** (leave empty)

**Attribute Name:** `learning_style`
- **Type:** String
- **Size:** 50
- **Required:** ❌ No
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `created_at`
- **Type:** String
- **Size:** 50
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

---

## 2. Create Collection: `tutoring_sessions`

**Attribute Name:** `session_id`
- **Type:** String
- **Size:** 36
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `user_id`
- **Type:** String
- **Size:** 36
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `topic`
- **Type:** String
- **Size:** 255
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `subject`
- **Type:** String
- **Size:** 100
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `explanation`
- **Type:** String
- **Size:** 5000
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `examples`
- **Type:** String
- **Size:** 500
- **Required:** ❌ No
- **Array:** ✅ Yes
- **Default:** (leave empty)

**Attribute Name:** `additional_resources`
- **Type:** String
- **Size:** 500
- **Required:** ❌ No
- **Array:** ✅ Yes
- **Default:** (leave empty)

**Attribute Name:** `learning_tips`
- **Type:** String
- **Size:** 500
- **Required:** ❌ No
- **Array:** ✅ Yes
- **Default:** (leave empty)

**Attribute Name:** `difficulty_addressed`
- **Type:** Boolean
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** false

**Attribute Name:** `timestamp`
- **Type:** String
- **Size:** 50
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

---

## 3. Create Collection: `study_schedules`

**Attribute Name:** `plan_id`
- **Type:** String
- **Size:** 36
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `user_id`
- **Type:** String
- **Size:** 36
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `start_date`
- **Type:** String
- **Size:** 50
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `end_date`
- **Type:** String
- **Size:** 50
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `duration_days`
- **Type:** Integer
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** 7

**Attribute Name:** `daily_schedule`
- **Type:** String
- **Size:** 10000
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** {}

**Attribute Name:** `weekly_goals`
- **Type:** String
- **Size:** 500
- **Required:** ❌ No
- **Array:** ✅ Yes
- **Default:** (leave empty)

**Attribute Name:** `total_hours`
- **Type:** Integer
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** 0

**Attribute Name:** `focus_areas`
- **Type:** String
- **Size:** 200
- **Required:** ❌ No
- **Array:** ✅ Yes
- **Default:** (leave empty)

**Attribute Name:** `learning_tips`
- **Type:** String
- **Size:** 500
- **Required:** ❌ No
- **Array:** ✅ Yes
- **Default:** (leave empty)

**Attribute Name:** `created_at`
- **Type:** String
- **Size:** 50
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

---

## 4. Create Collection: `curated_resources`

**Attribute Name:** `resource_id`
- **Type:** String
- **Size:** 36
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `collection_id`
- **Type:** String
- **Size:** 36
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `user_id`
- **Type:** String
- **Size:** 36
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `topic`
- **Type:** String
- **Size:** 255
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `subject`
- **Type:** String
- **Size:** 100
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `curated_resources`
- **Type:** String
- **Size:** 10000
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** []

**Attribute Name:** `total_found`
- **Type:** Integer
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** 0

**Attribute Name:** `search_summary`
- **Type:** String
- **Size:** 1000
- **Required:** ❌ No
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `recommendations`
- **Type:** String
- **Size:** 500
- **Required:** ❌ No
- **Array:** ✅ Yes
- **Default:** (leave empty)

**Attribute Name:** `created_at`
- **Type:** String
- **Size:** 50
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

---

## 5. Create Collection: `exam_results`

**Attribute Name:** `result_id`
- **Type:** String
- **Size:** 36
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `exam_id`
- **Type:** String
- **Size:** 36
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `user_id`
- **Type:** String
- **Size:** 36
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `topic`
- **Type:** String
- **Size:** 255
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `subject`
- **Type:** String
- **Size:** 100
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `action`
- **Type:** String
- **Size:** 50
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `questions`
- **Type:** String
- **Size:** 15000
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** []

**Attribute Name:** `time_limit_minutes`
- **Type:** Integer
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** 30

**Attribute Name:** `instructions`
- **Type:** String
- **Size:** 1000
- **Required:** ❌ No
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `score`
- **Type:** Double
- **Required:** ❌ No
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `correct_count`
- **Type:** Integer
- **Required:** ❌ No
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `feedback`
- **Type:** String
- **Size:** 2000
- **Required:** ❌ No
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `weak_areas`
- **Type:** String
- **Size:** 200
- **Required:** ❌ No
- **Array:** ✅ Yes
- **Default:** (leave empty)

**Attribute Name:** `strong_areas`
- **Type:** String
- **Size:** 200
- **Required:** ❌ No
- **Array:** ✅ Yes
- **Default:** (leave empty)

**Attribute Name:** `timestamp`
- **Type:** String
- **Size:** 50
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

---

## 6. Create Collection: `syllabus_analysis`

**Attribute Name:** `analysis_id`
- **Type:** String
- **Size:** 36
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `user_id`
- **Type:** String
- **Size:** 36
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `syllabus_id`
- **Type:** String
- **Size:** 36
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `path_id`
- **Type:** String
- **Size:** 36
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `course_overview`
- **Type:** String
- **Size:** 5000
- **Required:** ❌ No
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `total_resources_found`
- **Type:** Integer
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** 0

**Attribute Name:** `coverage_analysis`
- **Type:** String
- **Size:** 3000
- **Required:** ❌ No
- **Array:** ❌ No
- **Default:** {}

**Attribute Name:** `recommendations`
- **Type:** String
- **Size:** 2000
- **Required:** ❌ No
- **Array:** ❌ No
- **Default:** []

**Attribute Name:** `assessment_methods`
- **Type:** String
- **Size:** 1000
- **Required:** ❌ No
- **Array:** ❌ No
- **Default:** []

**Attribute Name:** `key_skills`
- **Type:** String
- **Size:** 1000
- **Required:** ❌ No
- **Array:** ❌ No
- **Default:** []

**Attribute Name:** `overall_difficulty`
- **Type:** String
- **Size:** 50
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** intermediate

**Attribute Name:** `created_at`
- **Type:** String
- **Size:** 50
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

---

## 7. Create Collection: `learning_paths`

**Attribute Name:** `path_id`
- **Type:** String
- **Size:** 36
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `user_id`
- **Type:** String
- **Size:** 36
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `course_name`
- **Type:** String
- **Size:** 255
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `subject`
- **Type:** String
- **Size:** 100
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `total_weeks`
- **Type:** Integer
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** 12

**Attribute Name:** `total_estimated_hours`
- **Type:** Integer
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** 0

**Attribute Name:** `learning_path_topics`
- **Type:** String
- **Size:** 15000
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** []

**Attribute Name:** `milestones`
- **Type:** String
- **Size:** 1000
- **Required:** ❌ No
- **Array:** ❌ No
- **Default:** []

**Attribute Name:** `recommended_pace`
- **Type:** String
- **Size:** 500
- **Required:** ❌ No
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `created_at`
- **Type:** String
- **Size:** 50
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

---

## 8. Create Collection: `syllabus_resources`

**Attribute Name:** `resource_id`
- **Type:** String
- **Size:** 36
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `user_id`
- **Type:** String
- **Size:** 36
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `topic_id`
- **Type:** String
- **Size:** 36
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `path_id`
- **Type:** String
- **Size:** 36
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `title`
- **Type:** String
- **Size:** 500
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `url`
- **Type:** String
- **Size:** 1000
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `type`
- **Type:** String
- **Size:** 50
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `description`
- **Type:** String
- **Size:** 2000
- **Required:** ❌ No
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `source`
- **Type:** String
- **Size:** 100
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

**Attribute Name:** `relevance_score`
- **Type:** Double
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** 0.5

**Attribute Name:** `difficulty_level`
- **Type:** String
- **Size:** 50
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** medium

**Attribute Name:** `estimated_time_minutes`
- **Type:** Integer
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** 30

**Attribute Name:** `created_at`
- **Type:** String
- **Size:** 50
- **Required:** ✅ Yes
- **Array:** ❌ No
- **Default:** (leave empty)

### Notes:
- Free tier includes 75K requests/month
- Handles authentication, database, and file storage
- No additional JWT setup needed - Appwrite handles all auth

---

## 🌐 3. Tavily API

### How to get it:
1. Go to [Tavily](https://tavily.com/)
2. Sign up for an account
3. Navigate to your dashboard
4. Find the API section and generate an API key
5. Copy the API key

### Add to .env:
```env
TAVILY_API_KEY=your_actual_tavily_api_key_here
```

### Notes:
- Free tier available
- Used for searching educational content from trusted sources
- Essential for the Resource Curator Agent

---

## 🧠 4. Mem0 API

### How to get it:
1. Go to [Mem0](https://mem0.dev/)
2. Sign up for an account
3. Access your dashboard
4. Find the API keys section
5. Generate a new API key
6. Copy the API key

### Add to .env:
```env
MEM0_API_KEY=your_actual_mem0_api_key_here
```

### Notes:
- Provides persistent memory for AI agents
- Essential for personalized learning experiences
- Free tier available

---

## 🎯 Quick Setup Checklist

- [ ] Google Gemini API key obtained
- [ ] Appwrite project created and API key generated
- [ ] Tavily API key obtained
- [ ] Mem0 API key obtained
- [ ] Copy .env.example to .env
- [ ] Fill in all API keys in .env file
- [ ] Appwrite database `eduverse_db` created
- [ ] All 8 collections created with exact attributes as specified above:
  - [ ] `users` (Collection 1)
  - [ ] `tutoring_sessions` (Collection 2)
  - [ ] `study_schedules` (Collection 3)
  - [ ] `curated_resources` (Collection 4)
  - [ ] `exam_results` (Collection 5)
  - [ ] `syllabus_analysis` (Collection 6) - **NEW**
  - [ ] `learning_paths` (Collection 7) - **NEW**
  - [ ] `syllabus_resources` (Collection 8) - **NEW**

---

## 🧪 Testing Your Setup

After adding all API keys to your `.env` file:

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit .env with your actual API keys**

3. **Test the setup:**
   ```bash
   python test_setup.py
   ```

4. **Start the server:**
   ```bash
   python run.py
   ```

5. **Check the health endpoint:**
   ```bash
   curl http://localhost:8000/health
   ```

---

## 💡 Cost Considerations

- **Google Gemini**: Generous free tier
- **Appwrite**: 75K requests/month free
- **Tavily**: Free tier available
- **Mem0**: Free tier available

**Total estimated cost for development/testing: $0-5/month**

---

## 🆘 Troubleshooting

### Common Issues:

1. **"Module not found" errors:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Authentication errors:**
   - Double-check API keys in `.env` file
   - Ensure no extra spaces or quotes around keys

3. **Appwrite connection issues:**
   - Verify the endpoint URL is correct
   - Check project ID matches your Appwrite project

### Getting Help:
- Check the `/health` endpoint for service status
- Review logs in the console when starting the server
- Each service has fallback handling for graceful degradation

---

---

## 📄 File Upload Support

### Syllabus Agent File Types

The Syllabus Agent (`/agents/syllabus/analyze/{user_id}`) accepts these file formats:

**Supported File Types:**
- **PDF files** (`.pdf`) - Course syllabi, curriculum documents
- **Word documents** (`.docx`) - Microsoft Word syllabus files  
- **Text files** (`.txt`) - Plain text syllabi

**API Usage:**
```bash
# Using curl with file upload
curl -X POST "http://localhost:8000/agents/syllabus/analyze/user123" \
  -F "syllabus_file=@/path/to/syllabus.pdf" \
  -F "subject=Computer Science" \
  -F "course_name=Data Structures" \
  -F "semester=Fall 2024" \
  -F "difficulty_level=intermediate"
```

**FastAPI Swagger UI:**
- Navigate to `http://localhost:8000/docs`
- Find the "Analyze Syllabus" endpoint
- Click "Try it out" 
- Use the file upload button to select your syllabus file
- Fill in the form fields (subject, course_name, etc.)
- Click "Execute"

**Alternative Text Endpoint:**
For testing with direct text input, use:
`POST /agents/syllabus/analyze-text/{user_id}`

**Required Dependencies:**
The following packages are automatically installed:
- `PyPDF2` - For PDF text extraction
- `python-docx` - For Word document processing

---

**🎓 Once all keys are configured, your EduVerse system will be fully operational!** 