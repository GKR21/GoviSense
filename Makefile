.PHONY: help install install-all test test-task18 test-cov lint format run-api run-frontend docker-build docker-up docker-down clean data-validate init-db migrate

# Default target
all: help

help:
	@echo "======================================================================"
	@echo "GoviSense - Agricultural Forecasting & Decision Support System"
	@echo "======================================================================"
	@echo "Available make commands:"
	@echo "  make install        - Install all backend dependencies"
	@echo "  make install-all    - Install both backend and frontend dependencies"
	@echo "  make test           - Run full Pytest test suite"
	@echo "  make test-task18    - Run comprehensive quality & concurrency tests"
	@echo "  make test-cov       - Run tests with HTML coverage report"
	@echo "  make lint           - Check code style and formatting with Ruff"
	@echo "  make format         - Automatically format code with Ruff"
	@echo "  make run-api        - Start the FastAPI backend server on port 8000"
	@echo "  make run-frontend   - Start the Vite React frontend on port 5173"
	@echo "  make docker-build   - Build Docker container images"
	@echo "  make docker-up      - Run application stack with Docker Compose"
	@echo "  make docker-down    - Tear down Docker Compose services and networks"
	@echo "  make init-db        - Seed SQLite database with baseline tables & data"
	@echo "  make migrate        - Run Alembic migrations to upgrade schema head"
	@echo "  make data-validate  - Verify master dataset integrity and source taxonomy"
	@echo "  make clean          - Clean temporary caches and build artifacts"
	@echo "======================================================================"

install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt

install-all: install
	cd frontend && npm install

test:
	python -m pytest

test-task18:
	python -m pytest tests/test_task_18_comprehensive_quality.py -v

test-cov:
	python -m pytest --cov=src/govisense --cov-report=html --cov-report=term

lint:
	ruff check src tests

format:
	ruff format src tests

run-api:
	uvicorn govisense.api.main:app --host 0.0.0.0 --port 8000 --reload

run-frontend:
	cd frontend && npm run dev

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

init-db:
	python -c "from govisense.db.session import init_db; init_db()"

migrate:
	alembic upgrade head

data-validate:
	python -m pytest tests/test_extract.py -k "test_master_dataset_structural_integrity or test_catalogue_licence_and_provenance"

clean:
	python -c "import shutil, pathlib; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('.pytest_cache')]; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('.coverage')]"
