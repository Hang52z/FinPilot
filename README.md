# FinPilot

AI financial research app for iOS and Android. Research only — it never places trades.

Status: **Phase 0 — Project Foundation**. See [PLAN.md](PLAN.md) for the roadmap.

## Requirements

- Docker with Compose v2
- Node.js 22 (mobile app only)

## Start

```bash
make up
```

Postgres and the API start at `http://localhost:8000` with migrations applied. Check it:

```bash
curl http://localhost:8000/api/v1/health
```

Mobile app (runs on your machine, not in Docker):

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
| Mobile checks only | `make check-mobile` |
| New migration | `make migration m="add securities"` |
| Stop | `make down` |

Backend code reloads on save. API docs are at `http://localhost:8000/docs` outside production.

## Layout

```text
apps/mobile/   Expo app (Expo Router, TanStack Query, i18next)
backend/       FastAPI, SQLAlchemy, Alembic
docs/          Architecture, API contract, decision records
```

Contributors and coding agents: read [AGENTS.md](AGENTS.md) first.
