from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.market.models import MarketPrice, Security
from app.market.sync import sync_prices, validate_bar
from tests.conftest import FakeProvider, bar, weekdays

NOW = datetime(2026, 11, 26, 1, 0, tzinfo=UTC)
DAYS = weekdays(date(2026, 11, 2), 10)


def security(db: Session) -> Security:
    s = Security(
        symbol="NVDA", name="NVIDIA", source="tiingo", listed_from=DAYS[0], info_fetched_at=NOW
    )
    db.add(s)
    db.commit()
    return s


def count(db: Session) -> int:
    return db.scalar(select(func.count()).select_from(MarketPrice)) or 0


def test_first_sync_stores_full_history(db: Session, provider: FakeProvider) -> None:
    provider.add("NVDA", "NVIDIA", [bar(d, "100") for d in DAYS])

    result = sync_prices(db, provider, security(db), DAYS[-1], NOW)

    assert result.full_refresh and result.stored == 10
    assert count(db) == 10
    assert provider.calls == [("prices", f"NVDA:{DAYS[0]}")]


def test_resync_is_idempotent_and_incremental(db: Session, provider: FakeProvider) -> None:
    provider.add("NVDA", "NVIDIA", [bar(d, "100") for d in DAYS[:5]])
    s = security(db)
    sync_prices(db, provider, s, DAYS[4], NOW)

    provider.bars["NVDA"] = [bar(d, "100") for d in DAYS[:5]] + [bar(d, "101") for d in DAYS[5:]]
    sync_prices(db, provider, s, DAYS[-1], NOW)
    sync_prices(db, provider, s, DAYS[-1], NOW)

    assert count(db) == 10
    assert provider.calls[1] == ("prices", f"NVDA:{DAYS[4]}")


def test_revised_bar_is_updated_not_duplicated(db: Session, provider: FakeProvider) -> None:
    provider.add("NVDA", "NVIDIA", [bar(DAYS[0], "100")])
    s = security(db)
    sync_prices(db, provider, s, DAYS[0], NOW)

    provider.bars["NVDA"] = [bar(DAYS[0], "100.5")]
    sync_prices(db, provider, s, DAYS[0], NOW)

    assert count(db) == 1
    assert db.scalar(select(MarketPrice.close)) == Decimal("100.5")


def test_split_after_last_sync_refetches_full_history(db: Session, provider: FakeProvider) -> None:
    provider.add("NVDA", "NVIDIA", [bar(d, "1000") for d in DAYS[:5]])
    s = security(db)
    sync_prices(db, provider, s, DAYS[4], NOW)

    # After a 10:1 split, Tiingo restates every earlier adjusted close.
    restated = [bar(d, "1000", adj="100") for d in DAYS[:5]]
    provider.bars["NVDA"] = [*restated, bar(DAYS[5], "101", split="10")]
    result = sync_prices(db, provider, s, DAYS[5], NOW)

    assert result.full_refresh
    assert provider.calls[-1] == ("prices", f"NVDA:{DAYS[0]}")
    first = db.scalar(select(MarketPrice).order_by(MarketPrice.date).limit(1))
    assert first is not None and first.adj_close == Decimal("100")


def test_dividend_after_last_sync_refetches_full_history(
    db: Session, provider: FakeProvider
) -> None:
    provider.add("NVDA", "NVIDIA", [bar(d, "100") for d in DAYS[:5]])
    s = security(db)
    sync_prices(db, provider, s, DAYS[4], NOW)

    provider.bars["NVDA"].append(bar(DAYS[5], "100", div="0.01"))
    assert sync_prices(db, provider, s, DAYS[5], NOW).full_refresh


def test_invalid_bars_are_rejected(db: Session, provider: FakeProvider) -> None:
    broken = bar(DAYS[1], "100")
    broken = broken.__class__(**{**broken.__dict__, "high": Decimal("90")})
    provider.add("NVDA", "NVIDIA", [bar(DAYS[0], "100"), broken])

    result = sync_prices(db, provider, security(db), DAYS[1], NOW)

    assert (result.stored, result.rejected) == (1, 1)
    assert count(db) == 1


def test_validate_bar_rules() -> None:
    good = bar(DAYS[0], "10")
    assert validate_bar(good)
    assert not validate_bar(good.__class__(**{**good.__dict__, "close": Decimal("0")}))
    assert not validate_bar(good.__class__(**{**good.__dict__, "volume": -1}))
