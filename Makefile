.PHONY: setup lint format typecheck test test-fast bench run docker-build clean
setup:
	uv sync --all-groups
lint:
	uv run ruff check .
format:
	uv run ruff format .
typecheck:
	uv run mypy src
test test-fast:
	uv run pytest
bench:
	uv run python -c "from pathlib import Path; from kyc.synth.generator import generate; generate(42, Path('data/smoke'), 10)"
run:
	uv run uvicorn kyc.api.main:app --reload
docker-build:
	@echo "No Dockerfile is shipped in the CPU-first v0.1.0 demo."
clean:
	@echo "Remove .venv, data, and local databases manually if desired."
