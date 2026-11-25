"""Provider-neutral market data contract. Business code depends on this, never on a vendor."""

import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Literal, Protocol

from fastapi import status

from app.core.errors import AppError

SYMBOL_PATTERN = re.compile(r"^[A-Z0-9.\-]{1,10}$")


@dataclass(frozen=True)
class SearchResult:
    symbol: str
    name: str
    asset_type: Literal["stock", "etf"] | None


@dataclass(frozen=True)
class SecurityInfo:
    symbol: str
    name: str
    exchange: str | None
    description: str | None
    start_date: date | None
    end_date: date | None


@dataclass(frozen=True)
class DailyBar:
    """One trading day on the exchange's market date. adj_* are split- and dividend-adjusted."""

    date: date
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int
    adj_open: Decimal
    adj_high: Decimal
    adj_low: Decimal
    adj_close: Decimal
    adj_volume: int
    div_cash: Decimal
    split_factor: Decimal


class MarketDataProvider(Protocol):
    name: str

    def search(self, query: str) -> list[SearchResult]: ...

    def get_security(self, symbol: str) -> SecurityInfo: ...

    def get_daily_bars(self, symbol: str, start: date, end: date) -> list[DailyBar]: ...


class InvalidSymbol(AppError):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    code = "invalid_symbol"


class SymbolNotFound(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "symbol_not_found"


class ProviderUnavailable(AppError):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    code = "provider_unavailable"


class ProviderNotConfigured(ProviderUnavailable):
    code = "provider_not_configured"


class QuotaExceeded(ProviderUnavailable):
    code = "provider_quota_exceeded"


def normalize_symbol(raw: str) -> str:
    symbol = raw.strip().upper()
    if not SYMBOL_PATTERN.fullmatch(symbol):
        raise InvalidSymbol(raw)
    return symbol
