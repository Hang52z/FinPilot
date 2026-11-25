# FinPilot

AI financial research app for iOS, Android and the web. Research only — it never places trades.

Status: **Phase 1 — Market Data**. See [PLAN.md](PLAN.md) for the roadmap.

## Requirements

- Docker with Compose v2
- Node.js 22 (app only)

## Start

```bash
make up
```

Postgres and the API start at `http://localhost:8000` with migrations applied. For market data,
put your Tiingo key in `.env` as `TIINGO_API_KEY` (copy `.env.example`). Check it:

```bash
curl http://localhost:8000/api/v1/health
```

The app runs on your machine, not in Docker:

```bash
make web
```

Opens the web app at `http://localhost:8081`. For iOS and Android:

```bash
make mobile
```

Press `i` for the iOS simulator or `a` for Android. On a physical device, copy
`apps/mobile/.env.example` to `apps/mobile/.env` and set `EXPO_PUBLIC_API_URL` to your computer's LAN IP.

## Develop

| Task | Command |
|---|---|
| Run every CI check | `make check` |
| Backend checks only | `make check-backend` |
| App checks only | `make check-mobile` |
| New migration | `make migration m="add securities"` |
| Stop | `make down` |

Backend code reloads on save. API docs are at `http://localhost:8000/docs` outside production.

## Web deployment (Cloudflare Pages)

The web app is the same Expo app exported as static files. The API runs on its own subdomain.

1. Cloudflare Pages → Create → connect this repository.
2. Root directory `apps/mobile`, build command `npx expo export --platform web`, output directory `dist`.
3. Environment variables: `NODE_VERSION=22`, `EXPO_PUBLIC_API_URL=https://finpilotapi.<your-domain>`.
4. Add your web subdomain under Custom domains.
5. On the backend, set `CORS_ORIGINS=["https://<web-subdomain>.<your-domain>"]`.

Every path serves `index.html`, so links such as `/settings` open directly. Security headers come
from `apps/mobile/public/_headers`. The site works once the API is publicly reachable (Phase 10).

## Layout

```text
apps/mobile/   Expo app for iOS, Android and web (Expo Router, TanStack Query, i18next)
backend/       FastAPI, SQLAlchemy, Alembic
docs/          Architecture, API contract, decision records
```

Contributors and coding agents: read [AGENTS.md](AGENTS.md) first.
