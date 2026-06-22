"""subscriptions table

Revision ID: 0005_subscriptions
Revises: 0004_training_plans
Create Date: 2026-06-22
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0005_subscriptions"
down_revision: Union[str, None] = "0004_training_plans"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "subscriptions",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("paddle_customer_id", sa.String(80), nullable=True),
        sa.Column("paddle_subscription_id", sa.String(80), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="free"),
        sa.Column("price_id", sa.String(80), nullable=True),
        sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", name="uq_subscription_user"),
    )
    op.create_index("ix_subscriptions_user_id", "subscriptions", ["user_id"])
    op.create_index("ix_subscriptions_paddle_subscription_id", "subscriptions", ["paddle_subscription_id"])


def downgrade() -> None:
    op.drop_table("subscriptions")
