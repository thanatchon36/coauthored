.PHONY: test lint check reproduce

test:
	uv run pytest --cov=coauthored

lint:
	uv run ruff check . && uv run ruff format --check . && uv run mypy

check: lint test

# Rebuild every table and figure from committed aggregates, no network (filled in Phase 7)
reproduce:
	uv run --extra analysis coauthored analyze --offline
