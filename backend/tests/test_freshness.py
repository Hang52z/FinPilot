from datetime import UTC, datetime

import pytest

from app.market.service import latest_data_ready, needs_sync

# November 2026: New York is UTC-5. 18:00 New York = 23:00 UTC.


@pytest.mark.parametrize(
    ("now", "expected"),
    [
        (datetime(2026, 11, 25, 23, 30, tzinfo=UTC), datetime(2026, 11, 25, 23, 0, tzinfo=UTC)),
        (datetime(2026, 11, 25, 22, 0, tzinfo=UTC), datetime(2026, 11, 24, 23, 0, tzinfo=UTC)),
        # Saturday and Sunday fall back to Friday.
        (datetime(2026, 11, 28, 15, 0, tzinfo=UTC), datetime(2026, 11, 27, 23, 0, tzinfo=UTC)),
        (datetime(2026, 11, 30, 12, 0, tzinfo=UTC), datetime(2026, 11, 27, 23, 0, tzinfo=UTC)),
        # Summer time: 18:00 New York = 22:00 UTC.
        (datetime(2026, 7, 1, 22, 30, tzinfo=UTC), datetime(2026, 7, 1, 22, 0, tzinfo=UTC)),
    ],
)
def test_latest_data_ready(now: datetime, expected: datetime) -> None:
    assert latest_data_ready(now) == expected


def test_needs_sync() -> None:
    now = datetime(2026, 11, 26, 15, 0, tzinfo=UTC)  # Thursday morning New York
    assert needs_sync(None, now)
    assert needs_sync(datetime(2026, 11, 25, 22, 0, tzinfo=UTC), now)
    assert not needs_sync(datetime(2026, 11, 25, 23, 30, tzinfo=UTC), now)
