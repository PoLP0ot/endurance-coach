"""Cached AI coach analysis per activity ("What This Run Means")."""
from __future__ import annotations

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, gen_uuid


class AIAnalysis(Base, TimestampMixin):
    __tablename__ = "ai_analyses"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=gen_uuid
    )
    activity_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("activities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    model: Mapped[str] = mapped_column(String(60), nullable=False)
    # The deterministic metrics fed to the LLM (provenance / reproducibility)
    facts: Mapped[dict] = mapped_column(JSONB, nullable=False)
    # The narrative the LLM produced from those facts
    narrative: Mapped[str] = mapped_column(Text, nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(20), default="v1", nullable=False)

    activity = relationship("Activity", back_populates="analyses")
