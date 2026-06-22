"""training_plans table

Revision ID: 0004_training_plans
Revises: 0003_chat_messages
Create Date: 2026-06-22
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004_training_plans"
down_revision: Union[str, None] = "0003_chat_messages"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "training_plans",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("goal", sa.String(40), nullable=False),
        sa.Column("weeks", sa.Integer(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("structure", postgresql.JSONB(), nullable=False),
        sa.Column("narrative", sa.Text(), nullable=True),
        sa.Column("model", sa.String(60), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_training_plans_user_id", "training_plans", ["user_id"])


def downgrade() -> None:
    op.drop_table("training_plans")
