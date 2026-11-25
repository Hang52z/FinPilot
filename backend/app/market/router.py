from collections.abc import Callable, Iterator
from datetime import UTC, datetime
from functools import lru_cache
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.core.db import get_db, get_engine
from app.market.provider import MarketDataProvider
from app.market.quota import ProviderLimits, UsageGuard
from app.market.schemas import (
    HistoryOut,
    Range,
    SearchOut,
    SearchResultOut,
    StockOut,
    WatchlistAdd,
    WatchlistItemOut,
    WatchlistOut,
)
from app.market.service import MarketService
from app.market.tiingo import TiingoProvider


def utcnow() -> datetime:
    return datetime.now(UTC)


@lru_cache
def _http_client(base_url: str) -> httpx.Client:
    return httpx.Client(base_url=base_url, timeout=10.0)


def get_provider() -> Iterator[MarketDataProvider | None]:
    settings = get_settings()
    if settings.tiingo_api_key is None:
        yield None
        return
    limits = ProviderLimits(
        requests_per_hour=settings.tiingo_max_requests_per_hour,
        requests_per_day=settings.tiingo_max_requests_per_day,
        symbols_per_month=settings.tiingo_max_symbols_per_month,
        bytes_per_month=settings.tiingo_max_bytes_per_month,
    )
    guard = UsageGuard(sessionmaker(bind=get_engine()), "tiingo", limits)
    yield TiingoProvider(
        settings.tiingo_api_key.get_secret_value(), guard, _http_client(settings.tiingo_base_url)
    )


def get_clock() -> Callable[[], datetime]:
    return utcnow


def get_service(
    db: Annotated[Session, Depends(get_db)],
    provider: Annotated[MarketDataProvider | None, Depends(get_provider)],
    clock: Annotated[Callable[[], datetime], Depends(get_clock)],
) -> MarketService:
    return MarketService(db, provider, clock)


Service = Annotated[MarketService, Depends(get_service)]

market = APIRouter(prefix="/market", tags=["market"])
watchlist = APIRouter(prefix="/watchlist", tags=["watchlist"])


@market.get("/search", response_model=SearchOut)
def search(service: Service, q: Annotated[str, Query(min_length=1, max_length=50)]) -> SearchOut:
    results = [
        SearchResultOut(symbol=r.symbol, name=r.name, asset_type=r.asset_type)
        for r in service.search(q)
    ]
    return SearchOut(results=results)


@market.get("/stocks/{symbol}", response_model=StockOut)
def stock(service: Service, symbol: str) -> StockOut:
    return service.stock(symbol)


@market.get("/stocks/{symbol}/history", response_model=HistoryOut)
def history(service: Service, symbol: str, range: Range = "1Y") -> HistoryOut:
    return service.history(symbol, range)


@watchlist.get("", response_model=WatchlistOut)
def list_watchlist(service: Service) -> WatchlistOut:
    return service.watchlist()


@watchlist.post("", response_model=WatchlistItemOut)
def add_to_watchlist(service: Service, body: WatchlistAdd, response: Response) -> WatchlistItemOut:
    item, created = service.add_to_watchlist(body.symbol)
    response.status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
    return item


@watchlist.delete("/{symbol}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_watchlist(service: Service, symbol: str) -> None:
    service.remove_from_watchlist(symbol)
