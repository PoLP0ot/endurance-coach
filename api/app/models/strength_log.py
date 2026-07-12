"""Logged strength sets and session completions (epic MUSCU, M4)."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import GUID, Base, TimestampMixin, gen_uuid


class StrengthSetLog(Base, TimestampMixin):
    __tablename__ = "strength_set_logs"
    __table_args__ = (
        UniqueConstraint(
            "plan_id", "week", "day", "exercise_id", "set_index",
            name="uq_strength_set",
        ),
    )

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    plan_id: Mapped[str] = mapped_column(
        GUID(),
        ForeignKey("strength_plans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    week: Mapped[int] = mapped_column(Integer, nullable=False)
    day: Mapped[int] = mapped_column(Integer, nullable=False)
    exercise_id: Mapped[str] = mapped_column(String(8), nullable=False)
    set_index: Mapped[int] = mapped_column(Integer, nullable=False)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    reps: Mapped[int] = mapped_column(Integer, nullable=False)
    rpe: Mapped[float | None] = mapped_column(Float, nullable=True)


class StrengthSessionDone(Base, TimestampMixin):
    __tablename__ = "strength_session_done"
    __table_args__ = (
        UniqueConstraint("plan_id", "week", "day", name="uq_strength_session_done"),
    )

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    plan_id: Mapped[str] = mapped_column(
        GUID(),
        ForeignKey("strength_plans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    week: Mapped[int] = mapped_column(Integer, nullable=False)
    day: Mapped[int] = mapped_column(Integer, nullable=False)
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
