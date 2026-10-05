from __future__ import annotations

import json
import os
import re
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .resume_parser import extract_resume_text, detect_skills
from .ai_service import GeminiService, GeminiServiceError

load_dotenv()

app = FastAPI(
    title="CareerGuide AI",
    version="3.0.0",
    description="AI-powered career guidance and resume analysis.",
)

frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ai = GeminiService()


class AnalyzeRequest(BaseModel):
    resume_text: str = Field(min_length=20, max_length=30000)
    skills: list[str] = Field(default_factory=list)
    target_role: str = Field(default="Data Analyst", max_length=120)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    resume_text: str = Field(default="", max_length=12000)
    target_role: str = Field(default="Data Analyst", max_length=120)


@app.get("/")
def root() -> dict[str, Any]:
    return {
        "name": "CareerGuide AI",
        "version": "3.0.0",
        "status": "running",
        "frontend": "http://localhost:5173",
        "docs": "http://localhost:8000/docs",
    }


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "gemini_configured": ai.configured,
        "model": ai.model,
    }


@app.get("/careers")
def careers() -> list[dict[str, str]]:
    return [
        {"title": "Data Analyst", "description": "Turn business data into insights and dashboards."},
        {"title": "Business Analyst", "description": "Translate business problems into measurable solutions."},
        {"title": "Data Scientist", "description": "Build statistical and machine-learning solutions."},
        {"title": "ML Engineer", "description": "Build and deploy machine-learning systems."},
        {"title": "Product Analyst", "description": "Use product data to improve user and business outcomes."},
        {"title": "Data Engineer", "description": "Build reliable pipelines and data platforms."},
    ]


@app.post("/resume")
async def resume(file: UploadFile = File(...)) -> dict[str, Any]:
    filename = file.filename or "resume"
    content_type = file.content_type or ""
    data = await file.read()

    if len(data) > 8 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Resume is too large. Please keep it under 8 MB.")

    try:
        text = extract_resume_text(filename, content_type, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if len(text.strip()) < 30:
        raise HTTPException(
            status_code=400,
            detail="I could not find enough readable text. If this is a scanned PDF, export it as a text-readable PDF or DOCX.",
        )

    skills = detect_skills(text)
    return {
        "filename": filename,
        "text": text[:30000],
        "skills": skills,
        "characters": len(text),
    }


@app.post("/analyze")
def analyze(request: AnalyzeRequest) -> dict[str, Any]:
    skills = sorted(set(s.strip() for s in request.skills if s.strip()))
    try:
        result = ai.analyze_resume(
            resume_text=request.resume_text,
            skills=skills,
            target_role=request.target_role,
        )
        return result
    except GeminiServiceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected analysis error: {type(exc).__name__}") from exc


@app.post("/chat")
def chat(request: ChatRequest) -> dict[str, str]:
    try:
        reply = ai.chat(
            message=request.message,
            resume_text=request.resume_text,
            target_role=request.target_role,
        )
        return {"reply": reply}
    except GeminiServiceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected chat error: {type(exc).__name__}") from exc
