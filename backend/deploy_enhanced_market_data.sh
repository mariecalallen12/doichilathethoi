#!/bin/bash
# =============================================================================
# CMEETRADING Deployment Script
# Twelve Data + Self-Calculate Integration
# =============================================================================

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "\n${BLUE}======================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}======================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Check if running from correct directory
if [ ! -f "main.py" ]; then
    print_error "Please run this script from the backend directory"
    exit 1
fi

print_header "CMEETRADING Deployment - Enhanced Market Data"

# Step 1: Check Python version
print_info "Checking Python version..."
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    print_error "Python $REQUIRED_VERSION or higher required (found $PYTHON_VERSION)"
    exit 1
fi
print_success "Python $PYTHON_VERSION"

# Step 2: Install dependencies
print_header "Step 1: Installing Dependencies"
pip install -r requirements.txt --quiet
print_success "Dependencies installed"

# Step 3: Check .env file
print_header "Step 2: Environment Configuration"
if [ ! -f ".env" ]; then
    print_info "Creating .env from .env.example..."
    cp .env.example .env
    print_info "Please edit .env file with your configuration"
    print_info "Optional: Add TWELVEDATA_API_KEY for instant Forex 24h change"
    
    read -p "Press Enter to continue after editing .env..."
fi
print_success "Environment configured"

# Step 4: Database migrations
print_header "Step 3: Database Migrations"
print_info "Running Alembic migrations..."

# Check if alembic is initialized
if [ ! -d "alembic" ]; then
    print_error "Alembic not initialized"
    exit 1
fi

# Run migrations
alembic upgrade head

if [ $? -eq 0 ]; then
    print_success "Migrations completed successfully"
else
    print_error "Migration failed"
    exit 1
fi

# Verify new tables
print_info "Verifying new tables..."
python3 << 'PYEOF'
from app.db.session import SessionLocal
from app.models.customization import ForexHistory, MetalHistory
db = SessionLocal()
try:
    forex_count = db.query(ForexHistory).count()
    metal_count = db.query(MetalHistory).count()
    print(f"✅ forex_history table: {forex_count} records")
    print(f"✅ metal_history table: {metal_count} records")
except Exception as e:
    print(f"⚠️  Error verifying tables: {e}")
finally:
    db.close()
PYEOF

# Step 5: Check Twelve Data API (optional)
print_header "Step 4: API Keys Check"

if [ -f ".env" ]; then
    source .env
    if [ -z "$TWELVEDATA_API_KEY" ]; then
        print_info "TWELVEDATA_API_KEY not set"
        print_info "Forex 24h change will use self-calculated method"
        print_info "To get instant Forex data:"
        echo "  1. Sign up at https://twelvedata.com/"
        echo "  2. Get free API key (800 req/day)"
        echo "  3. Add to .env: TWELVEDATA_API_KEY=your_key"
    else
        print_success "Twelve Data API key configured"
        
        # Test API key
        print_info "Testing Twelve Data API..."
        python3 << PYEOF
import asyncio
import aiohttp

async def test_api():
    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": "EUR/USD",
        "interval": "1day",
        "outputsize": 1,
        "apikey": "$TWELVEDATA_API_KEY"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                data = await resp.json()
                if "status" in data and data["status"] == "error":
                    print(f"⚠️  API Error: {data.get('message')}")
                    return False
                elif "values" in data:
                    print("✅ Twelve Data API working")
                    return True
                else:
                    print("⚠️  Unexpected response")
                    return False
    except Exception as e:
        print(f"⚠️  API test failed: {e}")
        return False

result = asyncio.run(test_api())
exit(0 if result else 1)
PYEOF
        
        if [ $? -eq 0 ]; then
            print_success "API key validated"
        else
            print_info "API key may be invalid, but deployment will continue"
        fi
    fi
fi

# Step 6: Initialize market data collector
print_header "Step 5: Market Data Collector"
print_info "The collector will start automatically when you run the server"
print_info "It will collect forex and metal prices every hour"
print_info "After 24 hours, self-calculated 24h change will be available"

# Step 7: Create startup script
print_header "Step 6: Creating Startup Scripts"

cat > start.sh << 'STARTEOF'
#!/bin/bash
# Start CMEETRADING Backend

echo "🚀 Starting CMEETRADING Backend..."

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

STARTEOF

chmod +x start.sh
print_success "Created start.sh"

cat > start_production.sh << 'PRODEOF'
#!/bin/bash
# Start CMEETRADING Backend (Production)

echo "🚀 Starting CMEETRADING Backend (Production)..."

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start with gunicorn (production)
gunicorn main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --log-level info

PRODEOF

chmod +x start_production.sh
print_success "Created start_production.sh"

# Step 8: Test configuration
print_header "Step 7: Testing Configuration"
print_info "Running configuration tests..."

python3 << 'TESTEOF'
import sys
import os

print("Testing imports...")
try:
    from app.services.market_data_enhanced import EnhancedMarketDataAggregator, TwelveDataProvider
    print("✅ Enhanced market data provider")
    
    from app.tasks.market_data_collector import MarketDataCollector
    print("✅ Market data collector")
    
    from app.models.customization import ForexHistory, MetalHistory
    print("✅ History models")
    
    from app.services.customization_engine import customization_engine
    print("✅ Customization engine")
    
    print("\n✅ All imports successful")
    sys.exit(0)
    
except ImportError as e:
    print(f"\n❌ Import error: {e}")
    sys.exit(1)
TESTEOF

if [ $? -ne 0 ]; then
    print_error "Configuration test failed"
    exit 1
fi

# Step 9: Summary
print_header "Deployment Summary"

echo -e "${GREEN}✅ Deployment completed successfully!${NC}\n"

echo "📊 System Status:"
echo "  - Database: Migrated"
echo "  - Models: Imported"
echo "  - Market Data Collector: Ready"
echo "  - Customization Engine: Ready"

if [ -n "$TWELVEDATA_API_KEY" ]; then
    echo "  - Twelve Data API: Configured ✅"
else
    echo "  - Twelve Data API: Not configured (using self-calculate)"
fi

echo ""
echo "🚀 Next Steps:"
echo ""
echo "1. Start the server:"
echo "   Development:  ./start.sh"
echo "   Production:   ./start_production.sh"
echo ""
echo "2. Access the API:"
echo "   http://localhost:8000/docs"
echo ""
echo "3. Test market data:"
echo "   curl http://localhost:8000/api/market/prices?symbol=BTC"
echo "   curl http://localhost:8000/api/market/prices?symbol=EUR/USD"
echo ""
echo "4. Monitor collector logs:"
echo "   tail -f logs/app.log | grep 'Market data collection'"
echo ""
echo "📝 Important Notes:"
echo ""
echo "  - Crypto (BTC, ETH...): Real 24h change available immediately ✅"
echo "  - Forex (EUR/USD...): "
if [ -n "$TWELVEDATA_API_KEY" ]; then
    echo "    → Real 24h change available immediately (Twelve Data) ✅"
else
    echo "    → Real 24h change available after 24 hours (self-calculated) ⏳"
fi
echo "  - Metals (Gold, Silver): Real 24h change after 24 hours (self-calculated) ⏳"
echo ""
echo "  - Background collector runs every hour automatically"
echo "  - Historical data is kept for 30 days"
echo "  - Customization engine is active (use X-Session-Id header)"
echo ""

print_success "Deployment complete! 🎉"
