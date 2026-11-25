"""Tiingo implementation of MarketDataProvider (https://www.tiingo.com/documentation/end-of-day)."""

import json
import logging
import time
from collections.abc import Callable
from datetime import date
from decimal import Decimal
from typing import Any, Literal

import httpx

from app.market.provider import (
    DailyBar,
    ProviderUnavailable,
    QuotaExceeded,
    SearchResult,
    SecurityInfo,
    SymbolNotFound,
)
from app.market.quota import UsageGuard

log = logging.getLogger(__name__)

ASSET_TYPES: dict[str, Literal["stock", "etf"]] = {"Stock": "stock", "ETF": "etf"}


def _date(value: str | None) -> date | None:
    return date.fromisoformat(value[:10]) if value else None


class TiingoProvider:
    name = "tiingo"

    def __init__(
        self,
        api_key: str,
        guard: UsageGuard,
        client: httpx.Client,
        retries: int = 2,
        backoff_seconds: float = 0.5,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._headers = {"Authorization": f"Token {api_key}", "Accept": "application/json"}
        self._guard = guard
        self._client = client
        self._retries = retries
        self._backoff = backoff_seconds
        self._sleep = sleep

    def search(self, query: str) -> list[SearchResult]:
        rows = self._get("search", "/tiingo/utilities/search", {"query": query}, symbol=None)
        results: dict[str, SearchResult] = {}
        for row in rows:
            asset_type = ASSET_TYPES.get(row.get("assetType", ""))
            if not (asset_type and row.get("isActive") and row.get("countryCode") == "US"):
                continue
            symbol = str(row["ticker"]).upper()
            results.setdefault(symbol, SearchResult(symbol, str(row["name"]).strip(), asset_type))
        return list(results.values())

    def get_security(self, symbol: str) -> SecurityInfo:
        row = self._get("meta", f"/tiingo/daily/{symbol}", {}, symbol=symbol)
        return SecurityInfo(
            symbol=str(row["ticker"]).upper(),
            name=str(row["name"]).strip(),
            exchange=row.get("exchangeCode") or None,
            description=row.get("description") or None,
            start_date=_date(row.get("startDate")),
            end_date=_date(row.get("endDate")),
        )

    def get_daily_bars(self, symbol: str, start: date, end: date) -> list[DailyBar]:
        params = {"startDate": start.isoformat(), "endDate": end.isoformat()}
        rows = self._get("prices", f"/tiingo/daily/{symbol}/prices", params, symbol=symbol)
        return [
            DailyBar(
                date=date.fromisoformat(r["date"][:10]),
                open=Decimal(r["open"]),
                high=Decimal(r["high"]),
                low=Decimal(r["low"]),
                close=Decimal(r["close"]),
                volume=int(r["volume"]),
                adj_open=Decimal(r["adjOpen"]),
                adj_high=Decimal(r["adjHigh"]),
                adj_low=Decimal(r["adjLow"]),
                adj_close=Decimal(r["adjClose"]),
                adj_volume=int(r["adjVolume"]),
                div_cash=Decimal(r["divCash"]),
                split_factor=Decimal(r["splitFactor"]),
            )
            for r in rows
        ]

    def _get(self, endpoint: str, path: str, params: dict[str, str], symbol: str | None) -> Any:
        for attempt in range(self._retries + 1):
            last_attempt = attempt == self._retries
            self._guard.check(symbol)
            try:
                response = self._client.get(path, params=params, headers=self._headers)
            except httpx.TransportError as exc:
                self._guard.record(endpoint, symbol, 0, 0)
                log.warning("tiingo %s request failed: %s", endpoint, type(exc).__name__)
                if last_attempt:
                    raise ProviderUnavailable("network") from exc
                self._sleep(self._backoff * 2**attempt)
                continue

            self._guard.record(endpoint, symbol, response.status_code, len(response.content))
            if response.status_code == 200:
                return json.loads(response.text, parse_float=Decimal)
            if response.status_code == 404:
                raise SymbolNotFound(symbol)
            if response.status_code == 429:
                raise QuotaExceeded("rate limited by provider")
            if response.status_code >= 500 and not last_attempt:
                self._sleep(self._backoff * 2**attempt)
                continue
            log.warning("tiingo %s returned HTTP %s", endpoint, response.status_code)
            raise ProviderUnavailable(f"http {response.status_code}")
        raise ProviderUnavailable("retries exhausted")  # pragma: no cover
