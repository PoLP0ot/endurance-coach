"""Daily coaching brief — one proactive message per user per day (B4)."""
from __future__ import annotations

from datetime import date

from sqlalchemy import Date, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import GUID, Base, JSONType, TimestampMixin, gen_uuid


class DailyBrief(Base, TimestampMixin):
    """Cached morning brief: today's prescription + a short narrated message."""

    __tablename__ = "daily_briefs"
    __table_args__ = (UniqueConstraint("user_id", "day", name="uq_user_brief_day"),)

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    day: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    headline: Mapped[str | None] = mapped_column(String(200), nullable=True)
    body: Mapped[str] = mapped_column(Text, nullable=False, default="")
    prescription: Mapped[dict | None] = mapped_column(JSONType, nullable=True)
    model: Mapped[str | None] = mapped_column(String(60), nullable=True)
