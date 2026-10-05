from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..services import agent

router = APIRouter()


class ChatReq(BaseModel):
    resume_id: int
    message: str


@router.post("/chat")
def chat(req: ChatReq, db: Session = Depends(get_db)):
    return agent.run_agent(db, req.resume_id, req.message)
