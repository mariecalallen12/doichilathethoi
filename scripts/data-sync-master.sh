#!/bin/bash
# Script master để thực hiện toàn bộ quy trình kiểm tra, backup, cleanup và validation dữ liệu

set -e

echo "=========================================="
echo "QUY TRÌNH ĐỒNG BỘ VÀ DỌN DẸP DỮ LIỆU"
echo "=========================================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Bước 1: Kiểm tra và đánh giá
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}BƯỚC 1: KIỂM TRA VÀ ĐÁNH GIÁ DỮ LIỆU${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
./scripts/data-audit.sh
echo ""

# Bước 2: Phân tích dữ liệu
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}BƯỚC 2: PHÂN TÍCH DỮ LIỆU DƯ THỪA/CŨ${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
./scripts/data-analysis.sh
echo ""

# Bước 3: Backup dữ liệu
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}BƯỚC 3: BACKUP DỮ LIỆU${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
./scripts/data-backup.sh
echo ""

# Bước 4: Dọn dẹp dữ liệu
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}BƯỚC 4: DỌN DẸP DỮ LIỆU${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${YELLOW}Lưu ý: Script cleanup sẽ yêu cầu xác nhận${NC}"
./scripts/data-cleanup.sh
echo ""

# Bước 5: Validation
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}BƯỚC 5: VALIDATION DỮ LIỆU${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
./scripts/data-validation.sh
echo ""

echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}HOÀN THÀNH QUY TRÌNH ĐỒNG BỘ DỮ LIỆU${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"

