#!/bin/bash

# k6 Installation Script
# Install k6 using official method

set -e

echo "=========================================="
echo "k6 Installation Script"
echo "=========================================="
echo ""

# Check if k6 is already installed
if command -v k6 &> /dev/null; then
    echo "✅ k6 is already installed"
    k6 version
    exit 0
fi

echo "Installing k6..."
echo ""

# Method 1: Using official repository (Linux)
if [ -f /etc/debian_version ]; then
    echo "Detected Debian/Ubuntu system"
    echo ""
    
    # Add GPG key
    sudo gpg -k
    sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
    
    # Add repository
    echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
    
    # Update and install
    sudo apt-get update
    sudo apt-get install -y k6
    
    echo ""
    echo "✅ k6 installed successfully"
    k6 version
    
elif [ -f /etc/redhat-release ]; then
    echo "Detected RedHat/CentOS system"
    echo ""
    echo "Please install k6 manually:"
    echo "  https://k6.io/docs/getting-started/installation/"
    exit 1
    
else
    echo "Unknown Linux distribution"
    echo "Please install k6 manually:"
    echo "  https://k6.io/docs/getting-started/installation/"
    exit 1
fi

echo ""
echo "=========================================="
echo "k6 Installation Complete"
echo "=========================================="
echo ""
echo "Alternative: Use Docker"
echo "  docker run --rm -i grafana/k6 run - <tests/load/websocket_test.js"
echo ""

