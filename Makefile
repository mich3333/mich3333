# Multi-Agent System - Backend Quality Gates

.PHONY: help install install-dev lint format test test-cov clean run

help:  ## Show this help message
	@echo "Multi-Agent System - Backend Commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install production dependencies
	pip install -r requirements.txt

install-dev:  ## Install development dependencies
	pip install -r requirements.txt -r requirements-dev.txt

lint:  ## Run linter (ruff)
	ruff check .

format:  ## Format code with ruff
	ruff check --fix .
	ruff format .

test:  ## Run tests
	pytest

test-cov:  ## Run tests with coverage report
	pytest --cov=. --cov-report=term-missing --cov-report=html

clean:  ## Clean up generated files
	rm -rf __pycache__ .pytest_cache .coverage htmlcov
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run:  ## Run the Flask server
	python app.py
