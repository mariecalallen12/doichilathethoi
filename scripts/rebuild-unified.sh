#!/bin/bash
# Script rebuild Docker images và containers với data migration

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

ENVIRONMENT="${1:-dev}"

log "Rebuilding for environment: $ENVIRONMENT"

# Backup
log "Backing up data..."
"$SCRIPT_DIR/data-backup.sh" || error "Backup failed"

# Stop containers
log "Stopping containers..."
docker-compose -f docker-compose.yml -f "docker-compose.${ENVIRONMENT}.yml" down || true

# Rebuild images
log "Rebuilding images..."
docker-compose -f docker-compose.yml -f "docker-compose.${ENVIRONMENT}.yml" build --no-cache || error "Build failed"

# Start containers
log "Starting containers..."
docker-compose -f docker-compose.yml -f "docker-compose.${ENVIRONMENT}.yml" up -d || error "Start failed"

# Wait for services
log "Waiting for services..."
sleep 10

# Run migrations
log "Running migrations..."
docker-compose -f docker-compose.yml -f "docker-compose.${ENVIRONMENT}.yml" exec -T backend alembic upgrade head || error "Migration failed"

log "✅ Rebuild completed"

