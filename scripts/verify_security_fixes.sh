#!/bin/bash

# ============================================
# Security Fixes Verification Script
# ============================================
# Verifies that all security fixes have been
# properly applied
# ============================================

set -e

echo "=========================================="
echo "CMEETRADING - Security Verification"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASS_COUNT=0
FAIL_COUNT=0
WARN_COUNT=0

check_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASS_COUNT++))
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
    ((FAIL_COUNT++))
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARN_COUNT++))
}

# ============================================
# Check 1: SECRET_KEY
# ============================================

echo "Checking SECRET_KEY..."
if grep -q "CHANGE-THIS" .env 2>/dev/null; then
    check_fail "SECRET_KEY still contains placeholder"
elif grep -q "SECRET_KEY=" .env 2>/dev/null; then
    SECRET_LEN=$(grep "SECRET_KEY=" .env | cut -d'=' -f2 | wc -c)
    if [ "$SECRET_LEN" -gt 50 ]; then
        check_pass "SECRET_KEY appears to be strong (length: $SECRET_LEN)"
    else
        check_warn "SECRET_KEY might be too short (length: $SECRET_LEN)"
    fi
else
    check_fail "SECRET_KEY not found in .env"
fi

# ============================================
# Check 2: POSTGRES_PASSWORD
# ============================================

echo "Checking POSTGRES_PASSWORD..."
if grep -q "CHANGE_THIS_STRONG_PASSWORD" .env 2>/dev/null; then
    check_fail "POSTGRES_PASSWORD still contains placeholder"
elif grep -q "POSTGRES_PASSWORD=" .env 2>/dev/null; then
    PG_LEN=$(grep "POSTGRES_PASSWORD=" .env | cut -d'=' -f2 | wc -c)
    if [ "$PG_LEN" -gt 20 ]; then
        check_pass "POSTGRES_PASSWORD appears to be strong (length: $PG_LEN)"
    else
        check_warn "POSTGRES_PASSWORD might be too short (length: $PG_LEN)"
    fi
else
    check_fail "POSTGRES_PASSWORD not found in .env"
fi

# ============================================
# Check 3: REDIS_PASSWORD
# ============================================

echo "Checking REDIS_PASSWORD..."
if grep -q "CHANGE_THIS_REDIS_PASSWORD" .env 2>/dev/null; then
    check_fail "REDIS_PASSWORD still contains placeholder"
elif grep -q "REDIS_PASSWORD=" .env 2>/dev/null; then
    REDIS_LEN=$(grep "REDIS_PASSWORD=" .env | cut -d'=' -f2 | wc -c)
    if [ "$REDIS_LEN" -gt 20 ]; then
        check_pass "REDIS_PASSWORD appears to be strong (length: $REDIS_LEN)"
    else
        check_warn "REDIS_PASSWORD might be too short (length: $REDIS_LEN)"
    fi
else
    check_fail "REDIS_PASSWORD not found in .env"
fi

# ============================================
# Check 4: DEBUG Mode
# ============================================

echo "Checking DEBUG mode..."
if grep -q "DEBUG=false" .env 2>/dev/null || grep -q "DEBUG=False" .env 2>/dev/null; then
    check_pass "DEBUG is disabled"
else
    check_fail "DEBUG should be set to false"
fi

# ============================================
# Check 5: ENVIRONMENT
# ============================================

echo "Checking ENVIRONMENT..."
if grep -q "ENVIRONMENT=production" .env 2>/dev/null; then
    check_pass "ENVIRONMENT is set to production"
else
    check_warn "ENVIRONMENT should be set to production"
fi

# ============================================
# Check 6: CORS_ORIGINS
# ============================================

echo "Checking CORS_ORIGINS..."
if grep "CORS_ORIGINS=" .env 2>/dev/null | grep -q "localhost"; then
    check_fail "CORS_ORIGINS contains localhost (should be removed for production)"
else
    check_pass "CORS_ORIGINS does not contain localhost"
fi

# ============================================
# Check 7: Backend Health
# ============================================

echo "Checking backend health..."
if curl -s -f http://localhost:8000/api/health > /dev/null 2>&1; then
    HEALTH=$(curl -s http://localhost:8000/api/health | jq -r '.status' 2>/dev/null)
    if [ "$HEALTH" = "ok" ]; then
        check_pass "Backend is healthy"
    else
        check_fail "Backend health check failed"
    fi
else
    check_fail "Backend is not responding"
fi

# ============================================
# Check 8: Database Connection
# ============================================

echo "Checking database connection..."
DB_STATUS=$(curl -s http://localhost:8000/api/health | jq -r '.database' 2>/dev/null)
if [ "$DB_STATUS" = "connected" ]; then
    check_pass "Database is connected"
else
    check_fail "Database connection failed"
fi

# ============================================
# Check 9: Redis Connection
# ============================================

echo "Checking Redis connection..."
REDIS_STATUS=$(curl -s http://localhost:8000/api/health | jq -r '.redis' 2>/dev/null)
if [ "$REDIS_STATUS" = "connected" ]; then
    check_pass "Redis is connected"
else
    check_fail "Redis connection failed"
fi

# ============================================
# Check 10: Container Status
# ============================================

echo "Checking container status..."
BACKEND_STATUS=$(docker ps --filter "name=digital_utopia_backend" --format "{{.Status}}" | grep -i "healthy\|up")
if [ -n "$BACKEND_STATUS" ]; then
    check_pass "Backend container is running"
else
    check_fail "Backend container is not running"
fi

# ============================================
# Summary
# ============================================

echo ""
echo "=========================================="
echo "VERIFICATION SUMMARY"
echo "=========================================="
echo ""
echo -e "${GREEN}Passed:${NC} $PASS_COUNT"
echo -e "${YELLOW}Warnings:${NC} $WARN_COUNT"
echo -e "${RED}Failed:${NC} $FAIL_COUNT"
echo ""

TOTAL=$((PASS_COUNT + FAIL_COUNT + WARN_COUNT))
SCORE=$((PASS_COUNT * 100 / TOTAL))

echo "Score: $SCORE/100"
echo ""

if [ "$FAIL_COUNT" -eq 0 ]; then
    echo -e "${GREEN}✓ All security checks passed!${NC}"
    echo ""
    echo "System is ready for production deployment."
    exit 0
else
    echo -e "${RED}✗ Some security checks failed${NC}"
    echo ""
    echo "Please fix the failed checks before deploying to production."
    echo "Review: SECURITY_AUDIT_REPORT_20251210.md"
    exit 1
fi
