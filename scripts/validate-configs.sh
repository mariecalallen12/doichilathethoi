#!/bin/bash
# Script validate và chuẩn hóa configurations

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Validating configurations...${NC}"

# Validate .env.example exists
if [ ! -f "$PROJECT_ROOT/env.example" ]; then
    echo -e "${RED}Error: env.example not found${NC}"
    exit 1
fi

# Validate docker-compose files
for file in docker-compose.yml docker-compose.staging.yml docker-compose.prod.yml; do
    if [ ! -f "$PROJECT_ROOT/$file" ]; then
        echo -e "${RED}Error: $file not found${NC}"
        exit 1
    fi
    
    # Validate YAML syntax
    if command -v docker-compose &> /dev/null; then
        docker-compose -f "$PROJECT_ROOT/$file" config > /dev/null 2>&1
        if [ $? -ne 0 ]; then
            echo -e "${RED}Error: Invalid YAML in $file${NC}"
            exit 1
        fi
    fi
done

echo -e "${GREEN}✅ All configurations validated${NC}"

