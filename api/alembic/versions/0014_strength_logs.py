"""strength set logs + session completions

Revision ID: 0014_strength_logs
Revises: 0013_strength_plans
Create Date: 2026-07-12
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.models.base import GUID

revision: str = "0014_strength_logs"
down_revision: Union[str, None] = "0013_strength_plans"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "strength_set_logs",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("user_id", GUID(), nullable=False),
        sa.Column("plan_id", GUID(), nullable=False),
        sa.Column("week", sa.Integer(), nullable=False),
        sa.Column("day", sa.Integer(), nullable=False),
        sa.Column("exercise_id", sa.String(length=8), nullable=False),
        sa.Column("set_index", sa.Integer(), nullable=False),
        sa.Column("weight_kg", sa.Float(), nullable=True),
        sa.Column("reps", sa.Integer(), nullable=False),
        sa.Column("rpe", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["plan_id"], ["strength_plans.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "plan_id", "week", "day", "exercise_id", "set_index",
            name="uq_strength_set",
        ),
    )
    op.create_index("ix_strength_set_logs_user_id", "strength_set_logs", ["user_id"])
    op.create_index("ix_strength_set_logs_plan_id", "strength_set_logs", ["plan_id"])

    op.create_table(
        "strength_session_done",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("user_id", GUID(), nullable=False),
        sa.Column("plan_id", GUID(), nullable=False),
        sa.Column("week", sa.Integer(), nullable=False),
        sa.Column("day", sa.Integer(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["plan_id"], ["strength_plans.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("plan_id", "week", "day", name="uq_strength_session_done"),
    )
    op.create_index("ix_strength_session_done_user_id", "strength_session_done", ["user_id"])
    op.create_index("ix_strength_session_done_plan_id", "strength_session_done", ["plan_id"])


def downgrade() -> None:
    op.drop_index("ix_strength_session_done_plan_id", table_name="strength_session_done")
    op.drop_index("ix_strength_session_done_user_id", table_name="strength_session_done")
    op.drop_table("strength_session_done")
    op.drop_index("ix_strength_set_logs_plan_id", table_name="strength_set_logs")
    op.drop_index("ix_strength_set_logs_user_id", table_name="strength_set_logs")
    op.drop_table("strength_set_logs")
