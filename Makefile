RUFF_VERSION=0.1.7

.PHONY: help
help: ## Show help messages
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-40s\033[0m %s\n", $$1, $$2}'

.PHONY: ruff
ruff:
	pip install ruff==$(RUFF_VERSION)

.PHONY: format
format: ruff ## Format code
	ruff check --fix .
	ruff format .
