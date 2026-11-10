"""Add feedback and decision metadata columns.

Revision ID: 7f2c9a1d4e6b
Revises: 463d322bd585
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7f2c9a1d4e6b"
down_revision: Union[str, Sequence[str], None] = "463d322bd585"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "decision_history",
        sa.Column("is_demo", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "decision_history",
        sa.Column("data_available", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.add_column(
        "decision_history",
        sa.Column(
            "source_type",
            sa.String(length=64),
            nullable=False,
            server_default="officer_audit_log",
        ),
    )
    op.add_column(
        "planting_reports",
        sa.Column("harvest_outcome_mt", sa.Float(), nullable=True),
    )
    op.add_column(
        "planting_reports",
        sa.Column("sale_price_rs_kg", sa.Float(), nullable=True),
    )
    op.add_column(
        "planting_reports",
        sa.Column("sale_channel", sa.String(length=64), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("planting_reports", "sale_channel")
    op.drop_column("planting_reports", "sale_price_rs_kg")
    op.drop_column("planting_reports", "harvest_outcome_mt")
    op.drop_column("decision_history", "source_type")
    op.drop_column("decision_history", "data_available")
    op.drop_column("decision_history", "is_demo")
