BIN := venv/bin

.PHONY: all
all: install lint test build

.PHONY: clean
clean:
	rm -rf .ruff_cache .mypy_cache .pytest_cache
	find . -name "*.pyc" -delete
	rm -rf *.egg-info build
	rm -rf coverage*.xml .coverage
	rm -rf .benchmarks

.PHONY: install
install:
	poetry install --all-extras --with=dev

.PHONY: lint
lint: lint/ruff lint/mypy

.PHONY: lint/ruff
lint/ruff:
	poetry run ruff pure_protobuf tests

.PHONY: lint/mypy
lint/mypy:
	poetry run mypy pure_protobuf tests

.PHONY: format
format: format/ruff

.PHONY: format/ruff
format/ruff:
	poetry run ruff --fix pure_protobuf tests

.PHONY: test
test:
	poetry run pytest tests --benchmark-disable

.PHONY: benchmark
benchmark:
	poetry run pytest tests --benchmark-only --benchmark-columns=mean,stddev,median,ops --benchmark-warmup=on

.PHONY: build
build:
	poetry build
