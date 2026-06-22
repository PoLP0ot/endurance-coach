"""Paddle subscription mirror (US8). Source of truth is Paddle; we cache state."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import GUID, Base, TimestampMixin, gen_uuid


class Subscription(Base, TimestampMixin):
    __tablename__ = "subscriptions"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(
        GUID(),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    paddle_customer_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    paddle_subscription_id: Mapped[str | None] = mapped_column(
        String(80), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(String(20), default="free", nullable=False)
    price_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    current_period_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    user = relationship("User")
