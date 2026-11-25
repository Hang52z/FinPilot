# AGENTS.md

Rules and facts for coding agents. Keep this file in sync with the code.

## Read first

1. This file.
2. [PLAN.md](PLAN.md) — product scope, phases, and the full agent workflow (§8) and Definition of Done (§9).
3. [docs/architecture.md](docs/architecture.md) and [docs/api.md](docs/api.md).
4. [docs/decisions/](docs/decisions/) — why things are the way they are.

**Current phase: 1 — Market Data (complete).** Do not start work from a later phase unless asked.

## Principles

- Clean as Linear / Apple Notes: no taglines, hint text, decorative labels or repeated information.
  If a screen needs explanatory text, change the layout instead. Never remove error feedback,
  accessibility labels, data sources, risk notices or legally required text.
- Every change must improve UX, DX and AX together; record any unavoidable trade-off in `docs/decisions/`.
- Do not break anything. YAGNI, KISS, DRY. No new dependency, table or module without a current need.
- Never fabricate data. No mock data outside tests.

## Commands (Docker-first)

| Task | Command |
|---|---|
| Start db + API | `make up` |
| All CI checks | `make check` |
| Backend checks | `make check-backend` (ruff, mypy, migration round-trip, pytest) |
| App checks | `make check-mobile` (eslint, prettier, tsc, jest, web build) |
| Web app | `make web` |
| New migration | `make migration m="..."` |

The app can also be checked on the host: `cd apps/mobile && npm run check`.
`make web` serves the web app at `http://localhost:8081`; the dev API already allows that origin.

`apps/mobile` is one codebase for iOS, Android and web. Every change must work on all three;
use `Platform.OS` only for a real platform difference, never to hide a bug.
Add mobile packages with `npx expo install <pkg>` so versions match the Expo SDK.

## Module map

### Backend (`backend/app/`)

| Path | Responsibility |
|---|---|
| `main.py` | `create_app()`: middleware and routers. All routes live under `/api/v1`. |
| `core/config.py` | `Settings` from environment variables. The only place config is read. |
| `core/db.py` | `Base` for ORM models, `get_engine()`, `get_db()` session dependency. |
| `core/health.py` | `GET /api/v1/health`. |
| `core/errors.py` | `AppError` and the `{"error": "<code>"}` response contract. |
| `market/provider.py` | `MarketDataProvider` protocol, data classes, market error codes, symbol rules. |
| `market/tiingo.py` | Tiingo implementation (the only file that knows Tiingo's API). |
| `market/quota.py` | `UsageGuard`: plan limits checked and recorded in `provider_usage`. |
| `market/sync.py` | Incremental, idempotent price sync; split/dividend full refresh; bar validation. |
| `market/service.py` | Use cases: search, stock, history, watchlist; freshness rule; stored-data fallback. |
| `market/router.py` | `/market/*` and `/watchlist` routes; dependencies `get_provider`, `get_clock`. |

New business modules go in `backend/app/<module>/` (e.g. `market/`) with their own router,
models, schemas and service. No circular imports between modules. All financial math lives in the backend.

### App (`apps/mobile/`, iOS + Android + web)

| Path | Responsibility |
|---|---|
| `app/` | Routes only (Expo Router). `(tabs)/` holds the four tabs; `stock/[symbol].tsx` is the detail; `settings.tsx` is a modal. |
| `components/` | Shared UI. `Screen` is the base container for every screen. |
| `hooks/` | TanStack Query hooks, one per server resource. |
| `services/api.ts` | The only place that calls `fetch`. `ApiError.code` carries the backend error code. |
| `services/market.ts` | Market and watchlist endpoints and their types. |
| `features/market/` | Pure logic: formatting, error-code → message, chart path math. |
| `theme/` | Design tokens and `useTheme()`. Never hard-code colors, spacing or radius. |
| `i18n/` | `en.ts` (source of truth, default) and `zh.ts`. Every UI string uses `t()`. |
| `public/` | Copied as-is into the web build (`_headers` for Cloudflare Pages). |

## Conventions

- **Python**: typed (`mypy --strict`), ruff-formatted, line length 100. Pydantic models for every request/response.
- **TypeScript**: strict, Prettier, `@/` imports from the app root.
- **Strings**: add a key to `i18n/en.ts` and `i18n/zh.ts` together; a test fails if keys differ.
- **API errors**: return stable machine codes, never user-facing prose. The client localizes.
- **Database**: one Alembic migration per change; must upgrade and downgrade cleanly. UTC everywhere,
  exact numeric types for money. Tables are created only by the phase that needs them.
- **Market data**: never call a provider from a route; go through `MarketService`. Show every price
  with its date and source; daily closes are never "real-time". Compute changes from adjusted prices.
- **Tests**: backend tests use the real test database and `FakeProvider` (`tests/conftest.py`);
  app tests mock `fetch` with `test-utils/mockApi.ts`. Every change adds or updates tests. Never delete or skip a test to get green.

## Completion report

Finish every task with the report format in PLAN.md §8. Mark anything not actually run as **Unverified**.
