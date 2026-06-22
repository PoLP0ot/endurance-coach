"""Adaptive training plans (US5)."""
from __future__ import annotations

from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import GUID, Base, JSONType, TimestampMixin, gen_uuid

PLAN_ACTIVE = "active"
PLAN_ARCHIVED = "archived"


class TrainingPlan(Base, TimestampMixin):
    __tablename__ = "training_plans"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(
        GUID(),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    goal: Mapped[str] = mapped_column(String(40), nullable=False)
    weeks: Mapped[int] = mapped_column(Integer, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=PLAN_ACTIVE, nullable=False)
    # Deterministic periodized structure (list of week dicts).
    structure: Mapped[dict] = mapped_column(JSONType, nullable=False)
    # LLM-generated rationale narrating the structure.
    narrative: Mapped[str | None] = mapped_column(Text, nullable=True)
    model: Mapped[str | None] = mapped_column(String(60), nullable=True)

    user = relationship("User")
