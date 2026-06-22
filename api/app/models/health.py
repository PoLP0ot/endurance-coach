"""Daily health metrics imported from Garmin (sleep, HRV, resting HR…)."""
from __future__ import annotations

from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import GUID, Base, TimestampMixin, gen_uuid


class DailyHealth(Base, TimestampMixin):
    """One row per user per calendar day. Idempotent on (user_id, day)."""

    __tablename__ = "daily_health"
    __table_args__ = (
        UniqueConstraint("user_id", "day", name="uq_user_health_day"),
    )

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(
        GUID(),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    day: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    resting_hr: Mapped[int | None] = mapped_column(Integer, nullable=True)
    hrv: Mapped[float | None] = mapped_column(Float, nullable=True)
    sleep_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    steps: Mapped[int | None] = mapped_column(Integer, nullable=True)
    body_battery: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stress_avg: Mapped[int | None] = mapped_column(Integer, nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)

    user = relationship("User")
