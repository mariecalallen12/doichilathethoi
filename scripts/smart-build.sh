#!/bin/bash
# Smart Build Script
# Digital Utopia Platform - Build with error handling and auto-fix

set -e

# Source libraries
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/error-handler.sh"
source "$SCRIPT_DIR/lib/retry.sh"
source "$SCRIPT_DIR/lib/log-parser.sh"
source "$SCRIPT_DIR/config/build-config.sh"
source "$SCRIPT_DIR/error-detector.sh"
source "$SCRIPT_DIR/auto-fix.sh"
source "$SCRIPT_DIR/monitor-logs.sh"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Build tracking
BUILD_START_TIME=$(date +%s)
BUILDS_SUCCEEDED=0
BUILDS_FAILED=0

# Initialize
init_build() {
    echo "🔨 Smart Build - Digital Utopia Platform"
    echo "========================================"
    echo ""
    
    # Initialize error log
    init_error_log
    
    # Check prerequisites
    echo "📋 Pre-build validation..."
    check_prerequisites
    
    # Check resources
    check_resources
    
    echo "✅ Pre-build checks passed"
    echo ""
}

# Check prerequisites
check_prerequisites() {
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error $ERROR_TYPE_CONFIG $SEVERITY_CRITICAL "Docker is not installed" ""
        echo "❌ Docker is not installed"
        exit 1
    fi
    
    # Check docker-compose
    if ! command -v docker-compose &> /dev/null; then
        log_error $ERROR_TYPE_CONFIG $SEVERITY_CRITICAL "docker-compose is not installed" ""
        echo "❌ docker-compose is not installed"
        exit 1
    fi
    
    # Check .env file
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            echo "⚠️  .env file not found. Creating from template..."
            cp .env.example .env
            echo "✅ Created .env from .env.example"
            echo "⚠️  Please edit .env file with your actual configuration!"
            read -p "Press Enter to continue or Ctrl+C to cancel..."
        else
            log_error $ERROR_TYPE_CONFIG $SEVERITY_CRITICAL ".env file not found" ""
            echo "❌ .env file not found"
            exit 1
        fi
    fi
    
    echo "  ✅ Docker: $(docker --version)"
    echo "  ✅ docker-compose: $(docker-compose --version)"
    echo "  ✅ .env file: exists"
}

# Check resources
check_resources() {
    # Check disk space
    local available_space=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
    if [ "$available_space" -lt "$MIN_DISK_SPACE_GB" ]; then
        echo "⚠️  Low disk space: ${available_space}GB available (minimum: ${MIN_DISK_SPACE_GB}GB)"
        echo "🔧 Attempting to free up space..."
        fix_disk_space || true
    else
        echo "  ✅ Disk space: ${available_space}GB available"
    fi
    
    # Check memory (if possible)
    if command -v free &> /dev/null; then
        local available_mem=$(free -m | awk 'NR==2{print $7}')
        if [ "$available_mem" -lt "$MIN_MEMORY_MB" ]; then
            echo "⚠️  Low memory: ${available_mem}MB available (minimum: ${MIN_MEMORY_MB}MB)"
        else
            echo "  ✅ Memory: ${available_mem}MB available"
        fi
    fi
}

# Build service with error handling
build_service() {
    local service="$1"
    local build_log="/tmp/build_${service}.log"
    
    echo ""
    echo "📦 Building $service..."
    echo "----------------------"
    
    # Start log monitoring in background
    monitor_build_logs "$service" > "$build_log" 2>&1 &
    local monitor_pid=$!
    
    # Build with retry
    local build_success=false
    retry_build $MAX_BUILD_RETRIES "docker-compose build $service" > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        build_success=true
    else
        # Check for errors in log
        local errors=$(scan_logs_for_errors "$build_log" "$service")
        if [ $? -gt 0 ]; then
            # Try auto-fix
            echo "🔧 Attempting to auto-fix errors..."
            while IFS= read -r error_line; do
                if [ -n "$error_line" ]; then
                    auto_fix_error "$error_line" || true
                fi
            done <<< "$errors"
            
            # Retry build after fixes
            echo "🔄 Retrying build after fixes..."
            retry_build $MAX_BUILD_RETRIES "docker-compose build $service" > /dev/null 2>&1
            if [ $? -eq 0 ]; then
                build_success=true
            fi
        fi
    fi
    
    # Stop monitoring
    kill $monitor_pid 2>/dev/null || true
    wait $monitor_pid 2>/dev/null || true
    
    # Verify build
    if [ "$build_success" = true ]; then
        if verify_build "$service"; then
            echo "✅ $service built successfully"
            BUILDS_SUCCEEDED=$((BUILDS_SUCCEEDED + 1))
            return 0
        fi
    fi
    
    echo "❌ $service build failed"
    BUILDS_FAILED=$((BUILDS_FAILED + 1))
    
    # Show recent errors
    echo ""
    echo "Recent errors:"
    get_recent_errors "$service" 10 | head -5 | sed 's/^/  /'
    
    return 1
}

# Verify build
verify_build() {
    local service="$1"
    
    # Check if image exists
    if docker images | grep -q "$(basename $(pwd))_${service}"; then
        return 0
    fi
    
    return 1
}

# Build all services
build_all_services() {
    echo ""
    echo "🚀 Building all services..."
    echo "============================"
    
    # Build in order
    for service in "${BUILD_ORDER[@]}"; do
        # Check if service should be built
        if should_build_service "$service"; then
            build_service "$service"
        else
            echo "⏭️  Skipping $service (already built)"
        fi
    done
}

# Post-build verification
post_build_verification() {
    echo ""
    echo "🔍 Post-build verification..."
    echo "============================="
    
    local all_verified=true
    
    for service in "${BUILD_ORDER[@]}"; do
        if verify_build "$service"; then
            echo "  ✅ $service: verified"
        else
            echo "  ❌ $service: verification failed"
            all_verified=false
        fi
    done
    
    if [ "$all_verified" = true ]; then
        echo ""
        echo "✅ All builds verified successfully"
        return 0
    else
        echo ""
        echo "❌ Some builds failed verification"
        return 1
    fi
}

# Build summary
build_summary() {
    local build_end_time=$(date +%s)
    local build_duration=$((build_end_time - BUILD_START_TIME))
    
    echo ""
    echo "========================================"
    echo "📊 Build Summary"
    echo "========================================"
    echo "Build duration: ${build_duration}s"
    echo "Builds succeeded: $BUILDS_SUCCEEDED"
    echo "Builds failed: $BUILDS_FAILED"
    echo ""
    
    # Error summary
    get_error_summary
    
    # Fix summary
    get_fix_summary
    
    echo ""
    if [ $BUILDS_FAILED -eq 0 ]; then
        echo "✅ All builds completed successfully!"
        return 0
    else
        echo "❌ Some builds failed"
        return 1
    fi
}

# Main function
main() {
    local service="${1:-}"
    
    # Initialize
    init_build
    
    if [ -n "$service" ]; then
        # Build single service
        build_service "$service"
    else
        # Build all services
        build_all_services
    fi
    
    # Post-build verification
    post_build_verification
    
    # Summary
    build_summary
}

# Run if executed directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi

