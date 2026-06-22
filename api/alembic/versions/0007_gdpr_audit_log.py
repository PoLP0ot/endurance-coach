"""gdpr_audit_log table

Revision ID: 0007_gdpr_audit_log
Revises: 0006_user_prefs
Create Date: 2026-06-22
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from app.models.base import GUID

revision: str = "0007_gdpr_audit_log"
down_revision: Union[str, None] = "0006_user_prefs"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "gdpr_audit_log",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        # Deliberately NOT a foreign key — must outlive the deleted user.
        sa.Column("user_id", GUID(), nullable=False),
        sa.Column("action", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_gdpr_audit_log_user_id", "gdpr_audit_log", ["user_id"])


def downgrade() -> None:
    op.drop_table("gdpr_audit_log")
