#!/bin/bash
# Build Configuration
# Digital Utopia Platform - Build Settings

# Build settings
BUILD_PARALLEL=true
BUILD_CACHE=true
BUILD_NO_CACHE=false
BUILD_PULL=false

# Timeout settings (seconds)
BUILD_TIMEOUT=1800  # 30 minutes
DEPLOY_TIMEOUT=300   # 5 minutes
HEALTH_CHECK_TIMEOUT=120  # 2 minutes

# Retry settings
MAX_BUILD_RETRIES=2
MAX_DEPLOY_RETRIES=3
MAX_NETWORK_RETRIES=5
MAX_DATABASE_RETRIES=3

# Resource limits
MIN_DISK_SPACE_GB=10
MIN_MEMORY_MB=2048
MIN_CPU_CORES=2

# Service build order (dependencies first)
BUILD_ORDER=(
    "postgres"
    "redis"
    "backend"
    "client-app"
    "admin-app"
)

# Service dependencies
SERVICE_DEPENDENCIES=(
    "backend:postgres,redis"
    "client-app:backend"
    "admin-app:backend"
)

# Health check intervals
HEALTH_CHECK_INTERVAL=5
HEALTH_CHECK_RETRIES=12

# Log settings
LOG_LEVEL="INFO"
LOG_RETENTION_DAYS=7
LOG_MAX_SIZE_MB=100

# Auto-fix settings
AUTO_FIX_ENABLED=true
AUTO_CLEANUP_ENABLED=true
AUTO_RETRY_ENABLED=true

# Notification settings
NOTIFY_ON_ERROR=true
NOTIFY_ON_SUCCESS=false
NOTIFY_ON_CRITICAL=true

# Get service dependencies
get_service_dependencies() {
    local service="$1"
    for dep in "${SERVICE_DEPENDENCIES[@]}"; do
        if [[ "$dep" =~ ^$service: ]]; then
            echo "${dep#*:}" | tr ',' ' '
            return 0
        fi
    done
    echo ""
}

# Check if service should be built
should_build_service() {
    local service="$1"
    
    # Always build if no cache
    if [ "$BUILD_NO_CACHE" = true ]; then
        return 0
    fi
    
    # Check if image exists and is recent
    if docker images | grep -q "$service"; then
        return 0
    fi
    
    return 0  # Default: build
}

# Get build command for service
get_build_command() {
    local service="$1"
    local extra_args="$2"
    
    local cmd="docker-compose build"
    
    if [ "$BUILD_NO_CACHE" = true ]; then
        cmd="$cmd --no-cache"
    fi
    
    if [ "$BUILD_PULL" = true ]; then
        cmd="$cmd --pull"
    fi
    
    cmd="$cmd $service"
    
    if [ -n "$extra_args" ]; then
        cmd="$cmd $extra_args"
    fi
    
    echo "$cmd"
}

