#!/bin/bash
# Quick script to restart client-app container after rebuild
# Usage: ./restart-client-app.sh

set -e

cd /root/forexxx

echo "Restarting client-app container..."

# Stop and remove old container
docker compose stop client-app
docker compose rm -f client-app

# Start new container with updated image
docker compose up -d client-app

# Wait a bit for startup
sleep 5

# Check status
if docker ps | grep -q "digital_utopia_client"; then
    echo "✅ Container restarted successfully!"
    echo ""
    docker ps | grep client-app
    echo ""
    echo "Application available at: http://localhost:3002"
else
    echo "❌ Container failed to start!"
    docker logs digital_utopia_client --tail 20
    exit 1
fi

