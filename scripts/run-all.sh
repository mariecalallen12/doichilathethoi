#!/bin/bash
# Master Run Script
# Digital Utopia Platform - Chạy toàn bộ quy trình build và deploy
#
# Script này chạy toàn bộ quy trình:
# 1. Smart Build - Build tất cả services với error handling
# 2. Smart Deploy - Deploy tất cả services với health checks
# 3. Status Monitor - Monitor service status (optional)
# 4. Log Monitor - Monitor logs real-time (optional)

set -e

# Source libraries
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/error-handler.sh"
source "$SCRIPT_DIR/config/build-config.sh"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Global tracking
TOTAL_START_TIME=$(date +%s)
BUILD_SUCCESS=false
DEPLOY_SUCCESS=false
MONITORING_ENABLED=false

# Initialize
init_error_log

# Print banner
print_banner() {
    echo ""
    echo "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo "${CYAN}║                                                              ║${NC}"
    echo "${CYAN}║     Digital Utopia Platform - Master Run Script             ║${NC}"
    echo "${CYAN}║     Chạy toàn bộ quy trình Build & Deploy                   ║${NC}"
    echo "${CYAN}║                                                              ║${NC}"
    echo "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Print section header
print_section() {
    local title="$1"
    echo ""
    echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo "${BLUE}  $title${NC}"
    echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# Print step
print_step() {
    local step="$1"
    local description="$2"
    echo "${YELLOW}[Step $step]${NC} $description"
}

# Check prerequisites
check_prerequisites() {
    print_section "Pre-flight Checks"
    
    local all_ok=true
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo "${RED}❌ Docker is not installed${NC}"
        all_ok=false
    else
        echo "${GREEN}✅ Docker: $(docker --version | cut -d' ' -f3 | cut -d',' -f1)${NC}"
    fi
    
    # Check docker-compose
    if ! command -v docker-compose &> /dev/null; then
        echo "${RED}❌ docker-compose is not installed${NC}"
        all_ok=false
    else
        echo "${GREEN}✅ docker-compose: $(docker-compose --version | cut -d' ' -f3 | cut -d',' -f1)${NC}"
    fi
    
    # Check .env file
    if [ ! -f "$SCRIPT_DIR/../.env" ]; then
        if [ -f "$SCRIPT_DIR/../.env.example" ]; then
            echo "${YELLOW}⚠️  .env file not found. Creating from template...${NC}"
            cp "$SCRIPT_DIR/../.env.example" "$SCRIPT_DIR/../.env"
            echo "${GREEN}✅ Created .env from .env.example${NC}"
            echo "${YELLOW}⚠️  Please edit .env file with your actual configuration!${NC}"
            read -p "Press Enter to continue or Ctrl+C to cancel..."
        else
            echo "${RED}❌ .env file not found and no .env.example available${NC}"
            all_ok=false
        fi
    else
        echo "${GREEN}✅ .env file: exists${NC}"
    fi
    
    # Check disk space
    local available_space=$(df -BG "$SCRIPT_DIR/.." | tail -1 | awk '{print $4}' | sed 's/G//')
    if [ "$available_space" -lt "$MIN_DISK_SPACE_GB" ]; then
        echo "${YELLOW}⚠️  Low disk space: ${available_space}GB available (minimum: ${MIN_DISK_SPACE_GB}GB)${NC}"
    else
        echo "${GREEN}✅ Disk space: ${available_space}GB available${NC}"
    fi
    
    if [ "$all_ok" = false ]; then
        echo ""
        echo "${RED}❌ Prerequisites check failed. Please fix the issues above.${NC}"
        exit 1
    fi
    
    echo ""
    echo "${GREEN}✅ All prerequisites check passed${NC}"
}

# Run smart build
run_build() {
    print_section "Phase 1: Smart Build"
    print_step "1.1" "Running smart-build.sh..."
    
    local build_start=$(date +%s)
    
    if "$SCRIPT_DIR/smart-build.sh"; then
        BUILD_SUCCESS=true
        local build_end=$(date +%s)
        local build_duration=$((build_end - build_start))
        echo ""
        echo "${GREEN}✅ Build completed successfully in ${build_duration}s${NC}"
        return 0
    else
        BUILD_SUCCESS=false
        local build_end=$(date +%s)
        local build_duration=$((build_end - build_start))
        echo ""
        echo "${RED}❌ Build failed after ${build_duration}s${NC}"
        return 1
    fi
}

# Run smart deploy
run_deploy() {
    print_section "Phase 2: Smart Deploy"
    print_step "2.1" "Running smart-deploy.sh..."
    
    local deploy_start=$(date +%s)
    
    if "$SCRIPT_DIR/smart-deploy.sh"; then
        DEPLOY_SUCCESS=true
        local deploy_end=$(date +%s)
        local deploy_duration=$((deploy_end - deploy_start))
        echo ""
        echo "${GREEN}✅ Deploy completed successfully in ${deploy_duration}s${NC}"
        return 0
    else
        DEPLOY_SUCCESS=false
        local deploy_end=$(date +%s)
        local deploy_duration=$((deploy_end - deploy_start))
        echo ""
        echo "${RED}❌ Deploy failed after ${deploy_duration}s${NC}"
        return 1
    fi
}

# Start monitoring (optional)
start_monitoring() {
    if [ "$MONITORING_ENABLED" = true ]; then
        print_section "Phase 3: Monitoring"
        print_step "3.1" "Starting status monitor in background..."
        
        # Start status monitor in background
        "$SCRIPT_DIR/status-monitor.sh" monitor > /tmp/status_monitor.log 2>&1 &
        local status_monitor_pid=$!
        echo "$status_monitor_pid" > /tmp/status_monitor.pid
        echo "${GREEN}✅ Status monitor started (PID: $status_monitor_pid)${NC}"
        
        print_step "3.2" "Starting log monitor in background..."
        
        # Start log monitor in background
        "$SCRIPT_DIR/monitor-logs.sh" > /tmp/log_monitor.log 2>&1 &
        local log_monitor_pid=$!
        echo "$log_monitor_pid" > /tmp/log_monitor.pid
        echo "${GREEN}✅ Log monitor started (PID: $log_monitor_pid)${NC}"
        
        echo ""
        echo "${CYAN}📊 Monitoring is running in background${NC}"
        echo "${CYAN}   Status monitor log: /tmp/status_monitor.log${NC}"
        echo "${CYAN}   Log monitor log: /tmp/log_monitor.log${NC}"
        echo "${CYAN}   To stop monitoring: kill \$(cat /tmp/status_monitor.pid) \$(cat /tmp/log_monitor.pid)${NC}"
    fi
}

# Stop monitoring
stop_monitoring() {
    if [ -f /tmp/status_monitor.pid ]; then
        local pid=$(cat /tmp/status_monitor.pid)
        kill "$pid" 2>/dev/null || true
        rm -f /tmp/status_monitor.pid
    fi
    
    if [ -f /tmp/log_monitor.pid ]; then
        local pid=$(cat /tmp/log_monitor.pid)
        kill "$pid" 2>/dev/null || true
        rm -f /tmp/log_monitor.pid
    fi
}

# Print final summary
print_summary() {
    local total_end=$(date +%s)
    local total_duration=$((total_end - TOTAL_START_TIME))
    
    print_section "Final Summary"
    
    echo "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo "${CYAN}  Execution Summary${NC}"
    echo "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Total execution time: ${total_duration}s"
    echo ""
    echo "Build Status:"
    if [ "$BUILD_SUCCESS" = true ]; then
        echo "  ${GREEN}✅ Build: SUCCESS${NC}"
    else
        echo "  ${RED}❌ Build: FAILED${NC}"
    fi
    
    echo ""
    echo "Deploy Status:"
    if [ "$DEPLOY_SUCCESS" = true ]; then
        echo "  ${GREEN}✅ Deploy: SUCCESS${NC}"
    else
        echo "  ${RED}❌ Deploy: FAILED${NC}"
    fi
    
    echo ""
    echo "Overall Status:"
    if [ "$BUILD_SUCCESS" = true ] && [ "$DEPLOY_SUCCESS" = true ]; then
        echo "  ${GREEN}✅ Overall: SUCCESS${NC}"
        echo ""
        echo "${GREEN}🎉 All services are built and deployed successfully!${NC}"
        echo ""
        
        # Show access URLs
        if [ -f "$SCRIPT_DIR/../.env" ]; then
            source "$SCRIPT_DIR/../.env"
            echo "${CYAN}🌐 Access URLs:${NC}"
            echo "   Backend API:    http://localhost:${BACKEND_PORT:-8000}"
            echo "   API Docs:       http://localhost:${BACKEND_PORT:-8000}/docs"
            echo "   Client App:     http://localhost:${CLIENT_PORT:-3002}"
            echo "   Admin App:      http://localhost:${ADMIN_PORT:-3001}"
            echo ""
        fi
    else
        echo "  ${RED}❌ Overall: FAILED${NC}"
        echo ""
        echo "${RED}⚠️  Some steps failed. Please check the logs above.${NC}"
        echo ""
        echo "${YELLOW}Error log: /tmp/build_errors.log${NC}"
        echo "${YELLOW}To retry: ./scripts/run-all.sh${NC}"
    fi
    
    echo ""
    echo "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    
    # Error summary
    if [ -f /tmp/build_errors.log ] && [ -s /tmp/build_errors.log ]; then
        echo ""
        echo "${YELLOW}Recent Errors:${NC}"
        tail -5 /tmp/build_errors.log | sed 's/^/  /'
    fi
    
    echo ""
}

# Cleanup function
cleanup() {
    echo ""
    echo "${YELLOW}🛑 Cleaning up...${NC}"
    stop_monitoring
    exit 0
}

trap cleanup SIGINT SIGTERM

# Main function
main() {
    local monitor_flag=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --monitor|-m)
                monitor_flag=true
                shift
                ;;
            --help|-h)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --monitor, -m    Enable monitoring after deploy"
                echo "  --help, -h       Show this help message"
                echo ""
                echo "This script runs the complete build and deploy process:"
                echo "  1. Smart Build - Build all services"
                echo "  2. Smart Deploy - Deploy all services"
                echo "  3. Monitoring (optional) - Monitor status and logs"
                exit 0
                ;;
            *)
                echo "${RED}Unknown option: $1${NC}"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    # Set monitoring flag
    MONITORING_ENABLED=$monitor_flag
    
    # Print banner
    print_banner
    
    # Check prerequisites
    check_prerequisites
    
    # Run build
    if ! run_build; then
        echo ""
        echo "${RED}❌ Build phase failed. Stopping execution.${NC}"
        print_summary
        exit 1
    fi
    
    # Run deploy
    if ! run_deploy; then
        echo ""
        echo "${RED}❌ Deploy phase failed.${NC}"
        print_summary
        exit 1
    fi
    
    # Start monitoring if enabled
    if [ "$MONITORING_ENABLED" = true ]; then
        start_monitoring
    fi
    
    # Print summary
    print_summary
    
    # Exit with appropriate code
    if [ "$BUILD_SUCCESS" = true ] && [ "$DEPLOY_SUCCESS" = true ]; then
        exit 0
    else
        exit 1
    fi
}

# Run if executed directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi

