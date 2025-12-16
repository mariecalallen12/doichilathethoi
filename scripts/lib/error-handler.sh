#!/bin/bash
# Error Handler Library
# Digital Utopia Platform - Comprehensive Error Handling

# Error types
ERROR_TYPE_BUILD=1
ERROR_TYPE_DEPLOY=2
ERROR_TYPE_NETWORK=3
ERROR_TYPE_DATABASE=4
ERROR_TYPE_CONFIG=5
ERROR_TYPE_PERMISSION=6
ERROR_TYPE_RESOURCE=7
ERROR_TYPE_UNKNOWN=99

# Error severity
SEVERITY_CRITICAL=1
SEVERITY_HIGH=2
SEVERITY_MEDIUM=3
SEVERITY_LOW=4

# Global error tracking
ERROR_COUNT=0
CRITICAL_ERRORS=0
ERROR_LOG_FILE="/tmp/build_errors.log"

# Initialize error log
init_error_log() {
    > "$ERROR_LOG_FILE"
}

# Log error
log_error() {
    local error_type=$1
    local severity=$2
    local message=$3
    local details=$4
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo "[$timestamp] [TYPE:$error_type] [SEVERITY:$severity] $message" >> "$ERROR_LOG_FILE"
    if [ -n "$details" ]; then
        echo "  Details: $details" >> "$ERROR_LOG_FILE"
    fi
    
    ERROR_COUNT=$((ERROR_COUNT + 1))
    if [ "$severity" -eq "$SEVERITY_CRITICAL" ]; then
        CRITICAL_ERRORS=$((CRITICAL_ERRORS + 1))
    fi
}

# Get error type from error message
get_error_type() {
    local error_msg="$1"
    
    case "$error_msg" in
        *"docker build"*|*"build failed"*|*"Dockerfile"*)
            echo $ERROR_TYPE_BUILD
            ;;
        *"container"*|*"deploy"*|*"startup"*)
            echo $ERROR_TYPE_DEPLOY
            ;;
        *"connection"*|*"network"*|*"timeout"*|*"refused"*)
            echo $ERROR_TYPE_NETWORK
            ;;
        *"database"*|*"postgres"*|*"migration"*|*"alembic"*)
            echo $ERROR_TYPE_DATABASE
            ;;
        *"permission"*|*"denied"*|*"access"*)
            echo $ERROR_TYPE_PERMISSION
            ;;
        *"disk"*|*"space"*|*"memory"*|*"resource"*)
            echo $ERROR_TYPE_RESOURCE
            ;;
        *"config"*|*"environment"*|*".env"*)
            echo $ERROR_TYPE_CONFIG
            ;;
        *)
            echo $ERROR_TYPE_UNKNOWN
            ;;
    esac
}

# Get error severity
get_error_severity() {
    local error_msg="$1"
    local error_type=$2
    
    # Critical errors
    if [[ "$error_msg" =~ (fatal|critical|cannot start|failed to start|corrupted) ]]; then
        echo $SEVERITY_CRITICAL
    # High severity
    elif [[ "$error_msg" =~ (error|failed|exception|abort) ]] || [ "$error_type" -eq "$ERROR_TYPE_DATABASE" ]; then
        echo $SEVERITY_HIGH
    # Medium severity
    elif [[ "$error_msg" =~ (warning|timeout|retry) ]]; then
        echo $SEVERITY_MEDIUM
    # Low severity
    else
        echo $SEVERITY_LOW
    fi
}

# Check if error is recoverable
is_recoverable() {
    local error_type=$1
    local error_msg="$2"
    
    # Non-recoverable errors
    if [[ "$error_msg" =~ (syntax error|invalid config|permission denied permanently) ]]; then
        return 1
    fi
    
    # Recoverable errors
    case "$error_type" in
        $ERROR_TYPE_NETWORK)
            return 0  # Network errors are usually recoverable
            ;;
        $ERROR_TYPE_RESOURCE)
            return 0  # Resource issues can be fixed
            ;;
        $ERROR_TYPE_DATABASE)
            if [[ "$error_msg" =~ (connection|timeout) ]]; then
                return 0  # Connection issues are recoverable
            fi
            return 1
            ;;
        *)
            return 0  # Default: assume recoverable
            ;;
    esac
}

# Format error message
format_error() {
    local error_type=$1
    local severity=$2
    local message="$3"
    
    local type_name=""
    case "$error_type" in
        $ERROR_TYPE_BUILD) type_name="BUILD" ;;
        $ERROR_TYPE_DEPLOY) type_name="DEPLOY" ;;
        $ERROR_TYPE_NETWORK) type_name="NETWORK" ;;
        $ERROR_TYPE_DATABASE) type_name="DATABASE" ;;
        $ERROR_TYPE_CONFIG) type_name="CONFIG" ;;
        $ERROR_TYPE_PERMISSION) type_name="PERMISSION" ;;
        $ERROR_TYPE_RESOURCE) type_name="RESOURCE" ;;
        *) type_name="UNKNOWN" ;;
    esac
    
    local severity_name=""
    case "$severity" in
        $SEVERITY_CRITICAL) severity_name="CRITICAL" ;;
        $SEVERITY_HIGH) severity_name="HIGH" ;;
        $SEVERITY_MEDIUM) severity_name="MEDIUM" ;;
        *) severity_name="LOW" ;;
    esac
    
    echo "[$type_name:$severity_name] $message"
}

# Get error summary
get_error_summary() {
    echo ""
    echo "📊 Error Summary"
    echo "================"
    echo "Total Errors: $ERROR_COUNT"
    echo "Critical Errors: $CRITICAL_ERRORS"
    
    if [ -f "$ERROR_LOG_FILE" ] && [ -s "$ERROR_LOG_FILE" ]; then
        echo ""
        echo "Recent Errors:"
        tail -10 "$ERROR_LOG_FILE" | sed 's/^/  /'
    fi
}

# Check if build should continue
should_continue() {
    if [ "$CRITICAL_ERRORS" -gt 0 ]; then
        return 1
    fi
    return 0
}

# Cleanup error log
cleanup_error_log() {
    if [ -f "$ERROR_LOG_FILE" ]; then
        rm -f "$ERROR_LOG_FILE"
    fi
}

