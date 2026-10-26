.PHONY: up down restart build test test-api test-web seed lint migrate clean help

# Default target
all: help

help:
	@echo "Allocate - AI-Assisted Resource Allocation Platform"
	@echo "Available commands:"
	@echo "  make up          - Start all services with Docker Compose"
	@echo "  make down        - Stop all Docker Compose services"
	@echo "  make build       - Build docker images"
	@echo "  make test        - Run backend and frontend tests"
	@echo "  make test-api    - Run backend pytest suite"
	@echo "  make test-web    - Run frontend test suite"
	@echo "  make seed        - Run database seed script (40 employees, 12 projects)"
	@echo "  make migrate     - Run database migrations"
	@echo "  make lint        - Run linters (ruff for backend, eslint for web)"
	@echo "  make clean       - Clean temporary build and cache files"

up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose down && docker compose up -d

build:
	docker compose build

migrate:
	@which docker >/dev/null 2>&1 && docker compose exec api alembic upgrade head || (cd apps/api && alembic upgrade head)

seed:
	@which docker >/dev/null 2>&1 && docker compose exec api python -m app.scripts.seed || (cd apps/api && python -m app.scripts.seed)

test: test-api test-web

test-api:
	@which docker >/dev/null 2>&1 && docker compose exec api pytest -v || (cd apps/api && pytest -v)

test-web:
	@which docker >/dev/null 2>&1 && docker compose exec web npm test || (cd apps/web && npm test)

lint:
	cd apps/api && ruff check .
	cd apps/web && npm run lint

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".next" -exec rm -rf {} +
