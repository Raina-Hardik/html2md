# Makefile for html2md development

.PHONY: help install install-dev test test-setup clean lint format build upload-test upload

help:  ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

install:  ## Install the package
	pip install -e .

install-dev:  ## Install development dependencies
	pip install -e .
	pip install pytest pytest-cov black flake8 mypy

test-setup:  ## Create test directory structure
	python test_setup.py

test:  ## Run tests (placeholder for future test suite)
	@echo "Test suite not yet implemented"
	@echo "Use 'make test-setup' to create test files, then manually test with:"
	@echo "  html2md --help"
	@echo "  html2md ."

clean:  ## Clean up build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint:  ## Run linting
	flake8 html2md/
	mypy html2md/ --ignore-missing-imports

format:  ## Format code with black
	black html2md/

build:  ## Build distribution packages
	python -m build

upload-test:  ## Upload to test PyPI
	python -m twine upload --repository testpypi dist/*

upload:  ## Upload to PyPI
	python -m twine upload dist/*

dev-setup:  ## Complete development setup
	make install-dev
	make test-setup
	@echo ""
	@echo "Development setup complete!"
	@echo "Try: html2md --help"
