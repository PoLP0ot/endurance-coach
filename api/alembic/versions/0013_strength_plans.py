"""strength programs

Revision ID: 0013_strength_plans
Revises: 0012_exercises
Create Date: 2026-07-12
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.models.base import GUID, JSONType

revision: str = "0013_strength_plans"
down_revision: Union[str, None] = "0012_exercises"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "strength_plans",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("user_id", GUID(), nullable=False),
        sa.Column("goal_kind", sa.String(length=40), nullable=True),
        sa.Column("weeks", sa.Integer(), nullable=False),
        sa.Column("frequency", sa.Integer(), nullable=False),
        sa.Column("level", sa.String(length=20), nullable=False),
        sa.Column("equipment", JSONType(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("structure", JSONType(), nullable=False),
        sa.Column("narrative", sa.Text(), nullable=True),
        sa.Column("model", sa.String(length=60), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_strength_plans_user_id", "strength_plans", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_strength_plans_user_id", table_name="strength_plans")
    op.drop_table("strength_plans")
