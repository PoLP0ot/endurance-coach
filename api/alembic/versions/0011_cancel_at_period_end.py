"""subscription cancel_at_period_end flag

Revision ID: 0011_cancel_at_period_end
Revises: 0010_daily_brief
Create Date: 2026-07-06
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0011_cancel_at_period_end"
down_revision: Union[str, None] = "0010_daily_brief"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "subscriptions",
        sa.Column(
            "cancel_at_period_end",
            sa.Boolean(),
            nullable=False,
            server_default="0",
        ),
    )


def downgrade() -> None:
    op.drop_column("subscriptions", "cancel_at_period_end")
