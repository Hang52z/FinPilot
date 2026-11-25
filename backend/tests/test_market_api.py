from datetime import UTC, date, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import create_app
from app.market.provider import SearchResult
from app.market.router import get_provider
from tests.conftest import NOW, FakeProvider, bar, weekdays

DAYS = weekdays(date(2026, 11, 2), 18)  # ends Wednesday 2026-11-25


def nvda(provider: FakeProvider) -> None:
    provider.add("NVDA", "NVIDIA Corp", [bar(d, str(100 + i)) for i, d in enumerate(DAYS)])


# Search ------------------------------------------------------------------------------


def test_search_returns_provider_results_and_caches(
    api: TestClient, provider: FakeProvider
) -> None:
    provider.search_results = [SearchResult("NVDA", "NVIDIA Corp", "stock")]

    first = api.get("/api/v1/market/search", params={"q": "Nvidia"})
    api.get("/api/v1/market/search", params={"q": "nvidia "})

    assert first.json() == {
        "results": [{"symbol": "NVDA", "name": "NVIDIA Corp", "asset_type": "stock"}]
    }
    assert provider.calls == [("search", "nvidia")]


def test_search_falls_back_to_stored_securities(api: TestClient, provider: FakeProvider) -> None:
    nvda(provider)
    api.get("/api/v1/market/stocks/NVDA")
    provider.unavailable = True

    response = api.get("/api/v1/market/search", params={"q": "nvid"})

    assert response.status_code == 200
    assert response.json()["results"] == [
        {"symbol": "NVDA", "name": "NVIDIA Corp", "asset_type": None}
    ]


def test_search_reports_provider_error_when_nothing_is_stored(
    api: TestClient, provider: FakeProvider
) -> None:
    provider.unavailable = True
    response = api.get("/api/v1/market/search", params={"q": "apple"})
    assert (response.status_code, response.json()) == (503, {"error": "provider_unavailable"})


def test_search_requires_query(api: TestClient) -> None:
    response = api.get("/api/v1/market/search")
    assert response.status_code == 422
    assert response.json()["error"] == "invalid_request"


# Stock -------------------------------------------------------------------------------


def test_stock_returns_last_close_and_source(api: TestClient, provider: FakeProvider) -> None:
    nvda(provider)

    body = api.get("/api/v1/market/stocks/nvda").json()

    assert body["symbol"] == "NVDA"
    assert body["source"] == "tiingo"
    assert body["last_close"]["date"] == "2026-11-25"
    assert body["last_close"]["close"] == "117.0000"
    assert body["last_close"]["change"] == "1.0000"
    assert body["last_close"]["change_pct"] == "0.86"
    assert body["fetched_at"].startswith("2026-11-26T01:00")


def test_change_uses_adjusted_prices_across_a_split(
    api: TestClient, provider: FakeProvider
) -> None:
    provider.add(
        "NVDA",
        "NVIDIA Corp",
        [bar(DAYS[-2], "1000", adj="100"), bar(DAYS[-1], "110", split="10")],
    )

    last = api.get("/api/v1/market/stocks/NVDA").json()["last_close"]

    assert last["change_pct"] == "10.00"
    assert last["change"] == "10.0000"


def test_repeated_requests_do_not_call_provider_again(
    api: TestClient, provider: FakeProvider
) -> None:
    nvda(provider)
    api.get("/api/v1/market/stocks/NVDA")
    calls = len(provider.calls)

    api.get("/api/v1/market/stocks/NVDA")
    api.get("/api/v1/market/stocks/NVDA/history")

    assert len(provider.calls) == calls


def test_next_day_triggers_incremental_sync(
    api: TestClient, provider: FakeProvider, clock: list[datetime]
) -> None:
    nvda(provider)
    api.get("/api/v1/market/stocks/NVDA")
    provider.bars["NVDA"].append(bar(date(2026, 11, 26), "120"))
    clock[0] = NOW + timedelta(days=1)

    body = api.get("/api/v1/market/stocks/NVDA").json()

    assert body["last_close"]["date"] == "2026-11-26"
    assert provider.calls[-1] == ("prices", "NVDA:2026-11-25")


def test_stale_data_is_served_when_provider_fails(
    api: TestClient, provider: FakeProvider, clock: list[datetime]
) -> None:
    nvda(provider)
    api.get("/api/v1/market/stocks/NVDA")
    provider.unavailable = True
    clock[0] = NOW + timedelta(days=1)

    response = api.get("/api/v1/market/stocks/NVDA")

    assert response.status_code == 200
    assert response.json()["last_close"]["date"] == "2026-11-25"


def test_unknown_symbol(api: TestClient) -> None:
    response = api.get("/api/v1/market/stocks/ZZZZ")
    assert (response.status_code, response.json()) == (404, {"error": "symbol_not_found"})


def test_invalid_symbol_makes_no_provider_call(api: TestClient, provider: FakeProvider) -> None:
    response = api.get("/api/v1/market/stocks/bad symbol!")
    assert (response.status_code, response.json()) == (422, {"error": "invalid_symbol"})
    assert provider.calls == []


def test_provider_down_with_no_data(api: TestClient, provider: FakeProvider) -> None:
    provider.unavailable = True
    response = api.get("/api/v1/market/stocks/NVDA")
    assert (response.status_code, response.json()) == (503, {"error": "provider_unavailable"})


def test_provider_not_configured(db: Session) -> None:
    app = create_app()
    app.dependency_overrides[get_provider] = lambda: None
    response = TestClient(app).get("/api/v1/market/stocks/NVDA")
    assert (response.status_code, response.json()) == (503, {"error": "provider_not_configured"})


# History -----------------------------------------------------------------------------


def test_history_ranges(api: TestClient, provider: FakeProvider) -> None:
    nvda(provider)

    month = api.get("/api/v1/market/stocks/NVDA/history", params={"range": "1M"}).json()
    full = api.get("/api/v1/market/stocks/NVDA/history", params={"range": "MAX"}).json()

    assert month["as_of"] == "2026-11-25"
    assert len(full["bars"]) == 18
    assert month["bars"][0]["date"] >= str(date(2026, 10, 25))
    assert [b["date"] for b in full["bars"]] == sorted(b["date"] for b in full["bars"])
    assert set(full["bars"][0]) == {"date", "open", "high", "low", "close", "adj_close", "volume"}


def test_history_rejects_unknown_range(api: TestClient) -> None:
    response = api.get("/api/v1/market/stocks/NVDA/history", params={"range": "2W"})
    assert response.status_code == 422


# Watchlist ---------------------------------------------------------------------------


def test_watchlist_add_list_remove(api: TestClient, provider: FakeProvider) -> None:
    nvda(provider)

    assert api.get("/api/v1/watchlist").json()["items"] == []
    assert api.post("/api/v1/watchlist", json={"symbol": "nvda"}).status_code == 201
    assert api.post("/api/v1/watchlist", json={"symbol": "NVDA"}).status_code == 200

    items = api.get("/api/v1/watchlist").json()["items"]
    assert [i["symbol"] for i in items] == ["NVDA"]
    assert items[0]["last_close"]["close"] == "117.0000"

    assert api.delete("/api/v1/watchlist/NVDA").status_code == 204
    assert api.get("/api/v1/watchlist").json()["items"] == []
    assert api.delete("/api/v1/watchlist/NVDA").json() == {"error": "symbol_not_found"}


def test_watchlist_add_unknown_symbol(api: TestClient) -> None:
    response = api.post("/api/v1/watchlist", json={"symbol": "ZZZZ"})
    assert (response.status_code, response.json()) == (404, {"error": "symbol_not_found"})


def test_watchlist_still_lists_when_provider_fails(
    api: TestClient, provider: FakeProvider, clock: list[datetime]
) -> None:
    nvda(provider)
    api.post("/api/v1/watchlist", json={"symbol": "NVDA"})
    provider.unavailable = True
    clock[0] = datetime(2026, 11, 27, 1, 0, tzinfo=UTC)

    items = api.get("/api/v1/watchlist").json()["items"]

    assert items[0]["last_close"]["date"] == "2026-11-25"
