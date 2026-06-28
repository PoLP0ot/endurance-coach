"""daily coaching brief

Revision ID: 0010_daily_brief
Revises: 0009_goal_params
Create Date: 2026-06-24
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.models.base import GUID, JSONType

revision: str = "0010_daily_brief"
down_revision: Union[str, None] = "0009_goal_params"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "daily_briefs",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("user_id", GUID(), nullable=False),
        sa.Column("day", sa.Date(), nullable=False),
        sa.Column("headline", sa.String(length=200), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("prescription", JSONType(), nullable=True),
        sa.Column("model", sa.String(length=60), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "day", name="uq_user_brief_day"),
    )
    op.create_index("ix_daily_briefs_user_id", "daily_briefs", ["user_id"])
    op.create_index("ix_daily_briefs_day", "daily_briefs", ["day"])


def downgrade() -> None:
    op.drop_index("ix_daily_briefs_day", table_name="daily_briefs")
    op.drop_index("ix_daily_briefs_user_id", table_name="daily_briefs")
    op.drop_table("daily_briefs")
