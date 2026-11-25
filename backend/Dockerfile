# syntax=docker/dockerfile:1

# Shared settings. The virtualenv lives outside /app so a source bind-mount never hides it.
FROM python:3.13-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"
WORKDIR /app

FROM base AS builder
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv
RUN pip install --no-cache-dir uv==0.11.32
COPY pyproject.toml uv.lock ./

FROM builder AS runtime-deps
RUN uv sync --frozen --no-dev --no-install-project

# Development and test: all dependencies; source is bind-mounted in development.
FROM builder AS dev
RUN uv sync --frozen --no-install-project
COPY . .
EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]

# Production: runtime dependencies and source only, non-root.
FROM base AS runtime
COPY --from=runtime-deps /opt/venv /opt/venv
COPY . .
RUN useradd --create-home --uid 1000 app
USER app
EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
