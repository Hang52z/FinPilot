from collections.abc import Iterator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app import __version__
from app.core.db import get_db
from app.main import create_app


def test_health_ok(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok", "version": __version__}


def test_health_reports_unavailable_database() -> None:
    unreachable = create_engine(
        "postgresql+psycopg://nobody:nothing@127.0.0.1:1/none",
        connect_args={"connect_timeout": 1},
    )

    def broken_db() -> Iterator[Session]:
        with sessionmaker(bind=unreachable)() as session:
            yield session

    app = create_app()
    app.dependency_overrides[get_db] = broken_db

    response = TestClient(app).get("/api/v1/health")

    assert response.status_code == 503
    assert response.json()["status"] == "degraded"
    assert response.json()["database"] == "unavailable"
