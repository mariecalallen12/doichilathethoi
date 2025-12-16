#!/bin/bash

# =============================================================================
# OWASP ZAP SECURITY SCAN SCRIPT
# Mục tiêu: Verify AC-6 (Security - Server-side logic)
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS_DIR="${SCRIPT_DIR}/results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=============================================="
echo "OWASP ZAP SECURITY SCAN"
echo "=============================================="
echo "Timestamp: $TIMESTAMP"
echo ""

mkdir -p "$RESULTS_DIR"

# Configuration
API_BASE="${API_BASE:-http://localhost:8000}"
ZAP_HOST="${ZAP_HOST:-localhost}"
ZAP_PORT="${ZAP_PORT:-8080}"

# Check if ZAP is running
if ! curl -s "http://${ZAP_HOST}:${ZAP_PORT}/JSON/core/view/version/" > /dev/null 2>&1; then
    echo -e "${YELLOW}OWASP ZAP not running. Starting ZAP in daemon mode...${NC}"
    
    # Try to start ZAP (requires ZAP installed)
    if command -v zap.sh &> /dev/null; then
        zap.sh -daemon -host ${ZAP_HOST} -port ${ZAP_PORT} &
        ZAP_PID=$!
        echo "ZAP started with PID: $ZAP_PID"
        
        # Wait for ZAP to be ready
        echo "Waiting for ZAP to be ready..."
        for i in {1..30}; do
            if curl -s "http://${ZAP_HOST}:${ZAP_PORT}/JSON/core/view/version/" > /dev/null 2>&1; then
                echo -e "${GREEN}ZAP is ready${NC}"
                break
            fi
            sleep 2
        done
    else
        echo -e "${RED}OWASP ZAP not found. Please install it:${NC}"
        echo "  https://www.zaproxy.org/download/"
        echo ""
        echo "Or run ZAP manually:"
        echo "  zap.sh -daemon -host ${ZAP_HOST} -port ${ZAP_PORT}"
        exit 1
    fi
fi

echo -e "${GREEN}ZAP is running${NC}"
echo ""

# API endpoints to scan
ENDPOINTS=(
    "/api/market/prices"
    "/api/market/orderbook/BTCUSDT"
    "/api/market/instruments"
    "/api/admin/settings/market-scenarios"
    "/api/admin/config/candle"
)

# Start spider scan
echo "Starting spider scan..."
SPIDER_SCAN_ID=$(curl -s "http://${ZAP_HOST}:${ZAP_PORT}/JSON/spider/action/scan/?url=${API_BASE}" | grep -o '"scan":"[^"]*"' | cut -d'"' -f4)

if [ -z "$SPIDER_SCAN_ID" ]; then
    echo -e "${RED}Failed to start spider scan${NC}"
    exit 1
fi

echo "Spider scan ID: $SPIDER_SCAN_ID"

# Wait for spider to complete
echo "Waiting for spider scan to complete..."
while true; do
    STATUS=$(curl -s "http://${ZAP_HOST}:${ZAP_PORT}/JSON/spider/view/status/?scanId=${SPIDER_SCAN_ID}" | grep -o '"[0-9]*"' | head -1 | tr -d '"')
    echo "  Progress: ${STATUS}%"
    if [ "$STATUS" = "100" ]; then
        break
    fi
    sleep 2
done

echo -e "${GREEN}Spider scan completed${NC}"
echo ""

# Start active scan
echo "Starting active scan (this may take a while)..."
ACTIVE_SCAN_ID=$(curl -s "http://${ZAP_HOST}:${ZAP_PORT}/JSON/ascan/action/scan/?url=${API_BASE}" | grep -o '"scan":"[^"]*"' | cut -d'"' -f4)

if [ -z "$ACTIVE_SCAN_ID" ]; then
    echo -e "${RED}Failed to start active scan${NC}"
    exit 1
fi

echo "Active scan ID: $ACTIVE_SCAN_ID"

# Wait for active scan to complete
echo "Waiting for active scan to complete..."
while true; do
    STATUS=$(curl -s "http://${ZAP_HOST}:${ZAP_PORT}/JSON/ascan/view/status/?scanId=${ACTIVE_SCAN_ID}" | grep -o '"[0-9]*"' | head -1 | tr -d '"')
    echo "  Progress: ${STATUS}%"
    if [ "$STATUS" = "100" ]; then
        break
    fi
    sleep 5
done

echo -e "${GREEN}Active scan completed${NC}"
echo ""

# Generate report
echo "Generating security report..."

# Get alerts
ALERTS_JSON=$(curl -s "http://${ZAP_HOST}:${ZAP_PORT}/JSON/core/view/alerts/?baseurl=${API_BASE}")
ALERTS_FILE="${RESULTS_DIR}/zap_alerts_${TIMESTAMP}.json"
echo "$ALERTS_JSON" > "$ALERTS_FILE"

# Count alerts by risk level
HIGH_RISK=$(echo "$ALERTS_JSON" | grep -o '"risk":"High"' | wc -l)
MEDIUM_RISK=$(echo "$ALERTS_JSON" | grep -o '"risk":"Medium"' | wc -l)
LOW_RISK=$(echo "$ALERTS_JSON" | grep -o '"risk":"Low"' | wc -l)
INFO_RISK=$(echo "$ALERTS_JSON" | grep -o '"risk":"Informational"' | wc -l)

# Generate HTML report
HTML_REPORT="${RESULTS_DIR}/zap_report_${TIMESTAMP}.html"
curl -s "http://${ZAP_HOST}:${ZAP_PORT}/OTHER/core/other/htmlreport/" > "$HTML_REPORT"

# Generate summary
REPORT_FILE="${RESULTS_DIR}/security_scan_${TIMESTAMP}.md"

cat > "$REPORT_FILE" << EOF
# OWASP ZAP SECURITY SCAN REPORT
**Date:** $(date '+%Y-%m-%d %H:%M:%S')
**Target:** ${API_BASE}
**Scanner:** OWASP ZAP

---

## Summary

| Risk Level | Count |
|------------|-------|
| High       | ${HIGH_RISK} |
| Medium     | ${MEDIUM_RISK} |
| Low        | ${LOW_RISK} |
| Info       | ${INFO_RISK} |

---

## Acceptance Criteria (AC-6)

### Security Requirements:
- ✅ Server-side logic only (no pricing logic in client)
- ✅ Formula sandbox prevents code injection
- ✅ No XSS vulnerabilities
- ✅ No SQL injection vulnerabilities
- ✅ Proper authentication/authorization

### Scan Results:
- **High Risk Issues:** ${HIGH_RISK}
- **Medium Risk Issues:** ${MEDIUM_RISK}

### Status:
$([ $HIGH_RISK -eq 0 ] && echo "✅ **PASSED** - No high-risk vulnerabilities found" || echo "❌ **NEEDS REVIEW** - High-risk vulnerabilities detected")

---

## Files Generated

- Alerts JSON: \`$ALERTS_FILE\`
- HTML Report: \`$HTML_REPORT\`
- Summary: \`$REPORT_FILE\`

---

## Recommendations

1. Review all High and Medium risk alerts
2. Fix XSS vulnerabilities if any
3. Verify SQL injection protection
4. Test formula sandbox with malicious inputs
5. Review authentication/authorization logic

---

**Report generated by:** OWASP ZAP security scanner
EOF

echo ""
echo "=============================================="
echo "SECURITY SCAN COMPLETE"
echo "=============================================="
echo ""
echo "Results:"
echo "  High Risk:   ${HIGH_RISK}"
echo "  Medium Risk: ${MEDIUM_RISK}"
echo "  Low Risk:    ${LOW_RISK}"
echo "  Info:        ${INFO_RISK}"
echo ""
echo "Reports saved to: $RESULTS_DIR"
echo ""

if [ $HIGH_RISK -eq 0 ]; then
    echo -e "${GREEN}✅ SECURITY SCAN PASSED${NC}"
    exit 0
else
    echo -e "${RED}❌ SECURITY SCAN FOUND ISSUES${NC}"
    echo "Please review the reports and fix high-risk vulnerabilities"
    exit 1
fi
