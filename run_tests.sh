#!/bin/bash
# Test runner script

echo "🧪 Running MCP Server Tests"
echo "=========================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Run all tests
echo ""
echo "Running all tests..."
pytest tests/ -v

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
else
    echo -e "${RED}❌ Some tests failed${NC}"
    exit 1
fi

# Run tests with coverage
echo ""
echo "Running tests with coverage..."
pytest tests/ --cov=app --cov-report=term-missing --cov-report=html

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Coverage report generated in htmlcov/${NC}"
else
    echo -e "${RED}❌ Coverage tests failed${NC}"
    exit 1
fi

echo ""
echo "=========================="
echo "✨ Test run complete!"
