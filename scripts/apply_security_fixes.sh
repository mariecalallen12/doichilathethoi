#!/bin/bash

# ============================================
# Security Fixes Application Script
# ============================================
# This script applies critical security fixes
# identified in SECURITY_AUDIT_REPORT_20251210.md
# ============================================

set -e  # Exit on error

echo "=========================================="
echo "CMEETRADING - Security Fixes Application"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_info() {
    echo "[INFO] $1"
}

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then 
    print_error "Please run with sudo or as root"
    exit 1
fi

# Navigate to project directory
cd /root/forexxx || {
    print_error "Project directory not found"
    exit 1
}

print_info "Current directory: $(pwd)"
echo ""

# ============================================
# Step 1: Backup Current Configuration
# ============================================

print_info "Step 1: Backing up current configuration..."

BACKUP_DIR="/root/backups/security_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

if [ -f .env ]; then
    cp .env "$BACKUP_DIR/.env.backup"
    print_success "Backed up .env to $BACKUP_DIR"
else
    print_warning ".env file not found"
fi

if [ -f docker-compose.yml ]; then
    cp docker-compose.yml "$BACKUP_DIR/docker-compose.yml.backup"
    print_success "Backed up docker-compose.yml"
fi

echo ""

# ============================================
# Step 2: Generate Strong Secrets
# ============================================

print_info "Step 2: Generating strong secrets..."

NEW_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(64))")
NEW_POSTGRES_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
NEW_REDIS_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

print_success "Generated SECRET_KEY (64 bytes)"
print_success "Generated POSTGRES_PASSWORD (32 bytes)"
print_success "Generated REDIS_PASSWORD (32 bytes)"

echo ""

# ============================================
# Step 3: Save Secrets to Secure File
# ============================================

print_info "Step 3: Saving secrets to secure file..."

SECRETS_FILE="$BACKUP_DIR/secrets.txt"
cat > "$SECRETS_FILE" << EOF
============================================
PRODUCTION SECRETS
Generated: $(date)
============================================

⚠️  KEEP THIS FILE SECURE - DO NOT COMMIT TO GIT

SECRET_KEY=$NEW_SECRET_KEY

POSTGRES_PASSWORD=$NEW_POSTGRES_PASSWORD

REDIS_PASSWORD=$NEW_REDIS_PASSWORD

============================================
EOF

chmod 600 "$SECRETS_FILE"
print_success "Secrets saved to: $SECRETS_FILE"
print_warning "IMPORTANT: Save this file to a password manager!"

echo ""

# ============================================
# Step 4: Display Instructions
# ============================================

print_info "Step 4: Manual update instructions"
echo ""

echo "============================================"
echo "MANUAL STEPS REQUIRED:"
echo "============================================"
echo ""
echo "1. Update .env file with new secrets:"
echo ""
echo "   SECRET_KEY=$NEW_SECRET_KEY"
echo ""
echo "   POSTGRES_PASSWORD=$NEW_POSTGRES_PASSWORD"
echo ""
echo "   REDIS_PASSWORD=$NEW_REDIS_PASSWORD"
echo ""
echo "2. Update CORS_ORIGINS in .env (remove localhost):"
echo ""
echo "   CORS_ORIGINS=https://cmeetrading.com,https://admin.cmeetrading.com"
echo ""
echo "3. Verify DEBUG and ENVIRONMENT settings:"
echo ""
echo "   DEBUG=false"
echo "   ENVIRONMENT=production"
echo ""
echo "4. Update docker-compose.yml postgres service:"
echo ""
echo "   postgres:"
echo "     environment:"
echo "       POSTGRES_PASSWORD: $NEW_POSTGRES_PASSWORD"
echo ""
echo "5. Update docker-compose.yml redis service:"
echo ""
echo "   redis:"
echo "     command: redis-server --requirepass $NEW_REDIS_PASSWORD --appendonly yes"
echo ""
echo "============================================"
echo ""

# ============================================
# Step 5: Verification Checklist
# ============================================

print_info "Step 5: Verification checklist"
echo ""

echo "After applying changes, verify:"
echo "  [ ] .env file updated with new secrets"
echo "  [ ] docker-compose.yml updated"
echo "  [ ] CORS_ORIGINS contains only production domains"
echo "  [ ] DEBUG=false"
echo "  [ ] ENVIRONMENT=production"
echo "  [ ] Services restarted: docker-compose down && docker-compose up -d"
echo "  [ ] Health check passing: curl http://localhost:8000/api/health"
echo "  [ ] Authentication working: test login"
echo "  [ ] Database connected"
echo "  [ ] Redis connected"
echo ""

# ============================================
# Step 6: Summary
# ============================================

echo "============================================"
echo "SECURITY FIXES PREPARATION COMPLETE"
echo "============================================"
echo ""
print_success "Backup location: $BACKUP_DIR"
print_success "Secrets file: $SECRETS_FILE"
print_warning "Apply manual steps above to complete security fixes"
echo ""
echo "After applying fixes, run:"
echo "  ./scripts/verify_security_fixes.sh"
echo ""
echo "============================================"
