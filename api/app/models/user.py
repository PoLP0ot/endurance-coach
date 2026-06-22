"""User profile, extends Supabase auth.users (1:1 by id)."""
from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import GUID, Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    # Mirrors auth.users.id (Supabase). No FK across schemas in app code; the
    # SQL migration wires the auth.users foreign key.
    id: Mapped[str] = mapped_column(GUID(), primary_key=True)
    email: Mapped[str | None] = mapped_column(String(320), unique=True, nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    # Modular goal: marathon | weight_loss | hyrox | triathlon | health
    primary_goal: Mapped[str | None] = mapped_column(String(40), nullable=True)
    onboarding_complete: Mapped[bool] = mapped_column(default=False, nullable=False)
    subscription_status: Mapped[str] = mapped_column(
        String(20), default="free", nullable=False
    )
    # Preferred units and weekly coaching email opt-in (US6, US11a).
    units: Mapped[str] = mapped_column(String(10), default="metric", nullable=False)
    weekly_email_opt_in: Mapped[bool] = mapped_column(default=True, nullable=False)

    garmin_connection = relationship(
        "GarminConnection", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    activities = relationship(
        "Activity", back_populates="user", cascade="all, delete-orphan"
    )
