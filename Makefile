.PHONY: test lint check reproduce paper

test:
	uv run pytest --cov=coauthored --cov-fail-under=85

lint:
	uv run ruff check . && uv run ruff format --check . && uv run mypy

check: lint test

# Rebuild every table and figure from committed aggregates, no network
reproduce:
	uv run --extra analysis coauthored analyze --offline

# Fill paper/paper.md from results/numbers.json and build paper/coauthored.pdf (needs pandoc and typst)
paper:
	uv run coauthored paper
