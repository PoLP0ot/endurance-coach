"""User profile, extends Supabase auth.users (1:1 by id)."""
from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    # Mirrors auth.users.id (Supabase). No FK across schemas in app code; the
    # SQL migration wires the auth.users foreign key.
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    email: Mapped[str | None] = mapped_column(String(320), unique=True, nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    # Modular goal: marathon | weight_loss | hyrox | triathlon | health
    primary_goal: Mapped[str | None] = mapped_column(String(40), nullable=True)
    onboarding_complete: Mapped[bool] = mapped_column(default=False, nullable=False)
    subscription_status: Mapped[str] = mapped_column(
        String(20), default="free", nullable=False
    )

    garmin_connection = relationship(
        "GarminConnection", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    activities = relationship(
        "Activity", back_populates="user", cascade="all, delete-orphan"
    )
