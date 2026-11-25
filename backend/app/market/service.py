"""Market data use cases. Reads come from Postgres; the provider is called only when stale."""

import logging
import time
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from datetime import time as clock_time
from decimal import Decimal
from zoneinfo import ZoneInfo

from sqlalchemy import delete, func, or_, select
from sqlalchemy.orm import Session

from app.market.models import MarketPrice, Security, WatchlistItem
from app.market.provider import (
    MarketDataProvider,
    ProviderNotConfigured,
    ProviderUnavailable,
    SearchResult,
    SymbolNotFound,
    normalize_symbol,
)
from app.market.schemas import (
    Bar,
    HistoryOut,
    LastClose,
    Range,
    StockOut,
    WatchlistItemOut,
    WatchlistOut,
)
from app.market.sync import sync_prices

log = logging.getLogger(__name__)

NEW_YORK = ZoneInfo("America/New_York")
# Daily bars are final some time after the 16:00 close; sync only after this time.
DATA_READY = clock_time(18, 0)
RANGE_DAYS: dict[Range, int | None] = {
    "1M": 31,
    "3M": 92,
    "6M": 183,
    "1Y": 366,
    "5Y": 1827,
    "MAX": None,
}
SEARCH_TTL_SECONDS = 24 * 3600
PRICE_STEP = Decimal("0.0001")
PCT_STEP = Decimal("0.01")

_search_cache: dict[str, tuple[float, list[SearchResult]]] = {}


def clear_search_cache() -> None:
    _search_cache.clear()


def latest_data_ready(now: datetime) -> datetime:
    """The most recent weekday 18:00 New York time at or before `now` (UTC)."""
    local = now.astimezone(NEW_YORK)
    day = local.date()
    while True:
        ready = datetime.combine(day, DATA_READY, NEW_YORK)
        if day.weekday() < 5 and ready <= local:
            return ready.astimezone(UTC)
        day -= timedelta(days=1)


def needs_sync(synced_at: datetime | None, now: datetime) -> bool:
    return synced_at is None or synced_at < latest_data_ready(now)


def _last_close(bars: list[MarketPrice]) -> LastClose | None:
    """`bars` is newest first, at most two."""
    if not bars:
        return None
    last = bars[0]
    change = change_pct = None
    if len(bars) > 1 and bars[1].adj_close > 0:
        ratio = bars[1].adj_close / last.adj_close
        change = (last.close * (1 - ratio)).quantize(PRICE_STEP)
        change_pct = ((last.adj_close / bars[1].adj_close - 1) * 100).quantize(PCT_STEP)
    return LastClose(
        date=last.date, close=last.close.quantize(PRICE_STEP), change=change, change_pct=change_pct
    )


class MarketService:
    def __init__(
        self,
        db: Session,
        provider: MarketDataProvider | None,
        now: Callable[[], datetime],
        source: str = "tiingo",
    ) -> None:
        self._db = db
        self._provider = provider
        self._now = now
        self._source = source

    # Provider access -----------------------------------------------------------------

    def _require_provider(self) -> MarketDataProvider:
        if self._provider is None:
            raise ProviderNotConfigured()
        return self._provider

    # Search ----------------------------------------------------------------------------

    def search(self, query: str) -> list[SearchResult]:
        key = query.strip().lower()
        if not key:
            return []
        cached = _search_cache.get(key)
        if cached and cached[0] > time.monotonic():
            return cached[1]
        try:
            results = self._require_provider().search(key)
        except ProviderUnavailable:
            # Serve stored matches; with none, report the real reason instead of "no results".
            stored = self._search_stored(key)
            if not stored:
                raise
            log.info("search served from stored securities")
            return stored
        _search_cache[key] = (time.monotonic() + SEARCH_TTL_SECONDS, results)
        return results

    def _search_stored(self, query: str) -> list[SearchResult]:
        pattern = f"%{query}%"
        rows = self._db.scalars(
            select(Security)
            .where(or_(Security.symbol.ilike(pattern), Security.name.ilike(pattern)))
            .order_by(Security.symbol)
            .limit(20)
        )
        # Asset type is only known from provider search results, so it is not stored.
        return [SearchResult(s.symbol, s.name, None) for s in rows]

    # Securities and prices -------------------------------------------------------------

    def _find(self, symbol: str) -> Security | None:
        return self._db.scalar(select(Security).where(Security.symbol == symbol))

    def get_or_create_security(self, raw_symbol: str) -> Security:
        symbol = normalize_symbol(raw_symbol)
        security = self._find(symbol)
        if security is not None:
            return security
        provider = self._require_provider()
        info = provider.get_security(symbol)
        security = Security(
            symbol=info.symbol,
            name=info.name,
            exchange=info.exchange,
            description=info.description,
            listed_from=info.start_date,
            listed_until=info.end_date,
            source=provider.name,
            info_fetched_at=self._now(),
        )
        self._db.add(security)
        self._db.commit()
        return security

    def _has_prices(self, security: Security) -> bool:
        q = select(func.count()).where(MarketPrice.security_id == security.id)
        return bool(self._db.scalar(q))

    def ensure_fresh(self, security: Security) -> None:
        """Syncs when stale. If the provider fails but data is stored, serves the stored data."""
        now = self._now()
        if not needs_sync(security.prices_synced_at, now):
            return
        try:
            today = now.astimezone(NEW_YORK).date()
            sync_prices(self._db, self._require_provider(), security, today, now)
        except ProviderUnavailable:
            self._db.rollback()
            if not self._has_prices(security):
                raise
            log.info("%s: serving stored prices; provider unavailable", security.symbol)

    def _recent_bars(self, security: Security, limit: int) -> list[MarketPrice]:
        return list(
            self._db.scalars(
                select(MarketPrice)
                .where(MarketPrice.security_id == security.id)
                .order_by(MarketPrice.date.desc())
                .limit(limit)
            )
        )

    def stock(self, raw_symbol: str) -> StockOut:
        security = self.get_or_create_security(raw_symbol)
        self.ensure_fresh(security)
        return StockOut(
            symbol=security.symbol,
            name=security.name,
            exchange=security.exchange,
            description=security.description,
            currency=security.currency,
            last_close=_last_close(self._recent_bars(security, 2)),
            source=security.source,
            fetched_at=security.prices_synced_at,
        )

    def history(self, raw_symbol: str, range_: Range) -> HistoryOut:
        security = self.get_or_create_security(raw_symbol)
        self.ensure_fresh(security)
        as_of = self._db.scalar(
            select(func.max(MarketPrice.date)).where(MarketPrice.security_id == security.id)
        )
        query = select(MarketPrice).where(MarketPrice.security_id == security.id)
        days = RANGE_DAYS[range_]
        if as_of is not None and days is not None:
            query = query.where(MarketPrice.date >= as_of - timedelta(days=days))
        bars = [
            Bar(
                date=p.date,
                open=p.open.quantize(PRICE_STEP),
                high=p.high.quantize(PRICE_STEP),
                low=p.low.quantize(PRICE_STEP),
                close=p.close.quantize(PRICE_STEP),
                adj_close=p.adj_close.quantize(PRICE_STEP),
                volume=p.volume,
            )
            for p in self._db.scalars(query.order_by(MarketPrice.date))
        ]
        return HistoryOut(
            symbol=security.symbol,
            range=range_,
            bars=bars,
            source=security.source,
            as_of=as_of,
            fetched_at=security.prices_synced_at,
        )

    # Watchlist -------------------------------------------------------------------------

    def watchlist(self) -> WatchlistOut:
        securities = list(
            self._db.scalars(
                select(Security)
                .join(WatchlistItem, WatchlistItem.security_id == Security.id)
                .order_by(WatchlistItem.created_at, WatchlistItem.id)
            )
        )
        items = []
        for security in securities:
            try:
                self.ensure_fresh(security)
            except ProviderUnavailable:
                log.info("%s: no stored prices and provider unavailable", security.symbol)
            items.append(
                WatchlistItemOut(
                    symbol=security.symbol,
                    name=security.name,
                    last_close=_last_close(self._recent_bars(security, 2)),
                )
            )
        synced = [s.prices_synced_at for s in securities if s.prices_synced_at]
        return WatchlistOut(items=items, source=self._source, fetched_at=max(synced, default=None))

    def add_to_watchlist(self, raw_symbol: str) -> tuple[WatchlistItemOut, bool]:
        """Returns the item and whether it was newly added."""
        security = self.get_or_create_security(raw_symbol)
        exists = self._db.scalar(
            select(WatchlistItem).where(WatchlistItem.security_id == security.id)
        )
        if exists is None:
            self._db.add(WatchlistItem(security_id=security.id))
            self._db.commit()
        try:
            self.ensure_fresh(security)
        except ProviderUnavailable:
            log.info("%s: added without prices; provider unavailable", security.symbol)
        item = WatchlistItemOut(
            symbol=security.symbol,
            name=security.name,
            last_close=_last_close(self._recent_bars(security, 2)),
        )
        return item, exists is None

    def remove_from_watchlist(self, raw_symbol: str) -> None:
        symbol = normalize_symbol(raw_symbol)
        security = self._find(symbol)
        removed = 0
        if security is not None:
            result = self._db.execute(
                delete(WatchlistItem).where(WatchlistItem.security_id == security.id)
            )
            removed = result.rowcount  # type: ignore[attr-defined]
            self._db.commit()
        if not removed:
            raise SymbolNotFound(symbol)
