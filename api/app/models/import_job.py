"""Garmin import job state — backs the import-status polling endpoint."""
from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import GUID, Base, TimestampMixin, gen_uuid

# Lifecycle of an import job.
JOB_QUEUED = "queued"
JOB_RUNNING = "running"
JOB_DONE = "done"
JOB_ERROR = "error"


class ImportJob(Base, TimestampMixin):
    __tablename__ = "import_jobs"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(
        GUID(),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(20), default=JOB_QUEUED, nullable=False)
    # Human-facing step label shown during import (O2.3).
    progress_label: Mapped[str | None] = mapped_column(String(60), nullable=True)
    activities_imported: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    health_days_imported: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    user = relationship("User")
