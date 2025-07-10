.PHONY: format
format:
		ruff format .
		ruff check . --fix --unsafe-fixes