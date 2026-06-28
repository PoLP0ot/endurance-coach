"""goal params: structured per-goal target on users

Revision ID: 0009_goal_params
Revises: 0008_goal_race
Create Date: 2026-06-24
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.models.base import JSONType

revision: str = "0009_goal_params"
down_revision: Union[str, None] = "0008_goal_race"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("goal_params", JSONType(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "goal_params")
