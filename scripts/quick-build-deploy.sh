#!/bin/bash

# Quick build and deploy with minimal output
# Usage: ./scripts/quick-build-deploy.sh

set -e

CLIENT_APP_DIR="/root/forexxx/client-app"
API_BASE_URL="${CLIENT_API_BASE_URL:-https://cmeetrading.com/api}"
CONTAINER_NAME="digital_utopia_client"
IMAGE_NAME="forexxx-client-app:latest"
PORT="${CLIENT_PORT:-3002}"

echo "Starting build process..."

# Clean
cd "$CLIENT_APP_DIR"
rm -rf dist node_modules/.vite 2>/dev/null || true

# Install (skip if node_modules exists and recent)
if [ ! -d "node_modules" ] || [ "node_modules" -ot "package.json" ]; then
    echo "Installing dependencies..."
    npm install --legacy-peer-deps --silent
fi

# Build
echo "Building application (this may take a few minutes)..."
npm run build

# Stop old container
echo "Stopping old container..."
docker stop "$CONTAINER_NAME" 2>/dev/null || true
docker rm "$CONTAINER_NAME" 2>/dev/null || true

# Build Docker image
echo "Building Docker image..."
cd "$CLIENT_APP_DIR"
docker build \
  --build-arg VITE_API_BASE_URL="$API_BASE_URL" \
  -t "$IMAGE_NAME" \
  . > /tmp/docker-build.log 2>&1

if [ $? -ne 0 ]; then
    echo "Docker build failed. Check /tmp/docker-build.log"
    exit 1
fi

# Start container
echo "Starting container..."
docker run -d \
  --name "$CONTAINER_NAME" \
  --network digital_utopia_network \
  -p "$PORT:80" \
  --restart unless-stopped \
  "$IMAGE_NAME"

# Wait and verify
sleep 5
if docker ps | grep -q "$CONTAINER_NAME"; then
    echo "✓ Container started successfully"
    echo "✓ Application available at http://localhost:$PORT"
else
    echo "✗ Container failed to start"
    docker logs "$CONTAINER_NAME" | tail -20
    exit 1
fi

