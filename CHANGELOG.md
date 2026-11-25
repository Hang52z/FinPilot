# Changelog

## Unreleased

### Phase 1 — Market Data

- US stock and ETF search, security info and daily price history from Tiingo, stored in Postgres.
- Incremental, idempotent sync; full refresh after splits and dividends; invalid bars rejected.
- Tiingo plan limits enforced from settings and recorded in `provider_usage`; stored data is served
  when the provider fails or a limit is reached.
- Watchlist API and app: Home lists the watchlist, Research searches, stock detail shows price,
  change, chart with ranges, source and date; star adds or removes from the watchlist.
- One error format for the API (`{"error": "<code>"}`), translated in the app.

### Web

- The app also builds for the web (`make web`, `npm run build:web`); CI checks the web build.
- Cloudflare Pages setup documented; security headers in `apps/mobile/public/_headers`.
- `<html lang>` follows the chosen language.
- Development API allows the local web origin by default.

### Phase 0 — Project Foundation

- FastAPI backend with settings, SQLAlchemy, Alembic baseline migration and `GET /api/v1/health`.
- Docker Compose for development and an isolated test stack; `make` entry points.
- Expo app shell: Home, Research, AI and Portfolio tabs; Settings modal with English / 中文 switch.
- Design tokens with light and dark themes.
- CI: backend and mobile checks, tracked-secret guard.
