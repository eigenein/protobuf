# Please follow the Makefile style guide.
# http://clarkgrubb.com/makefile-style-guide

BIN := venv/bin

.PHONY: venv
venv:
	@python3.10 -m venv venv
	@$(BIN)/pip install -e.[dev]

.PHONY: test check
test check: check/pytest check/flake8 check/isort check/mypy

.PHONY: check/pytest
check/pytest:
	@$(BIN)/coverage run --source=pure_protobuf -m pytest tests

.PHONY: check/flake8
check/flake8:
	@$(BIN)/flake8 pure_protobuf tests

.PHONY: check/isort
check/isort:
	@$(BIN)/isort -c pure_protobuf tests

.PHONY: check/mypy
check/mypy:
	-@$(BIN)/mypy pure_protobuf tests
