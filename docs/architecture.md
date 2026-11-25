# Architecture

Modular monolith. One FastAPI service, one PostgreSQL database, one Expo app.

```text
iOS / Android / Web (one Expo app)
      │  HTTPS, JSON
      ▼
FastAPI  /api/v1   (finpilotapi.<domain>)
      │  SQLAlchemy
      ▼
PostgreSQL 16
```

## Modules

| Module | Responsibility |
|---|---|
| `core` | Config, database session, error contract, health |
| `market` | Securities, daily prices, provider access, plan limits, watchlist |

## Boundaries

- The app talks only to the API. It never reaches the database or holds server secrets.
- Configuration is read once, in `backend/app/core/config.py`, from environment variables.
- Schema changes go through Alembic migrations in `backend/migrations/versions/`.
- External data comes only through a provider interface (`market/provider.py`); see `docs/data-sources.md`.
- Backend modules are added per phase under `backend/app/<module>/`; `core/` holds shared infrastructure only.

## Environments

| `ENV` | Used by | Notes |
|---|---|---|
| `development` | `docker compose up` | Code reload, `/docs` enabled |
| `test` | `docker-compose.test.yml` | Throwaway database on tmpfs |
| `production` | Phase 10 | `/docs` disabled; runtime image target, non-root |

## App

One Expo codebase builds iOS, Android and web. The web build is static files (`output: "single"`)
hosted on Cloudflare Pages; it calls the API on a separate subdomain, allowed by `CORS_ORIGINS`.


- Navigation: Expo Router. Four tabs (Home, Research, AI, Portfolio); Settings opens as a modal from the header.
- Server state: TanStack Query. All requests go through `services/api.ts`.
- Theme: tokens in `theme/tokens.ts`, light and dark, chosen by the system setting.
- Language: English by default, Chinese selectable in Settings, choice stored on device.
