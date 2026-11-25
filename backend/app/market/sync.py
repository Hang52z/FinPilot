"""Daily price synchronisation: incremental, idempotent, and aware of splits and dividends."""

import logging
from collections.abc import Iterator, Sequence
from dataclasses import asdict, dataclass
from datetime import date, datetime
from itertools import islice

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.market.models import MarketPrice, Security
from app.market.provider import DailyBar, MarketDataProvider

log = logging.getLogger(__name__)

EARLIEST = date(1962, 1, 1)
CHUNK = 2000


@dataclass(frozen=True)
class SyncResult:
    fetched: int
    stored: int
    rejected: int
    full_refresh: bool


def validate_bar(bar: DailyBar) -> bool:
    """Rejects bars that cannot be real: non-positive prices, high below low, negative volume."""
    prices = (bar.open, bar.high, bar.low, bar.close, bar.adj_close)
    return (
        all(p > 0 for p in prices)
        and bar.high >= bar.low
        and bar.volume >= 0
        and bar.split_factor > 0
    )


def _has_corporate_action(bars: Sequence[DailyBar], after: date) -> bool:
    return any(b.date > after and (b.split_factor != 1 or b.div_cash != 0) for b in bars)


def _chunks(rows: list[dict[str, object]]) -> Iterator[list[dict[str, object]]]:
    it = iter(rows)
    while batch := list(islice(it, CHUNK)):
        yield batch


def sync_prices(
    db: Session, provider: MarketDataProvider, security: Security, today: date, now: datetime
) -> SyncResult:
    """Fetches new bars since the last stored date and upserts them.

    A split or dividend after the last stored date changes every earlier adjusted price,
    so the full history is fetched again in that case.
    """
    last = db.scalar(
        select(func.max(MarketPrice.date)).where(MarketPrice.security_id == security.id)
    )
    first = security.listed_from or EARLIEST

    bars = provider.get_daily_bars(security.symbol, last or first, today)
    full_refresh = last is None
    if last is not None and _has_corporate_action(bars, last):
        bars = provider.get_daily_bars(security.symbol, first, today)
        full_refresh = True

    valid = [b for b in bars if validate_bar(b)]
    rejected = len(bars) - len(valid)
    if rejected:
        log.warning("%s: rejected %d invalid bars", security.symbol, rejected)

    rows: list[dict[str, object]] = [
        {**asdict(b), "security_id": security.id, "source": provider.name, "fetched_at": now}
        for b in valid
    ]
    for batch in _chunks(rows):
        stmt = insert(MarketPrice).values(batch)
        updated = {c: stmt.excluded[c] for c in batch[0] if c not in ("security_id", "date")}
        db.execute(stmt.on_conflict_do_update(index_elements=["security_id", "date"], set_=updated))

    security.prices_synced_at = now
    db.commit()
    return SyncResult(len(bars), len(valid), rejected, full_refresh)
