from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app import __version__
from app.core.db import get_db

router = APIRouter(tags=["system"])


class Health(BaseModel):
    status: Literal["ok", "degraded"]
    database: Literal["ok", "unavailable"]
    version: str


@router.get("/health", response_model=Health)
def health(response: Response, db: Annotated[Session, Depends(get_db)]) -> Health:
    try:
        db.execute(text("SELECT 1"))
        database: Literal["ok", "unavailable"] = "ok"
    except SQLAlchemyError:
        database = "unavailable"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return Health(
        status="ok" if database == "ok" else "degraded",
        database=database,
        version=__version__,
    )
