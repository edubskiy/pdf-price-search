.PHONY: help install install-dev test test-unit test-integration test-e2e coverage format lint type-check clean run run-api run-cli demo

# Default target
help:
	@echo "PDF Price Search - Available commands:"
	@echo ""
	@echo "Installation:"
	@echo "  make install          - Install production dependencies"
	@echo "  make install-dev      - Install development dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make test             - Run all tests"
	@echo "  make test-unit        - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make test-e2e         - Run end-to-end tests only"
	@echo "  make coverage         - Run tests with coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  make format           - Format code with black"
	@echo "  make lint             - Lint code with flake8"
	@echo "  make type-check       - Type check with mypy"
	@echo ""
	@echo "Running:"
	@echo "  make run-api          - Start FastAPI server"
	@echo "  make run-cli          - Run CLI in interactive mode"
	@echo "  make demo             - Run CLI demo"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean            - Remove build artifacts and cache"

# Installation targets
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt
	pip install -e .

# Testing targets
test:
	pytest

test-unit:
	pytest tests/unit -m unit

test-integration:
	pytest tests/integration -m integration

test-e2e:
	pytest tests/e2e -m e2e

coverage:
	pytest --cov=src --cov-report=html --cov-report=term-missing

# Code quality targets
format:
	black src tests

lint:
	flake8 src tests

type-check:
	mypy src

# Utility targets
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	rm -f .coverage
	rm -f coverage.xml

# Running targets
run-api:
	@echo "Starting API server..."
	@./scripts/start_api.sh

run-cli:
	@echo "Starting CLI in interactive mode..."
	@./scripts/run_cli.sh interactive

demo:
	@echo "Running CLI demo..."
	@./scripts/run_cli.sh demo
