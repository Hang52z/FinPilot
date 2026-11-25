from collections.abc import Callable, Iterator
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker

from app.core.db import get_engine
from app.main import create_app
from app.market import service as market_service
from app.market.provider import DailyBar, ProviderUnavailable, SearchResult, SecurityInfo
from app.market.router import get_clock, get_provider

# Wednesday 2026-11-25 20:00 New York: after the 18:00 data-ready time.
NOW = datetime(2026, 11, 26, 1, 0, tzinfo=UTC)


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(create_app()) as c:
        yield c


@pytest.fixture
def db() -> Iterator[Session]:
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(
            text("TRUNCATE securities, market_prices, watchlists, provider_usage RESTART IDENTITY")
        )
    market_service.clear_search_cache()
    with sessionmaker(bind=engine)() as session:
        yield session


def bar(
    day: date, close: str, *, split: str = "1", div: str = "0", adj: str | None = None
) -> DailyBar:
    price = Decimal(close)
    return DailyBar(
        date=day,
        open=price,
        high=price + 1,
        low=price - 1,
        close=price,
        volume=1000,
        adj_open=price,
        adj_high=price + 1,
        adj_low=price - 1,
        adj_close=Decimal(adj) if adj else price,
        adj_volume=1000,
        div_cash=Decimal(div),
        split_factor=Decimal(split),
    )


def weekdays(start: date, count: int) -> list[date]:
    days: list[date] = []
    day = start
    while len(days) < count:
        if day.weekday() < 5:
            days.append(day)
        day += timedelta(days=1)
    return days


class FakeProvider:
    """In-memory MarketDataProvider that records calls."""

    name = "tiingo"

    def __init__(self) -> None:
        self.securities: dict[str, SecurityInfo] = {}
        self.bars: dict[str, list[DailyBar]] = {}
        self.search_results: list[SearchResult] = []
        self.calls: list[tuple[str, str]] = []
        self.unavailable = False

    def add(self, symbol: str, name: str, bars: list[DailyBar]) -> None:
        self.securities[symbol] = SecurityInfo(
            symbol, name, "NASDAQ", None, bars[0].date if bars else None, None
        )
        self.bars[symbol] = bars

    def _call(self, kind: str, arg: str) -> None:
        self.calls.append((kind, arg))
        if self.unavailable:
            raise ProviderUnavailable()

    def search(self, query: str) -> list[SearchResult]:
        self._call("search", query)
        return self.search_results

    def get_security(self, symbol: str) -> SecurityInfo:
        from app.market.provider import SymbolNotFound

        self._call("meta", symbol)
        if symbol not in self.securities:
            raise SymbolNotFound(symbol)
        return self.securities[symbol]

    def get_daily_bars(self, symbol: str, start: date, end: date) -> list[DailyBar]:
        self._call("prices", f"{symbol}:{start}")
        return [b for b in self.bars.get(symbol, []) if start <= b.date <= end]


@pytest.fixture
def provider() -> FakeProvider:
    return FakeProvider()


@pytest.fixture
def clock() -> list[datetime]:
    """Mutable current time: tests move it with `clock[0] = ...`."""
    return [NOW]


@pytest.fixture
def api(db: Session, provider: FakeProvider, clock: list[datetime]) -> Iterator[TestClient]:
    app = create_app()
    app.dependency_overrides[get_provider] = lambda: provider
    now: Callable[[], datetime] = lambda: clock[0]  # noqa: E731
    app.dependency_overrides[get_clock] = lambda: now
    with TestClient(app) as c:
        yield c
