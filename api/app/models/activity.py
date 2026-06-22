"""Activities imported from Garmin and their detailed metrics."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import GUID, Base, JSONType, TimestampMixin, gen_uuid


class Activity(Base, TimestampMixin):
    __tablename__ = "activities"
    __table_args__ = (
        UniqueConstraint("user_id", "garmin_activity_id", name="uq_user_garmin_activity"),
    )

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(
        GUID(),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    garmin_activity_id: Mapped[str] = mapped_column(String(64), nullable=False)
    activity_type: Mapped[str] = mapped_column(String(40), nullable=False)  # running, cycling...
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )

    # Summary metrics (computed/imported, never invented by the LLM)
    duration_s: Mapped[int | None] = mapped_column(Integer, nullable=True)
    distance_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_hr: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_hr: Mapped[int | None] = mapped_column(Integer, nullable=True)
    elevation_gain_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_power_w: Mapped[float | None] = mapped_column(Float, nullable=True)
    # TSS computed deterministically by AnalyticsEngine
    tss: Mapped[float | None] = mapped_column(Float, nullable=True)

    user = relationship("User", back_populates="activities")
    metrics = relationship(
        "ActivityMetric", back_populates="activity", cascade="all, delete-orphan"
    )
    analyses = relationship(
        "AIAnalysis", back_populates="activity", cascade="all, delete-orphan"
    )


class ActivityMetric(Base, TimestampMixin):
    """Detailed streams, laps and zone buckets for an activity."""

    __tablename__ = "activity_metrics"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=gen_uuid)
    activity_id: Mapped[str] = mapped_column(
        GUID(),
        ForeignKey("activities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # one of: stream | laps | zones
    kind: Mapped[str] = mapped_column(String(20), nullable=False)
    # JSON payload: time series samples, lap splits, or zone distribution
    data: Mapped[dict] = mapped_column(JSONType, nullable=False)

    activity = relationship("Activity", back_populates="metrics")
