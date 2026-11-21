UV ?= uv
PYTHON ?= python3
.PHONY: help init-env install up down logs user check backend-check frontend-check format contract contract-check e2e hooks
help:
	@echo "init-env install up user check contract e2e down logs hooks"
init-env:
	$(PYTHON) scripts/init_env.py
install:
	$(UV) sync --directory backend --frozen
	cd frontend && npm ci
up:
	docker compose up --build --wait
down:
	docker compose down
logs:
	docker compose logs --tail=100 -f
user:
	docker compose exec api python manage.py createsuperuser
backend-check:
	$(UV) run --directory backend --frozen ruff check .
	$(UV) run --directory backend --frozen ruff format --check .
	$(UV) run --directory backend --frozen mypy
	$(UV) run --directory backend --frozen python manage.py check --settings=config.test_settings
	$(UV) run --directory backend --frozen python manage.py makemigrations --check --dry-run --settings=config.test_settings
	$(UV) run --directory backend --frozen pytest --cov=pension --cov-report=term-missing --cov-fail-under=85
frontend-check:
	cd frontend && npm run format:check && npm run lint && npm run test && npm run build
contract:
	$(UV) run --directory backend --frozen python manage.py export_contract ../contracts/openapi.json --settings=config.test_settings
	cd frontend && npm run api:generate
contract-check:
	$(PYTHON) scripts/check_contract.py
check: backend-check frontend-check contract-check
	$(PYTHON) scripts/check_portability.py
format:
	$(UV) run --directory backend --frozen ruff check --fix .
	$(UV) run --directory backend --frozen ruff format .
	cd frontend && npm run format
e2e:
	cd frontend && npm run test:e2e
hooks:
	git config core.hooksPath .githooks
