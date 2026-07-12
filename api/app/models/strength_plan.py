"""Long-term periodized strength programs (epic MUSCU, M3)."""
from __future__ import annotations

from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import GUID, Base, JSONType, TimestampMixin, gen_uuid

STRENGTH_PLAN_ACTIVE = "active"
STRENGTH_PLAN_ARCHIVED = "archived"


class StrengthPlan(Base, TimestampMixin):
    __tablename__ = "strength_plans"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(
        GUID(),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    goal_kind: Mapped[str | None] = mapped_column(String(40), nullable=True)
    weeks: Mapped[int] = mapped_column(Integer, nullable=False)
    frequency: Mapped[int] = mapped_column(Integer, nullable=False)
    level: Mapped[str] = mapped_column(String(20), nullable=False)
    equipment: Mapped[list] = mapped_column(JSONType, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default=STRENGTH_PLAN_ACTIVE, nullable=False
    )
    # Deterministic periodized structure (blocks + weeks + sessions + items).
    structure: Mapped[dict] = mapped_column(JSONType, nullable=False)
    # LLM-generated rationale narrating the structure.
    narrative: Mapped[str | None] = mapped_column(Text, nullable=True)
    model: Mapped[str | None] = mapped_column(String(60), nullable=True)

    user = relationship("User")
