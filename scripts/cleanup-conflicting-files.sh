#!/bin/bash

# Script to clean up conflicting or confusing files
# Usage: ./scripts/cleanup-conflicting-files.sh

set -e

echo "=========================================="
echo "Cleanup Conflicting Files"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

CLIENT_APP_DIR="/root/forexxx/client-app"

# Files/directories that might cause confusion
CONFLICTING_PATTERNS=(
    # Old build artifacts
    "$CLIENT_APP_DIR/dist-old"
    "$CLIENT_APP_DIR/.vite"
    "$CLIENT_APP_DIR/node_modules/.vite"
    
    # Backup files
    "$CLIENT_APP_DIR/*.bak"
    "$CLIENT_APP_DIR/*.backup"
    "$CLIENT_APP_DIR/*~"
    
    # Temporary files
    "$CLIENT_APP_DIR/.tmp"
    "$CLIENT_APP_DIR/tmp"
    
    # IDE files that might cause issues
    "$CLIENT_APP_DIR/.idea"
    "$CLIENT_APP_DIR/.vscode/settings.json.bak"
)

echo -e "${YELLOW}Cleaning up conflicting files...${NC}"

for pattern in "${CONFLICTING_PATTERNS[@]}"; do
    if [ -e "$pattern" ] || [ -d "$pattern" ] 2>/dev/null; then
        echo -e "${YELLOW}Removing: $pattern${NC}"
        rm -rf "$pattern" 2>/dev/null && echo -e "${GREEN}✓ Removed${NC}" || echo -e "${YELLOW}⚠ Not found${NC}"
    fi
done

# Check for duplicate route definitions
echo -e "\n${YELLOW}Checking for duplicate routes...${NC}"
ROUTER_FILE="$CLIENT_APP_DIR/src/router/index.js"
if [ -f "$ROUTER_FILE" ]; then
    DUPLICATES=$(grep -n "path:" "$ROUTER_FILE" | sort | uniq -d)
    if [ -z "$DUPLICATES" ]; then
        echo -e "${GREEN}✓ No duplicate routes found${NC}"
    else
        echo -e "${RED}✗ Found duplicate routes:${NC}"
        echo "$DUPLICATES"
    fi
fi

# Check for unused imports
echo -e "\n${YELLOW}Checking for potential issues...${NC}"

# Check if all required components are imported
REQUIRED_COMPONENTS=(
    "EducationView"
    "AnalysisView"
    "HelpCenterView"
    "ContactView"
    "FAQView"
    "TermsOfServiceView"
    "PrivacyPolicyView"
    "RiskWarningView"
    "ComplaintsView"
)

for component in "${REQUIRED_COMPONENTS[@]}"; do
    if grep -q "$component" "$ROUTER_FILE" 2>/dev/null; then
        echo -e "${GREEN}✓ $component is registered${NC}"
    else
        echo -e "${RED}✗ $component is missing${NC}"
    fi
done

echo -e "\n${GREEN}Cleanup Complete!${NC}"

