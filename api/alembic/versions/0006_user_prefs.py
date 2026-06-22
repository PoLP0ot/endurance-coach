"""user preferences: units + weekly_email_opt_in

Revision ID: 0006_user_prefs
Revises: 0005_subscriptions
Create Date: 2026-06-22
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0006_user_prefs"
down_revision: Union[str, None] = "0005_subscriptions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("units", sa.String(10), nullable=False, server_default="metric"),
    )
    op.add_column(
        "users",
        sa.Column(
            "weekly_email_opt_in",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "weekly_email_opt_in")
    op.drop_column("users", "units")
