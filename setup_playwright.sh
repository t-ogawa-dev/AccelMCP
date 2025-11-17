#!/bin/bash
# Setup Playwright browsers

echo "📦 Installing Playwright browsers..."
python -m playwright install

if [ $? -eq 0 ]; then
    echo "✅ Playwright browsers installed successfully"
else
    echo "❌ Failed to install Playwright browsers"
    exit 1
fi

echo ""
echo "You can now run E2E tests with:"
echo "  pytest tests/test_e2e.py"
echo "  or"
echo "  pytest -m e2e"
