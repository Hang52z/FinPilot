"""Market data: securities, daily prices, watchlist, provider usage.

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-25 23:32:24.417510

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "provider_usage",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("provider", sa.String(length=20), nullable=False),
        sa.Column("endpoint", sa.String(length=40), nullable=False),
        sa.Column("symbol", sa.String(length=10), nullable=True),
        sa.Column("status", sa.Integer(), nullable=False),
        sa.Column("bytes", sa.BigInteger(), nullable=False),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_provider_usage_provider_requested_at",
        "provider_usage",
        ["provider", "requested_at"],
        unique=False,
    )
    op.create_table(
        "securities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("symbol", sa.String(length=10), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("exchange", sa.String(length=20), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("listed_from", sa.Date(), nullable=True),
        sa.Column("listed_until", sa.Date(), nullable=True),
        sa.Column("source", sa.String(length=20), nullable=False),
        sa.Column("info_fetched_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("prices_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("symbol"),
    )
    op.create_table(
        "market_prices",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("security_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("open", sa.Numeric(precision=24, scale=10), nullable=False),
        sa.Column("high", sa.Numeric(precision=24, scale=10), nullable=False),
        sa.Column("low", sa.Numeric(precision=24, scale=10), nullable=False),
        sa.Column("close", sa.Numeric(precision=24, scale=10), nullable=False),
        sa.Column("volume", sa.BigInteger(), nullable=False),
        sa.Column("adj_open", sa.Numeric(precision=24, scale=10), nullable=False),
        sa.Column("adj_high", sa.Numeric(precision=24, scale=10), nullable=False),
        sa.Column("adj_low", sa.Numeric(precision=24, scale=10), nullable=False),
        sa.Column("adj_close", sa.Numeric(precision=24, scale=10), nullable=False),
        sa.Column("adj_volume", sa.BigInteger(), nullable=False),
        sa.Column("div_cash", sa.Numeric(precision=24, scale=10), nullable=False),
        sa.Column("split_factor", sa.Numeric(precision=24, scale=10), nullable=False),
        sa.Column("source", sa.String(length=20), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["security_id"], ["securities.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("security_id", "date"),
    )
    op.create_table(
        "watchlists",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("security_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["security_id"], ["securities.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("security_id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("watchlists")
    op.drop_table("market_prices")
    op.drop_table("securities")
    op.drop_index("ix_provider_usage_provider_requested_at", table_name="provider_usage")
    op.drop_table("provider_usage")
