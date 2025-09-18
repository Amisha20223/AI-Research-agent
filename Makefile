.PHONY: help build up down logs clean test lint format

# Default target
help:
	@echo "Available commands:"
	@echo "  build     - Build all Docker images"
	@echo "  up        - Start all services in development mode"
	@echo "  up-prod   - Start all services in production mode"
	@echo "  down      - Stop all services"
	@echo "  logs      - Show logs from all services"
	@echo "  clean     - Remove all containers, images, and volumes"
	@echo "  test      - Run tests"
	@echo "  lint      - Run linting"
	@echo "  format    - Format code"
	@echo "  migrate   - Run database migrations"
	@echo "  shell     - Open shell in backend container"

# Development commands
build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Services started. Backend available at http://localhost:8000"
	@echo "Frontend available at http://localhost:3000"

up-prod:
	docker-compose -f docker-compose.prod.yml up -d
	@echo "Production services started. API available at http://localhost"

down:
	docker-compose down
	docker-compose -f docker-compose.prod.yml down

logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-celery:
	docker-compose logs -f celery-worker celery-beat

# Maintenance commands
clean:
	docker-compose down -v --rmi all --remove-orphans
	docker system prune -f

migrate:
	docker-compose exec backend python -c "from database import create_tables; create_tables()"

shell:
	docker-compose exec backend /bin/bash

# Database commands
db-shell:
	docker-compose exec postgres psql -U postgres -d research_agent

db-backup:
	docker-compose exec postgres pg_dump -U postgres research_agent > backup_$(shell date +%Y%m%d_%H%M%S).sql

db-restore:
	@read -p "Enter backup file path: " backup_file; \
	docker-compose exec -T postgres psql -U postgres -d research_agent < $$backup_file

# Development tools
test:
	docker-compose exec backend python -m pytest tests/ -v

lint:
	docker-compose exec backend python -m flake8 .
	docker-compose exec backend python -m black --check .

format:
	docker-compose exec backend python -m black .
	docker-compose exec backend python -m isort .

# Monitoring
status:
	docker-compose ps

health:
	@echo "Checking service health..."
	@curl -f http://localhost:8000/health || echo "Backend health check failed"
	@docker-compose exec redis redis-cli ping || echo "Redis health check failed"
	@docker-compose exec postgres pg_isready -U postgres || echo "PostgreSQL health check failed"
