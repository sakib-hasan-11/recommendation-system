.PHONY: help venv install install-dev test lint format clean run-local run-api run-streamlit run-ingestion run-training

help:
	@echo "Available commands:"
	@echo "  make venv              Create virtual environment"
	@echo "  make install           Install dependencies"
	@echo "  make install-dev       Install dev dependencies"
	@echo "  make test              Run tests"
	@echo "  make lint              Run linting"
	@echo "  make format            Format code"
	@echo "  make clean             Clean up"
	@echo "  make run-local         Run full local pipeline"
	@echo "  make run-api           Run API server"
	@echo "  make run-streamlit     Run Streamlit frontend"
	@echo "  make run-ingestion     Run ingestion pipeline"
	@echo "  make run-training      Run training pipeline"
	@echo "  make docker-build      Build Docker images"
	@echo "  make docker-push       Push Docker images to ECR"
	@echo "  make aws-register      Register AWS Batch jobs"

venv:
	python -m venv .venv

install:
	.venv\Scripts\pip install -r requirements.txt

install-dev:
	.venv\Scripts\pip install -r requirements.txt -r tests/requirements.txt

test:
	.venv\Scripts\pytest tests/ -v --cov=. --cov-report=html

lint:
	.venv\Scripts\ruff check .

format:
	.venv\Scripts\black .
	.venv\Scripts\isort .

clean:
	rmdir /s /q __pycache__ 2>/dev/null || true
	rmdir /s /q .pytest_cache 2>/dev/null || true
	rmdir /s /q htmlcov 2>/dev/null || true
	rmdir /s /q .venv 2>/dev/null || true
	del /q .coverage 2>/dev/null || true
	del /q mlflow.db 2>/dev/null || true

run-local: install
	.venv\Scripts\python scripts/eda.py
	.venv\Scripts\python scripts/ingestion_job.py
	.venv\Scripts\python scripts/training_job.py

run-api:
	.venv\Scripts\python -m uvicorn scripts.api_server:app --host 0.0.0.0 --port 8000 --reload

run-streamlit:
	.venv\Scripts\streamlit run frontend/streamlit_app/app.py

run-ingestion:
	.venv\Scripts\python scripts/ingestion_job.py

run-training:
	.venv\Scripts\python scripts/training_job.py

docker-build:
	docker build -f infra/docker/Dockerfile.base -t recommendation-system:base .
	docker build -f infra/docker/Dockerfile.api -t recommendation-system:api .
	docker build -f infra/docker/Dockerfile.ingestion -t recommendation-system:ingestion .
	docker build -f infra/docker/Dockerfile.training -t recommendation-system:training .

docker-push:
	bash infra/scripts/deploy.sh

aws-register:
	bash infra/scripts/register_jobs.sh

.env:
	cp .env.example .env
	@echo "Created .env file. Please update with your configuration."
