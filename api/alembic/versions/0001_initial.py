"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-21
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from app.models.base import GUID, JSONType

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", GUID(), primary_key=True),
        sa.Column("email", sa.String(320), unique=True, nullable=True),
        sa.Column("display_name", sa.String(120), nullable=True),
        sa.Column("primary_goal", sa.String(40), nullable=True),
        sa.Column("onboarding_complete", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("subscription_status", sa.String(20), nullable=False, server_default="free"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "garmin_connections",
        sa.Column("id", GUID(), primary_key=True),
        sa.Column("user_id", GUID(), sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("encrypted_tokens", sa.Text(), nullable=False),
        sa.Column("garmin_username", sa.String(320), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="connected"),
        sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "activities",
        sa.Column("id", GUID(), primary_key=True),
        sa.Column("user_id", GUID(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("garmin_activity_id", sa.String(64), nullable=False),
        sa.Column("activity_type", sa.String(40), nullable=False),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("duration_s", sa.Integer(), nullable=True),
        sa.Column("distance_m", sa.Float(), nullable=True),
        sa.Column("avg_hr", sa.Integer(), nullable=True),
        sa.Column("max_hr", sa.Integer(), nullable=True),
        sa.Column("elevation_gain_m", sa.Float(), nullable=True),
        sa.Column("avg_power_w", sa.Float(), nullable=True),
        sa.Column("tss", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "garmin_activity_id", name="uq_user_garmin_activity"),
    )
    op.create_index("ix_activities_user_id", "activities", ["user_id"])
    op.create_index("ix_activities_start_time", "activities", ["start_time"])

    op.create_table(
        "activity_metrics",
        sa.Column("id", GUID(), primary_key=True),
        sa.Column("activity_id", GUID(), sa.ForeignKey("activities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("kind", sa.String(20), nullable=False),
        sa.Column("data", JSONType(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_activity_metrics_activity_id", "activity_metrics", ["activity_id"])

    op.create_table(
        "ai_analyses",
        sa.Column("id", GUID(), primary_key=True),
        sa.Column("activity_id", GUID(), sa.ForeignKey("activities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("model", sa.String(60), nullable=False),
        sa.Column("facts", JSONType(), nullable=False),
        sa.Column("narrative", sa.Text(), nullable=False),
        sa.Column("prompt_version", sa.String(20), nullable=False, server_default="v1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_ai_analyses_activity_id", "ai_analyses", ["activity_id"])


def downgrade() -> None:
    op.drop_table("ai_analyses")
    op.drop_table("activity_metrics")
    op.drop_table("activities")
    op.drop_table("garmin_connections")
    op.drop_table("users")
