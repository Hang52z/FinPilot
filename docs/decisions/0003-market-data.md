# 0003 — Market data foundation

Date: 2026-11-25 · Status: Accepted

## Provider interface

`MarketDataProvider` (`backend/app/market/provider.py`) is the only thing business code depends on.
Tiingo is one implementation. Provider errors are `AppError`s with stable codes, so the API error
contract needs no per-provider mapping.

- DX/AX: swapping or adding a provider touches one file; tests use an in-memory fake.

## Plan limits recorded in the database

Every outbound request is a row in `provider_usage`; limits are checked against it before each
request. Limits are settings, not constants in code. Rows survive restarts and are visible for the
cost monitoring planned in Phase 10. An in-memory counter was rejected: it resets on restart and
would let a restart loop exceed the plan.

## Freshness rule instead of a scheduler

Prices sync on read when the last sync predates the latest weekday 18:00 New York time. This needs
no background worker yet (Phase 8 adds one) and guarantees app refreshes do not call the provider.
Trade-off: the first request after the close waits for the sync (about 1–3 s for one symbol).

## Adjusted prices for change and charts

Daily change, range change and charts use adjusted closes; the displayed price is the traded
close. Without this, a split shows as a false −90% day (seen in real NVDA data, June 2024).

## Single-user watchlist

`watchlists` has no owner until accounts arrive in Phase 9, which will add `user_id` with a migration.

## Hand-drawn chart

The price chart is one SVG path (`react-native-svg`, which Expo supports on iOS, Android and web)
built by a small tested function. A chart library would add size and styling we would then remove.

## Effects

- UX: no fake or unlabeled data; every price shows "Daily close · date · Tiingo"; errors are one
  translated line; direction is shown with ▲/▼ and a sign, not only color.
- DX: real Tiingo responses are test fixtures; `pytest -m live` checks the real API on demand.
- AX: API contract, data rules and limits are written down in `docs/api.md` and `docs/data-sources.md`.
