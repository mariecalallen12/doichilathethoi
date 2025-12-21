# 🌐 API NGUỒN MỞ/MIỄN PHÍ CHO 24H CHANGE

## 🎯 MỤC TIÊU
Tìm API miễn phí để lấy **24h change** cho Forex và Metals thay thế phần mock hiện tại

---

## 💰 CÁC API MIỄN PHÍ PHỔ BIẾN

### 1️⃣ FOREX - 24H CHANGE

#### **Option A: Twelve Data API** ⭐ RECOMMENDED
**Website:** https://twelvedata.com/  
**Free Tier:** 800 requests/day  
**Endpoint:** `/time_series`

```python
# Example usage
import aiohttp

async def get_forex_change_twelvedata(pair: str):
    """Get 24h change from Twelve Data"""
    API_KEY = "YOUR_FREE_API_KEY"
    
    # Get last 2 data points (current and 24h ago)
    url = f"https://api.twelvedata.com/time_series"
    params = {
        "symbol": pair,  # e.g., "EUR/USD"
        "interval": "1day",
        "outputsize": 2,
        "apikey": API_KEY
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            data = await resp.json()
            
            if "values" in data and len(data["values"]) >= 2:
                current = float(data["values"][0]["close"])
                previous = float(data["values"][1]["close"])
                change_24h = ((current - previous) / previous) * 100
                
                return {
                    "price": current,
                    "change_24h": change_24h,
                    "source": "twelvedata"
                }
    
    return None

# Supported pairs
FOREX_PAIRS = [
    "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF",
    "AUD/USD", "USD/CAD", "NZD/USD"
]
```

**Pros:**
- ✅ Free tier: 800 requests/day
- ✅ Historical data included
- ✅ Clean API design
- ✅ Support major forex pairs

**Cons:**
- ⚠️ Need API key (free signup)
- ⚠️ Rate limited

---

#### **Option B: Alpha Vantage** 
**Website:** https://www.alphavantage.co/  
**Free Tier:** 25 requests/day (very limited)  
**Endpoint:** `/query?function=FX_DAILY`

```python
async def get_forex_change_alphavantage(from_currency: str, to_currency: str):
    """Get 24h change from Alpha Vantage"""
    API_KEY = "YOUR_FREE_API_KEY"
    
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "FX_DAILY",
        "from_symbol": from_currency,  # e.g., "EUR"
        "to_symbol": to_currency,      # e.g., "USD"
        "apikey": API_KEY
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            data = await resp.json()
            
            if "Time Series FX (Daily)" in data:
                time_series = data["Time Series FX (Daily)"]
                dates = sorted(time_series.keys(), reverse=True)
                
                if len(dates) >= 2:
                    current = float(time_series[dates[0]]["4. close"])
                    previous = float(time_series[dates[1]]["4. close"])
                    change_24h = ((current - previous) / previous) * 100
                    
                    return {
                        "price": current,
                        "change_24h": change_24h,
                        "source": "alphavantage"
                    }
    
    return None
```

**Pros:**
- ✅ Completely free
- ✅ No credit card required

**Cons:**
- ❌ Only 25 requests/day
- ❌ Too limited for production

---

#### **Option C: Self-Calculate with ExchangeRate API**
**Current API:** https://api.exchangerate-api.com/  
**Free Tier:** Unlimited  
**Strategy:** Store historical data in database

```python
from datetime import datetime, timedelta
from sqlalchemy import Column, String, Float, DateTime
from app.db.base_class import Base

class ForexHistory(Base):
    """Store forex historical data"""
    __tablename__ = "forex_history"
    
    id = Column(Integer, primary_key=True)
    pair = Column(String(10), index=True)
    price = Column(Float)
    timestamp = Column(DateTime, index=True)

async def get_forex_change_self_calculated(pair: str, db):
    """Calculate 24h change from stored data"""
    # Get current price
    current_data = await fetch_current_price(pair)
    current_price = current_data["price"]
    
    # Store current price
    history_entry = ForexHistory(
        pair=pair,
        price=current_price,
        timestamp=datetime.utcnow()
    )
    db.add(history_entry)
    await db.commit()
    
    # Get price from 24h ago
    time_24h_ago = datetime.utcnow() - timedelta(hours=24)
    
    historical = db.query(ForexHistory)\
        .filter(ForexHistory.pair == pair)\
        .filter(ForexHistory.timestamp >= time_24h_ago)\
        .order_by(ForexHistory.timestamp.asc())\
        .first()
    
    if historical:
        change_24h = ((current_price - historical.price) / historical.price) * 100
        return {
            "price": current_price,
            "change_24h": change_24h,
            "source": "self-calculated"
        }
    
    return None

# Background task to store data every hour
async def store_forex_prices_hourly():
    """Store forex prices every hour"""
    while True:
        for pair in FOREX_PAIRS:
            await get_forex_change_self_calculated(pair, db)
        
        await asyncio.sleep(3600)  # 1 hour
```

**Pros:**
- ✅ Completely free
- ✅ No rate limits
- ✅ Full control over data

**Cons:**
- ⚠️ Need database storage
- ⚠️ Need background task
- ⚠️ Delayed 24h (wait for data)

---

### 2️⃣ METALS - 24H CHANGE

#### **Option A: Metals-API** ⭐ RECOMMENDED
**Website:** https://metals-api.com/  
**Free Tier:** 50 requests/month  
**Endpoint:** `/latest` + calculate

```python
async def get_metal_change_metalsapi(symbol: str):
    """Get 24h change for metals"""
    API_KEY = "YOUR_FREE_API_KEY"
    
    # Get current price
    url = f"https://metals-api.com/api/latest"
    params = {
        "access_key": API_KEY,
        "base": "USD",
        "symbols": symbol  # e.g., "XAU" for gold
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            current_data = await resp.json()
            current_price = current_data["rates"][symbol]
        
        # Get historical (24h ago)
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        hist_url = f"https://metals-api.com/api/{yesterday}"
        
        async with session.get(hist_url, params=params) as resp:
            hist_data = await resp.json()
            hist_price = hist_data["rates"][symbol]
        
        change_24h = ((current_price - hist_price) / hist_price) * 100
        
        return {
            "price": current_price,
            "change_24h": change_24h,
            "source": "metals-api"
        }
```

**Pros:**
- ✅ Dedicated metals API
- ✅ Historical data included

**Cons:**
- ⚠️ Only 50 requests/month (free)
- ⚠️ Need paid plan for production

---

#### **Option B: Self-Calculate with Current API**
Similar to Forex, store historical data in database

```python
class MetalHistory(Base):
    """Store metal historical data"""
    __tablename__ = "metal_history"
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), index=True)
    price = Column(Float)
    timestamp = Column(DateTime, index=True)

async def get_metal_change_self_calculated(symbol: str, db):
    """Calculate 24h change from stored data"""
    # Similar logic to forex self-calculated
    # Store current price every hour
    # Calculate change from 24h ago
    pass
```

---

## 🔧 IMPLEMENTATION PLAN

### Step 1: Choose API Strategy

**Recommended combination:**
- **Crypto:** Keep Binance (100% real, free, unlimited)
- **Forex:** Twelve Data (800 req/day) + Self-calculate backup
- **Metals:** Self-calculate (100% free, unlimited)

### Step 2: Create Unified Provider

```python
# backend/app/services/market_data_enhanced.py

class EnhancedMarketDataProvider:
    """Enhanced provider with real 24h change"""
    
    def __init__(self):
        self.twelvedata_key = os.getenv("TWELVEDATA_API_KEY")
        self.use_selfcalc_forex = True  # Fallback to self-calculation
        self.use_selfcalc_metals = True
    
    async def get_forex_price(self, pair: str):
        """Get forex with real 24h change"""
        try:
            # Try Twelve Data first
            if self.twelvedata_key:
                data = await get_forex_change_twelvedata(pair)
                if data:
                    return data
        except Exception as e:
            logger.warning(f"Twelve Data failed: {e}")
        
        # Fallback to self-calculation
        if self.use_selfcalc_forex:
            return await get_forex_change_self_calculated(pair, db)
        
        # Last resort: current price only
        return await get_current_forex_price(pair)
    
    async def get_metal_price(self, symbol: str):
        """Get metal with real 24h change"""
        # Use self-calculation (free, unlimited)
        return await get_metal_change_self_calculated(symbol, db)
```

### Step 3: Database Migration

```python
# Migration file
def upgrade():
    op.create_table(
        'forex_history',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('pair', sa.String(10), index=True),
        sa.Column('price', sa.Float),
        sa.Column('timestamp', sa.DateTime, index=True)
    )
    
    op.create_table(
        'metal_history',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('symbol', sa.String(10), index=True),
        sa.Column('price', sa.Float),
        sa.Column('timestamp', sa.DateTime, index=True)
    )
```

### Step 4: Background Task

```python
# backend/app/tasks/market_data_collector.py

from fastapi_utils.tasks import repeat_every

@repeat_every(seconds=3600)  # Every hour
async def collect_market_data():
    """Collect and store market data hourly"""
    # Store forex prices
    for pair in FOREX_PAIRS:
        price = await fetch_current_forex_price(pair)
        await store_forex_price(pair, price)
    
    # Store metal prices
    for symbol in METAL_SYMBOLS:
        price = await fetch_current_metal_price(symbol)
        await store_metal_price(symbol, price)
    
    logger.info("Market data collected")

# Register in main.py
@app.on_event("startup")
async def startup_event():
    await collect_market_data()  # Start immediately
```

---

## 📊 COMPARISON TABLE

| Solution | Forex Change | Metals Change | Cost | Requests/Day | Setup Complexity |
|----------|--------------|---------------|------|--------------|------------------|
| **Twelve Data + Self-calc** | ✅ Real | ✅ Real | Free | 800 (forex) + ∞ (metals) | Medium |
| **Alpha Vantage** | ✅ Real | ❌ No metals | Free | 25 | Low |
| **Self-calculate only** | ✅ Real | ✅ Real | Free | ∞ | Medium |
| **Current (mock)** | ❌ Mock | ❌ Mock | Free | ∞ | Low |

---

## 🎯 RECOMMENDED SOLUTION

**Hybrid Approach:**

1. **Crypto:** Binance (current - 100% real) ✅
2. **Forex:** Self-calculate (store hourly, calculate 24h change) ✅
3. **Metals:** Self-calculate (store hourly, calculate 24h change) ✅

**Why:**
- ✅ 100% free
- ✅ Unlimited requests
- ✅ Full control
- ✅ Real 24h change
- ✅ No external API dependencies
- ⚠️ Requires 24 hours to start working

**Optional upgrade:**
- Add Twelve Data for Forex (800 free req/day) as primary source
- Use self-calculate as backup

---

## 📝 NEXT STEPS

1. **Immediate:** Implement database storage for forex/metals
2. **Hour 1:** Start background task collecting data
3. **Hour 24:** Self-calculated 24h change becomes available
4. **Optional:** Sign up for Twelve Data (instant forex change)

---

Bạn muốn tôi triển khai giải pháp nào?
A. Self-calculate (100% free, unlimited)
B. Twelve Data + Self-calculate (hybrid)
C. Chỉ implement database schema trước
