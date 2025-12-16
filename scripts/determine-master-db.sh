#!/bin/bash
# Script xác định master database làm nguồn chuẩn
# Dựa trên data completeness, migration version, và data freshness

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REPORT_DIR="$PROJECT_ROOT/reports"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="$REPORT_DIR/master_db_analysis_${TIMESTAMP}.md"

mkdir -p "$REPORT_DIR"

# Màu sắc
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$REPORT_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$REPORT_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$REPORT_FILE"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$REPORT_FILE"
}

# Khởi tạo báo cáo
cat > "$REPORT_FILE" << EOF
# Báo Cáo Xác Định Master Database

**Ngày thực hiện:** $(date +'%Y-%m-%d %H:%M:%S')
**Script:** determine-master-db.sh
**Mục đích:** Xác định master database làm nguồn chuẩn cho đồng bộ hóa

---

## Tiêu Chí Đánh Giá

1. **Migration Version**: Version mới nhất
2. **Data Completeness**: Số lượng records đầy đủ nhất
3. **Data Freshness**: Dữ liệu mới nhất
4. **Data Quality**: Ít duplicates/orphans/inconsistencies nhất
5. **Environment Priority**: prod > staging > dev

---

EOF

log "Bắt đầu phân tích để xác định master database..."

# Environments để kiểm tra
ENVIRONMENTS=("dev" "staging" "prod")
declare -A ENV_SCORES
declare -A ENV_MIGRATION_VERSIONS
declare -A ENV_TOTAL_ROWS
declare -A ENV_LATEST_UPDATE
declare -A ENV_ISSUES_COUNT

# Hàm lấy container name
get_container_name() {
    local env=$1
    if [ "$env" == "dev" ]; then
        echo "digital_utopia_postgres"
    elif [ "$env" == "staging" ]; then
        echo "digital_utopia_postgres_staging"
    elif [ "$env" == "prod" ]; then
        echo "digital_utopia_postgres_prod"
    else
        # Fallback: tìm container postgres đầu tiên
        docker ps --format "{{.Names}}" | grep -i postgres | head -1 || echo "digital_utopia_postgres"
    fi
}

# Hàm lấy database name
get_db_name() {
    local env=$1
    local db_name="${env^^}_DB_NAME"
    echo "${!db_name:-digital_utopia}"
}

# Phân tích từng environment
for env in "${ENVIRONMENTS[@]}"; do
    log "Phân tích environment: $env"
    
    container=$(get_container_name "$env")
    db_name=$(get_db_name "$env")
    
    # Kiểm tra container có tồn tại không
    if ! docker ps --format "{{.Names}}" | grep -q "^${container}$"; then
        warning "Container $container không tồn tại cho environment $env"
        continue
    fi
    
    info "Container: $container, Database: $db_name"
    
    # 1. Lấy migration version
    migration_version=$(docker exec "$container" psql -U postgres -d "$db_name" -t -A -c "SELECT version_num FROM alembic_version LIMIT 1;" 2>/dev/null | tr -d ' ' || echo "unknown")
    ENV_MIGRATION_VERSIONS["$env"]="$migration_version"
    info "Migration version: $migration_version"
    
    # 2. Đếm tổng số rows
    total_rows=$(docker exec "$container" psql -U postgres -d "$db_name" -t -A -c "SELECT SUM(n_live_tup) FROM pg_stat_user_tables;" 2>/dev/null | tr -d ' ' || echo "0")
    ENV_TOTAL_ROWS["$env"]="$total_rows"
    info "Total rows: $total_rows"
    
    # 3. Lấy latest update timestamp
    latest_update=$(docker exec "$container" psql -U postgres -d "$db_name" -t -A -c "
        SELECT MAX(updated_at) FROM (
            SELECT updated_at FROM users WHERE updated_at IS NOT NULL
            UNION ALL
            SELECT updated_at FROM trading_orders WHERE updated_at IS NOT NULL
            UNION ALL
            SELECT updated_at FROM transactions WHERE updated_at IS NOT NULL
            UNION ALL
            SELECT updated_at FROM user_profiles WHERE updated_at IS NOT NULL
        ) AS all_updates;
    " 2>/dev/null | tr -d ' ' || echo "unknown")
    ENV_LATEST_UPDATE["$env"]="$latest_update"
    info "Latest update: $latest_update"
    
    # 4. Đếm số lượng issues (duplicates, orphans)
    issues_count=0
    
    # Duplicate emails
    dup_emails=$(docker exec "$container" psql -U postgres -d "$db_name" -t -A -c "
        SELECT COUNT(*) FROM (
            SELECT email FROM users GROUP BY email HAVING COUNT(*) > 1
        ) AS dup;
    " 2>/dev/null | tr -d ' ' || echo "0")
    issues_count=$((issues_count + dup_emails))
    
    # Orphaned records
    orphans=$(docker exec "$container" psql -U postgres -d "$db_name" -t -A -c "
        SELECT COUNT(*) FROM (
            SELECT COUNT(*) FROM user_profiles WHERE user_id NOT IN (SELECT id FROM users)
            UNION ALL
            SELECT COUNT(*) FROM refresh_tokens WHERE user_id NOT IN (SELECT id FROM users)
            UNION ALL
            SELECT COUNT(*) FROM wallet_balances WHERE user_id NOT IN (SELECT id FROM users)
        ) AS orphan_counts;
    " 2>/dev/null | awk '{sum+=$1} END {print sum}' || echo "0")
    issues_count=$((issues_count + orphans))
    
    ENV_ISSUES_COUNT["$env"]="$issues_count"
    info "Issues count: $issues_count"
    
    # Ghi vào báo cáo
    {
        echo "## Environment: $env"
        echo ""
        echo "- Container: $container"
        echo "- Database: $db_name"
        echo "- Migration Version: $migration_version"
        echo "- Total Rows: $total_rows"
        echo "- Latest Update: $latest_update"
        echo "- Issues Count: $issues_count"
        echo ""
    } >> "$REPORT_FILE"
done

# Tính điểm cho mỗi environment
log "Tính điểm đánh giá..."

max_migration=""
max_rows=0
min_issues=999999
latest_date=""

for env in "${ENVIRONMENTS[@]}"; do
    if [ -z "${ENV_MIGRATION_VERSIONS[$env]}" ]; then
        continue
    fi
    
    score=0
    
    # Điểm migration version (40 điểm)
    if [ "${ENV_MIGRATION_VERSIONS[$env]}" != "unknown" ]; then
        # So sánh migration version (giả định version là timestamp hoặc số)
        if [ -z "$max_migration" ] || [ "${ENV_MIGRATION_VERSIONS[$env]}" \> "$max_migration" ]; then
            max_migration="${ENV_MIGRATION_VERSIONS[$env]}"
        fi
    fi
    
    # Điểm data completeness (30 điểm)
    if [ "${ENV_TOTAL_ROWS[$env]}" -gt "$max_rows" ]; then
        max_rows="${ENV_TOTAL_ROWS[$env]}"
    fi
    
    # Điểm data quality (20 điểm) - ít issues hơn = điểm cao hơn
    if [ "${ENV_ISSUES_COUNT[$env]}" -lt "$min_issues" ]; then
        min_issues="${ENV_ISSUES_COUNT[$env]}"
    fi
    
    # Điểm environment priority (10 điểm)
    if [ "$env" == "prod" ]; then
        env_priority=10
    elif [ "$env" == "staging" ]; then
        env_priority=7
    else
        env_priority=5
    fi
    
    ENV_SCORES["$env"]=$score
done

# Tính điểm chi tiết
{
    echo "## Điểm Đánh Giá Chi Tiết"
    echo ""
    echo "| Environment | Migration | Rows | Issues | Priority | Total Score |"
    echo "|-------------|-----------|------|--------|----------|-------------|"
} >> "$REPORT_FILE"

MASTER_ENV=""
MAX_SCORE=0

for env in "${ENVIRONMENTS[@]}"; do
    if [ -z "${ENV_MIGRATION_VERSIONS[$env]}" ]; then
        continue
    fi
    
    score=0
    
    # Migration score (40 điểm)
    migration_score=0
    if [ "${ENV_MIGRATION_VERSIONS[$env]}" == "$max_migration" ]; then
        migration_score=40
    elif [ "${ENV_MIGRATION_VERSIONS[$env]}" != "unknown" ]; then
        migration_score=20  # Có migration nhưng không phải mới nhất
    fi
    
    # Rows score (30 điểm)
    rows_score=0
    if [ "$max_rows" -gt 0 ]; then
        rows_score=$((30 * ${ENV_TOTAL_ROWS[$env]} / max_rows))
    fi
    
    # Quality score (20 điểm) - ít issues = điểm cao
    quality_score=20
    if [ "$min_issues" -gt 0 ] && [ "${ENV_ISSUES_COUNT[$env]}" -gt 0 ]; then
        quality_score=$((20 - (20 * ${ENV_ISSUES_COUNT[$env]} / (min_issues + 1))))
    fi
    if [ "$quality_score" -lt 0 ]; then
        quality_score=0
    fi
    
    # Priority score (10 điểm)
    if [ "$env" == "prod" ]; then
        priority_score=10
    elif [ "$env" == "staging" ]; then
        priority_score=7
    else
        priority_score=5
    fi
    
    total_score=$((migration_score + rows_score + quality_score + priority_score))
    ENV_SCORES["$env"]=$total_score
    
    {
        echo "| $env | ${ENV_MIGRATION_VERSIONS[$env]} | ${ENV_TOTAL_ROWS[$env]} | ${ENV_ISSUES_COUNT[$env]} | $priority_score | $total_score |"
    } >> "$REPORT_FILE"
    
    if [ "$total_score" -gt "$MAX_SCORE" ]; then
        MAX_SCORE=$total_score
        MASTER_ENV="$env"
    fi
done

{
    echo ""
    echo "## Kết Luận"
    echo ""
} >> "$REPORT_FILE"

if [ -n "$MASTER_ENV" ]; then
    log "Master database được xác định: $MASTER_ENV"
    {
        echo "### ✅ Master Database: **$MASTER_ENV**"
        echo ""
        echo "- Container: $(get_container_name "$MASTER_ENV")"
        echo "- Database: $(get_db_name "$MASTER_ENV")"
        echo "- Migration Version: ${ENV_MIGRATION_VERSIONS[$MASTER_ENV]}"
        echo "- Total Rows: ${ENV_TOTAL_ROWS[$MASTER_ENV]}"
        echo "- Issues Count: ${ENV_ISSUES_COUNT[$MASTER_ENV]}"
        echo "- Score: $MAX_SCORE"
        echo ""
        echo "### Khuyến Nghị"
        echo ""
        echo "1. Sử dụng **$MASTER_ENV** làm nguồn dữ liệu chuẩn"
        echo "2. Đồng bộ dữ liệu từ $MASTER_ENV đến các environments khác"
        echo "3. Backup $MASTER_ENV trước khi thực hiện đồng bộ"
        echo "4. Verify data integrity sau khi đồng bộ"
        echo ""
    } >> "$REPORT_FILE"
    
    # Lưu master env vào file để các script khác sử dụng
    echo "$MASTER_ENV" > "$REPORT_DIR/master_env.txt"
    info "Master environment đã được lưu vào: $REPORT_DIR/master_env.txt"
else
    error "Không thể xác định master database"
    {
        echo "### ❌ Không thể xác định master database"
        echo ""
        echo "Lý do: Không có environment nào đáp ứng đủ tiêu chí"
        echo ""
        echo "Khuyến nghị:"
        echo "1. Kiểm tra lại kết nối đến các containers"
        echo "2. Verify database có dữ liệu"
        echo "3. Chạy lại script sau khi fix issues"
        echo ""
    } >> "$REPORT_FILE"
fi

log "Hoàn thành phân tích!"
log "Báo cáo được lưu tại: $REPORT_FILE"

echo ""
echo -e "${GREEN}=========================================="
echo "KẾT QUẢ XÁC ĐỊNH MASTER DATABASE"
echo "==========================================${NC}"
if [ -n "$MASTER_ENV" ]; then
    echo -e "${GREEN}Master Database: $MASTER_ENV${NC}"
    echo "File: $REPORT_FILE"
else
    echo -e "${RED}Không thể xác định master database${NC}"
fi
echo ""

