#!/bin/bash
# Auto-Fix Script
# Digital Utopia Platform - Automatic error fixing

set -e

# Source libraries
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/error-handler.sh"
source "$SCRIPT_DIR/lib/retry.sh"
source "$SCRIPT_DIR/error-detector.sh"

# Fix counters
FIXES_ATTEMPTED=0
FIXES_SUCCEEDED=0
FIXES_FAILED=0

# Fix permission errors
fix_permission_error() {
    local file_path="$1"
    local service="${2:-}"
    
    echo "🔧 Fixing permission error for: $file_path"
    FIXES_ATTEMPTED=$((FIXES_ATTEMPTED + 1))
    
    if [ -f "$file_path" ] || [ -d "$file_path" ]; then
        # Fix ownership
        if [ -n "$service" ]; then
            chown -R $(id -u):$(id -g) "$file_path" 2>/dev/null || true
        fi
        
        # Fix permissions
        chmod -R u+rwX "$file_path" 2>/dev/null || true
        
        if [ $? -eq 0 ]; then
            echo "✅ Permission fixed"
            FIXES_SUCCEEDED=$((FIXES_SUCCEEDED + 1))
            return 0
        fi
    fi
    
    echo "❌ Failed to fix permission"
    FIXES_FAILED=$((FIXES_FAILED + 1))
    return 1
}

# Fix disk space issues
fix_disk_space() {
    echo "🔧 Attempting to free up disk space..."
    FIXES_ATTEMPTED=$((FIXES_ATTEMPTED + 1))
    
    local freed_space=0
    
    # Remove unused Docker images
    echo "  Cleaning up unused Docker images..."
    docker image prune -af > /dev/null 2>&1 && freed_space=$((freed_space + 1))
    
    # Remove stopped containers
    echo "  Removing stopped containers..."
    docker container prune -f > /dev/null 2>&1 && freed_space=$((freed_space + 1))
    
    # Remove unused volumes
    echo "  Cleaning up unused volumes..."
    docker volume prune -f > /dev/null 2>&1 && freed_space=$((freed_space + 1))
    
    # Remove build cache
    echo "  Cleaning up build cache..."
    docker builder prune -af > /dev/null 2>&1 && freed_space=$((freed_space + 1))
    
    if [ $freed_space -gt 0 ]; then
        echo "✅ Freed up disk space"
        FIXES_SUCCEEDED=$((FIXES_SUCCEEDED + 1))
        return 0
    fi
    
    echo "⚠️  Could not free up significant disk space"
    FIXES_FAILED=$((FIXES_FAILED + 1))
    return 1
}

# Fix port conflicts
fix_port_conflict() {
    local port="$1"
    local service="${2:-}"
    
    echo "🔧 Fixing port conflict on port: $port"
    FIXES_ATTEMPTED=$((FIXES_ATTEMPTED + 1))
    
    # Find process using the port
    local pid=$(lsof -ti:$port 2>/dev/null || true)
    
    if [ -n "$pid" ]; then
        echo "  Found process $pid using port $port"
        
        # Try to stop conflicting container
        if [ -n "$service" ]; then
            docker-compose stop "$service" > /dev/null 2>&1 || true
            sleep 2
        fi
        
        # Kill process if still running
        if kill -0 "$pid" 2>/dev/null; then
            echo "  Stopping process $pid"
            kill "$pid" 2>/dev/null || true
            sleep 1
        fi
        
        # Verify port is free
        if ! lsof -ti:$port > /dev/null 2>&1; then
            echo "✅ Port $port is now free"
            FIXES_SUCCEEDED=$((FIXES_SUCCEEDED + 1))
            return 0
        fi
    fi
    
    echo "❌ Could not free port $port"
    FIXES_FAILED=$((FIXES_FAILED + 1))
    return 1
}

# Fix container conflicts
fix_container_conflict() {
    local container_name="$1"
    
    echo "🔧 Fixing container conflict: $container_name"
    FIXES_ATTEMPTED=$((FIXES_ATTEMPTED + 1))
    
    # Stop and remove conflicting container
    if docker ps -a --format '{{.Names}}' | grep -q "^${container_name}$"; then
        echo "  Stopping conflicting container..."
        docker stop "$container_name" > /dev/null 2>&1 || true
        sleep 1
        
        echo "  Removing conflicting container..."
        docker rm "$container_name" > /dev/null 2>&1 || true
        
        if [ $? -eq 0 ]; then
            echo "✅ Container conflict resolved"
            FIXES_SUCCEEDED=$((FIXES_SUCCEEDED + 1))
            return 0
        fi
    fi
    
    echo "❌ Could not resolve container conflict"
    FIXES_FAILED=$((FIXES_FAILED + 1))
    return 1
}

# Fix network issues
fix_network_issue() {
    local service="$1"
    
    echo "🔧 Fixing network issue for: $service"
    FIXES_ATTEMPTED=$((FIXES_ATTEMPTED + 1))
    
    # Restart service
    echo "  Restarting service..."
    docker-compose restart "$service" > /dev/null 2>&1
    
    # Wait a bit
    sleep 3
    
    # Check if service is running
    if docker-compose ps "$service" | grep -q "Up"; then
        echo "✅ Service restarted successfully"
        FIXES_SUCCEEDED=$((FIXES_SUCCEEDED + 1))
        return 0
    fi
    
    echo "❌ Service restart failed"
    FIXES_FAILED=$((FIXES_FAILED + 1))
    return 1
}

# Fix database connection
fix_database_connection() {
    echo "🔧 Fixing database connection..."
    FIXES_ATTEMPTED=$((FIXES_ATTEMPTED + 1))
    
    # Wait for database with retry
    retry_database 3 "docker-compose exec -T postgres pg_isready -U \${POSTGRES_USER:-postgres}" > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        echo "✅ Database connection established"
        FIXES_SUCCEEDED=$((FIXES_SUCCEEDED + 1))
        return 0
    fi
    
    echo "❌ Database connection failed"
    FIXES_FAILED=$((FIXES_FAILED + 1))
    return 1
}

# Fix missing image
fix_missing_image() {
    local image_name="$1"
    
    echo "🔧 Fixing missing image: $image_name"
    FIXES_ATTEMPTED=$((FIXES_ATTEMPTED + 1))
    
    # Try to pull image
    if docker pull "$image_name" > /dev/null 2>&1; then
        echo "✅ Image pulled successfully"
        FIXES_SUCCEEDED=$((FIXES_SUCCEEDED + 1))
        return 0
    fi
    
    # Try to build image
    if docker-compose build "$image_name" > /dev/null 2>&1; then
        echo "✅ Image built successfully"
        FIXES_SUCCEEDED=$((FIXES_SUCCEEDED + 1))
        return 0
    fi
    
    echo "❌ Could not fix missing image"
    FIXES_FAILED=$((FIXES_FAILED + 1))
    return 1
}

# Auto-fix based on error
auto_fix_error() {
    local error_text="$1"
    local error_info=$(detect_error "$error_text")
    
    # Extract error type and auto-fixable flag
    local error_type=""
    local is_auto_fixable=false
    
    if [[ "$error_info" =~ TYPE:([0-9]+) ]]; then
        error_type="${BASH_REMATCH[1]}"
    fi
    
    if echo "$error_info" | grep -q "AUTO_FIXABLE:true"; then
        is_auto_fixable=true
    fi
    
    if [ "$is_auto_fixable" = false ]; then
        echo "⚠️  Error is not auto-fixable"
        return 1
    fi
    
    # Fix based on error type
    case "$error_type" in
        $ERROR_TYPE_PERMISSION)
            # Extract file path if possible
            if [[ "$error_text" =~ (permission denied.*: )([^ ]+) ]]; then
                fix_permission_error "${BASH_REMATCH[2]}"
            fi
            ;;
        $ERROR_TYPE_RESOURCE)
            if echo "$error_text" | grep -qi "disk\|space"; then
                fix_disk_space
            fi
            ;;
        $ERROR_TYPE_NETWORK)
            # Extract service name if possible
            if [[ "$error_text" =~ (service|container)\s+([a-zA-Z0-9_-]+) ]]; then
                fix_network_issue "${BASH_REMATCH[2]}"
            fi
            ;;
        $ERROR_TYPE_DATABASE)
            if echo "$error_text" | grep -qi "connection"; then
                fix_database_connection
            fi
            ;;
        $ERROR_TYPE_DEPLOY)
            if echo "$error_text" | grep -qi "port.*in use"; then
                # Extract port number
                if [[ "$error_text" =~ port\s+([0-9]+) ]]; then
                    fix_port_conflict "${BASH_REMATCH[1]}"
                fi
            elif echo "$error_text" | grep -qi "container.*already"; then
                # Extract container name
                if [[ "$error_text" =~ container\s+([a-zA-Z0-9_-]+) ]]; then
                    fix_container_conflict "${BASH_REMATCH[1]}"
                fi
            fi
            ;;
    esac
}

# Get fix summary
get_fix_summary() {
    echo ""
    echo "📊 Auto-Fix Summary"
    echo "==================="
    echo "Fixes attempted: $FIXES_ATTEMPTED"
    echo "Fixes succeeded: $FIXES_SUCCEEDED"
    echo "Fixes failed: $FIXES_FAILED"
    
    if [ $FIXES_ATTEMPTED -gt 0 ]; then
        local success_rate=$((FIXES_SUCCEEDED * 100 / FIXES_ATTEMPTED))
        echo "Success rate: ${success_rate}%"
    fi
}

# Main function
main() {
    local error_text="$1"
    
    if [ -z "$error_text" ]; then
        echo "Usage: $0 <error_text>"
        exit 1
    fi
    
    auto_fix_error "$error_text"
    get_fix_summary
}

# Run if executed directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi

