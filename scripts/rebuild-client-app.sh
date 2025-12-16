#!/bin/bash
# Script để rebuild và restart client-app container với code mới

set -e

echo "=========================================="
echo "Rebuilding và restarting client-app..."
echo "=========================================="

cd /root/forexxx

# 1. Build lại client-app image với code mới
echo "Step 1: Building client-app image..."
docker-compose build --no-cache client-app

# 2. Stop và remove container cũ
echo "Step 2: Stopping old container..."
docker-compose stop client-app
docker-compose rm -f client-app

# 3. Start container mới
echo "Step 3: Starting new container..."
docker-compose up -d client-app

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

