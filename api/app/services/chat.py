"""Coach chat orchestration (US4).

The coach answers from deterministic dashboard facts plus recent conversation
history. The LLM never computes numbers — it narrates the provided context.
"""
from __future__ import annotations

from datetime import date
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.chat import ROLE_ASSISTANT, ROLE_USER, ChatMessage
from app.services.coach_facts import build_coach_facts

HISTORY_LIMIT = 20
CHAT_INSTRUCTION = (
    "You are the athlete's coach in an ongoing conversation. Answer their latest "
    "message using the provided facts and history. Be concise and specific."
)


class _Narrator(Protocol):
    def model_for(self, task) -> str: ...  # noqa: ANN001
    def narrate(self, task, facts: dict, instruction: str) -> str: ...  # noqa: ANN001


def history(db: Session, user_id: str, limit: int = HISTORY_LIMIT) -> list[ChatMessage]:
    """Return the user's recent messages, oldest-first."""
    rows = list(
        db.execute(
            select(ChatMessage)
            .where(ChatMessage.user_id == user_id)
            .order_by(ChatMessage.id.desc())
            .limit(limit)
        ).scalars()
    )
    return list(reversed(rows))


def _chat_facts(db: Session, user_id: str, today: date) -> dict:
    """Goal-aware deterministic context for the coach (goal, projection, trend)."""
    return build_coach_facts(db, user_id, today)


def answer(
    db: Session,
    user_id: str,
    message: str,
    llm: _Narrator,
    today: date,
) -> ChatMessage:
    """Persist the user's message, generate a grounded reply, persist and return it."""
    from app.services.llm import Task

    prior = history(db, user_id)
    db.add(ChatMessage(user_id=user_id, role=ROLE_USER, content=message))
    db.commit()

    facts = _chat_facts(db, user_id, today)
    transcript = "\n".join(f"{m.role}: {m.content}" for m in prior)
    instruction = (
        f"{CHAT_INSTRUCTION}\n\nConversation so far:\n{transcript}\n\n"
        f"Latest message:\n{message}"
    )
    if settings.coach_tools_enabled and hasattr(llm, "converse"):
        from app.services.coach_tools import TOOL_SPECS, run_tool

        reply_text = llm.converse(
            Task.CHAT,
            facts,
            instruction,
            TOOL_SPECS,
            lambda name, args: run_tool(db, user_id, today, name, args),
        )
    else:
        reply_text = llm.narrate(Task.CHAT, facts, instruction)

    reply = ChatMessage(user_id=user_id, role=ROLE_ASSISTANT, content=reply_text)
    db.add(reply)
    db.commit()
    db.refresh(reply)
    return reply
