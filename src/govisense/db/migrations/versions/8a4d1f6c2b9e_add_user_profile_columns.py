"""Add user profile and compatibility columns.

Revision ID: 8a4d1f6c2b9e
Revises: 7f2c9a1d4e6b
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8a4d1f6c2b9e"
down_revision: Union[str, Sequence[str], None] = "7f2c9a1d4e6b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("id", sa.Integer(), nullable=True))
    op.add_column("users", sa.Column("hashed_password", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("full_name", sa.String(length=128), nullable=True))
    op.add_column("users", sa.Column("phone_number", sa.String(length=32), nullable=True))
    op.add_column(
        "users",
        sa.Column("district", sa.String(length=64), nullable=True, server_default="Anuradhapura"),
    )
    op.add_column(
        "users",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.add_column("users", sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "updated_at")
    op.drop_column("users", "is_active")
    op.drop_column("users", "district")
    op.drop_column("users", "phone_number")
    op.drop_column("users", "full_name")
    op.drop_column("users", "hashed_password")
    op.drop_column("users", "id")
