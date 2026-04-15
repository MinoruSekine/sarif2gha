# Top-level targets.
all: lint test

clean: samples-clean
	$(RM) -r .pytest_cache .ruff_cache
	find . -type d -name __pycache__ -exec $(RM) -r {} +

lint: ruff mypy

test: pytest

# Each specific targets.
mypy:
	uv run mypy .

pytest: samples
	uv run pytest

ruff:
	uv run ruff check .

samples:
	cd samples && $(MAKE) all

samples-clean:
	cd samples && $(MAKE) clean

.PHONY: all clean lint test mypy pytest ruff samples samples-clean
