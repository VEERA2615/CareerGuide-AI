from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..services import agent, rag

router = APIRouter()


class RoleReq(BaseModel):
    resume_id: int
    target_role: str


class RecReq(BaseModel):
    resume_id: int
    interests: str = ""


@router.get("/careers")
def list_careers():
    return {"careers": rag.careers()}


@router.post("/skill-gap")
def skill_gap(req: RoleReq, db: Session = Depends(get_db)):
    return agent.tool_skill_gap(db, req.resume_id, req.target_role)


@router.post("/roadmap")
def roadmap(req: RoleReq, db: Session = Depends(get_db)):
    return agent.tool_roadmap(db, req.resume_id, req.target_role)


@router.post("/recommend-career")
def recommend(req: RecReq, db: Session = Depends(get_db)):
    return agent.tool_recommend(db, req.resume_id, req.interests)
