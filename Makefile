.PHONY: help setup sync add run migrate shell test lint format clean precommit precommit-install verify

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: ## Setup the project with uv (create venv and install dependencies)
	@./scripts/uv_setup.sh
	@uv run pre-commit install
	@echo ""
	@echo " Pre-commit hooks installed"

verify: ## Verify the uv setup
	@./scripts/verify_uv_setup.sh

sync: ## Sync dependencies from pyproject.toml
	@uv sync

add: ## Add a package (usage: make add PACKAGE=package-name)
	@if [ -z "$(PACKAGE)" ]; then \
		echo "Usage: make add PACKAGE=package-name"; \
		exit 1; \
	fi
	@uv add $(PACKAGE)

run: ## Run the Django development server
	@uv run python manage.py runserver

migrate: ## Run database migrations
	@uv run python manage.py migrate

makemigrations: ## Create new migrations
	@uv run python manage.py makemigrations

shell: ## Open Django shell
	@uv run python manage.py shell

test: ## Run tests
	@uv run python manage.py test

lint: ## Run linting checks
	@uv run ruff check .

format: ## Format code with ruff
	@uv run ruff format .

precommit: ## Run pre-commit on all files
	@uv run pre-commit run --all-files

precommit-install: ## Install pre-commit hooks
	@uv run pre-commit install
	@echo " Pre-commit hooks installed"

collectstatic: ## Collect static files
	@uv run python manage.py collectstatic --noinput

fixtures: ## Load fixtures
	@uv run python load_fixtures.py

superuser: ## Create a superuser
	@uv run python manage.py createsuperuser

clean: ## Clean up cache and temporary files
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name ".DS_Store" -delete
	@echo "Cleaned up cache files"
