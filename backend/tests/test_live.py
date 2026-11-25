"""Calls the real provider. Opt-in: `TIINGO_API_KEY=... pytest -m live`. Not run in CI."""

import os
from datetime import date, timedelta

import httpx
import pytest
from sqlalchemy.orm import Session, sessionmaker

from app.core.db import get_engine
from app.market.quota import ProviderLimits, UsageGuard
from app.market.tiingo import TiingoProvider

pytestmark = pytest.mark.live


@pytest.fixture
def tiingo(db: Session) -> TiingoProvider:
    key = os.environ.get("TIINGO_API_KEY")
    if not key:
        pytest.fail("live tests need TIINGO_API_KEY")
    guard = UsageGuard(
        sessionmaker(bind=get_engine()), "tiingo", ProviderLimits(50, 1000, 500, 10**9)
    )
    return TiingoProvider(key, guard, httpx.Client(base_url="https://api.tiingo.com", timeout=10))


def test_nvda_search_and_recent_prices(tiingo: TiingoProvider) -> None:
    assert any(r.symbol == "NVDA" for r in tiingo.search("nvidia"))
    bars = tiingo.get_daily_bars("NVDA", date.today() - timedelta(days=10), date.today())
    assert bars and all(b.close > 0 for b in bars)
