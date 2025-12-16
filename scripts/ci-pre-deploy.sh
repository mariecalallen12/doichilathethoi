#!/bin/bash
# CI/CD Pre-deployment script: Kiểm tra và chuẩn bị dữ liệu trước khi deploy

set -e

echo "=========================================="
echo "CI/CD PRE-DEPLOYMENT CHECK"
echo "=========================================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

ERRORS=0

# 1. Kiểm tra trước khi deploy
echo -e "${GREEN}[1] Kiểm tra trước khi deploy...${NC}"
if [ -f "scripts/pre-migration-check.sh" ]; then
    ./scripts/pre-migration-check.sh
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Pre-migration check failed${NC}"
        ERRORS=$((ERRORS + 1))
    else
        echo -e "${GREEN}✓ Pre-migration check passed${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Pre-migration-check script not found${NC}"
fi
echo ""

# 2. Backup dữ liệu (nếu đang chạy)
echo -e "${GREEN}[2] Backup dữ liệu...${NC}"
if docker ps | grep -q digital_utopia_postgres; then
    if [ -f "scripts/data-backup.sh" ]; then
        ./scripts/data-backup.sh
        echo -e "${GREEN}✓ Backup completed${NC}"
    else
        echo -e "${YELLOW}⚠ Backup script not found${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Containers not running, skipping backup${NC}"
fi
echo ""

# 3. Cleanup tự động (nếu đang chạy)
echo -e "${GREEN}[3] Cleanup dữ liệu tự động...${NC}"
if docker ps | grep -q digital_utopia_postgres; then
    if [ -f "scripts/data-cleanup-auto.sh" ]; then
        ./scripts/data-cleanup-auto.sh
        echo -e "${GREEN}✓ Cleanup completed${NC}"
    else
        echo -e "${YELLOW}⚠ Cleanup script not found${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Containers not running, skipping cleanup${NC}"
fi
echo ""

# 4. Validation (nếu đang chạy)
echo -e "${GREEN}[4] Validation dữ liệu...${NC}"
if docker ps | grep -q digital_utopia_postgres; then
    if [ -f "scripts/data-validation.sh" ]; then
        ./scripts/data-validation.sh
        if [ $? -ne 0 ]; then
            echo -e "${RED}✗ Validation failed${NC}"
            ERRORS=$((ERRORS + 1))
        else
            echo -e "${GREEN}✓ Validation passed${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ Validation script not found${NC}"
    fi
    
    # Additional data checks
    if [ -f "scripts/check-integrity.sh" ]; then
        ./scripts/check-integrity.sh || ERRORS=$((ERRORS + 1))
    fi
    
    if [ -f "scripts/verify-schema.sh" ]; then
        ./scripts/verify-schema.sh || ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${YELLOW}⚠ Containers not running, skipping validation${NC}"
fi
echo ""

# Tổng hợp
if [ "$ERRORS" -eq 0 ]; then
    echo -e "${GREEN}═══════════════════════════════════════${NC}"
    echo -e "${GREEN}✓ PRE-DEPLOYMENT CHECK THÀNH CÔNG${NC}"
    echo -e "${GREEN}═══════════════════════════════════════${NC}"
    exit 0
else
    echo -e "${RED}═══════════════════════════════════════${NC}"
    echo -e "${RED}✗ PRE-DEPLOYMENT CHECK THẤT BẠI${NC}"
    echo -e "${RED}Tìm thấy $ERRORS lỗi${NC}"
    echo -e "${RED}═══════════════════════════════════════${NC}"
    exit 1
fi

