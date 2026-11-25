# API

Base path: `/api/v1`. JSON only. Interactive docs at `/docs` outside production.

## Conventions

- **Errors** are always `{"error": "<code>"}` with a stable machine code; the client translates it.
  Request validation errors are `422 {"error": "invalid_request", "fields": [...]}`.
- **Decimals** (prices, changes) are JSON strings to keep exact precision, e.g. `"149.3000"`.
- **Dates**: `date` fields are exchange market dates (`YYYY-MM-DD`); `*_at` fields are UTC timestamps.
- **Symbols** are case-insensitive in requests and upper-case in responses. Allowed: `A–Z 0–9 . -`, 1–10 characters.

| Code | Status | Meaning |
|---|---|---|
| `invalid_request` | 422 | A parameter or body field is invalid |
| `invalid_symbol` | 422 | Symbol has invalid characters or length |
| `symbol_not_found` | 404 | The provider does not know the symbol, or it is not in the watchlist |
| `provider_unavailable` | 503 | The data provider failed and nothing is stored for this request |
| `provider_quota_exceeded` | 503 | A plan limit was reached and nothing is stored for this request |
| `provider_not_configured` | 503 | No provider API key is set and nothing is stored for this request |

When the provider fails but data is stored, endpoints return the stored data with `200`; its
`date` / `as_of` / `fetched_at` show how old it is.

## `GET /health`

| Status | Body |
|---|---|
| `200` | `{"status": "ok", "database": "ok", "version": "0.1.0"}` |
| `503` | `{"status": "degraded", "database": "unavailable", "version": "0.1.0"}` |

## `GET /market/search?q=<text>`

US-listed active stocks and ETFs matching a symbol or company name. Cached for 24 hours per query.

```json
{"results": [{"symbol": "NVDA", "name": "NVIDIA Corp", "asset_type": "stock"}]}
```

`asset_type` is `stock`, `etf`, or `null` when unknown. When the provider is unavailable, matches
from stored securities are returned (`asset_type: null`); with none, the provider error is returned.

## `GET /market/stocks/{symbol}`

```json
{
  "symbol": "NVDA", "name": "NVIDIA Corp", "exchange": "NASDAQ", "description": "...",
  "currency": "USD",
  "last_close": {"date": "2026-11-25", "close": "149.3000", "change": "-6.0800", "change_pct": "-3.91"},
  "source": "tiingo", "fetched_at": "2026-11-25T23:32:49Z"
}
```

`last_close` is the latest **daily close**, not a real-time quote; `null` if no prices are stored.
`change` / `change_pct` compare with the previous close using adjusted prices, so splits do not
distort them; `null` when there is no previous close. `change_pct` is in percent.

## `GET /market/stocks/{symbol}/history?range=1M|3M|6M|1Y|5Y|MAX`

Default `1Y`. Ranges count calendar days back from `as_of` (31, 92, 183, 366, 1827, all).

```json
{
  "symbol": "NVDA", "range": "1Y", "source": "tiingo",
  "as_of": "2026-11-25", "fetched_at": "2026-11-25T23:32:49Z",
  "bars": [{"date": "2025-11-25", "open": "...", "high": "...", "low": "...", "close": "...",
            "adj_close": "...", "volume": 123}]
}
```

Bars are oldest first. `open/high/low/close` are as traded; `adj_close` is split- and
dividend-adjusted and is the value to chart or compute returns from.

## Watchlist

Single-user until accounts arrive (Phase 9).

| Request | Response |
|---|---|
| `GET /watchlist` | `{"items": [{"symbol", "name", "last_close"}], "source", "fetched_at"}`, oldest added first |
| `POST /watchlist` `{"symbol": "NVDA"}` | `201` with the item when added, `200` if already present |
| `DELETE /watchlist/{symbol}` | `204`; `404 symbol_not_found` if not in the watchlist |
