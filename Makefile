
.PHONY: test lint format type-check all

test:
	poetry run pytest tests/unit_tests -v

test-integration:
	poetry run pytest tests/integration_tests -v

lint:
	poetry run ruff check .

format:
	poetry run ruff format .

type-check:
	poetry run mypy langchain_searchapi/

all: lint type-check test
