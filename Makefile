# Top-level targets.
lint: ruff

test: pytest

# Each specific targets.
pytest: samples
	uv run pytest

ruff:
	uv run ruff check .

samples:
	cd samples && $(MAKE) all

.PHONY: lint test pytest ruff samples
