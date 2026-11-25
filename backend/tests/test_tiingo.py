import json
from datetime import date
from decimal import Decimal
from pathlib import Path

import httpx
import pytest

from app.market.provider import ProviderUnavailable, QuotaExceeded, SymbolNotFound
from app.market.tiingo import TiingoProvider

FIXTURES = Path(__file__).parent / "fixtures" / "tiingo"


class RecordingGuard:
    def __init__(self, blocked: bool = False) -> None:
        self.blocked = blocked
        self.records: list[tuple[str, str | None, int]] = []

    def check(self, symbol: str | None) -> None:
        if self.blocked:
            raise QuotaExceeded()

    def record(self, endpoint: str, symbol: str | None, status: int, size: int) -> None:
        self.records.append((endpoint, symbol, status))


def make(handler: httpx.MockTransport, guard: RecordingGuard | None = None) -> TiingoProvider:
    client = httpx.Client(base_url="https://api.tiingo.com", transport=handler)
    return TiingoProvider("test-key", guard or RecordingGuard(), client, sleep=lambda _: None)  # type: ignore[arg-type]


def fixture(name: str) -> bytes:
    return (FIXTURES / name).read_bytes()


def test_search_keeps_active_us_stocks_and_etfs() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, content=fixture("search_nvidia.json"))

    results = make(httpx.MockTransport(handler)).search("nvidia")

    # Canadian listings of the same companies are dropped; the US stock and US ETF remain.
    assert [(r.symbol, r.asset_type) for r in results] == [("NVDA", "stock"), ("NVDX", "etf")]
    assert results[1].name == results[1].name.strip()
    assert seen[0].headers["Authorization"] == "Token test-key"
    assert seen[0].url.params["query"] == "nvidia"


def test_get_security_parses_metadata() -> None:
    provider = make(
        httpx.MockTransport(lambda _: httpx.Response(200, content=fixture("meta_nvda.json")))
    )

    info = provider.get_security("NVDA")

    assert info.symbol == "NVDA"
    assert info.name == "NVIDIA Corp"
    assert info.exchange == "NASDAQ"
    assert info.start_date == date(1999, 1, 22)


def test_daily_bars_keep_exact_decimals_and_split_data() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["startDate"] == "2024-06-05"
        return httpx.Response(200, content=fixture("prices_nvda_split.json"))

    bars = make(httpx.MockTransport(handler)).get_daily_bars(
        "NVDA", date(2024, 6, 5), date(2024, 6, 12)
    )

    split_day = next(b for b in bars if b.date == date(2024, 6, 10))
    assert split_day.split_factor == Decimal("10.0")
    assert bars[0].adj_close == Decimal("122.0923218538")
    assert isinstance(bars[0].volume, int)


def test_unknown_symbol_raises_not_found() -> None:
    provider = make(
        httpx.MockTransport(lambda _: httpx.Response(404, json={"detail": "Not found."}))
    )
    with pytest.raises(SymbolNotFound):
        provider.get_security("ZZZZ")


def test_server_errors_are_retried_then_succeed() -> None:
    responses = iter([httpx.Response(502), httpx.Response(200, content=fixture("meta_nvda.json"))])
    guard = RecordingGuard()

    info = make(httpx.MockTransport(lambda _: next(responses)), guard).get_security("NVDA")

    assert info.symbol == "NVDA"
    assert [r[2] for r in guard.records] == [502, 200]


def test_network_failure_after_retries_is_unavailable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("timeout", request=request)

    guard = RecordingGuard()
    with pytest.raises(ProviderUnavailable):
        make(httpx.MockTransport(handler), guard).get_security("NVDA")
    assert len(guard.records) == 3


def test_client_errors_are_not_retried() -> None:
    guard = RecordingGuard()
    with pytest.raises(ProviderUnavailable):
        make(httpx.MockTransport(lambda _: httpx.Response(401)), guard).get_security("NVDA")
    assert len(guard.records) == 1


def test_provider_rate_limit_is_quota_exceeded() -> None:
    with pytest.raises(QuotaExceeded):
        make(httpx.MockTransport(lambda _: httpx.Response(429))).get_security("NVDA")


def test_quota_block_makes_no_request() -> None:
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(200, json={})

    with pytest.raises(QuotaExceeded):
        make(httpx.MockTransport(handler), RecordingGuard(blocked=True)).get_security("NVDA")
    assert calls == []


def test_fixtures_are_valid_json() -> None:
    for path in FIXTURES.glob("*.json"):
        json.loads(path.read_text())
