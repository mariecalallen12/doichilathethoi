#!/bin/bash
# Integration Test Script for Digital Utopia Platform
# Tests all services, connections, and integrations

set -e

echo "=========================================="
echo "Digital Utopia Platform - Integration Test"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASSED=0
FAILED=0

test_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ PASS${NC}: $2"
        ((PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC}: $2"
        ((FAILED++))
    fi
}

echo "1. Testing Container Status..."
echo "----------------------------"

# Test PostgreSQL container
if docker ps | grep -q "digital_utopia_postgres.*Up"; then
    test_result 0 "PostgreSQL container is running"
else
    test_result 1 "PostgreSQL container is not running"
fi

# Test Redis container
if docker ps | grep -q "digital_utopia_redis.*Up"; then
    test_result 0 "Redis container is running"
else
    test_result 1 "Redis container is not running"
fi

# Test Backend container
if docker ps | grep -q "digital_utopia_backend.*Up"; then
    test_result 0 "Backend container is running"
else
    test_result 1 "Backend container is not running"
fi

echo ""
echo "2. Testing Network Connectivity..."
echo "--------------------------------"

# Test PostgreSQL connection from backend
if docker exec digital_utopia_backend python -c "from app.db.session import check_db_connection; exit(0 if check_db_connection() else 1)" 2>/dev/null; then
    test_result 0 "Backend can connect to PostgreSQL"
else
    test_result 1 "Backend cannot connect to PostgreSQL"
fi

# Test Redis connection from backend
if docker exec digital_utopia_backend sh -c 'export REDIS_HOST=digital_utopia_redis REDIS_PORT=6379 REDIS_PASSWORD=CHANGE_THIS_REDIS_PASSWORD && redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -a "$REDIS_PASSWORD" ping' 2>&1 | grep -q PONG; then
    test_result 0 "Backend can connect to Redis"
else
    test_result 1 "Backend cannot connect to Redis"
fi

echo ""
echo "3. Testing Database..."
echo "---------------------"

# Test database tables exist
TABLE_COUNT=$(docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d ' ')
if [ -n "$TABLE_COUNT" ] && [ "$TABLE_COUNT" -gt 0 ]; then
    test_result 0 "Database tables exist ($TABLE_COUNT tables)"
else
    test_result 1 "No database tables found"
fi

# Test alembic version
if docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -t -c "SELECT version FROM alembic_version;" 2>/dev/null | grep -q .; then
    test_result 0 "Alembic migrations applied"
else
    test_result 1 "Alembic migrations not found"
fi

# Test database query
if docker exec digital_utopia_backend python -c "from app.db.session import SessionLocal; from app.models.user import User; db = SessionLocal(); db.query(User).count(); db.close()" 2>/dev/null; then
    test_result 0 "Database queries work"
else
    test_result 1 "Database queries fail"
fi

echo ""
echo "4. Testing Redis..."
echo "------------------"

# Test Redis operations
if docker exec digital_utopia_backend python -c "from app.db.redis_client import redis_client; r = redis_client.client; r.set('test', 'value'); v = r.get('test'); r.delete('test'); exit(0 if v == 'value' else 1)" 2>/dev/null; then
    test_result 0 "Redis SET/GET/DEL operations work"
else
    test_result 1 "Redis operations fail"
fi

# Test Redis initialization
if docker exec digital_utopia_backend python -c "from app.db.redis_client import redis_client; exit(0 if redis_client.is_connected else 1)" 2>/dev/null; then
    test_result 0 "Redis is initialized and connected"
else
    test_result 1 "Redis is not initialized"
fi

echo ""
echo "5. Testing API Endpoints..."
echo "--------------------------"

# Test health endpoint
if curl -s http://localhost:8000/api/health 2>&1 | python3 -m json.tool > /dev/null 2>&1; then
    test_result 0 "API health endpoint responds"
else
    test_result 1 "API health endpoint fails"
fi

# Test root endpoint
if curl -s http://localhost:8000/ 2>&1 | python3 -m json.tool > /dev/null 2>&1; then
    test_result 0 "API root endpoint responds"
else
    test_result 1 "API root endpoint fails"
fi

# Test docs endpoint
if curl -s http://localhost:8000/docs 2>&1 | grep -q "swagger" > /dev/null 2>&1; then
    test_result 0 "API docs endpoint accessible"
else
    test_result 1 "API docs endpoint not accessible"
fi

echo ""
echo "6. Testing Integration..."
echo "------------------------"

# Test backend can use both database and Redis
if docker exec digital_utopia_backend python -c "
from app.db.session import SessionLocal
from app.db.redis_client import redis_client
from app.models.user import User

# Test database
db = SessionLocal()
user_count = db.query(User).count()
db.close()

# Test Redis
r = redis_client.client
r.set('integration_test', 'success')
value = r.get('integration_test')
r.delete('integration_test')

exit(0 if value == 'success' else 1)
" 2>/dev/null; then
    test_result 0 "Backend can use both database and Redis"
else
    test_result 1 "Backend integration test failed"
fi

echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All integration tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed. Please review the output above.${NC}"
    exit 1
fi

