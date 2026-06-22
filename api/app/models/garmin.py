"""Garmin connection — encrypted credentials/tokens at rest."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import GUID, Base, TimestampMixin, gen_uuid


class GarminConnection(Base, TimestampMixin):
    __tablename__ = "garmin_connections"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(
        GUID(),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    # Fernet-encrypted Garmin session token blob. Never store plaintext.
    encrypted_tokens: Mapped[str] = mapped_column(Text, nullable=False)
    garmin_username: Mapped[str | None] = mapped_column(String(320), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="connected", nullable=False)
    last_sync_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    user = relationship("User", back_populates="garmin_connection")
