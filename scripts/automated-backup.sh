#!/bin/bash
# Enhanced Automated Backup Script
# Creates comprehensive backups with verification

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKUP_DIR="/root/backups/cmeetrading"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Create backup directory
create_backup_dir() {
    mkdir -p "$BACKUP_DIR"
    log_info "Backup directory: $BACKUP_DIR"
}

# Backup PostgreSQL database
backup_database() {
    log_info "Backing up PostgreSQL database..."
    
    backup_file="$BACKUP_DIR/database_${TIMESTAMP}.sql.gz"
    
    docker exec digital_utopia_postgres pg_dumpall -U postgres | gzip > "$backup_file" || {
        log_error "Database backup failed"
        return 1
    }
    
    # Verify backup
    if [ -f "$backup_file" ] && [ -s "$backup_file" ]; then
        log_success "Database backup created: $backup_file"
        echo "$backup_file" > "$BACKUP_DIR/latest_database_backup.txt"
        return 0
    else
        log_error "Database backup file is empty or missing"
        return 1
    fi
}

# Backup Redis
backup_redis() {
    log_info "Backing up Redis..."
    
    backup_file="$BACKUP_DIR/redis_${TIMESTAMP}.rdb"
    
    # Trigger Redis save
    docker exec digital_utopia_redis redis-cli BGSAVE || {
        log_warn "Redis BGSAVE failed, trying SAVE"
        docker exec digital_utopia_redis redis-cli SAVE
    }
    
    # Wait for save to complete
    sleep 5
    
    # Copy RDB file
    docker cp digital_utopia_redis:/data/dump.rdb "$backup_file" || {
        log_error "Redis backup failed"
        return 1
    }
    
    if [ -f "$backup_file" ] && [ -s "$backup_file" ]; then
        log_success "Redis backup created: $backup_file"
        echo "$backup_file" > "$BACKUP_DIR/latest_redis_backup.txt"
        return 0
    else
        log_error "Redis backup file is empty or missing"
        return 1
    fi
}

# Backup configuration files
backup_config() {
    log_info "Backing up configuration files..."
    
    backup_file="$BACKUP_DIR/config_${TIMESTAMP}.tar.gz"
    
    tar -czf "$backup_file" \
        -C "$PROJECT_ROOT" \
        docker-compose.yml \
        docker-compose.monitoring.yml \
        docker-compose.logging.yml \
        docker-compose.ha.yml \
        nginx/ \
        prometheus/ \
        grafana/ \
        .env.production 2>/dev/null || {
        log_warn "Some config files may be missing"
    }
    
    if [ -f "$backup_file" ] && [ -s "$backup_file" ]; then
        log_success "Configuration backup created: $backup_file"
        echo "$backup_file" > "$BACKUP_DIR/latest_config_backup.txt"
        return 0
    else
        log_error "Configuration backup failed"
        return 1
    fi
}

# Backup application data
backup_app_data() {
    log_info "Backing up application data..."
    
    backup_file="$BACKUP_DIR/app_data_${TIMESTAMP}.tar.gz"
    
    # Backup uploads and other application data
    docker run --rm \
        -v digital_utopia_backend_uploads:/data:ro \
        -v "$(dirname "$backup_file")":/backup \
        alpine tar czf "/backup/$(basename "$backup_file")" -C /data . || {
        log_warn "Application data backup may have failed (volume may not exist)"
        return 0
    }
    
    if [ -f "$backup_file" ] && [ -s "$backup_file" ]; then
        log_success "Application data backup created: $backup_file"
        return 0
    else
        log_warn "Application data backup file is empty or missing"
        return 0  # Not critical
    fi
}

# Verify backup integrity
verify_backup() {
    log_info "Verifying backup integrity..."
    
    # Verify database backup
    if [ -f "$BACKUP_DIR/database_${TIMESTAMP}.sql.gz" ]; then
        if gunzip -t "$BACKUP_DIR/database_${TIMESTAMP}.sql.gz" 2>/dev/null; then
            log_success "Database backup integrity verified"
        else
            log_error "Database backup integrity check failed"
            return 1
        fi
    fi
    
    # Verify config backup
    if [ -f "$BACKUP_DIR/config_${TIMESTAMP}.tar.gz" ]; then
        if tar -tzf "$BACKUP_DIR/config_${TIMESTAMP}.tar.gz" > /dev/null 2>&1; then
            log_success "Configuration backup integrity verified"
        else
            log_error "Configuration backup integrity check failed"
            return 1
        fi
    fi
    
    return 0
}

# Cleanup old backups
cleanup_old_backups() {
    log_info "Cleaning up backups older than $RETENTION_DAYS days..."
    
    find "$BACKUP_DIR" -type f -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete
    find "$BACKUP_DIR" -type f -name "*.rdb" -mtime +$RETENTION_DAYS -delete
    find "$BACKUP_DIR" -type f -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete
    
    log_success "Old backups cleaned up"
}

# Generate backup report
generate_report() {
    log_info "Generating backup report..."
    
    report_file="$BACKUP_DIR/backup_report_${TIMESTAMP}.txt"
    
    {
        echo "Backup Report"
        echo "Generated: $(date)"
        echo "=========================================="
        echo ""
        echo "Backup Location: $BACKUP_DIR"
        echo ""
        echo "Backups Created:"
        ls -lh "$BACKUP_DIR"/*${TIMESTAMP}* 2>/dev/null | awk '{print $9, $5}'
        echo ""
        echo "Total Backup Size:"
        du -sh "$BACKUP_DIR"
        echo ""
        echo "Available Space:"
        df -h "$BACKUP_DIR" | tail -1
    } > "$report_file"
    
    log_success "Backup report generated: $report_file"
    cat "$report_file"
}

# Main execution
main() {
    echo "=========================================="
    echo "Automated Backup Script"
    echo "Date: $(date)"
    echo "=========================================="
    echo ""
    
    create_backup_dir
    
    backup_database
    backup_redis
    backup_config
    backup_app_data
    
    verify_backup
    cleanup_old_backups
    generate_report
    
    log_success "Backup completed successfully!"
}

main
