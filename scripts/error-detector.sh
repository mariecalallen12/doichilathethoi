#!/bin/bash
# Error Detector
# Digital Utopia Platform - Detect and classify errors

set -e

# Source libraries
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/error-handler.sh"
source "$SCRIPT_DIR/config/error-patterns.conf"

# Load error patterns
load_error_patterns() {
    # Patterns are loaded from error-patterns.conf
    # This function can be extended to load from file
    return 0
}

# Detect error in text
detect_error() {
    local text="$1"
    local error_type=""
    local severity=$SEVERITY_LOW
    local is_critical=false
    local is_recoverable=true
    local is_auto_fixable=false
    
    # Check critical patterns
    for pattern in "${CRITICAL_ERROR_PATTERNS[@]}"; do
        if echo "$text" | grep -qiE "$pattern"; then
            is_critical=true
            severity=$SEVERITY_CRITICAL
            break
        fi
    done
    
    # Check build errors
    if [ -z "$error_type" ]; then
        for pattern in "${BUILD_ERROR_PATTERNS[@]}"; do
            if echo "$text" | grep -qiE "$pattern"; then
                error_type=$ERROR_TYPE_BUILD
                severity=$SEVERITY_HIGH
                break
            fi
        done
    fi
    
    # Check network errors
    if [ -z "$error_type" ]; then
        for pattern in "${NETWORK_ERROR_PATTERNS[@]}"; do
            if echo "$text" | grep -qiE "$pattern"; then
                error_type=$ERROR_TYPE_NETWORK
                severity=$SEVERITY_MEDIUM
                is_recoverable=true
                break
            fi
        done
    fi
    
    # Check database errors
    if [ -z "$error_type" ]; then
        for pattern in "${DATABASE_ERROR_PATTERNS[@]}"; do
            if echo "$text" | grep -qiE "$pattern"; then
                error_type=$ERROR_TYPE_DATABASE
                severity=$SEVERITY_HIGH
                break
            fi
        done
    fi
    
    # Check permission errors
    if [ -z "$error_type" ]; then
        for pattern in "${PERMISSION_ERROR_PATTERNS[@]}"; do
            if echo "$text" | grep -qiE "$pattern"; then
                error_type=$ERROR_TYPE_PERMISSION
                severity=$SEVERITY_MEDIUM
                is_auto_fixable=true
                break
            fi
        done
    fi
    
    # Check resource errors
    if [ -z "$error_type" ]; then
        for pattern in "${RESOURCE_ERROR_PATTERNS[@]}"; do
            if echo "$text" | grep -qiE "$pattern"; then
                error_type=$ERROR_TYPE_RESOURCE
                severity=$SEVERITY_HIGH
                is_auto_fixable=true
                break
            fi
        done
    fi
    
    # Check config errors
    if [ -z "$error_type" ]; then
        for pattern in "${CONFIG_ERROR_PATTERNS[@]}"; do
            if echo "$text" | grep -qiE "$pattern"; then
                error_type=$ERROR_TYPE_CONFIG
                severity=$SEVERITY_HIGH
                is_recoverable=false
                break
            fi
        done
    fi
    
    # Check deploy errors
    if [ -z "$error_type" ]; then
        for pattern in "${DEPLOY_ERROR_PATTERNS[@]}"; do
            if echo "$text" | grep -qiE "$pattern"; then
                error_type=$ERROR_TYPE_DEPLOY
                severity=$SEVERITY_HIGH
                break
            fi
        done
    fi
    
    # Check if auto-fixable
    if [ "$is_auto_fixable" = false ]; then
        for pattern in "${AUTO_FIXABLE_PATTERNS[@]}"; do
            if echo "$text" | grep -qiE "$pattern"; then
                is_auto_fixable=true
                break
            fi
        done
    fi
    
    # Check if recoverable
    if [ "$is_recoverable" = true ]; then
        for pattern in "${RECOVERABLE_ERROR_PATTERNS[@]}"; do
            if echo "$text" | grep -qiE "$pattern"; then
                is_recoverable=true
                break
            fi
        done
    fi
    
    # Default to unknown if no pattern matched
    if [ -z "$error_type" ]; then
        error_type=$ERROR_TYPE_UNKNOWN
    fi
    
    # Output error information as JSON-like structure
    echo "TYPE:$error_type|SEVERITY:$severity|CRITICAL:$is_critical|RECOVERABLE:$is_recoverable|AUTO_FIXABLE:$is_auto_fixable"
}

# Scan logs for errors
scan_logs_for_errors() {
    local log_source="$1"
    local service="${2:-}"
    
    local errors_found=0
    
    if [ -f "$log_source" ]; then
        # Scan file
        while IFS= read -r line; do
            local error_info=$(detect_error "$line")
            if [ -n "$error_info" ] && [[ "$error_info" =~ TYPE:([0-9]+) ]]; then
                local error_type="${BASH_REMATCH[1]}"
                if [ "$error_type" -ne "$ERROR_TYPE_UNKNOWN" ] || echo "$error_info" | grep -q "CRITICAL:true"; then
                    echo "ERROR: $line"
                    errors_found=$((errors_found + 1))
                fi
            fi
        done < "$log_source"
    elif [ -n "$service" ]; then
        # Scan service logs
        docker-compose logs "$service" 2>&1 | while IFS= read -r line; do
            local error_info=$(detect_error "$line")
            if [ -n "$error_info" ] && [[ "$error_info" =~ TYPE:([0-9]+) ]]; then
                local error_type="${BASH_REMATCH[1]}"
                if [ "$error_type" -ne "$ERROR_TYPE_UNKNOWN" ] || echo "$error_info" | grep -q "CRITICAL:true"; then
                    echo "ERROR: $line"
                    errors_found=$((errors_found + 1))
                fi
            fi
        done
    fi
    
    return $errors_found
}

# Get error suggestions
get_error_suggestions() {
    local error_text="$1"
    local error_info=$(detect_error "$error_text")
    
    local suggestions=()
    
    # Extract error type
    if [[ "$error_info" =~ TYPE:([0-9]+) ]]; then
        local error_type="${BASH_REMATCH[1]}"
        
        case "$error_type" in
            $ERROR_TYPE_NETWORK)
                suggestions+=("Check network connectivity")
                suggestions+=("Verify service is running")
                suggestions+=("Check firewall settings")
                ;;
            $ERROR_TYPE_PERMISSION)
                suggestions+=("Check file permissions")
                suggestions+=("Run with appropriate user")
                suggestions+=("Fix ownership")
                ;;
            $ERROR_TYPE_RESOURCE)
                suggestions+=("Free up disk space")
                suggestions+=("Increase memory limit")
                suggestions+=("Clean up old containers/images")
                ;;
            $ERROR_TYPE_DATABASE)
                suggestions+=("Check database connection")
                suggestions+=("Verify database is running")
                suggestions+=("Check migration status")
                ;;
            $ERROR_TYPE_CONFIG)
                suggestions+=("Validate configuration file")
                suggestions+=("Check environment variables")
                suggestions+=("Verify .env file exists")
                ;;
        esac
    fi
    
    # Check error messages mapping
    for mapping in "${ERROR_MESSAGES[@]}"; do
        local pattern=$(echo "$mapping" | cut -d'|' -f1)
        local suggestion=$(echo "$mapping" | cut -d'|' -f2)
        
        if echo "$error_text" | grep -qiE "$pattern"; then
            suggestions+=("$suggestion")
        fi
    done
    
    # Output suggestions
    for suggestion in "${suggestions[@]}"; do
        echo "  💡 $suggestion"
    done
}

# Main function
main() {
    local command="${1:-detect}"
    local input="${2:-}"
    
    case "$command" in
        detect)
            if [ -z "$input" ]; then
                echo "Usage: $0 detect <error_text>"
                exit 1
            fi
            detect_error "$input"
            ;;
        scan)
            scan_logs_for_errors "$input" "${3:-}"
            ;;
        suggest)
            if [ -z "$input" ]; then
                echo "Usage: $0 suggest <error_text>"
                exit 1
            fi
            get_error_suggestions "$input"
            ;;
        *)
            echo "Usage: $0 {detect|scan|suggest} [args...]"
            exit 1
            ;;
    esac
}

# Run if executed directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi

