#!/bin/bash
# Script kiểm tra trước khi chạy migration - ngăn việc đưa dữ liệu mock/example trở lại

set -e

echo "=========================================="
echo "KIỂM TRA TRƯỚC KHI MIGRATION"
echo "=========================================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

ERRORS=0

# 1. Kiểm tra migration files có chứa dữ liệu test/mock không
echo -e "${GREEN}[1] Kiểm tra migration files:${NC}"
MIGRATION_DIR="./backend/alembic/versions"
if [ -d "$MIGRATION_DIR" ]; then
    TEST_MIGRATIONS=$(grep -r -i "test\|mock\|example\|demo\|fake" "$MIGRATION_DIR" --include="*.py" | grep -v "def test" | grep -v "# test" | wc -l)
    if [ "$TEST_MIGRATIONS" -gt 0 ]; then
        echo -e "${YELLOW}⚠ Tìm thấy $TEST_MIGRATIONS dòng có thể chứa dữ liệu test trong migrations${NC}"
        echo "Các file cần kiểm tra:"
        grep -r -i "test\|mock\|example\|demo\|fake" "$MIGRATION_DIR" --include="*.py" | grep -v "def test" | grep -v "# test" | head -10
    else
        echo -e "${GREEN}✓ Không tìm thấy dữ liệu test trong migrations${NC}"
    fi
fi
echo ""

# 2. Kiểm tra seed files
echo -e "${GREEN}[2] Kiểm tra seed files:${NC}"
SEED_FILES=$(find ./backend -name "*seed*" -o -name "*fixture*" -o -name "*sample*" 2>/dev/null | head -10)
if [ -n "$SEED_FILES" ]; then
    echo -e "${YELLOW}⚠ Tìm thấy các file seed/fixture:${NC}"
    echo "$SEED_FILES"
    echo "Lưu ý: Đảm bảo các file này chỉ chứa dữ liệu production hợp lệ"
else
    echo -e "${GREEN}✓ Không tìm thấy seed files${NC}"
fi
echo ""

# 3. Kiểm tra database hiện tại có dữ liệu test không
echo -e "${GREEN}[3] Kiểm tra database hiện tại:${NC}"
if docker ps | grep -q digital_utopia_postgres; then
    TEST_DATA=$(docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -t -c "
    SELECT COUNT(*) FROM users WHERE email LIKE '%test%' OR email LIKE '%example%' OR email LIKE '%demo%'
    UNION ALL
    SELECT COUNT(*) FROM trading_orders WHERE status = 'test' OR source LIKE '%test%';
    " 2>/dev/null | awk '{sum+=$1} END {print sum}')
    
    if [ "$TEST_DATA" -gt 0 ]; then
        echo -e "${RED}✗ Tìm thấy $TEST_DATA records test trong database${NC}"
        ERRORS=$((ERRORS + 1))
    else
        echo -e "${GREEN}✓ Không có dữ liệu test trong database${NC}"
    fi
else
    echo -e "${YELLOW}⚠ PostgreSQL container không chạy, bỏ qua kiểm tra${NC}"
fi
echo ""

# 4. Kiểm tra environment variables
echo -e "${GREEN}[4] Kiểm tra environment variables:${NC}"
if [ -f ".env" ]; then
    if grep -q "test\|demo\|example" .env | grep -v "^#"; then
        echo -e "${YELLOW}⚠ Tìm thấy từ khóa test/demo trong .env${NC}"
    else
        echo -e "${GREEN}✓ Environment variables OK${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Không tìm thấy file .env${NC}"
fi
echo ""

# Tổng hợp
if [ "$ERRORS" -eq 0 ]; then
    echo -e "${GREEN}✓ Pre-migration check thành công!${NC}"
    exit 0
else
    echo -e "${RED}✗ Pre-migration check thất bại! Tìm thấy $ERRORS vấn đề.${NC}"
    exit 1
fi

