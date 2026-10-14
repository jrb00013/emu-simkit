.PHONY: test lint install
install:
	pip install -e ".[dev]"
test:
	pytest -q
lint:
	ruff check src tests
