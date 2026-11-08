.PHONY: test lint build run-backend run-frontend migrate clean

test:
	.venv\Scripts\python.exe -m pytest tests/

lint:
	.venv\Scripts\python.exe -m ruff check src/ tests/

build:
	npm --prefix frontend run build

run-backend:
	.venv\Scripts\uvicorn.exe govisense.api.main:app --host 0.0.0.0 --port 8000 --reload

run-frontend:
	npm --prefix frontend run dev

migrate:
	.venv\Scripts\alembic.exe upgrade head

clean:
	rmdir /s /q frontend\dist 2>nul || true
	del /s /q *.pyc 2>nul || true

