# Please follow the Makefile style guide.
# http://clarkgrubb.com/makefile-style-guide

BIN := venv/bin

.PHONY: venv
venv:
	@python3.10 -m venv venv
	@$(BIN)/pip install isort flake8 pytest pytest-cov mypy

.PHONY: test check
test check: check/pytest check/flake8 check/isort check/mypy

.PHONY: check/pytest
check/pytest:
	@$(BIN)/pytest --cov-report term-missing --cov pure_protobuf

.PHONY: check/flake8
check/flake8:
	@$(BIN)/flake8 pure_protobuf tests

.PHONY: check/isort
check/isort:
	@$(BIN)/isort -c pure_protobuf tests

.PHONY: check/mypy
check/mypy:
	-@$(BIN)/mypy pure_protobuf tests
