#!/bin/bash

# ============================================
# Performance Benchmarking Script
# ============================================
# Measures API response times and system performance
# ============================================

set -e

echo "=========================================="
echo "CMEETRADING - Performance Benchmark"
echo "=========================================="
echo ""

# Configuration
API_BASE="http://localhost:8000"
WARMUP_REQUESTS=10
BENCHMARK_REQUESTS=100
CONCURRENCY=10

# Test user credentials
TEST_EMAIL="test@cmeetrading.com"
TEST_PASSWORD="Test@123456"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_metric() {
    echo -e "${GREEN}$1:${NC} $2"
}

echo "Configuration:"
echo "  API Base: $API_BASE"
echo "  Requests: $BENCHMARK_REQUESTS"
echo "  Concurrency: $CONCURRENCY"
echo ""

# ============================================
# 1. Health Check Performance
# ============================================

echo "=========================================="
echo "1. Health Endpoint Performance"
echo "=========================================="
echo ""

HEALTH_START=$(date +%s%N)
for i in $(seq 1 $WARMUP_REQUESTS); do
    curl -s $API_BASE/api/health > /dev/null
done
HEALTH_END=$(date +%s%N)

HEALTH_TIME=$(( (HEALTH_END - HEALTH_START) / 1000000 ))
HEALTH_AVG=$(( HEALTH_TIME / WARMUP_REQUESTS ))

print_metric "Warmup time" "${HEALTH_TIME}ms for ${WARMUP_REQUESTS} requests"
print_metric "Average response time" "${HEALTH_AVG}ms"
echo ""

# Benchmark
echo "Running benchmark..."
RESULTS=$(ab -n $BENCHMARK_REQUESTS -c $CONCURRENCY -g /tmp/health.tsv "$API_BASE/api/health" 2>&1)

echo "$RESULTS" | grep -E "Time per request|Requests per second|50%|95%|99%"
echo ""

# ============================================
# 2. Authentication Performance
# ============================================

echo "=========================================="
echo "2. Authentication Performance"
echo "=========================================="
echo ""

LOGIN_PAYLOAD="{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}"

echo "Testing login endpoint..."
AUTH_START=$(date +%s%N)
for i in $(seq 1 10); do
    curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "$LOGIN_PAYLOAD" \
        "$API_BASE/api/auth/login" > /dev/null
done
AUTH_END=$(date +%s%N)

AUTH_TIME=$(( (AUTH_END - AUTH_START) / 1000000 ))
AUTH_AVG=$(( AUTH_TIME / 10 ))

print_metric "10 login requests" "${AUTH_TIME}ms"
print_metric "Average per login" "${AUTH_AVG}ms"
echo ""

# ============================================
# 3. Database Query Performance
# ============================================

echo "=========================================="
echo "3. Database Query Performance"
echo "=========================================="
echo ""

# Get token first
TOKEN=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d "$LOGIN_PAYLOAD" \
    "$API_BASE/api/auth/login" | jq -r '.data.access_token')

if [ "$TOKEN" != "null" ] && [ -n "$TOKEN" ]; then
    echo "Testing authenticated endpoint..."
    
    DB_START=$(date +%s%N)
    for i in $(seq 1 20); do
        curl -s -H "Authorization: Bearer $TOKEN" \
            "$API_BASE/api/admin/users" > /dev/null
    done
    DB_END=$(date +%s%N)
    
    DB_TIME=$(( (DB_END - DB_START) / 1000000 ))
    DB_AVG=$(( DB_TIME / 20 ))
    
    print_metric "20 database queries" "${DB_TIME}ms"
    print_metric "Average per query" "${DB_AVG}ms"
else
    echo "⚠ Authentication failed, skipping database tests"
fi
echo ""

# ============================================
# 4. OpenAPI Spec Load Time
# ============================================

echo "=========================================="
echo "4. OpenAPI Specification Load Time"
echo "=========================================="
echo ""

OPENAPI_START=$(date +%s%N)
curl -s "$API_BASE/openapi.json" > /tmp/openapi.json
OPENAPI_END=$(date +%s%N)

OPENAPI_TIME=$(( (OPENAPI_END - OPENAPI_START) / 1000000 ))
OPENAPI_SIZE=$(wc -c < /tmp/openapi.json)

print_metric "Load time" "${OPENAPI_TIME}ms"
print_metric "Spec size" "${OPENAPI_SIZE} bytes"
echo ""

# ============================================
# 5. System Resource Usage
# ============================================

echo "=========================================="
echo "5. System Resource Usage"
echo "=========================================="
echo ""

# CPU and Memory
BACKEND_STATS=$(docker stats digital_utopia_backend --no-stream --format "{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}")
BACKEND_CPU=$(echo "$BACKEND_STATS" | awk '{print $1}')
BACKEND_MEM=$(echo "$BACKEND_STATS" | awk '{print $2}')
BACKEND_MEM_PCT=$(echo "$BACKEND_STATS" | awk '{print $3}')

print_metric "Backend CPU" "$BACKEND_CPU"
print_metric "Backend Memory" "$BACKEND_MEM ($BACKEND_MEM_PCT)"
echo ""

# Database stats
PG_STATS=$(docker stats digital_utopia_postgres --no-stream --format "{{.CPUPerc}}\t{{.MemUsage}}")
PG_CPU=$(echo "$PG_STATS" | awk '{print $1}')
PG_MEM=$(echo "$PG_STATS" | awk '{print $2}')

print_metric "PostgreSQL CPU" "$PG_CPU"
print_metric "PostgreSQL Memory" "$PG_MEM"
echo ""

# Redis stats
REDIS_STATS=$(docker stats digital_utopia_redis --no-stream --format "{{.CPUPerc}}\t{{.MemUsage}}")
REDIS_CPU=$(echo "$REDIS_STATS" | awk '{print $1}')
REDIS_MEM=$(echo "$REDIS_STATS" | awk '{print $2}')

print_metric "Redis CPU" "$REDIS_CPU"
print_metric "Redis Memory" "$REDIS_MEM"
echo ""

# ============================================
# 6. Database Connection Pool
# ============================================

echo "=========================================="
echo "6. Database Connection Pool"
echo "=========================================="
echo ""

PG_CONNECTIONS=$(docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -t -c "SELECT count(*) FROM pg_stat_activity WHERE datname='digital_utopia';" 2>/dev/null | xargs)

print_metric "Active connections" "$PG_CONNECTIONS"
echo ""

# ============================================
# Summary & Recommendations
# ============================================

echo "=========================================="
echo "PERFORMANCE SUMMARY"
echo "=========================================="
echo ""

echo "API Response Times:"
echo "  - Health check: ${HEALTH_AVG}ms (target: <100ms) $([ $HEALTH_AVG -lt 100 ] && echo "✓" || echo "⚠")"
echo "  - Authentication: ${AUTH_AVG}ms (target: <500ms) $([ $AUTH_AVG -lt 500 ] && echo "✓" || echo "⚠")"
if [ -n "$DB_AVG" ]; then
    echo "  - Database query: ${DB_AVG}ms (target: <200ms) $([ $DB_AVG -lt 200 ] && echo "✓" || echo "⚠")"
fi
echo "  - OpenAPI spec: ${OPENAPI_TIME}ms (target: <1000ms) $([ $OPENAPI_TIME -lt 1000 ] && echo "✓" || echo "⚠")"
echo ""

echo "Resource Usage:"
echo "  - Backend CPU: $BACKEND_CPU"
echo "  - Backend Memory: $BACKEND_MEM_PCT"
echo "  - Database connections: $PG_CONNECTIONS"
echo ""

echo "Recommendations:"
if [ $HEALTH_AVG -gt 100 ]; then
    echo "  ⚠ Health check slower than target - consider optimization"
fi
if [ $AUTH_AVG -gt 500 ]; then
    echo "  ⚠ Authentication slower than target - review password hashing"
fi
if [ -n "$DB_AVG" ] && [ $DB_AVG -gt 200 ]; then
    echo "  ⚠ Database queries slow - add indexes or optimize queries"
fi

# Extract CPU percentage number
BACKEND_CPU_NUM=$(echo "$BACKEND_CPU" | sed 's/%//')
if (( $(echo "$BACKEND_CPU_NUM > 70" | bc -l) )); then
    echo "  ⚠ High CPU usage - consider scaling"
fi

echo ""
echo "=========================================="
echo "Benchmark complete!"
echo "=========================================="
