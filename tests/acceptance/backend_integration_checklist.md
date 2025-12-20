# Backend Integration Testing Checklist

**Date**: _______________  
**Tester**: _______________  
**Environment**: _______________ (local/staging/production)  
**Status**: ⏳ In Progress

---

## Overview

This checklist provides manual testing steps to verify backend integration components including WebSocket, API endpoints, database, Redis, and trade broadcaster.

---

## 1. WebSocket Integration Testing

### 1.1 WebSocket Connection

- [ ] **Test WebSocket Connection Establishment**
  - Connect to `ws://localhost:8000/ws?token=<access_token>&channels=prices,trades`
  - Verify connection is accepted
  - Verify welcome message received with `type: "connected"`
  - Verify message contains `user_id` and `channels`

- [ ] **Test WebSocket Authentication**
  - Try connecting without token → Should be rejected
  - Try connecting with invalid token → Should be rejected
  - Try connecting with valid token → Should be accepted

- [ ] **Test Channel Subscription**
  - Connect with `channels=prices` → Should only receive price updates
  - Connect with `channels=trades` → Should only receive trade updates
  - Connect with `channels=prices,trades` → Should receive both
  - Verify messages are filtered correctly

### 1.2 WebSocket Message Routing

- [ ] **Test Price Update Messages**
  - Subscribe to `prices` channel
  - Verify price update messages received
  - Verify message structure:
    ```json
    {
      "type": "price_update",
      "channel": "prices",
      "data": {
        "symbol": "BTCUSDT",
        "s": "BTCUSDT",
        "price": 45000.0,
        "p": 45000.0,
        "change": 100.0,
        "c": 100.0,
        "changePercent": 0.22,
        "cp": 0.22,
        "t": 1234567890
      }
    }
    ```
  - Verify both long keys (`symbol`, `price`, `change`, `changePercent`) and short keys (`s`, `p`, `c`, `cp`) are present

- [ ] **Test Trade Update Messages**
  - Subscribe to `trades` channel
  - Verify trade update messages received
  - Verify message structure:
    ```json
    {
      "type": "trade_update",
      "channel": "trades",
      "data": {
        "symbol": "BTCUSDT",
        "trade": {
          "id": "BTCUSDT_1234567890_1",
          "price": 45000.0,
          "quantity": 1.0,
          "side": "buy",
          "timestamp": "2025-01-01T00:00:00Z",
          "time": 1234567890000
        },
        "timestamp": "2025-01-01T00:00:00Z"
      }
    }
    ```

- [ ] **Test Channel Filtering**
  - Connect Client 1 to `prices` channel only
  - Connect Client 2 to `trades` channel only
  - Connect Client 3 to both `prices,trades`
  - Broadcast price update → Only Client 1 and Client 3 should receive
  - Broadcast trade update → Only Client 2 and Client 3 should receive

### 1.3 WebSocket Connection Management

- [ ] **Test Connection Cleanup**
  - Connect WebSocket
  - Disconnect WebSocket
  - Verify connection is removed from active connections
  - Verify no errors in server logs

- [ ] **Test Reconnection**
  - Connect WebSocket
  - Disconnect (network issue simulation)
  - Reconnect with same token
  - Verify connection is re-established successfully

- [ ] **Test Ping/Pong**
  - Connect WebSocket
  - Send `{"type": "ping"}`
  - Verify `{"type": "pong"}` response received
  - Verify connection stays alive

---

## 2. API Endpoints Integration Testing

### 2.1 Health Check

- [ ] **Test Health Endpoint**
  ```bash
  curl http://localhost:8000/api/health
  ```
  - Verify status code: `200`
  - Verify response structure:
    ```json
    {
      "status": "ok",
      "service": "backend",
      "version": "2.0.0",
      "database": "connected",
      "redis": "connected",
      "timestamp": "..."
    }
    ```

### 2.2 Authentication Endpoints

- [ ] **Test Login Endpoint**
  ```bash
  curl -X POST http://localhost:8000/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email": "test@example.com", "password": "password123"}'
  ```
  - Verify status code: `200`
  - Verify response contains `access_token` and `refresh_token`

- [ ] **Test Register Endpoint**
  ```bash
  curl -X POST http://localhost:8000/api/auth/register \
    -H "Content-Type: application/json" \
    -d '{"email": "new@example.com", "password": "password123", "displayName": "Test User"}'
  ```
  - Verify status code: `200` or `201`
  - Verify user is created

### 2.3 Market Data Endpoints

- [ ] **Test Market Symbols Endpoint**
  ```bash
  curl http://localhost:8000/api/market/symbols
  ```
  - Verify status code: `200`
  - Verify response is array of symbols

- [ ] **Test Orderbook Endpoint**
  ```bash
  curl http://localhost:8000/api/market/orderbook/BTCUSDT
  ```
  - Verify status code: `200`
  - Verify response contains `symbol`, `bids`, `asks`

### 2.4 Simulator Endpoints

- [ ] **Test Simulator Status**
  ```bash
  curl http://localhost:8000/api/sim/status
  ```
  - Verify endpoint exists (may return 200 or 404 depending on implementation)

---

## 3. Database Integration Testing

### 3.1 Database Connection

- [ ] **Test Database Connection**
  - Check backend logs for database connection messages
  - Verify `✅ Database connection verified` in startup logs
  - If connection fails, verify graceful degradation

- [ ] **Test Database Health Check**
  - Call `/api/health` endpoint
  - Verify `database` field shows `connected` or `disconnected`
  - Verify application continues to work even if database is disconnected (graceful degradation)

### 3.2 Database Operations

- [ ] **Test Database Queries**
  - Login with valid credentials
  - Verify user data is retrieved from database
  - Verify response time is acceptable (< 500ms)

- [ ] **Test Database Transactions**
  - Create a new user
  - Verify user is saved to database
  - Update user profile
  - Verify changes are persisted

---

## 4. Redis Integration Testing

### 4.1 Redis Connection

- [ ] **Test Redis Connection**
  - Check backend logs for Redis connection messages
  - Verify `✅ Redis connection initialized successfully` in startup logs
  - If connection fails, verify graceful degradation (app should continue without Redis)

- [ ] **Test Redis Health Check**
  - Call `/api/health` endpoint
  - Verify `redis` field shows `connected` or `disconnected`
  - Verify application continues to work even if Redis is disconnected

### 4.2 Redis Cache Operations

- [ ] **Test Cache Functionality** (if Redis is connected)
  - Make API request that should be cached
  - Make same request again
  - Verify second request is faster (cached)
  - Verify cache TTL is working

- [ ] **Test Session Management** (if Redis is connected)
  - Login and get session token
  - Verify session is stored in Redis
  - Logout
  - Verify session is removed from Redis

---

## 5. Trade Broadcaster Integration Testing

### 5.1 Broadcaster Initialization

- [ ] **Test Broadcaster Startup**
  - Check backend startup logs
  - Verify `✅ Trade broadcaster started` message
  - Verify broadcaster is initialized in `lifespan` function

- [ ] **Test Broadcaster Configuration**
  - Verify broadcaster has correct symbols: `BTCUSDT`, `ETHUSDT`, `BNBUSDT`
  - Verify base prices are set correctly
  - Verify broadcast functions are set

### 5.2 Trade Broadcasting

- [ ] **Test Trade Updates**
  - Connect WebSocket to `trades` channel
  - Wait for trade update messages
  - Verify messages are received every ~2 seconds
  - Verify trade data structure:
    - `symbol`: Trading symbol (e.g., "BTCUSDT")
    - `trade.id`: Trade ID
    - `trade.price`: Trade price
    - `trade.quantity`: Trade quantity
    - `trade.side`: "buy" or "sell"
    - `trade.timestamp`: ISO timestamp

- [ ] **Test Price Updates**
  - Connect WebSocket to `prices` channel
  - Wait for price update messages
  - Verify messages are received every ~2 seconds
  - Verify price data includes:
    - `symbol`: Trading symbol
    - `price`: Current price
    - `change`: Price change (if available)
    - `changePercent`: Price change percentage (if available)

- [ ] **Test Symbol Format**
  - Verify all messages use `BTCUSDT` format (not `BTC/USD`)
  - Verify symbol format is consistent across all messages

### 5.3 Price Change Calculation

- [ ] **Test Change/ChangePercent**
  - Monitor price updates over time
  - Verify `change` field shows price difference from previous price
  - Verify `changePercent` field shows percentage change
  - Verify calculations are correct:
    - `change = current_price - previous_price`
    - `changePercent = (change / previous_price) * 100`

- [ ] **Test Change Indicators**
  - Verify positive change shows green indicator
  - Verify negative change shows red indicator
  - Verify zero change is handled correctly

---

## 6. System Integration Testing

### 6.1 Component Initialization

- [ ] **Test All Components Start**
  - Start backend server
  - Verify all components initialize:
    - [ ] Database connection
    - [ ] Redis connection
    - [ ] Trade broadcaster
    - [ ] WebSocket manager
  - Verify no errors in startup logs

### 6.2 Error Handling

- [ ] **Test Graceful Degradation**
  - Stop database → Verify app continues (may show degraded status)
  - Stop Redis → Verify app continues (may show degraded status)
  - Verify health endpoint reflects actual status

- [ ] **Test Error Responses**
  - Make invalid API request
  - Verify error response format:
    ```json
    {
      "error": true,
      "message": "Error description",
      "status_code": 400,
      "timestamp": "..."
    }
    ```

### 6.3 Performance

- [ ] **Test Response Times**
  - Health check: < 100ms
  - API endpoints: < 500ms
  - WebSocket message delivery: < 50ms

- [ ] **Test Resource Usage**
  - Monitor CPU usage
  - Monitor memory usage
  - Verify no memory leaks over time

---

## 7. End-to-End Integration Testing

### 7.1 Complete Flow Test

- [ ] **Test Complete User Flow**
  1. Register new user
  2. Login and get token
  3. Connect WebSocket with token
  4. Subscribe to `prices` and `trades` channels
  5. Verify receiving price and trade updates
  6. Make API calls (e.g., get market data)
  7. Verify all operations work together

### 7.2 Multi-Client Test

- [ ] **Test Multiple Clients**
  - Connect 3+ WebSocket clients
  - Subscribe to different channels
  - Verify each client receives only relevant messages
  - Verify no message leakage between clients

---

## 8. Logging and Monitoring

### 8.1 Log Verification

- [ ] **Check Application Logs**
  - Verify no errors in logs
  - Verify informative log messages
  - Verify log levels are appropriate

### 8.2 Monitoring

- [ ] **Test Health Monitoring**
  - Verify health endpoint is accessible
  - Verify health status is accurate
  - Verify monitoring tools can access health endpoint

---

## Test Results Summary

### Passed Tests: ___ / ___

### Failed Tests: ___ / ___

### Notes:
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

---

## Sign-off

**Tester**: _______________ Date: _______  
**Reviewed By**: _______________ Date: _______

---

## Next Steps

- [ ] Fix any failed tests
- [ ] Re-run failed tests
- [ ] Update documentation if needed
- [ ] Create bug reports for any issues found

