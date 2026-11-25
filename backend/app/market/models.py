from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base

Price = Numeric(24, 10)


class Security(Base):
    __tablename__ = "securities"

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(10), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    exchange: Mapped[str | None] = mapped_column(String(20))
    description: Mapped[str | None] = mapped_column(Text)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    listed_from: Mapped[date | None] = mapped_column(Date)
    listed_until: Mapped[date | None] = mapped_column(Date)
    source: Mapped[str] = mapped_column(String(20))
    info_fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    prices_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class MarketPrice(Base):
    """Daily bar, unique per security and market date: re-syncing updates, never duplicates."""

    __tablename__ = "market_prices"
    __table_args__ = (UniqueConstraint("security_id", "date"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    security_id: Mapped[int] = mapped_column(ForeignKey("securities.id", ondelete="CASCADE"))
    date: Mapped[date] = mapped_column(Date)
    open: Mapped[Decimal] = mapped_column(Price)
    high: Mapped[Decimal] = mapped_column(Price)
    low: Mapped[Decimal] = mapped_column(Price)
    close: Mapped[Decimal] = mapped_column(Price)
    volume: Mapped[int] = mapped_column(BigInteger)
    adj_open: Mapped[Decimal] = mapped_column(Price)
    adj_high: Mapped[Decimal] = mapped_column(Price)
    adj_low: Mapped[Decimal] = mapped_column(Price)
    adj_close: Mapped[Decimal] = mapped_column(Price)
    adj_volume: Mapped[int] = mapped_column(BigInteger)
    div_cash: Mapped[Decimal] = mapped_column(Price)
    split_factor: Mapped[Decimal] = mapped_column(Price)
    source: Mapped[str] = mapped_column(String(20))
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class WatchlistItem(Base):
    """Single-user watchlist. Phase 9 adds an owner."""

    __tablename__ = "watchlists"

    id: Mapped[int] = mapped_column(primary_key=True)
    security_id: Mapped[int] = mapped_column(
        ForeignKey("securities.id", ondelete="CASCADE"), unique=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ProviderUsage(Base):
    """One row per outbound provider request, used to enforce plan limits."""

    __tablename__ = "provider_usage"
    __table_args__ = (Index("ix_provider_usage_provider_requested_at", "provider", "requested_at"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    provider: Mapped[str] = mapped_column(String(20))
    endpoint: Mapped[str] = mapped_column(String(40))
    symbol: Mapped[str | None] = mapped_column(String(10))
    status: Mapped[int] = mapped_column(Integer)
    bytes: Mapped[int] = mapped_column(BigInteger)
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
