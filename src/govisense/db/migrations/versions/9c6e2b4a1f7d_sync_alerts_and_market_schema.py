"""Synchronize alert and market-price tables with ORM models.

Revision ID: 9c6e2b4a1f7d
Revises: 8a4d1f6c2b9e
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9c6e2b4a1f7d"
down_revision: Union[str, Sequence[str], None] = "8a4d1f6c2b9e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    for name, column in (
        ("title_en", sa.Column("title_en", sa.String(length=255), nullable=True)),
        ("title_si", sa.Column("title_si", sa.String(length=255), nullable=True)),
        ("title_ta", sa.Column("title_ta", sa.String(length=255), nullable=True)),
        ("message_en", sa.Column("message_en", sa.Text(), nullable=True)),
        ("message_si", sa.Column("message_si", sa.Text(), nullable=True)),
        ("message_ta", sa.Column("message_ta", sa.Text(), nullable=True)),
        ("target_role", sa.Column("target_role", sa.String(length=32), nullable=True)),
        ("status", sa.Column("status", sa.String(length=32), nullable=True)),
    ):
        op.add_column("alerts", column)

    for name, column in (
        ("farmer_id", sa.Column("farmer_id", sa.String(length=64), nullable=True)),
        ("acknowledged", sa.Column("acknowledged", sa.Boolean(), nullable=False, server_default=sa.false())),
        ("question", sa.Column("question", sa.Text(), nullable=True)),
        ("officer_response", sa.Column("officer_response", sa.Text(), nullable=True)),
        ("created_at", sa.Column("created_at", sa.DateTime(timezone=True), nullable=True)),
        ("updated_at", sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True)),
    ):
        op.add_column("alert_status", column)

    if not inspector.has_table("market_prices"):
        op.create_table(
            "market_prices",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("crop_id", sa.String(length=64), nullable=False),
            sa.Column("crop_name", sa.String(length=128), nullable=False),
            sa.Column("crop_en", sa.String(length=128), nullable=True),
            sa.Column("crop_si", sa.String(length=128), nullable=True),
            sa.Column("crop_ta", sa.String(length=128), nullable=True),
            sa.Column("category", sa.String(length=64), nullable=False, server_default="vegetable"),
            sa.Column("market_center", sa.String(length=128), nullable=False),
            sa.Column("economic_center_en", sa.String(length=128), nullable=True),
            sa.Column("economic_center_si", sa.String(length=128), nullable=True),
            sa.Column("economic_center_ta", sa.String(length=128), nullable=True),
            sa.Column("wholesale_price", sa.Float(), nullable=True),
            sa.Column("retail_price", sa.Float(), nullable=True),
            sa.Column("wholesale_price_display", sa.String(length=64), nullable=True),
            sa.Column("retail_price_display", sa.String(length=64), nullable=True),
            sa.Column("trend_pct", sa.String(length=64), nullable=False, server_default="±0% (Stable)"),
            sa.Column("is_up", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("is_stable", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("price_date", sa.String(length=32), nullable=False),
            sa.Column("source", sa.String(length=64), nullable=False, server_default="HARTI/CBSL"),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )
    existing_indexes = {index["name"] for index in inspector.get_indexes("market_prices")}
    for name, columns in (
        ("ix_market_prices_crop_id", ["crop_id"]),
        ("ix_market_prices_market_center", ["market_center"]),
        ("ix_market_prices_price_date", ["price_date"]),
        ("idx_price_crop_date", ["crop_id", "price_date"]),
    ):
        if name not in existing_indexes:
            op.create_index(name, "market_prices", columns, unique=False)


def downgrade() -> None:
    op.drop_index("idx_price_crop_date", table_name="market_prices")
    op.drop_index("ix_market_prices_price_date", table_name="market_prices")
    op.drop_index("ix_market_prices_market_center", table_name="market_prices")
    op.drop_index("ix_market_prices_crop_id", table_name="market_prices")
    op.drop_table("market_prices")
    for name in ("updated_at", "created_at", "officer_response", "question", "acknowledged", "farmer_id"):
        op.drop_column("alert_status", name)
    for name in ("status", "target_role", "message_ta", "message_si", "message_en", "title_ta", "title_si", "title_en"):
        op.drop_column("alerts", name)
