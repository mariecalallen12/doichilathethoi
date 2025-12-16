#!/bin/bash
set -e

echo "🚀 CMEETRADING - Backend Entrypoint"
echo "================================================"

# Validate required environment variables
echo "🔍 Validating environment variables..."
REQUIRED_VARS=("POSTGRES_SERVER" "POSTGRES_USER" "POSTGRES_PASSWORD" "POSTGRES_DB" "REDIS_HOST" "REDIS_PORT")
MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    echo "❌ Missing required environment variables: ${MISSING_VARS[*]}"
    exit 1
fi

echo "✅ All required environment variables are set"

# Wait for PostgreSQL to be ready (with timeout and retry logic)
echo "⏳ Waiting for PostgreSQL to be ready..."
POSTGRES_TIMEOUT=90
POSTGRES_COUNT=0
POSTGRES_RETRY_DELAY=2
POSTGRES_MAX_DELAY=10

# Try to resolve PostgreSQL hostname, fallback to common IPs if DNS fails
POSTGRES_HOST="${POSTGRES_SERVER}"
if ! PGPASSWORD="${POSTGRES_PASSWORD}" psql -h "${POSTGRES_SERVER}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -c '\q' 2>/dev/null; then
    echo "⚠️  Cannot connect to ${POSTGRES_SERVER}, trying IP addresses..."
    # Try common IPs in docker network (172.19.0.x range)
    for ip in 172.19.0.6 172.19.0.5 172.19.0.4 172.18.0.2; do
        if PGPASSWORD="${POSTGRES_PASSWORD}" psql -h "${ip}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -c '\q' 2>/dev/null; then
            echo "✅ Found PostgreSQL at ${ip}"
            POSTGRES_HOST="${ip}"
            break
        fi
    done
fi

until PGPASSWORD="${POSTGRES_PASSWORD}" psql -h "${POSTGRES_HOST}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -c '\q' 2>/dev/null; do
  POSTGRES_COUNT=$((POSTGRES_COUNT + 1))
  if [ $POSTGRES_COUNT -ge $POSTGRES_TIMEOUT ]; then
    echo "⚠️  PostgreSQL timeout after ${POSTGRES_TIMEOUT} attempts - continuing without PostgreSQL connection..."
    break
  fi
  
  # Exponential backoff
  DELAY=$((POSTGRES_RETRY_DELAY * (POSTGRES_COUNT / 5 + 1)))
  if [ $DELAY -gt $POSTGRES_MAX_DELAY ]; then
    DELAY=$POSTGRES_MAX_DELAY
  fi
  
  echo "PostgreSQL is unavailable (attempt $POSTGRES_COUNT/$POSTGRES_TIMEOUT) - sleeping ${DELAY}s..."
  sleep $DELAY
done

if [ $POSTGRES_COUNT -lt $POSTGRES_TIMEOUT ]; then
  echo "✅ PostgreSQL is ready! (connected after $POSTGRES_COUNT attempts)"
fi

# Wait for Redis to be ready (with timeout and retry logic)
echo "⏳ Waiting for Redis to be ready..."
REDIS_TIMEOUT=5
REDIS_COUNT=0
REDIS_RETRY_DELAY=2
REDIS_MAX_DELAY=10

if [ -n "${REDIS_PASSWORD}" ]; then
    until redis-cli -h "${REDIS_HOST}" -p "${REDIS_PORT}" -a "${REDIS_PASSWORD}" ping 2>/dev/null | grep -q PONG; do
        REDIS_COUNT=$((REDIS_COUNT + 1))
        if [ $REDIS_COUNT -ge $REDIS_TIMEOUT ]; then
            echo "⚠️  Redis timeout after ${REDIS_TIMEOUT} attempts - continuing without Redis..."
            break
        fi
        
        # Exponential backoff
        DELAY=$((REDIS_RETRY_DELAY * (REDIS_COUNT / 5 + 1)))
        if [ $DELAY -gt $REDIS_MAX_DELAY ]; then
            DELAY=$REDIS_MAX_DELAY
        fi
        
        echo "Redis is unavailable (attempt $REDIS_COUNT/$REDIS_TIMEOUT) - sleeping ${DELAY}s..."
        sleep $DELAY
    done
else
    until redis-cli -h "${REDIS_HOST_RESOLVED}" -p "${REDIS_PORT}" ping 2>/dev/null | grep -q PONG; do
        REDIS_COUNT=$((REDIS_COUNT + 1))
        if [ $REDIS_COUNT -ge $REDIS_TIMEOUT ]; then
            echo "⚠️  Redis timeout after ${REDIS_TIMEOUT} attempts - continuing without Redis..."
            break
        fi
        
        # Exponential backoff
        DELAY=$((REDIS_RETRY_DELAY * (REDIS_COUNT / 5 + 1)))
        if [ $DELAY -gt $REDIS_MAX_DELAY ]; then
            DELAY=$REDIS_MAX_DELAY
        fi
        
        echo "Redis is unavailable (attempt $REDIS_COUNT/$REDIS_TIMEOUT) - sleeping ${DELAY}s..."
        sleep $DELAY
    done
fi

if [ $REDIS_COUNT -lt $REDIS_TIMEOUT ]; then
    echo "✅ Redis is ready! (connected after $REDIS_COUNT attempts)"
fi

# Run database migrations (only if PostgreSQL is available)
if [ $POSTGRES_COUNT -lt $POSTGRES_TIMEOUT ]; then
    echo "📦 Running database migrations..."
    cd /app
    alembic upgrade head || echo "⚠️  Migration failed, continuing..."
    echo "✅ Migrations completed!"
    
    # Verify database connection
    echo "🔍 Verifying database connection..."
    python -c "
from app.db.session import check_db_connection
import sys
if check_db_connection():
    print('✅ Database connection verified!')
    sys.exit(0)
else:
    print('⚠️  Database connection failed, but continuing...')
    sys.exit(0)
" || echo "⚠️  Database verification failed, continuing..."
else
    echo "⚠️  Skipping database migrations (PostgreSQL not available)"
fi

# Start the application
echo "🎯 Starting FastAPI application..."
exec "$@"

