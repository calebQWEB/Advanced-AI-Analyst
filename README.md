# AI Analyst Project Documentation

Overview
The AI Analyst is a web application that allows users to upload spreadsheets (CSV, XLS, XLSX), analyze sales data using an AI model (Together AI for development, OpenAI for production), and interact with the data via a chat interface with per-file conversation history. The project includes secure authentication, file deletion, and history limits (100 messages per file, 30 days). The backend is built with FastAPI and Supabase (PostgreSQL, storage, authentication), and the frontend uses Next.js with React Hook Form and Lucide icons.

## Features

- File Upload: Upload spreadsheets (up to 10MB) to Supabase storage.
- File Analysis: Parse spreadsheets and generate insights (trends, anomalies, predictions) using an AI model.
- Chat Interface: Ask questions about analyzed data with per-file chat history.
- Chat History Limits: Enforce 100 messages per file and 30-day retention.
- File Deletion: Delete files, metadata, analyses, and chat history.
- Security: Row-Level Security (RLS) ensures users only access their own data.
- Scalability: Production-ready with hosting on Render (backend), Vercel (frontend), and Supabase (database).

## Folder Structure

```
ai-analyst/
├── backend/
│ ├── app/
│ │ ├── config/
│ │ │ └── settings.py # Environment variables and settings
│ │ ├── services/
| | | ├── data_analysis_service.py # Generates insights using Pandas.
| | | ├── pdf_export_service.py # Handles pdf formatting using matplotlib and seaborn
│ │ │ ├── chat_service.py # Handles chat processing
│ │ │ ├── langgraph_service.py # Generates insights using LangGraph
│ │ │ ├── parser_service.py # Parses spreadsheet files
│ │ │ └── supabase_service.py # Interacts with Supabase (storage, database)
│ │ ├── utils/
│ │ │ ├── auth.py # Supabase JWT authentication
│ │ │ └── logger.py # Structured logging with structlog
│ │ └── main.py # FastAPI application with endpoints
│ ├── requirements.txt # Backend dependencies
│ ├── .env # Environment variables (not committed)
├── frontend/
```

## File Descriptions

### Backend

- app/config/settings.py: Loads environment variables using pydantic_settings (e.g., SUPABASE_URL, TOGETHER_API_KEY).
- app/services/chat_service.py: Processes chat requests using the AI model, integrating analysis data and chat history.
- app/services/langgraph_service.py: Generates insights (trends, anomalies, predictions) from spreadsheet data.
- app/services/parser_service.py: Parses CSV/XLS/XLSX files into raw text and descriptions.
- app/services/data_analysis.service.py Uses pandas to generate advanced sales insights.
- app/services/pdf_export_service.py Uses Matplotlib to format generate a beautiful pdf format to be exported.
- app/services/supabase_service.py: Manages Supabase interactions (file upload, metadata, analysis, chat history, deletion).
- app/utils/auth.py: Verifies Supabase JWT tokens for user authentication.
- app/utils/logger.py: Configures structured logging with structlog.
- app/main.py: Defines FastAPI endpoints (/upload, /files, /files/{file_id}, /analyze/{file_id}, /analyses/{file_id}, /chat, /chat/history/{file_id}, /files/{file_id} for DELETE).
- requirements.txt: Lists dependencies (e.g., fastapi, supabase, together, langgraph, pandas).
- .env: Stores sensitive variables (e.g., SUPABASE_KEY, TOGETHER_API_KEY).
- Procfile: Specifies Heroku start command (web: uvicorn app.main:app --host 0.0.0.0 --port $PORT).

### Frontend

---

## Setup Steps

### Prerequisites

- Node.js: v16 or higher
- Python: 3.9 or higher
- Supabase Account: For database, storage, and authentication
- Together AI Account: For development (switch to OpenAI for production)
- GitHub Repository: For version control and CI/CD

## Backend Setup

### Clone Repository:

- git clone <your-repo-url>
- cd ai-analyst/backend

### Create Virtual Environment:

- python -m venv venv
- venv\Scripts\activate #Activate virtual environment

### Install Dependencies:

- pip install -r requirements.txt

### Set Up Environment Variables:Create .env in backend/:

- SUPABASE_URL=<your-supabase-url>
- SUPABASE_KEY=<your-supabase-service-key>
- ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend-domain.com
- ALLOWED_FILE_TYPES=csv,xls,xlsx
- MAX_FILE_SIZE=10485760 # 10MB
- TOGETHER_API_KEY=<your-together-ai-key> # Switch to OPENAI_API_KEY in production

### Set Up Supabase Database:

Create a Supabase project at supabase.com.
Run the following SQL in Supabase’s SQL editor to create tables and enable RLS:CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

```
CREATE TABLE uploaded_files (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
filename TEXT NOT NULL,
file_path TEXT NOT NULL,
user_id UUID NOT NULL,
file_size INTEGER NOT NULL,
file_type TEXT NOT NULL,
status TEXT DEFAULT 'uploaded',
created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
analysis_id UUID
);
ALTER TABLE uploaded_files ENABLE ROW LEVEL SECURITY;
CREATE POLICY user_access ON uploaded_files
USING (auth.uid() = user_id)
FOR ALL TO authenticated;

CREATE TABLE file_analyses (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
file_id UUID NOT NULL REFERENCES uploaded_files(id) ON DELETE CASCADE,
user_id UUID NOT NULL,
raw_text TEXT,
description TEXT,
insights JSONB,
status TEXT DEFAULT 'pending',
created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
ALTER TABLE file_analyses ENABLE ROW LEVEL SECURITY;
CREATE POLICY user_access ON file_analyses
USING (auth.uid() = user_id)
FOR ALL TO authenticated;

CREATE TABLE chat_history (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
file_id UUID NOT NULL REFERENCES uploaded_files(id) ON DELETE CASCADE,
analysis_id UUID NOT NULL REFERENCES file_analyses(id) ON DELETE CASCADE,
user_id UUID NOT NULL,
question TEXT NOT NULL,
answer TEXT NOT NULL,
created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
ALTER TABLE chat_history ENABLE ROW LEVEL SECURITY;
CREATE POLICY user_access ON chat_history
USING (auth.uid() = user_id)
FOR ALL TO authenticated;

ALTER TABLE uploaded_files
ADD CONSTRAINT uploaded_files_analysis_id_fkey
FOREIGN KEY (analysis_id)
REFERENCES file_analyses(id)
ON DELETE SET NULL;

CREATE OR REPLACE FUNCTION cleanup_chat_history()
RETURNS void AS $$
BEGIN
DELETE FROM chat_history
WHERE created_at < NOW() - INTERVAL '30 days';
END;

<!-- $$
LANGUAGE plpgsql; -->
```

Schedule the cleanup_chat_history function to run daily in Supabase’s dashboard.

### Run Backend:

uvicorn app.main:app --host 0.0.0.0 --port 8000

## Frontend Setup

- Navigate to Frontend:
- cd ai-analyst/frontend

### Install Dependencies:

- npm install

### Set Up Environment Variables:Create .env.local in frontend/:

- NEXT_PUBLIC_SUPABASE_URL=<your-supabase-url>
- NEXT_PUBLIC_SUPABASE_ANON_KEY=<your-supabase-anon-key>
- NEXT_PUBLIC_API_URL=http://localhost:8000 # Update to production backend URL

### Run Frontend:

- npm run dev

Access at http://localhost:3000.

## Hosting

### Supabase:

Use Supabase’s hosted service for PostgreSQL, storage (spreadsheets bucket), and authentication.
Set up email authentication in the Supabase dashboard.

### Backend (Render):

- Create a Render account at render.com.
- Create a new web service, connect your GitHub repository (backend/), and configure:
- Runtime: Python
- Build Command: pip install -r requirements.txt
- Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT

#### Environment Variables:

- SUPABASE_URL=<your-supabase-url>
- SUPABASE_KEY=<your-supabase-service-key>
- ALLOWED_ORIGINS=https://your-frontend-domain.com
- TOGETHER_API_KEY=<your-together-ai-key> # Switch to OPENAI_API_KEY
- PYTHONUNBUFFERED=1

Deploy and note the URL (e.g., https://your-backend.onrender.com).

### Frontend (Vercel):

- Create a Vercel account at vercel.com.
- Import your GitHub repository (frontend/), and configure:
- Framework: Next.js
- Environment Variables:NEXT_PUBLIC_SUPABASE_URL=<your-supabase-url>
- NEXT_PUBLIC_SUPABASE_ANON_KEY=<your-supabase-anon-key>
- NEXT_PUBLIC_API_URL=https://your-backend.onrender.com

Deploy and note the URL (e.g., https://your-frontend.vercel.app).

#### Custom Domain:

Vercel: Add app.yourdomain.com in the dashboard, update DNS (e.g., CNAME to Vercel).
Render: Add api.yourdomain.com, update DNS (e.g., A record to Render’s IP).
Update ALLOWED_ORIGINS in Render to include the frontend domain.

## CI/CD:

- Create .github/workflows/ci.yml

```
name: CI/CD Pipeline

on:
  push:
    branches: ["master"]
  pull_request:
    branches: ["master"]

jobs:
  build-and-test:
    runs-on: ubuntu-latest

    env:
      SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
      SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
      ALLOWED_FILE_TYPES: ${{ secrets.ALLOWED_FILE_TYPES }}
      MAX_FILE_SIZE: ${{ secrets.MAX_FILE_SIZE }}
      SUPABASE_JWT_SECRET: ${{ secrets.SUPABASE_JWT_SECRET }}
      ALLOWED_ORIGINS: ${{ secrets.ALLOWED_ORIGINS }}
      TOGETHER_API_KEY: ${{ secrets.TOGETHER_API_KEY }}

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"
          cache-dependency-path: frontend/package-lock.json

      - name: Install & build frontend
        run: |
          cd frontend
          npm ci  # Use ci for CI environments (faster, exact deps)
          npm run build
          npm run test --if-present

      - name: Setup Python
        uses: actions/setup-python@v5 # Updated to v5
        with:
          python-version: "3.13" # Latest 3.13.x
          cache: "pip" # Cache pip deps
          cache-dependency-path: backend/requirements.txt

      - name: Install & test backend
        run: |
          cd backend
          pip install -r requirements.txt
          pytest || echo "No tests yet"  # Consider adding real tests later

  deploy:
    runs-on: ubuntu-latest
    needs: build-and-test # Only run if CI succeeds
    if: github.ref == 'refs/heads/master' && github.event_name == 'push' # Only on master pushes

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Deploy Frontend to Vercel
        uses: amondnet/vercel-action@v25 # Official Vercel action
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          working-directory: frontend # Deploy only frontend dir
          vercel-args: "--prod" # Deploy to production

      - name: Deploy Backend to Render
        run: |
          curl -X POST ${{ secrets.RENDER_DEPLOY_HOOK }}  # Triggers Render deploy via webhook
```

### Add secrets in GitHub Settings.

#### Switch to OpenAI:

- Update requirements.txt:

```
-together==1.3.0
+openai==1.47.0
```

- Update settings.py:

```
-together_api_key: str
+openai_api_key: str
```

- Update langgraph_service.py and chat_service.py:

```
-from together import AsyncTogether
+from openai import AsyncOpenAI
-self.client = AsyncTogether(api_key=settings.together_api_key)
+self.client = AsyncOpenAI(api_key=settings.openai_api_key)
-model="meta-llama/Mixtral-8x7B-Instruct-v0.1"
+model="gpt-4o-mini"
```

- Set OPENAI_API_KEY in Render.

### Functionality Details

#### File Upload

##### Endpoint: POST /upload

- Logic: Validates file type (CSV, XLS, XLSX) and size (≤10MB), uploads to Supabase storage (spreadsheets bucket), saves metadata to - uploaded_files.
- Security: RLS ensures users only access their files.

#### File Analysis

##### Endpoint: POST /analyze/{file_id}

- Logic: Parses spreadsheet, generates insights (trends, anomalies, predictions) using LangGraph, generates advanced insights using Pandas, saves to file_analyses, updates analysis_id in uploaded_files.
- Security: RLS restricts access to user’s files.

#### Chat Interface

##### Endpoint: POST /chat

- Logic: Processes questions using AI model, integrates analysis data and chat history, saves to chat_history.
- Frontend: Displays messages, suggested questions, and timestamps; supports deletion.
- Security: RLS ensures chat history is user-specific.

#### Chat History

##### Endpoint: GET /chat/history/{file_id}

- Logic: Retrieves up to 100 messages per file, deletes messages older than 30 days (via cleanup_chat_history function).
- Frontend: Displays history

#### File Deletion

##### Endpoint: DELETE /files/{file_id}

- Logic: Deletes file from storage, metadata from uploaded_files, analyses from file_analyses, and history from chat_history. Clears analysis_id - to avoid foreign key violations.
- Frontend: Adds "Delete" buttons with confirmation prompts.
- Security: RLS restricts deletions to file owners.

#### Export PDF

##### Endpoint: POST /export/pdf/{file_id}

- Logic: Calls pdf_export_service, generates pdf for specific file and sends to the frontend
- Security: RLS restricts export to file owners.

## Testing

### Backend:

```
curl -X POST -H "Authorization: Bearer <jwt>" -F "file=@test.xlsx" http://localhost:8000/upload
curl -X GET -H "Authorization: Bearer <jwt>" http://localhost:8000/files
curl -X POST -H "Authorization: Bearer <jwt>" http://localhost:8000/analyze/<file_id>
curl -X GET -H "Authorization: Bearer <jwt>" http://localhost:8000/analyses/<file_id>
curl -X POST -H "Authorization: Bearer <jwt>" -H "Content-Type: application/json" -d '{"file_id": "<file_id>", "question": "What are the sales trends?"}' http://localhost:8000/chat
curl -X GET -H "Authorization: Bearer <jwt>" http://localhost:8000/chat/history/<file_id>
curl -X DELETE -H "Authorization: Bearer <jwt>" http://localhost:8000/files/<file_id>
```

Verify logs (backend.log) and Supabase tables.

### Frontend:

- Access http://localhost:3000, sign in, upload a file, analyze it, chat, view history, and delete.
- Check browser console for errors.
- Verify RLS by attempting actions with a different user’s JWT.

### Hosted Environment:

- Test endpoints with production URLs.
- Confirm file deletion removes all associated data.
- Verify history limits (100 messages, 30 days).

### Troubleshooting

Backend Errors: Check Render logs or backend.log for dependency issues or Supabase connection errors.
Frontend Errors: Verify NEXT_PUBLIC_API_URL matches backend URL; check CORS settings.
Supabase Errors: Ensure SUPABASE_KEY is the service key; verify RLS policies.
Foreign Key Errors: Ensure analysis_id foreign key has ON DELETE SET NULL or clear analysis_id before deleting file_analyses.

Contributors

Developed with assistance from Grok (xAI), created on August 13, 2025.
