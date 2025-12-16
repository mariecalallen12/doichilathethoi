#!/bin/bash
set -e

echo "🗄️  Initializing Digital Utopia Platform Database..."

# This script runs automatically when PostgreSQL container starts for the first time
# It creates the database if it doesn't exist and sets up basic configuration

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Create extensions if needed
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pgcrypto";
    
    -- Set timezone
    SET timezone = 'UTC';
    
    -- Log initialization
    SELECT 'Database initialized successfully' AS status;
EOSQL

echo "✅ Database initialization completed!"

