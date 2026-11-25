from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core import health
from app.core.config import get_settings

API_PREFIX = "/api/v1"


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="FinPilot API",
        docs_url=None if settings.env == "production" else "/docs",
        redoc_url=None,
    )
    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    app.include_router(health.router, prefix=API_PREFIX)
    return app


app = create_app()
