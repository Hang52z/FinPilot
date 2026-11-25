from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.orm import Session, sessionmaker

from app.core.db import get_engine
from app.market.provider import QuotaExceeded
from app.market.quota import ProviderLimits, UsageGuard

NOW = datetime(2026, 11, 25, 12, 0, tzinfo=UTC)
LIMITS = ProviderLimits(
    requests_per_hour=3, requests_per_day=5, symbols_per_month=2, bytes_per_month=1000
)


def guard(now: datetime = NOW, limits: ProviderLimits = LIMITS) -> UsageGuard:
    return UsageGuard(sessionmaker(bind=get_engine()), "tiingo", limits, clock=lambda: now)


def test_hourly_limit(db: Session) -> None:
    g = guard()
    for _ in range(3):
        g.check("NVDA")
        g.record("prices", "NVDA", 200, 10)

    with pytest.raises(QuotaExceeded):
        g.check("NVDA")
    guard(NOW + timedelta(hours=1, minutes=1)).check("NVDA")


def test_daily_limit(db: Session) -> None:
    for hour in range(5):
        guard(NOW + timedelta(hours=hour)).record("prices", "NVDA", 200, 10)

    with pytest.raises(QuotaExceeded):
        guard(NOW + timedelta(hours=6)).check("NVDA")
    guard(NOW + timedelta(days=1, hours=1)).check("NVDA")


def test_new_symbols_per_month(db: Session) -> None:
    g = guard(limits=ProviderLimits(100, 100, 2, 10**9))
    g.record("prices", "NVDA", 200, 10)
    g.record("prices", "SPY", 200, 10)

    g.check("NVDA")
    g.check(None)
    with pytest.raises(QuotaExceeded):
        g.check("AAPL")
    guard(datetime(2026, 12, 1, tzinfo=UTC), ProviderLimits(100, 100, 2, 10**9)).check("AAPL")


def test_monthly_bandwidth(db: Session) -> None:
    g = guard(limits=ProviderLimits(100, 100, 100, 1000))
    g.record("prices", "NVDA", 200, 1000)
    with pytest.raises(QuotaExceeded):
        g.check("NVDA")


def test_other_providers_do_not_count(db: Session) -> None:
    other = UsageGuard(sessionmaker(bind=get_engine()), "other", LIMITS, clock=lambda: NOW)
    for _ in range(3):
        other.record("prices", "NVDA", 200, 10)
    guard().check("NVDA")
