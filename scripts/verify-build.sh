#!/bin/bash

# Build Verification Script
# Verify that the build was successful and all assets are present
#
# Usage:
#   ./scripts/verify-build.sh [--image=<image>]

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

IMAGE_NAME="client-app:latest"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --image=*)
      IMAGE_NAME="${1#*=}"
      shift
      ;;
    *)
      echo -e "${RED}Unknown option: $1${NC}"
      exit 1
      ;;
  esac
done

log_info() {
  echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
  echo -e "${GREEN}[✓]${NC} $1"
}

log_error() {
  echo -e "${RED}[✗]${NC} $1"
}

verify_image_exists() {
  log_info "Checking if image exists..."
  if docker images | grep -q "$IMAGE_NAME"; then
    log_success "Image $IMAGE_NAME exists"
  else
    log_error "Image $IMAGE_NAME not found"
    exit 1
  fi
}

verify_image_size() {
  log_info "Checking image size..."
  local size=$(docker images "$IMAGE_NAME" --format "{{.Size}}")
  log_info "Image size: $size"
  
  # Extract numeric size
  local size_num=$(echo "$size" | sed 's/[^0-9.]//g')
  if (( $(echo "$size_num > 1000" | bc -l) )); then
    log_error "Image size is very large: $size"
  else
    log_success "Image size is acceptable"
  fi
}

verify_container_starts() {
  log_info "Testing if container starts..."
  
  local test_container="test-verify-$$"
  docker run -d --name "$test_container" -p 8080:80 "$IMAGE_NAME" > /dev/null 2>&1 || {
    log_error "Container failed to start"
    exit 1
  }
  
  sleep 3
  
  if curl -f -s http://localhost:8080/health > /dev/null 2>&1; then
    log_success "Container starts and health endpoint works"
  else
    log_error "Health endpoint not accessible"
  fi
  
  docker stop "$test_container" > /dev/null 2>&1
  docker rm "$test_container" > /dev/null 2>&1
}

verify_build_assets() {
  log_info "Verifying build assets..."
  
  local test_container="test-verify-assets-$$"
  docker run -d --name "$test_container" "$IMAGE_NAME" > /dev/null 2>&1
  
  # Check for key files
  local required_files=(
    "/usr/share/nginx/html/index.html"
    "/usr/share/nginx/html/assets"
  )
  
  for file in "${required_files[@]}"; do
    if docker exec "$test_container" test -e "$file" 2>/dev/null; then
      log_success "Required file exists: $file"
    else
      log_error "Required file missing: $file"
    fi
  done
  
  docker stop "$test_container" > /dev/null 2>&1
  docker rm "$test_container" > /dev/null 2>&1
}

main() {
  echo "=========================================="
  echo "  Build Verification"
  echo "=========================================="
  echo ""
  
  verify_image_exists
  verify_image_size
  verify_container_starts
  verify_build_assets
  
  echo ""
  echo "=========================================="
  log_success "Build verification completed!"
  echo "=========================================="
}

main "$@"

