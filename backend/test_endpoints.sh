#!/bin/bash
# Test script for new module endpoints

BASE_URL="http://localhost:8000/api"
echo "Testing Backend Endpoints..."
echo "=============================="

# Education endpoints
echo -e "\n1. Education Module:"
echo "  - Videos:"
curl -s "$BASE_URL/education/videos" | python3 -m json.tool | head -5
echo "  - Ebooks:"
curl -s "$BASE_URL/education/ebooks" | python3 -m json.tool | head -5
echo "  - Reports:"
curl -s "$BASE_URL/education/reports" | python3 -m json.tool | head -5

# Support endpoints
echo -e "\n2. Support Module:"
echo "  - Articles:"
curl -s "$BASE_URL/support/articles" | python3 -m json.tool | head -5
echo "  - Categories:"
curl -s "$BASE_URL/support/categories" | python3 -m json.tool | head -5
echo "  - FAQ:"
curl -s "$BASE_URL/support/faq" | python3 -m json.tool | head -5
echo "  - Offices:"
curl -s "$BASE_URL/support/offices" | python3 -m json.tool | head -5
echo "  - Channels:"
curl -s "$BASE_URL/support/channels" | python3 -m json.tool | head -5

# Legal endpoints
echo -e "\n3. Legal Module:"
echo "  - Terms:"
curl -s "$BASE_URL/legal/terms" | python3 -m json.tool | head -5
echo "  - Privacy:"
curl -s "$BASE_URL/legal/privacy" | python3 -m json.tool | head -5
echo "  - Risk Warning:"
curl -s "$BASE_URL/legal/risk-warning" | python3 -m json.tool | head -5

# Analysis endpoints
echo -e "\n4. Analysis Module:"
echo "  - Technical Analysis:"
curl -s "$BASE_URL/analysis/technical/BTCUSDT" | python3 -m json.tool | head -5

echo -e "\n=============================="
echo "Testing complete!"

