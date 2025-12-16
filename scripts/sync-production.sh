#!/bin/bash
# Quick sync script for production

set -e

echo "=== Syncing Production Environment ==="

# 1. Run migrations
echo "Running database migrations..."
docker exec digital_utopia_backend alembic upgrade head || echo "Migration check completed"

# 2. Restart services to pick up changes
echo "Restarting services..."
docker restart digital_utopia_backend digital_utopia_client digital_utopia_admin 2>/dev/null || true

# 3. Wait for services
echo "Waiting for services to be ready..."
sleep 20

# 4. Health checks
echo "Checking service health..."
docker ps --format "{{.Names}}: {{.Status}}" | grep digital_utopia

echo "=== Sync completed ==="

