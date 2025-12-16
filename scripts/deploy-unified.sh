#!/bin/bash
# Script deploy lên các environments với health checks và rollback

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

ENVIRONMENT="${1:-staging}"

log "Deploying to: $ENVIRONMENT"

# Health check function
health_check() {
    local env=$1
    log "Health checking $env..."
    
    # Check backend
    docker-compose -f docker-compose.yml -f "docker-compose.${env}.yml" exec -T backend curl -f http://localhost:8000/api/health || return 1
    
    # Check database
    docker-compose -f docker-compose.yml -f "docker-compose.${env}.yml" exec -T postgres pg_isready -U postgres || return 1
    
    return 0
}

# Rollback function
rollback() {
    local env=$1
    error "Deployment failed, rolling back..."
    docker-compose -f docker-compose.yml -f "docker-compose.${env}.yml" down
    # Restore backup if needed
    exit 1
}

# Deploy
log "Deploying..."
"$SCRIPT_DIR/rebuild-unified.sh" "$ENVIRONMENT" || rollback "$ENVIRONMENT"

# Health check
health_check "$ENVIRONMENT" || rollback "$ENVIRONMENT"

log "✅ Deployment successful"

