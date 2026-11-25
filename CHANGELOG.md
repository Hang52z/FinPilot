# Changelog

## Unreleased

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
