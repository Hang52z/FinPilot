# Data sources

## Tiingo — daily US stock and ETF prices

Plan: Tiingo Starter, personal key (`TIINGO_API_KEY`). Code: `backend/app/market/tiingo.py`.

| Use | Endpoint |
|---|---|
| Search | `GET /tiingo/utilities/search?query=` — filtered to active, `countryCode=US`, Stock/ETF |
| Security info | `GET /tiingo/daily/{ticker}` — name, exchange, description, listing dates |
| Daily prices | `GET /tiingo/daily/{ticker}/prices?startDate=&endDate=` — OHLCV, adjusted OHLCV, dividends, splits |

### Plan limits

Configured in `backend/app/core/config.py`, enforced by `UsageGuard` (`backend/app/market/quota.py`)
before every request, using the `provider_usage` table:

| Limit | Setting | Default | Window |
|---|---|---|---|
| Requests | `TIINGO_MAX_REQUESTS_PER_HOUR` | 50 | rolling hour |
| Requests | `TIINGO_MAX_REQUESTS_PER_DAY` | 1,000 | rolling 24 hours |
| Unique symbols | `TIINGO_MAX_SYMBOLS_PER_MONTH` | 500 | calendar month (UTC) |
| Bandwidth | `TIINGO_MAX_BYTES_PER_MONTH` | 1 GB | calendar month (UTC) |

Retries count as requests. A full history is about 1.8 MB for a symbol listed since 1999.

### When data is fetched

- **Prices** sync only when the last sync is older than the latest weekday 18:00 New York time
  (daily bars are final some time after the 16:00 close). App refreshes in between are served
  from Postgres with no provider call. Market holidays cost one extra call that finds no new bar.
- **Incremental**: from the last stored date (inclusive, to pick up revisions) to today, upserted on
  `(security_id, date)` — re-runs never duplicate.
- **Splits and dividends**: if a new bar has a split factor ≠ 1 or a dividend, Tiingo restates all
  earlier adjusted prices, so the full history is fetched again.
- **Validation**: bars with non-positive prices, high below low, or negative volume are rejected,
  logged and not stored.
- **Search** results are cached in memory for 24 hours per query.

If a limit is reached or Tiingo fails, stored data is served; only requests with nothing stored fail.

### Attribution and licensing

Prices are shown as "Daily close · date · Tiingo". Personal use under the Starter plan; commercial
display, redistribution and AI processing must be reviewed before release (PLAN.md Phase 11).
