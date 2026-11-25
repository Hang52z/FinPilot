from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

Range = Literal["1M", "3M", "6M", "1Y", "5Y", "MAX"]


class SearchResultOut(BaseModel):
    symbol: str
    name: str
    asset_type: Literal["stock", "etf"] | None


class SearchOut(BaseModel):
    results: list[SearchResultOut]


class LastClose(BaseModel):
    """Most recent daily close. Change uses adjusted closes, so splits do not distort it."""

    date: date
    close: Decimal
    change: Decimal | None
    change_pct: Decimal | None


class StockOut(BaseModel):
    symbol: str
    name: str
    exchange: str | None
    description: str | None
    currency: str
    last_close: LastClose | None
    source: str
    fetched_at: datetime | None


class Bar(BaseModel):
    date: date
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    adj_close: Decimal
    volume: int


class HistoryOut(BaseModel):
    symbol: str
    range: Range
    bars: list[Bar]
    source: str
    as_of: date | None
    fetched_at: datetime | None


class WatchlistItemOut(BaseModel):
    symbol: str
    name: str
    last_close: LastClose | None


class WatchlistOut(BaseModel):
    items: list[WatchlistItemOut]
    source: str
    fetched_at: datetime | None


class WatchlistAdd(BaseModel):
    symbol: str
