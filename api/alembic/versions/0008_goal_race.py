"""goal race: race_name + race_date on users

Revision ID: 0008_goal_race
Revises: 0007_gdpr_audit_log
Create Date: 2026-06-24
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0008_goal_race"
down_revision: Union[str, None] = "0007_gdpr_audit_log"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("race_name", sa.String(120), nullable=True))
    op.add_column("users", sa.Column("race_date", sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "race_date")
    op.drop_column("users", "race_name")
