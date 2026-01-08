.PHONY: format lint test install setup upgrade run

format: lint
	uv run -- ruff format

lint:
	uv run -- ruff check --fix

test:
	uv run -- pytest -v -n auto

install:
	uv sync --frozen --compile-bytecode --all-extras

setup:
	uv sync --frozen --compile-bytecode --all-extras
	uv run -- pre-commit install --install-hooks

upgrade:
	uv sync --upgrade --all-extras

run:
	uv run main.py

postgres:
	docker compose up -d postgres --remove-orphans

mysql:
	docker compose up -d mysql --remove-orphans