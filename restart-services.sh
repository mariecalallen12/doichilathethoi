#!/bin/bash
set -e

echo "🔄 Restarting backend and client services with new images..."

# Stop and remove old containers if they exist
docker stop digital_utopia_backend digital_utopia_client 2>/dev/null || true
docker rm digital_utopia_backend digital_utopia_client 2>/dev/null || true

# Get the network name
NETWORK="forexxx_digital_utopia_network"

# Start backend
echo "🚀 Starting backend..."
docker run -d \
  --name digital_utopia_backend \
  --network $NETWORK \
  -p 8000:8000 \
  -e POSTGRES_SERVER=postgres \
  -e POSTGRES_PORT=5432 \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=digital_utopia \
  -e REDIS_HOST=redis \
  -e REDIS_PORT=6379 \
  -e REDIS_PASSWORD= \
  -e REDIS_DB=0 \
  -e APP_NAME=CMEETRADING \
  -e APP_VERSION=2.0.0 \
  -e DEBUG=false \
  -e ENVIRONMENT=production \
  -e SECRET_KEY=CHANGE-THIS-IN-PRODUCTION \
  -e ALGORITHM=HS256 \
  -e ACCESS_TOKEN_EXPIRE_MINUTES=30 \
  -e REFRESH_TOKEN_EXPIRE_DAYS=7 \
  -e CORS_ORIGINS="http://localhost:3001,http://localhost:3002,http://localhost:5173,http://localhost:5174,https://cmeetrading.com,http://cmeetrading.com" \
  -e LOG_LEVEL=INFO \
  -e MARKET_DATA_SOURCE=simulator \
  -v backend_uploads:/app/uploads \
  --restart always \
  --health-cmd='curl -f http://localhost:8000/api/health || exit 1' \
  --health-interval=30s \
  --health-timeout=10s \
  --health-retries=5 \
  --health-start-period=60s \
  digital_utopia_backend:latest

# Start client
echo "🚀 Starting client..."
docker run -d \
  --name digital_utopia_client \
  --network $NETWORK \
  -p 3002:80 \
  --restart always \
  --health-cmd='wget --quiet --tries=1 --spider http://127.0.0.1/health || exit 1' \
  --health-interval=30s \
  --health-timeout=10s \
  --health-retries=3 \
  digital_utopia_client:latest

# Restart nginx to pick up new containers
echo "🔄 Restarting nginx..."
docker restart digital_utopia_nginx_proxy

# Wait for services to be ready
echo "⏳ Waiting for services to be healthy..."
sleep 40

# Show status
echo "📊 Service Status:"
docker ps --filter "name=digital_utopia" --format "table {{.Names}}\t{{.Status}}"

echo "✅ Done! Services restarted successfully."

