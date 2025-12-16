#!/bin/bash
# Script để rebuild và restart client-app container với code mới
# Sử dụng docker commands trực tiếp (không dùng docker-compose)

set -e

echo "=========================================="
echo "Rebuilding và restarting client-app..."
echo "=========================================="

cd /root/forexxx/client-app

# 1. Build lại image
echo "Step 1: Building client-app image..."
docker build --no-cache -t forexxx-client-app:latest .

# 2. Stop container cũ
echo "Step 2: Stopping old container..."
docker stop digital_utopia_client 2>/dev/null || true
docker rm digital_utopia_client 2>/dev/null || true

# 3. Start container mới
echo "Step 3: Starting new container..."
docker run -d \
  --name digital_utopia_client \
  --network forexxx_digital_utopia_network \
  -p 3002:80 \
  --restart unless-stopped \
  forexxx-client-app:latest

# 4. Kiểm tra status
echo "Step 4: Checking container status..."
sleep 5
docker ps --filter "name=digital_utopia_client" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# 5. Kiểm tra logs
echo ""
echo "Step 5: Recent logs (last 20 lines):"
docker logs --tail 20 digital_utopia_client

echo ""
echo "=========================================="
echo "✅ Client-app đã được rebuild và restart!"
echo "=========================================="
echo ""
echo "Lưu ý:"
echo "- Service worker cache cần được clear trong browser"
echo "- Hard refresh (Ctrl+Shift+R) để load code mới"
echo "- Kiểm tra tại: https://cmeetrading.com/register"

