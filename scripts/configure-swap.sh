#!/bin/bash
# Configure Swap Space Script
# Adds 2-4GB swap space for safety margin

set -e

SWAP_SIZE_GB=${1:-3}  # Default 3GB, can be overridden
SWAP_FILE="/swapfile"
SWAPPINESS=10  # Low swappiness for server

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if swap already exists
check_existing_swap() {
    if swapon --show | grep -q "$SWAP_FILE"; then
        log_warn "Swap file $SWAP_FILE already exists and is active"
        return 0
    fi
    
    if [ -f "$SWAP_FILE" ]; then
        log_warn "Swap file $SWAP_FILE exists but is not active"
        return 1
    fi
    
    return 2
}

# Create swap file
create_swap_file() {
    log_info "Creating swap file of ${SWAP_SIZE_GB}GB..."
    
    # Calculate size in MB
    SWAP_SIZE_MB=$((SWAP_SIZE_GB * 1024))
    
    # Check available disk space
    available_space=$(df -m / | tail -1 | awk '{print $4}')
    required_space=$((SWAP_SIZE_MB + 100))  # Add 100MB buffer
    
    if [ "$available_space" -lt "$required_space" ]; then
        log_error "Not enough disk space. Available: ${available_space}MB, Required: ${required_space}MB"
        exit 1
    fi
    
    # Create swap file using fallocate (faster) or dd (fallback)
    if command -v fallocate &> /dev/null; then
        log_info "Using fallocate to create swap file..."
        fallocate -l "${SWAP_SIZE_GB}G" "$SWAP_FILE"
    else
        log_info "Using dd to create swap file (this may take a while)..."
        dd if=/dev/zero of="$SWAP_FILE" bs=1M count="$SWAP_SIZE_MB" status=progress
    fi
    
    # Set correct permissions
    chmod 600 "$SWAP_FILE"
    
    # Make it a swap file
    log_info "Formatting swap file..."
    mkswap "$SWAP_FILE"
    
    log_success "Swap file created successfully"
}

# Enable swap
enable_swap() {
    log_info "Enabling swap file..."
    swapon "$SWAP_FILE"
    
    if swapon --show | grep -q "$SWAP_FILE"; then
        log_success "Swap file enabled successfully"
        
        # Show swap status
        log_info "Current swap status:"
        swapon --show
        free -h
    else
        log_error "Failed to enable swap file"
        exit 1
    fi
}

# Configure swappiness
configure_swappiness() {
    log_info "Configuring swappiness to $SWAPPINESS..."
    
    # Set current swappiness
    sysctl vm.swappiness="$SWAPPINESS"
    
    # Make it persistent
    if ! grep -q "vm.swappiness" /etc/sysctl.conf; then
        echo "" >> /etc/sysctl.conf
        echo "# Swap configuration" >> /etc/sysctl.conf
        echo "vm.swappiness=$SWAPPINESS" >> /etc/sysctl.conf
        log_success "Swappiness configured persistently"
    else
        log_info "Swappiness already configured in /etc/sysctl.conf"
    fi
}

# Make swap persistent
make_persistent() {
    log_info "Making swap persistent across reboots..."
    
    # Check if already in fstab
    if grep -q "$SWAP_FILE" /etc/fstab; then
        log_warn "Swap file already in /etc/fstab"
    else
        echo "$SWAP_FILE none swap sw 0 0" >> /etc/fstab
        log_success "Swap file added to /etc/fstab"
    fi
}

# Main execution
main() {
    log_info "=== Swap Configuration Script ==="
    log_info "Target swap size: ${SWAP_SIZE_GB}GB"
    log_info "Target swappiness: $SWAPPINESS"
    echo ""
    
    # Check existing swap
    check_existing_swap
    status=$?
    
    if [ $status -eq 0 ]; then
        log_info "Swap is already active. Current status:"
        swapon --show
        free -h
        exit 0
    elif [ $status -eq 1 ]; then
        log_info "Swap file exists but is not active. Enabling..."
        enable_swap
    else
        # Create and enable swap
        create_swap_file
        enable_swap
    fi
    
    # Configure swappiness
    configure_swappiness
    
    # Make persistent
    make_persistent
    
    log_success "=== Swap Configuration Complete ==="
    log_info "Summary:"
    echo "  - Swap file: $SWAP_FILE"
    echo "  - Size: ${SWAP_SIZE_GB}GB"
    echo "  - Swappiness: $SWAPPINESS"
    echo ""
    log_info "Current memory and swap status:"
    free -h
}

# Run main function
main
