#!/bin/bash
# Script to rebuild and restart client-app container
# This script will:
# 1. Build the Docker image with latest code changes
# 2. Stop the old container
# 3. Start the new container with the updated image

set -e

echo "=========================================="
echo "Rebuilding and deploying client-app"
echo "=========================================="

cd /root/forexxx

# Step 1: Build the Docker image
echo ""
echo "Step 1: Building Docker image..."
echo "This may take 5-10 minutes..."
docker compose build client-app

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

echo "✅ Build completed successfully!"

# Step 2: Stop and remove old container
echo ""
echo "Step 2: Stopping old container..."
docker compose stop client-app
docker compose rm -f client-app

# Step 3: Start new container
echo ""
echo "Step 3: Starting new container..."
docker compose up -d client-app

# Step 4: Wait for health check
echo ""
echo "Step 4: Waiting for container to be healthy..."
sleep 10

# Step 5: Verify
echo ""
echo "Step 5: Verifying deployment..."
if docker ps | grep -q "digital_utopia_client"; then
    echo "✅ Container is running!"
    echo ""
    echo "Container status:"
    docker ps | grep client-app
    echo ""
    echo "Recent logs:"
    docker logs digital_utopia_client --tail 10
    echo ""
    echo "✅ Deployment completed successfully!"
    echo "Application available at: http://localhost:3002"
else
    echo "❌ Container failed to start!"
    echo "Check logs with: docker logs digital_utopia_client"
    exit 1
fi

