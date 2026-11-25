from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    """Base class for all ORM models. Models are added per phase."""


@lru_cache
def get_engine() -> Engine:
    return create_engine(get_settings().database_url, pool_pre_ping=True)


def get_db() -> Iterator[Session]:
    session = sessionmaker(bind=get_engine())()
    try:
        yield session
    finally:
        session.close()
