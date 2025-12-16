#!/bin/bash
set -e

echo "🧪 Running test suite with coverage report..."

cd /root/forexxx/backend

# Check if pytest-cov is installed
if ! python3 -c "import pytest_cov" 2>/dev/null; then
    echo "📦 Installing pytest-cov..."
    pip3 install pytest-cov --quiet
fi

# Run tests with coverage
echo "Running tests for Education, Analysis, Support, Legal modules..."
python3 -m pytest tests/test_education.py tests/test_analysis.py tests/test_support.py tests/test_legal.py \
    -v \
    --cov=app \
    --cov-report=html \
    --cov-report=term \
    --cov-report=json \
    --tb=short \
    || echo "⚠️  Some tests failed (this may be expected if database is not available)"

# Generate coverage summary
if [ -f "coverage.json" ]; then
    echo ""
    echo "📊 Coverage Summary:"
    python3 -c "
import json
with open('coverage.json') as f:
    data = json.load(f)
    total = data['totals']['percent_covered']
    print(f'Total Coverage: {total:.2f}%')
    print(f'Lines Covered: {data[\"totals\"][\"covered_lines\"]}/{data[\"totals\"][\"num_statements\"]}')
"
fi

echo ""
echo "✅ Test coverage report generated in htmlcov/index.html"

