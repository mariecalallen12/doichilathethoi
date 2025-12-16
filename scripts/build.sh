#!/bin/bash
set -e

echo "🔨 Building Docker Images"
echo "========================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Created .env from .env.example"
        echo "⚠️  Please edit .env file with your actual configuration before continuing!"
        read -p "Press Enter to continue after editing .env, or Ctrl+C to cancel..."
    else
        echo "❌ .env.example not found. Please create .env manually."
        exit 1
    fi
fi

# Build images
echo ""
echo "📦 Building backend image..."
docker-compose build backend

echo ""
echo "📦 Building client-app image..."
docker-compose build client-app

echo ""
echo "📦 Building admin-app image..."
docker-compose build admin-app

echo ""
echo "✅ All images built successfully!"
echo ""
echo "📊 Image summary:"
docker images | grep -E "forexxx|digital_utopia" || docker images | head -5

