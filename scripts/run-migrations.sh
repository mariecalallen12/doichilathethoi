#!/bin/bash
set -e

echo "📦 Running Database Migrations"
echo "================================"

# Check if backend container is running
if ! docker-compose ps backend | grep -q "Up"; then
    echo "❌ Backend container is not running. Please start it first:"
    echo "   docker-compose up -d backend"
    exit 1
fi

# Run migrations
echo "⏳ Running Alembic migrations..."
docker-compose exec -T backend alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✅ Migrations completed successfully!"
    
    # Show current migration version
    echo ""
    echo "📊 Current migration version:"
    docker-compose exec -T backend alembic current
    
    # Show migration history
    echo ""
    echo "📜 Migration history:"
    docker-compose exec -T backend alembic history --verbose | head -20
else
    echo "❌ Migration failed!"
    exit 1
fi

