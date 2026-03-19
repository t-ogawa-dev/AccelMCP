#!/bin/bash
# Code quality auto-fix script

set -e

echo "=== Fixing with Ruff ==="
ruff check app/ tests/ --fix --config pyproject.toml

echo ""
echo "=== Formatting with Ruff ==="
ruff format app/ tests/ --config pyproject.toml

echo ""
echo "✅ Auto-fix and formatting completed!"
echo "💡 Run ./run_check.sh to verify the changes"
