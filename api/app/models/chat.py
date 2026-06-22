"""Coach chat messages — one rolling conversation per user (US4)."""
from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import GUID, Base, TimestampMixin

# Message roles.
ROLE_USER = "user"
ROLE_ASSISTANT = "assistant"


class ChatMessage(Base, TimestampMixin):
    __tablename__ = "chat_messages"

    # Auto-incrementing PK gives a stable conversation ordering across dialects.
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        GUID(),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    user = relationship("User")
