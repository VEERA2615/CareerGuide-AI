# CareerGuide AI v3

A polished local AI career assistant built with FastAPI + React + Gemini.

## Features
- Resume upload: PDF, DOCX, TXT
- Resume text extraction
- Skill detection + editable skill chips
- AI career analysis
- Readiness score and skill gaps
- 3-phase personalized roadmap
- "Do this today" action
- AI career chat
- Helpful fallback messages when Gemini is unavailable
- Modern responsive dashboard
- No database or ChromaDB required

## 1. Backend

Open PowerShell:

```powershell
cd "D:\nextwave proj\CareerGuide-AI-v3\backend"
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Open `.env` and set:

```env
GEMINI_API_KEY=YOUR_NEW_KEY_HERE
GEMINI_MODEL=gemini-2.5-flash
FRONTEND_URL=http://localhost:5173
```

Start:

```powershell
python -m uvicorn app.main:app --reload
```

Backend:
- http://localhost:8000
- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## 2. Frontend

Open a second PowerShell:

```powershell
cd "D:\nextwave proj\CareerGuide-AI-v3\frontend"
npm install
npm run dev
```

Open:
http://localhost:5173

## Important
Never put your Gemini API key in React/frontend code. Keep it in backend `.env`.

If Gemini fails, the backend returns a useful error instead of silently returning a generic 503.

The current Gemini integration uses Google's official `google-genai` Python SDK.
