# EduPlatform Makefile

.PHONY: help install dev test lint format clean infrastructure services

# Цвета для вывода
GREEN=\033[0;32m
YELLOW=\033[0;33m
RED=\033[0;31m
NC=\033[0m # No Color

help: ## Показать помощь
	@echo "$(GREEN)EduPlatform Development Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Установить зависимости с Poetry
	@echo "$(GREEN)Installing dependencies...$(NC)"
	poetry install --extras all
	poetry run pre-commit install

dev: install ## Настроить окружение для разработки
	@echo "$(GREEN)Setting up development environment...$(NC)"
	poetry shell

infrastructure: ## Запустить инфраструктуру (БД, брокеры, мониторинг)
	@echo "$(GREEN)Starting infrastructure services...$(NC)"
	docker-compose up -d postgres redis rabbitmq kafka minio elasticsearch prometheus grafana kafka-init
	@echo "$(YELLOW)Waiting for services to be ready...$(NC)"
	sleep 30
	@echo "$(GREEN)Infrastructure is ready!$(NC)"
	@echo ""
	@echo "$(YELLOW)Available services:$(NC)"
	@echo "PostgreSQL: localhost:5432 (eduuser/edupass)"
	@echo "Redis: localhost:6379"
	@echo "RabbitMQ Management: http://localhost:15672 (eduuser/edupass)"
	@echo "Kafka: localhost:9092"
	@echo "MinIO: http://localhost:9001 (eduuser/edupassword)"
	@echo "Elasticsearch: http://localhost:9200"
	@echo "Prometheus: http://localhost:9090"
	@echo "Grafana: http://localhost:3000 (admin/admin)"

services: ## Запустить все микросервисы
	@echo "$(GREEN)Starting microservices...$(NC)"
	docker-compose up -d

stop: ## Остановить все сервисы
	@echo "$(RED)Stopping all services...$(NC)"
	docker-compose down

clean: ## Очистить контейнеры и volumes
	@echo "$(RED)Cleaning up containers and volumes...$(NC)"
	docker-compose down -v --remove-orphans
	docker system prune -f

logs: ## Показать логи всех сервисов
	docker-compose logs -f

logs-service: ## Показать логи конкретного сервиса (make logs-service SERVICE=api-gateway)
	@if [ -z "$(SERVICE)" ]; then \
		echo "$(RED)Please specify SERVICE name: make logs-service SERVICE=api-gateway$(NC)"; \
		exit 1; \
	fi
	docker-compose logs -f $(SERVICE)

test: ## Запустить тесты
	@echo "$(GREEN)Running tests...$(NC)"
	poetry run pytest tests/ -v --cov=shared --cov=services --cov-report=html

test-unit: ## Запустить только unit тесты
	poetry run pytest tests/unit/ -v

test-integration: ## Запустить integration тесты
	poetry run pytest tests/integration/ -v -m integration

lint: ## Проверить код линтерами
	@echo "$(GREEN)Running linters...$(NC)"
	poetry run black --check .
	poetry run isort --check-only .
	poetry run flake8 .
	poetry run mypy shared/ services/

format: ## Отформатировать код
	@echo "$(GREEN)Formatting code...$(NC)"
	poetry run black .
	poetry run isort .

init-db: ## Инициализировать базу данных
	@echo "$(GREEN)Initializing database...$(NC)"
	poetry run python scripts/init_db.py
	poetry run alembic upgrade head

seed-data: ## Загрузить тестовые данные
	@echo "$(GREEN)Seeding test data...$(NC)"
	poetry run python scripts/seed_data.py

create-migration: ## Создать новую миграцию (make create-migration MESSAGE="add users table")
	@if [ -z "$(MESSAGE)" ]; then \
		echo "$(RED)Please specify MESSAGE: make create-migration MESSAGE='add users table'$(NC)"; \
		exit 1; \
	fi
	poetry run alembic revision --autogenerate -m "$(MESSAGE)"

migrate: ## Применить миграции
	poetry run alembic upgrade head

migrate-down: ## Откатить последнюю миграцию
	poetry run alembic downgrade -1

generate-openapi: ## Сгенерировать OpenAPI спецификации
	@echo "$(GREEN)Generating OpenAPI specs...$(NC)"
	poetry run python scripts/generate_openapi.py

docker-build: ## Собрать Docker образы
	@echo "$(GREEN)Building Docker images...$(NC)"
	docker-compose build

health-check: ## Проверить статус всех сервисов
	@echo "$(GREEN)Checking services health...$(NC)"
	@docker-compose ps
	@echo ""
	@echo "$(YELLOW)Testing connections:$(NC)"
	@curl -s http://localhost:9090/-/healthy > /dev/null && echo "✅ Prometheus: OK" || echo "❌ Prometheus: FAIL"
	@curl -s http://localhost:3000/api/health > /dev/null && echo "✅ Grafana: OK" || echo "❌ Grafana: FAIL"
	@curl -s http://localhost:15672/api/overview > /dev/null && echo "✅ RabbitMQ: OK" || echo "❌ RabbitMQ: FAIL"
	@curl -s http://localhost:9200/_cluster/health > /dev/null && echo "✅ Elasticsearch: OK" || echo "❌ Elasticsearch: FAIL"

# Создание структуры проекта
create-structure: ## Создать структуру директорий
	@echo "$(GREEN)Creating project structure...$(NC)"
	@mkdir -p shared/{config,database,events,middleware,exceptions,messaging,utils}
	@mkdir -p services/{api-gateway,user-service,course-service,progress-service,notification-service,file-service,certificate-service}
	@mkdir -p {monitoring/grafana/{dashboards,datasources},tests/{unit,integration,performance},alembic/versions,scripts,docs/{api,architecture,deployment}}
	@touch shared/__init__.py
	@for service in api-gateway user-service course-service progress-service notification-service file-service certificate-service; do \
		mkdir -p services/$service/app/{models,schemas,routes,services,repositories}; \
		touch services/$service/app/__init__.py; \
		touch services/$service/main.py; \
		echo "FROM python:3.11-slim\nWORKDIR /app\nCOPY pyproject.toml .\nRUN pip install poetry && poetry install\nCOPY . .\nCMD [\"poetry\", \"run\", \"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]" > services/$service/Dockerfile; \
	done
	@echo "$(GREEN)Project structure created!$(NC)"

# Kafka операции
kafka-topics: ## Показать Kafka топики
	docker exec -it $(docker-compose ps -q kafka) kafka-topics --bootstrap-server localhost:9092 --list

kafka-create-topic: ## Создать Kafka топик (make kafka-create-topic TOPIC=test.topic)
	@if [ -z "$(TOPIC)" ]; then \
		echo "$(RED)Please specify TOPIC: make kafka-create-topic TOPIC=test.topic$(NC)"; \
		exit 1; \
	fi
	docker exec -it $(docker-compose ps -q kafka) kafka-topics --bootstrap-server localhost:9092 --create --topic $(TOPIC) --replication-factor 1 --partitions 3

kafka-consume: ## Читать сообщения из топика (make kafka-consume TOPIC=user.registered)
	@if [ -z "$(TOPIC)" ]; then \
		echo "$(RED)Please specify TOPIC: make kafka-consume TOPIC=user.registered$(NC)"; \
		exit 1; \
	fi
	docker exec -it $(docker-compose ps -q kafka) kafka-console-consumer --bootstrap-server localhost:9092 --topic $(TOPIC) --from-beginning

# База данных операции
db-shell: ## Подключиться к PostgreSQL
	docker exec -it $(docker-compose ps -q postgres) psql -U eduuser -d eduplatform

db-backup: ## Создать бэкап базы данных
	@echo "$(GREEN)Creating database backup...$(NC)"
	docker exec $(docker-compose ps -q postgres) pg_dump -U eduuser eduplatform > backup_$(date +%Y%m%d_%H%M%S).sql

db-restore: ## Восстановить из бэкапа (make db-restore BACKUP=backup_20231201_120000.sql)
	@if [ -z "$(BACKUP)" ]; then \
		echo "$(RED)Please specify BACKUP file: make db-restore BACKUP=backup_20231201_120000.sql$(NC)"; \
		exit 1; \
	fi
	@if [ ! -f "$(BACKUP)" ]; then \
		echo "$(RED)Backup file $(BACKUP) not found!$(NC)"; \
		exit 1; \
	fi
	docker exec -i $(docker-compose ps -q postgres) psql -U eduuser eduplatform < $(BACKUP)

# Redis операции
redis-shell: ## Подключиться к Redis CLI
	docker exec -it $(docker-compose ps -q redis) redis-cli

redis-monitor: ## Мониторить команды Redis
	docker exec -it $(docker-compose ps -q redis) redis-cli MONITOR

# Мониторинг
monitor: ## Открыть все мониторинг панели
	@echo "$(GREEN)Opening monitoring dashboards...$(NC)"
	@echo "Opening Grafana..."
	@open http://localhost:3000 2>/dev/null || echo "Grafana: http://localhost:3000"
	@echo "Opening Prometheus..."
	@open http://localhost:9090 2>/dev/null || echo "Prometheus: http://localhost:9090"
	@echo "Opening RabbitMQ Management..."
	@open http://localhost:15672 2>/dev/null || echo "RabbitMQ: http://localhost:15672"

# Разработка конкретных сервисов
dev-user-service: ## Запустить user-service для разработки
	cd services/user-service && poetry run uvicorn main:app --reload --port 8001

dev-course-service: ## Запустить course-service для разработки
	cd services/course-service && poetry run uvicorn main:app --reload --port 8002

dev-api-gateway: ## Запустить api-gateway для разработки
	cd services/api-gateway && poetry run uvicorn main:app --reload --port 8000

# Производственные команды
prod-build: ## Собрать продакшн образы
	@echo "$(GREEN)Building production images...$(NC)"
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

prod-deploy: ## Задеплоить в продакшн
	@echo "$(GREEN)Deploying to production...$(NC)"
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

prod-logs: ## Логи продакшн
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f

# Безопасность
security-scan: ## Сканирование зависимостей на уязвимости
	@echo "$(GREEN)Scanning for security vulnerabilities...$(NC)"
	poetry run safety check
	poetry run bandit -r shared/ services/ -f json -o security-report.json || true
	@echo "Security report saved to security-report.json"

# Документация
docs-serve: ## Запустить документацию локально
	@echo "$(GREEN)Starting documentation server...$(NC)"
	poetry run mkdocs serve

docs-build: ## Собрать документацию
	poetry run mkdocs build

# Очистка
clean-cache: ## Очистить кэши Python
	@echo "$(GREEN)Cleaning Python caches...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true

clean-logs: ## Очистить логи Docker
	docker system prune --volumes -f

# Запуск локальных сервисов
run-user: ## Запустить User Service локально
	poetry run uvicorn services.user_service.main:app --reload --port 8001

run-course: ## Запустить Course Service локально
	poetry run uvicorn services.course_service.main:app --reload --port 8002

run-gateway: ## Запустить API Gateway локально
	poetry run uvicorn services.api_gateway.main:app --reload --port 8000

run-all-local: ## Запустить все сервисы локально (в фоне)
	@echo "$(GREEN)Starting all services locally...$(NC)"
	@poetry run uvicorn services.user_service.main:app --port 8001 > logs/user-service.log 2>&1 &
	@poetry run uvicorn services.course_service.main:app --port 8002 > logs/course-service.log 2>&1 &
	@poetry run uvicorn services.api_gateway.main:app --port 8000 > logs/gateway.log 2>&1 &
	@echo "$(GREEN)All services started!$(NC)"
	@echo "User Service: http://localhost:8001/docs"
	@echo "Course Service: http://localhost:8002/docs"
	@echo "API Gateway: http://localhost:8000/docs"
	@echo ""
	@echo "Logs: tail -f logs/*.log"

stop-local: ## Остановить все локальные сервисы
	@echo "$(RED)Stopping local services...$(NC)"
	@pkill -f "uvicorn services" || true

logs-local: ## Показать логи локальных сервисов
	tail -f logs/*.log

# По умолчанию показываем help
.DEFAULT_GOAL := help
