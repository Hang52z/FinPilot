# API

Base path: `/api/v1`. JSON only. Interactive docs at `/docs` outside production.

Responses carry stable machine values; the client is responsible for user-facing text and translation.

## `GET /health`

Liveness and database connectivity.

| Status | Body |
|---|---|
| `200` | `{"status": "ok", "database": "ok", "version": "0.1.0"}` |
| `503` | `{"status": "degraded", "database": "unavailable", "version": "0.1.0"}` |

| Field | Values |
|---|---|
| `status` | `ok` \| `degraded` |
| `database` | `ok` \| `unavailable` |
| `version` | Backend version (semver) |
