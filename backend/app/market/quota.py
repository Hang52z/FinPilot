"""Provider usage tracking and plan-limit enforcement, stored in `provider_usage`."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.market.models import ProviderUsage
from app.market.provider import QuotaExceeded


@dataclass(frozen=True)
class ProviderLimits:
    requests_per_hour: int
    requests_per_day: int
    symbols_per_month: int
    bytes_per_month: int


def utcnow() -> datetime:
    return datetime.now(UTC)


class UsageGuard:
    """Checks limits before each request and records each request after it.

    Uses its own sessions so usage is committed even when the caller's transaction rolls back.
    Hour and day are rolling windows; month is the calendar month in UTC.
    """

    def __init__(
        self,
        session_factory: sessionmaker[Session],
        provider: str,
        limits: ProviderLimits,
        clock: Callable[[], datetime] = utcnow,
    ) -> None:
        self._sessions = session_factory
        self._provider = provider
        self._limits = limits
        self._clock = clock

    def check(self, symbol: str | None) -> None:
        now = self._clock()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        mine = ProviderUsage.provider == self._provider
        with self._sessions() as db:

            def requests_since(start: datetime) -> int:
                q = select(func.count()).where(mine, ProviderUsage.requested_at >= start)
                return db.scalar(q) or 0

            if requests_since(now - timedelta(hours=1)) >= self._limits.requests_per_hour:
                raise QuotaExceeded("hourly request limit")
            if requests_since(now - timedelta(days=1)) >= self._limits.requests_per_day:
                raise QuotaExceeded("daily request limit")

            this_month = (mine, ProviderUsage.requested_at >= month_start)
            used_bytes = db.scalar(select(func.sum(ProviderUsage.bytes)).where(*this_month)) or 0
            if used_bytes >= self._limits.bytes_per_month:
                raise QuotaExceeded("monthly bandwidth limit")

            if symbol is not None:
                symbols = select(ProviderUsage.symbol).where(
                    *this_month, ProviderUsage.symbol.is_not(None)
                )
                seen = set(db.scalars(symbols.distinct()))
                if symbol not in seen and len(seen) >= self._limits.symbols_per_month:
                    raise QuotaExceeded("monthly symbol limit")

    def record(self, endpoint: str, symbol: str | None, status: int, size: int) -> None:
        with self._sessions() as db:
            db.add(
                ProviderUsage(
                    provider=self._provider,
                    endpoint=endpoint,
                    symbol=symbol,
                    status=status,
                    bytes=size,
                    requested_at=self._clock(),
                )
            )
            db.commit()
