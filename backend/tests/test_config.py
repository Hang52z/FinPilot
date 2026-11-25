import tomllib
from pathlib import Path

import pytest

from app import __version__
from app.core.config import Settings


def test_version_matches_pyproject() -> None:
    pyproject = tomllib.loads((Path(__file__).parents[1] / "pyproject.toml").read_text())
    assert pyproject["project"]["version"] == __version__


def test_settings_read_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENV", "production")
    monkeypatch.setenv("CORS_ORIGINS", '["https://example.com"]')

    settings = Settings(_env_file=None)

    assert settings.env == "production"
    assert settings.cors_origins == ["https://example.com"]


def test_settings_reject_unknown_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENV", "staging")

    with pytest.raises(ValueError):
        Settings(_env_file=None)
