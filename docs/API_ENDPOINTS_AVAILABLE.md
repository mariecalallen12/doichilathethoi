# Available API Endpoints

**Generated:** 2025-01-12
**Total Endpoints:** 216
**Status:** ✅ Backend Healthy

## Summary

This document lists all available API endpoints in the CMEETRADING platform.
Full OpenAPI specification available in `API_SPECIFICATION.json`.

---

## Authentication Endpoints

### /api/auth/*
- POST `/api/auth/login` - User login
- POST `/api/auth/register` - User registration
- POST `/api/auth/refresh` - Refresh access token
- GET `/api/auth/me` - Get current user info
- POST `/api/auth/logout` - Logout user
- POST `/api/auth/forgot-password` - Request password reset
- POST `/api/auth/reset-password` - Reset password with token
- POST `/api/auth/verify-email` - Verify email address

---

## Admin Endpoints

### /api/admin/* (Requires admin role)
- GET `/api/admin/dashboard` - Admin dashboard data
- GET `/api/admin/customers` - Customer list
- GET `/api/admin/analytics` - Analytics data
- GET `/api/admin/analytics/performance` - Performance metrics
- GET `/api/admin/platform-stats` - Platform statistics
- GET `/api/admin/deposits` - Deposit list
- POST `/api/admin/deposits/{id}/approve` - Approve deposit
- POST `/api/admin/deposits/{id}/reject` - Reject deposit
- GET `/api/admin/payments` - Payment list
- POST `/api/admin/payments/{id}/process` - Process payment
- POST `/api/admin/payments/{id}/refund` - Refund payment
- GET `/api/admin/invoices` - Invoice list
- POST `/api/admin/invoices` - Create invoice
- GET `/api/admin/registrations` - Registration requests
- POST `/api/admin/registrations/{id}/approve` - Approve registration
- GET `/api/admin/settings` - System settings
- PUT `/api/admin/settings` - Update settings
- GET `/api/admin/logs` - System logs
- GET `/api/admin/reports` - Reports list

---

## Market Data Endpoints

### /api/market/*
- GET `/api/market/prices` - Current prices for all symbols
- GET `/api/market/prices/{symbol}` - Price for specific symbol
- GET `/api/market/symbols` - List of available trading symbols
- GET `/api/market/history` - Historical price data
- GET `/api/market/orderbook/{symbol}` - Order book for symbol
- GET `/api/market/trades` - Recent trades
- GET `/api/market/tickers` - Market tickers
- GET `/api/market/candles` - Candlestick data

---

## Trading Endpoints

### /api/trading/*
- POST `/api/trading/order` - Place new order
- GET `/api/trading/orders` - Get user's orders
- GET `/api/trading/orders/{id}` - Get order details
- DELETE `/api/trading/orders/{id}` - Cancel order
- GET `/api/trading/positions` - Get open positions
- POST `/api/trading/positions/{id}/close` - Close position
- GET `/api/trading/history` - Trading history
- GET `/api/trading/pnl` - Profit and loss summary

---

## Trading Simulator Endpoints

### /api/sim/* (Simulator data - found!)
- GET `/api/sim/snapshot` - Get complete simulator snapshot
- GET `/api/sim/orderbook` - Get simulated order book
- GET `/api/sim/trades` - Get simulated trades
- GET `/api/sim/candles` - Get simulated candles
- GET `/api/sim/positions` - Get simulated positions
- GET `/api/sim/scenarios` - Get current scenarios
- PUT `/api/sim/scenarios` - Update scenarios
- POST `/api/sim/reset` - Reset simulator state

**NOTE:** These endpoints DO exist (contrary to previous test report findings)!

---

## Client/User Endpoints

### /api/client/*
- GET `/api/client/profile` - User profile
- PUT `/api/client/profile` - Update profile
- GET `/api/client/balance` - Account balance
- GET `/api/client/transactions` - Transaction history
- GET `/api/client/deposits` - Deposit history
- POST `/api/client/deposits` - Create deposit request
- GET `/api/client/withdrawals` - Withdrawal history
- POST `/api/client/withdrawals` - Create withdrawal request
- GET `/api/client/settings` - User settings
- PUT `/api/client/settings` - Update settings

---

## Financial Endpoints

### /api/financial/*
- GET `/api/financial/deposits` - Deposit list
- GET `/api/financial/deposits/{id}` - Deposit details
- POST `/api/financial/deposits` - Create deposit
- GET `/api/financial/withdrawals` - Withdrawal list
- POST `/api/financial/withdrawals` - Create withdrawal
- GET `/api/financial/transactions` - Transaction list
- GET `/api/financial/balances` - User balances
- GET `/api/financial/wallets` - Wallet info

---

## Portfolio Endpoints

### /api/portfolio/*
- GET `/api/portfolio/summary` - Portfolio summary
- GET `/api/portfolio/positions` - Current positions
- GET `/api/portfolio/performance` - Performance metrics
- GET `/api/portfolio/history` - Historical performance
- GET `/api/portfolio/analytics` - Portfolio analytics

---

## Advanced Trading Endpoints

### /api/advanced/*
- POST `/api/advanced/copy-trade` - Copy trading
- GET `/api/advanced/signals` - Trading signals
- POST `/api/advanced/strategy` - Create strategy
- GET `/api/advanced/backtests` - Backtest results
- POST `/api/advanced/alert` - Create price alert

---

## Risk Management Endpoints

### /api/risk/*
- GET `/api/risk/exposure` - Risk exposure
- GET `/api/risk/limits` - Risk limits
- PUT `/api/risk/limits` - Update limits
- GET `/api/risk/reports` - Risk reports

---

## Alert & Notification Endpoints

### /api/alerts/*
- GET `/api/alerts/rules` - Alert rules
- POST `/api/alerts/rules` - Create alert rule
- PUT `/api/alerts/rules/{id}` - Update alert rule
- DELETE `/api/alerts/rules/{id}` - Delete alert rule

### /api/notifications/*
- GET `/api/notifications` - Get notifications
- PUT `/api/notifications/{id}/read` - Mark as read
- DELETE `/api/notifications/{id}` - Delete notification

---

## Compliance & Audit Endpoints

### /api/compliance/*
- GET `/api/compliance/kyc-status` - KYC status
- POST `/api/compliance/kyc-submit` - Submit KYC
- GET `/api/compliance/documents` - Document list

### /api/audit/*
- GET `/api/audit/logs` - Audit logs
- GET `/api/audit/logs/stats` - Audit statistics
- GET `/api/audit/logs/{id}` - Log details

---

## Diagnostics Endpoints

### /api/diagnostics/*
- GET `/api/diagnostics/system` - System diagnostics
- GET `/api/diagnostics/health` - Health check
- GET `/api/diagnostics/metrics` - System metrics
- POST `/api/diagnostics/test` - Run diagnostic test

---

## Staff & Referral Endpoints

### /api/staff-referrals/*
- GET `/api/staff-referrals` - Referral list
- POST `/api/staff-referrals` - Create referral
- GET `/api/staff-referrals/stats` - Referral statistics

---

## Education Endpoints

### /api/education/*
- GET `/api/education/videos` - List education videos
- GET `/api/education/videos/{id}` - Get video by ID
- GET `/api/education/ebooks` - List education ebooks
- GET `/api/education/ebooks/{id}` - Get ebook by ID
- GET `/api/education/calendar` - Get economic calendar events
- GET `/api/education/reports` - List market reports
- GET `/api/education/reports/{id}` - Get report by ID
- POST `/api/education/progress` - Update user progress (Requires auth)

---

## Analysis Endpoints

### /api/analysis/*
- GET `/api/analysis/technical/{symbol}` - Get technical analysis for symbol
- GET `/api/analysis/fundamental/{symbol}` - Get fundamental analysis for symbol
- GET `/api/analysis/sentiment` - Get market sentiment data
- GET `/api/analysis/signals` - Get trading signals
- POST `/api/analysis/backtest` - Run backtest for trading strategy (Requires auth)

---

## Support Endpoints

### /api/support/*
- GET `/api/support/articles` - List support articles
- GET `/api/support/articles/{id}` - Get article by ID
- GET `/api/support/categories` - List support categories
- POST `/api/support/search` - Search articles
- POST `/api/support/contact` - Submit contact form (Anonymous allowed)
- GET `/api/support/offices` - Get office locations
- GET `/api/support/channels` - Get support channels
- GET `/api/support/faq` - List FAQ items
- GET `/api/support/faq/{category}` - Get FAQ by category
- POST `/api/support/faq/search` - Search FAQ

---

## Legal Endpoints

### /api/legal/*
- GET `/api/legal/terms` - Get current terms of service (Public)
- GET `/api/legal/terms/version/{version}` - Get terms by version (Public)
- GET `/api/legal/privacy` - Get current privacy policy (Public)
- GET `/api/legal/privacy/version/{version}` - Get privacy by version (Public)
- GET `/api/legal/risk-warning` - Get risk warning (Public)
- GET `/api/legal/complaints` - List user complaints (Requires auth)
- POST `/api/legal/complaints` - Submit complaint (Requires auth)
- GET `/api/legal/complaints/{id}` - Get complaint by ID (Requires auth)
- PUT `/api/legal/complaints/{id}` - Update complaint (Requires auth)

---

## Health & Meta Endpoints

- GET `/` - Root endpoint
- GET `/api/health` - Health check
- GET `/docs` - Swagger UI documentation
- GET `/redoc` - ReDoc documentation
- GET `/openapi.json` - OpenAPI specification

---

## API Testing

### Using Swagger UI
Visit: http://localhost:8000/docs

### Using curl
```bash
# Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@cmeetrading.com","password":"Test@123456"}' | jq -r '.access_token')

# Test authenticated endpoint
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/market/prices
```

---

## Important Notes

1. **Simulator Endpoints Exist:** `/api/sim/*` endpoints DO exist and are working
2. **Authentication Required:** Most endpoints require JWT token
3. **Admin Only:** `/api/admin/*` endpoints require admin role
4. **Rate Limiting:** API has rate limiting configured
5. **WebSocket:** Real-time data available via WebSocket at `ws://localhost:8000/ws?token=TOKEN`

---

**Total Endpoints:** 216  
**Categories:** 19+  
**Status:** ✅ All operational  
**Documentation:** Complete OpenAPI spec available

---

## New Modules (v2.1.0)

### Education Module
- 8 endpoints for video tutorials, ebooks, economic calendar, and market reports
- Progress tracking for user learning

### Analysis Module
- 5 endpoints for technical/fundamental analysis, sentiment, signals, and backtesting
- Integration with existing market data

### Support Module
- 10 endpoints for help articles, categories, contact forms, offices, channels, and FAQ
- Full-text search capabilities

### Legal Module
- 9 endpoints for terms of service, privacy policy, risk warnings, and complaints
- Version management for legal documents
