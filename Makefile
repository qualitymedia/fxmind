.PHONY: setup dev test migrate train backtest lint clean help

# ─── Variables ──────────────────────────────────
PYTHON := python
PIP := pip
NPM := npm
DOCKER := docker-compose

# ─── Help ───────────────────────────────────────
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ─── Setup ──────────────────────────────────────
setup: ## Initial project setup
	cp -n .env.example .env || true
	cd backend && $(PIP) install -r requirements.txt
	cd frontend && $(NPM) install
	$(MAKE) migrate
	@echo "✅ Setup complete. Run 'make dev' to start."

setup-docker: ## Setup with Docker
	cp -n .env.example .env || true
	$(DOCKER) build
	$(DOCKER) run --rm api alembic upgrade head
	@echo "✅ Docker setup complete. Run 'make docker-dev' to start."

# ─── Development ────────────────────────────────
dev: ## Start all services locally
	@echo "Starting API and Web..."
	cd backend && $(PYTHON) -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 &
	cd frontend && $(NPM) run dev &
	@echo "✅ Services starting. API: http://127.0.0.1:8000 | Web: http://localhost:3000"

docker-dev: ## Start all services with Docker
	$(DOCKER) up --build

docker-down: ## Stop Docker services
	$(DOCKER) down

# ─── Database ───────────────────────────────────
migrate: ## Run database migrations
	cd backend && alembic upgrade head

migrate-new: ## Create a new migration (usage: make migrate-new MSG="description")
	cd backend && alembic revision --autogenerate -m "$(MSG)"

migrate-down: ## Rollback last migration
	cd backend && alembic downgrade -1

# ─── Testing ────────────────────────────────────
test: ## Run all tests
	cd backend && $(PYTHON) -m pytest tests/ -v
	$(PYTHON) -m pytest ml/validation/leakage_tests.py -v

test-api: ## Run API tests only
	cd backend && $(PYTHON) -m pytest tests/ -v

test-ml: ## Run ML tests only
	$(PYTHON) -m pytest ml/ -v

test-leakage: ## Run leakage tests
	$(PYTHON) -m pytest ml/validation/leakage_tests.py -v

# ─── ML Pipeline ────────────────────────────────
demo-data: ## Generate demo data
	cd backend && $(PYTHON) scripts/create_demo_data.py

features: ## Build feature matrix
	cd backend && $(PYTHON) scripts/build_features.py --config configs/training.yaml

train: ## Train the model
	cd backend && $(PYTHON) scripts/retrain_v2.py

evaluate: ## Evaluate the model
	cd backend && $(PYTHON) scripts/evaluate_model.py --config configs/training.yaml

backtest: ## Run backtester
	cd backend && $(PYTHON) scripts/run_backtest.py --config configs/training.yaml

# ─── Utilities ──────────────────────────────────
lint: ## Run linters
	cd backend && $(PYTHON) -m ruff check .
	cd frontend && $(NPM) run lint

clean: ## Clean generated files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -rf frontend/.next 2>/dev/null || true
	@echo "✅ Cleaned."
