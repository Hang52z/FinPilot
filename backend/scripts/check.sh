#!/bin/sh
# Full backend check: lint, types, migration round-trip, tests. Runs inside the dev container.
set -eu
ruff check .
ruff format --check .
mypy app tests migrations
alembic upgrade head
alembic downgrade base
alembic upgrade head
pytest
