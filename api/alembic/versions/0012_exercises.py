"""exercise library

Revision ID: 0012_exercises
Revises: 0011_cancel_at_period_end
Create Date: 2026-07-12
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.models.base import JSONType

revision: str = "0012_exercises"
down_revision: Union[str, None] = "0011_cancel_at_period_end"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "exercises",
        sa.Column("id", sa.String(length=8), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("body_part", sa.String(length=40), nullable=False),
        sa.Column("target", sa.String(length=80), nullable=False),
        sa.Column("muscle_group", sa.String(length=80), nullable=True),
        sa.Column("secondary_muscles", JSONType(), nullable=False),
        sa.Column("equipment", sa.String(length=80), nullable=False),
        sa.Column("instructions", JSONType(), nullable=False),
        sa.Column("image_url", sa.String(length=300), nullable=False),
        sa.Column("gif_url", sa.String(length=300), nullable=False),
        sa.Column("attribution", sa.String(length=200), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_exercises_name", "exercises", ["name"])
    op.create_index("ix_exercises_body_part", "exercises", ["body_part"])
    op.create_index("ix_exercises_target", "exercises", ["target"])
    op.create_index("ix_exercises_equipment", "exercises", ["equipment"])


def downgrade() -> None:
    op.drop_index("ix_exercises_equipment", table_name="exercises")
    op.drop_index("ix_exercises_target", table_name="exercises")
    op.drop_index("ix_exercises_body_part", table_name="exercises")
    op.drop_index("ix_exercises_name", table_name="exercises")
    op.drop_table("exercises")
