import json
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from ..database import get_db, Resume
from ..services import resume_parser

router = APIRouter()


@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Please upload a PDF file.")
    text = resume_parser.pdf_to_text(await file.read())
    if len(text.strip()) < 30:
        raise HTTPException(400, "Could not read text from this PDF.")
    profile = resume_parser.extract_profile(text)
    row = Resume(filename=file.filename, text=text, profile_json=json.dumps(profile))
    db.add(row)
    db.commit()
    return {"resume_id": row.id, "profile": profile}
