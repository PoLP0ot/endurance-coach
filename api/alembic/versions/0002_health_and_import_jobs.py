"""daily_health and import_jobs tables

Revision ID: 0002_health_and_import_jobs
Revises: 0001_initial
Create Date: 2026-06-22
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_health_and_import_jobs"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "daily_health",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("day", sa.Date(), nullable=False),
        sa.Column("resting_hr", sa.Integer(), nullable=True),
        sa.Column("hrv", sa.Float(), nullable=True),
        sa.Column("sleep_score", sa.Integer(), nullable=True),
        sa.Column("steps", sa.Integer(), nullable=True),
        sa.Column("body_battery", sa.Integer(), nullable=True),
        sa.Column("stress_avg", sa.Integer(), nullable=True),
        sa.Column("weight_kg", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "day", name="uq_user_health_day"),
    )
    op.create_index("ix_daily_health_user_id", "daily_health", ["user_id"])
    op.create_index("ix_daily_health_day", "daily_health", ["day"])

    op.create_table(
        "import_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="queued"),
        sa.Column("progress_label", sa.String(60), nullable=True),
        sa.Column("activities_imported", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("health_days_imported", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_import_jobs_user_id", "import_jobs", ["user_id"])


def downgrade() -> None:
    op.drop_table("import_jobs")
    op.drop_table("daily_health")
