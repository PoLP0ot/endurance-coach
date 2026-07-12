"""Strength exercise library seeded from the exercises-dataset JSON."""
from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, JSONType, TimestampMixin


class Exercise(Base, TimestampMixin):
    __tablename__ = "exercises"

    # Dataset id, zero-padded to 4 digits ("0001").
    id: Mapped[str] = mapped_column(String(8), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    body_part: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    target: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    muscle_group: Mapped[str | None] = mapped_column(String(80), nullable=True)
    secondary_muscles: Mapped[list] = mapped_column(JSONType, nullable=False, default=list)
    equipment: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    # Ordered English instruction steps.
    instructions: Mapped[list] = mapped_column(JSONType, nullable=False, default=list)
    image_url: Mapped[str] = mapped_column(String(300), nullable=False)
    gif_url: Mapped[str] = mapped_column(String(300), nullable=False)
    attribution: Mapped[str | None] = mapped_column(String(200), nullable=True)
