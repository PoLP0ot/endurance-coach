"""Coach chat endpoints (US4, premium)."""
from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_llm_provider, require_premium
from app.models.chat import ChatMessage
from app.models.user import User
from app.services.chat import answer, history

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)


def _serialize(m: ChatMessage) -> dict:
    return {
        "id": m.id,
        "role": m.role,
        "content": m.content,
        "created_at": m.created_at.isoformat() if m.created_at else None,
    }


@router.get("/messages")
async def get_messages(
    user: User = Depends(require_premium),
    db: Session = Depends(get_db),
) -> dict:
    """Return the user's coach conversation, oldest-first."""
    return {"messages": [_serialize(m) for m in history(db, user.id)]}


@router.post("")
async def post_message(
    body: ChatRequest,
    user: User = Depends(require_premium),
    db: Session = Depends(get_db),
    llm=Depends(get_llm_provider),
) -> dict:
    """Send a message to the coach and get a grounded reply."""
    reply = answer(db, user.id, body.message, llm, today=date.today())
    return _serialize(reply)
