# OPEX Integration Guide

**Version:** 1.0.0  
**Last Updated:** 2025-12-16  
**Status:** Production Ready

---

## Overview

This guide provides comprehensive documentation for the OPEX Core integration with the Digital Utopia Platform. OPEX Core is a Kotlin-based cryptocurrency exchange system that provides order matching, wallet management, and trading services.

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Vue.js)                      │
│  - Trading Dashboard                                      │
│  - Order Placement UI                                     │
│  - Real-time WebSocket Updates                           │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│              FastAPI Backend (Python)                    │
│  - OPEX Trading Service                                  │
│  - OPEX Client (HTTP Client)                             │
│  - Risk Validation Service                               │
│  - WebSocket Manager                                     │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│              OPEX Core Services (Kotlin)                 │
│  - API Service (port 8082)                               │
│  - Market Service (port 8083)                            │
│  - Matching Engine                                       │
│  - Wallet Service                                        │
│  - Matching Gateway                                      │
└──────────────────────────────────────────────────────────┘
```

---

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# OPEX API Configuration
OPEX_API_URL=http://core-main-api-1:8080
OPEX_MARKET_URL=http://core-main-market-1:8080
OPEX_API_KEY=your_api_key_here  # Optional, if required
OPEX_TIMEOUT=30  # Request timeout in seconds
```

### Network Configuration

Ensure backend and OPEX services are on the same Docker network:

```bash
# Connect backend to OPEX network
docker network connect opex-network digital_utopia_backend

# Or add OPEX services to backend network
docker network connect forexxx_digital_utopia_network core-main-api-1
```

---

## API Endpoints

### Trading Endpoints

#### Place Order
```http
POST /api/trading/orders
Authorization: Bearer {token}
Content-Type: application/json

{
  "symbol": "BTCUSDT",
  "side": "buy",
  "type": "market",
  "quantity": 0.001,
  "price": 45000.0  # Required for limit/stop orders
}
```

#### Get Orders
```http
GET /api/trading/orders?symbol=BTCUSDT&status=open&limit=100
Authorization: Bearer {token}
```

#### Cancel Order
```http
DELETE /api/trading/orders/{order_id}
Authorization: Bearer {token}
```

#### Get Positions
```http
GET /api/trading/positions?symbol=BTCUSDT
Authorization: Bearer {token}
```

#### Close Position
```http
POST /api/trading/positions/{position_id}/close
Authorization: Bearer {token}
```

### Market Data Endpoints

#### Get Orderbook
```http
GET /api/market/orderbook/BTCUSDT?limit=20
```

#### Get Ticker
```http
GET /api/market/ticker/BTCUSDT
```

---

## User Account Setup

### Automatic Account Creation

When a user registers in the FastAPI backend, the system automatically attempts to create an account in OPEX:

1. User registers via `/api/auth/register`
2. Backend creates user in database
3. Background task syncs user to OPEX:
   - Creates OPEX user account
   - Initializes wallet with default currency (USDT)
   - Sets initial balance to 0

### Manual Account Creation

If automatic creation fails, create user manually in OPEX admin panel:

1. Access OPEX admin panel
2. Navigate to User Management
3. Create user with matching user_id from FastAPI backend
4. Initialize wallet for the user

---

## Order Placement Flow

### 1. Frontend Request
```javascript
// client-app/src/stores/opex_trading.js
await tradingStore.placeOrder({
  symbol: 'BTCUSDT',
  side: 'buy',
  type: 'market',
  quantity: 0.001
})
```

### 2. Backend Validation
- Symbol format validation
- Order type validation
- Quantity validation
- Risk checks (balance, position limits, daily loss)

### 3. OPEX API Call
```python
# backend/app/services/opex_trading_service.py
result = await self.opex.place_order(
    user_id=str(user_id),
    symbol="BTC_USDT",  # Converted format
    side="BUY",
    order_type="MARKET",
    quantity=0.001
)
```

### 4. WebSocket Update
- Order update broadcast to user's WebSocket connections
- Frontend receives real-time update
- UI updates automatically

---

## Risk Management

### Pre-Trade Checks

The system performs the following risk checks before placing orders:

1. **Balance Validation**: Checks if user has sufficient balance
2. **Position Size Limits**: Ensures position doesn't exceed maximum size
3. **Daily Loss Limits**: Prevents trading if daily loss limit exceeded
4. **Margin Requirements**: Validates margin for leveraged trading

### Configuration

Risk limits can be configured in `backend/app/services/risk_validation_service.py`:

```python
MAX_POSITION_SIZE = Decimal("1000000")  # $1M
MAX_DAILY_LOSS = Decimal("10000")  # $10K
MIN_MARGIN_RATIO = Decimal("0.1")  # 10%
MAX_LEVERAGE = Decimal("100")  # 100x
```

---

## WebSocket Integration

### Connection

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws?token={jwt_token}&channels=orders,positions')

// Subscribe to channels
ws.send(JSON.stringify({
  type: 'subscribe',
  channels: ['orders', 'positions', 'account']
}))
```

### Message Types

#### Order Update
```json
{
  "type": "order_update",
  "data": {
    "id": "order_123",
    "status": "filled",
    "filled_quantity": 0.001,
    "filled_price": 45000.0
  },
  "timestamp": "2025-12-16T10:30:00Z"
}
```

#### Position Update
```json
{
  "type": "position_update",
  "data": {
    "id": "pos_456",
    "symbol": "BTCUSDT",
    "quantity": 0.001,
    "unrealized_pnl": 5.50
  },
  "timestamp": "2025-12-16T10:30:00Z"
}
```

---

## Testing

### Test Scripts

1. **Order Placement Test**
   ```bash
   python tests/test_opex_order_placement.py
   ```

2. **Authentication Test**
   ```bash
   python tests/test_authentication_opex.py
   ```

3. **Order History Test**
   ```bash
   python tests/test_order_history_positions.py
   ```

### Setup Test User

```bash
./scripts/setup_test_user_opex.sh
```

---

## Troubleshooting

### Common Issues

#### 1. OPEX Service Not Available
**Error**: `OPEX service unavailable: Connection refused`

**Solution**:
- Check if OPEX services are running: `docker ps | grep opex`
- Verify network connectivity: `docker network inspect opex-network`
- Check OPEX API health: `curl http://localhost:8082/actuator/health`

#### 2. User Not Found in OPEX
**Error**: `User not found in OPEX`

**Solution**:
- Create user manually in OPEX admin panel
- Or wait for automatic sync (runs in background after registration)

#### 3. Order Placement Fails
**Error**: `Failed to place order: Insufficient balance`

**Solution**:
- Verify user has wallet in OPEX
- Check wallet balance via OPEX admin panel
- Ensure sufficient balance for order value

#### 4. WebSocket Connection Fails
**Error**: `WebSocket connection failed`

**Solution**:
- Verify JWT token is valid
- Check WebSocket endpoint: `ws://localhost:8000/ws`
- Ensure channels are correctly specified

---

## Monitoring

### Health Checks

#### Backend Trading Health
```bash
curl http://localhost:8000/api/trading/health
```

#### OPEX API Health
```bash
curl http://localhost:8082/actuator/health
```

### Logs

#### Backend Logs
```bash
docker logs digital_utopia_backend | grep -i opex
```

#### OPEX Service Logs
```bash
docker logs core-main-api-1
```

---

## Performance Optimization

### Connection Pooling

The OPEX client uses `httpx.AsyncClient` with connection pooling enabled by default.

### Caching

Order and position data is cached for 10 seconds to reduce API calls:
- Orders cache TTL: 10 seconds
- Positions cache TTL: 10 seconds
- Statistics cache TTL: 30 seconds

### Rate Limiting

OPEX API calls are rate-limited to prevent overload. Adjust timeout in config if needed.

---

## Security

### Authentication

- All trading endpoints require JWT authentication
- User ID is extracted from JWT token
- User can only access their own orders/positions

### Authorization

- Orders are validated against user's account
- Position access is restricted to owner
- Risk checks prevent unauthorized trading

---

## Support

For issues or questions:
- Check logs: `docker logs digital_utopia_backend`
- Review OPEX documentation: `core-main/README.md`
- Contact development team

---

## Changelog

### Version 1.0.0 (2025-12-16)
- Initial OPEX integration
- Order placement functionality
- WebSocket real-time updates
- Risk validation service
- User account auto-creation
- Comprehensive test scripts

---

**Document maintained by:** Development Team  
**Last reviewed:** 2025-12-16

