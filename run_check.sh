#!/bin/bash
# Code quality check script

set -e

echo "=== Running Ruff Linter ==="
ruff check app/ tests/ --config pyproject.toml

echo ""
echo "=== Running Ruff Formatter (check only) ==="
ruff format app/ tests/ --check --config pyproject.toml

echo ""
echo "=== Running MyPy Type Checker ==="
mypy app/ --config-file pyproject.toml

echo ""
echo "✅ All checks passed!"
