#!/bin/bash
# Restore Procedure Script
# Restores from backups with verification

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKUP_DIR="/root/backups/cmeetrading"

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

# List available backups
list_backups() {
    log_info "Available backups:"
    
    echo ""
    echo "Database backups:"
    ls -lh "$BACKUP_DIR"/database_*.sql.gz 2>/dev/null | tail -5
    
    echo ""
    echo "Redis backups:"
    ls -lh "$BACKUP_DIR"/redis_*.rdb 2>/dev/null | tail -5
    
    echo ""
    echo "Configuration backups:"
    ls -lh "$BACKUP_DIR"/config_*.tar.gz 2>/dev/null | tail -5
}

# Restore database
restore_database() {
    local backup_file=$1
    
    if [ -z "$backup_file" ]; then
        log_error "Backup file not specified"
        return 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        log_error "Backup file not found: $backup_file"
        return 1
    fi
    
    log_info "Restoring database from: $backup_file"
    
    # Stop services that depend on database
    docker compose stop backend client-app admin-app || true
    
    # Restore database
    gunzip -c "$backup_file" | docker exec -i digital_utopia_postgres psql -U postgres || {
        log_error "Database restore failed"
        return 1
    }
    
    log_success "Database restored successfully"
    
    # Restart services
    docker compose start backend client-app admin-app || true
}

# Restore Redis
restore_redis() {
    local backup_file=$1
    
    if [ -z "$backup_file" ]; then
        log_error "Backup file not specified"
        return 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        log_error "Backup file not found: $backup_file"
        return 1
    fi
    
    log_info "Restoring Redis from: $backup_file"
    
    # Stop Redis
    docker compose stop redis || true
    
    # Copy backup file
    docker cp "$backup_file" digital_utopia_redis:/data/dump.rdb || {
        log_error "Redis restore failed"
        return 1
    }
    
    # Restart Redis
    docker compose start redis || true
    
    log_success "Redis restored successfully"
}

# Restore configuration
restore_config() {
    local backup_file=$1
    
    if [ -z "$backup_file" ]; then
        log_error "Backup file not specified"
        return 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        log_error "Backup file not found: $backup_file"
        return 1
    fi
    
    log_info "Restoring configuration from: $backup_file"
    
    # Extract to temporary directory
    temp_dir=$(mktemp -d)
    tar -xzf "$backup_file" -C "$temp_dir" || {
        log_error "Configuration restore failed"
        rm -rf "$temp_dir"
        return 1
    }
    
    # Copy files back
    cp -r "$temp_dir"/* "$PROJECT_ROOT/" || {
        log_error "Failed to copy configuration files"
        rm -rf "$temp_dir"
        return 1
    }
    
    rm -rf "$temp_dir"
    log_success "Configuration restored successfully"
}

# Main execution
main() {
    echo "=========================================="
    echo "Restore Procedure"
    echo "Date: $(date)"
    echo "=========================================="
    echo ""
    
    if [ "$1" = "list" ]; then
        list_backups
        exit 0
    fi
    
    if [ "$1" = "database" ] && [ -n "$2" ]; then
        restore_database "$2"
        exit 0
    fi
    
    if [ "$1" = "redis" ] && [ -n "$2" ]; then
        restore_redis "$2"
        exit 0
    fi
    
    if [ "$1" = "config" ] && [ -n "$2" ]; then
        restore_config "$2"
        exit 0
    fi
    
    echo "Usage: $0 [list|database|redis|config] [backup_file]"
    echo ""
    echo "Examples:"
    echo "  $0 list"
    echo "  $0 database /root/backups/cmeetrading/database_20251210_120000.sql.gz"
    echo "  $0 redis /root/backups/cmeetrading/redis_20251210_120000.rdb"
    echo "  $0 config /root/backups/cmeetrading/config_20251210_120000.tar.gz"
    exit 1
}

main "$@"
