#!/bin/bash
# Retry Mechanism Library
# Digital Utopia Platform - Exponential Backoff Retry

# Default retry configuration
DEFAULT_MAX_RETRIES=3
DEFAULT_INITIAL_DELAY=2
DEFAULT_MAX_DELAY=32
DEFAULT_BACKOFF_MULTIPLIER=2

# Retry counter
RETRY_COUNT=0

# Execute command with retry
retry() {
    local max_retries="${1:-$DEFAULT_MAX_RETRIES}"
    local initial_delay="${2:-$DEFAULT_INITIAL_DELAY}"
    local command="${@:3}"
    
    local delay=$initial_delay
    local attempt=1
    
    while [ $attempt -le $max_retries ]; do
        echo "🔄 Attempt $attempt/$max_retries: $command"
        
        # Execute command
        if eval "$command"; then
            echo "✅ Command succeeded on attempt $attempt"
            RETRY_COUNT=0
            return 0
        fi
        
        local exit_code=$?
        
        # Check if we should retry
        if [ $attempt -lt $max_retries ]; then
            echo "⚠️  Command failed (exit code: $exit_code). Retrying in ${delay}s..."
            sleep $delay
            
            # Exponential backoff
            delay=$((delay * DEFAULT_BACKOFF_MULTIPLIER))
            if [ $delay -gt $DEFAULT_MAX_DELAY ]; then
                delay=$DEFAULT_MAX_DELAY
            fi
        else
            echo "❌ Command failed after $max_retries attempts"
            RETRY_COUNT=$attempt
            return $exit_code
        fi
        
        attempt=$((attempt + 1))
    done
    
    return 1
}

# Retry with custom condition
retry_with_condition() {
    local max_retries="${1:-$DEFAULT_MAX_RETRIES}"
    local condition_check="${2}"
    local command="${@:3}"
    
    local attempt=1
    local delay=$DEFAULT_INITIAL_DELAY
    
    while [ $attempt -le $max_retries ]; do
        echo "🔄 Attempt $attempt/$max_retries"
        
        # Execute command
        eval "$command"
        local exit_code=$?
        
        # Check condition
        if eval "$condition_check"; then
            echo "✅ Condition met on attempt $attempt"
            RETRY_COUNT=0
            return 0
        fi
        
        if [ $attempt -lt $max_retries ]; then
            echo "⚠️  Condition not met. Retrying in ${delay}s..."
            sleep $delay
            delay=$((delay * DEFAULT_BACKOFF_MULTIPLIER))
            if [ $delay -gt $DEFAULT_MAX_DELAY ]; then
                delay=$DEFAULT_MAX_DELAY
            fi
        else
            echo "❌ Condition not met after $max_retries attempts"
            RETRY_COUNT=$attempt
            return 1
        fi
        
        attempt=$((attempt + 1))
    done
    
    return 1
}

# Retry network operations
retry_network() {
    local max_retries="${1:-5}"
    local command="${@:2}"
    
    retry "$max_retries" 2 "$command"
}

# Retry database operations
retry_database() {
    local max_retries="${1:-3}"
    local command="${@:2}"
    
    retry "$max_retries" 4 "$command"
}

# Retry build operations
retry_build() {
    local max_retries="${1:-2}"
    local command="${@:2}"
    
    # Builds are expensive, fewer retries
    retry "$max_retries" 5 "$command"
}

# Wait for condition with retry
wait_for_condition() {
    local condition="$1"
    local timeout="${2:-60}"
    local interval="${3:-2}"
    local description="${4:-Condition}"
    
    local start_time=$(date +%s)
    local elapsed=0
    local attempt=1
    
    echo "⏳ Waiting for $description..."
    
    while [ $elapsed -lt $timeout ]; do
        if eval "$condition"; then
            echo "✅ $description met after ${elapsed}s (attempt $attempt)"
            return 0
        fi
        
        echo "   Attempt $attempt: $description not met yet... (${elapsed}s/${timeout}s)"
        sleep $interval
        elapsed=$(($(date +%s) - start_time))
        attempt=$((attempt + 1))
    done
    
    echo "❌ $description not met within ${timeout}s"
    return 1
}

# Retry with exponential backoff (custom)
retry_exponential() {
    local max_retries="${1:-$DEFAULT_MAX_RETRIES}"
    local base_delay="${2:-$DEFAULT_INITIAL_DELAY}"
    local multiplier="${3:-$DEFAULT_BACKOFF_MULTIPLIER}"
    local max_delay="${4:-$DEFAULT_MAX_DELAY}"
    local command="${@:5}"
    
    local delay=$base_delay
    local attempt=1
    
    while [ $attempt -le $max_retries ]; do
        echo "🔄 Attempt $attempt/$max_retries (delay: ${delay}s)"
        
        if eval "$command"; then
            echo "✅ Success on attempt $attempt"
            return 0
        fi
        
        if [ $attempt -lt $max_retries ]; then
            echo "⚠️  Failed. Waiting ${delay}s before retry..."
            sleep $delay
            
            # Exponential backoff
            delay=$((delay * multiplier))
            if [ $delay -gt $max_delay ]; then
                delay=$max_delay
            fi
        fi
        
        attempt=$((attempt + 1))
    done
    
    echo "❌ Failed after $max_retries attempts"
    return 1
}

# Get retry statistics
get_retry_stats() {
    echo "Retry Statistics:"
    echo "  Last retry count: $RETRY_COUNT"
    echo "  Default max retries: $DEFAULT_MAX_RETRIES"
    echo "  Default initial delay: ${DEFAULT_INITIAL_DELAY}s"
    echo "  Default max delay: ${DEFAULT_MAX_DELAY}s"
}

