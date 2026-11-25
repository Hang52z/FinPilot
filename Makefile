# Docker-first entry points. Run `make` to list targets.
.DEFAULT_GOAL := help
TEST := docker compose -f docker-compose.test.yml

help: ## List targets
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F ':.*## ' '{printf "  %-14s %s\n", $$1, $$2}'

up: ## Start database and backend (http://localhost:8000)
	docker compose up --build

down: ## Stop the development stack
	docker compose down

check: check-backend check-mobile ## Run every check CI runs

check-backend: ## Lint, types, migrations and tests for the backend
	$(TEST) build backend
	$(TEST) run --rm backend; status=$$?; $(TEST) down -v; exit $$status

check-mobile: ## Lint, types, tests and web build for the app
	$(TEST) --profile mobile run --rm mobile

migration: ## Create a migration: make migration m="add securities"
	docker compose run --rm backend alembic revision --autogenerate -m "$(m)"

mobile: ## Start the Expo dev server for iOS and Android (runs on the host)
	cd apps/mobile && npm install && npx expo start

web: ## Start the web app at http://localhost:8081 (runs on the host)
	cd apps/mobile && npm install && npx expo start --web
