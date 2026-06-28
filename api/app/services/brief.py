"""Daily coaching brief — proactive 'here's today' message (B4).

Deterministic facts (today's prescription, adherence, goal band, recovery) come
from the loop services; the LLM narrates a short morning message on top. Cached
once per user per day.
"""
from __future__ import annotations

from datetime import date
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.brief import DailyBrief
from app.services.coach_facts import build_coach_facts
from app.services.today import todays_session

BRIEF_INSTRUCTION = (
    "Write a short morning brief for the athlete (2-3 sentences): what to do "
    "today and why it matters for their goal, plus one note on recovery or "
    "adherence. Warm, specific, no numbers you weren't given."
)


class _Narrator(Protocol):
    def model_for(self, task) -> str: ...  # noqa: ANN001
    def narrate(self, task, facts: dict, instruction: str) -> str: ...  # noqa: ANN001


def build_daily_brief(db: Session, user_id: str, llm: _Narrator, today: date) -> dict:
    """Build (not persist) today's brief: headline, narrated body, prescription."""
    from app.services.llm import Task

    info = todays_session(db, user_id, today)
    facts = build_coach_facts(db, user_id, today)
    brief_facts = {
        "goal": facts["goal"],
        "recovery": facts["recovery"],
        "form": facts["form"],
        "today": {
            "session": info.get("session"),
            "is_rest": info.get("is_rest"),
            "phase": info.get("phase"),
            "adherence": info.get("adherence"),
            "status": info.get("status"),
        },
    }
    body = llm.narrate(Task.CHAT, brief_facts, BRIEF_INSTRUCTION)
    return {
        "headline": info.get("headline") or facts["goal"].get("headline"),
        "body": body,
        "prescription": info.get("session"),
        "model": llm.model_for(Task.CHAT),
    }


def get_or_create_brief(
    db: Session, user_id: str, llm: _Narrator, today: date
) -> DailyBrief:
    """Return today's cached brief, generating it once on first access."""
    existing = db.execute(
        select(DailyBrief).where(
            DailyBrief.user_id == user_id, DailyBrief.day == today
        )
    ).scalars().first()
    if existing is not None:
        return existing

    built = build_daily_brief(db, user_id, llm, today)
    brief = DailyBrief(
        user_id=user_id,
        day=today,
        headline=built["headline"],
        body=built["body"],
        prescription=built["prescription"],
        model=built["model"],
    )
    db.add(brief)
    db.commit()
    db.refresh(brief)
    return brief
