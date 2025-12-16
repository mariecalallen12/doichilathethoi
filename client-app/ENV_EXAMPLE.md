# Environment Variables Configuration

Copy the content below to create a `.env` file in the root of `client-app` directory.

```env
# Digital Utopia Platform - Client App Environment Variables
# Copy this content to .env file and update with your actual values

# API Configuration
# Backend API base URL (FastAPI server)
VITE_API_BASE_URL=http://localhost:8000

# WebSocket Configuration
# WebSocket server URL for real-time updates
VITE_WS_URL=ws://localhost:8000/ws

# Application Configuration
# Application name
VITE_APP_NAME=LuxeTrade

# Application version
VITE_APP_VERSION=1.0.0

# Environment (development, staging, production)
VITE_APP_ENV=development

# Feature Flags (optional)
# Enable/disable specific features
VITE_ENABLE_SOCIAL_LOGIN=true
VITE_ENABLE_2FA=true
VITE_ENABLE_ANALYTICS=false
VITE_ENABLE_CLIENT_LOGGING=false  # Enable client-side logging/metrics to console

# Trading Configuration (optional)
# Default trading settings
VITE_DEFAULT_LEVERAGE=100
VITE_MIN_TRADE_AMOUNT=10

# Market Data Configuration (optional)
# Market data provider settings
VITE_MARKET_DATA_PROVIDER=binance
VITE_MARKET_DATA_UPDATE_INTERVAL=1000

# PWA Configuration (optional)
# Progressive Web App settings
VITE_PWA_ENABLED=true

# Sentry Configuration (optional)
# Error tracking and monitoring
# VITE_SENTRY_DSN=your-sentry-dsn-here

# Google Analytics (optional)
# VITE_GA_TRACKING_ID=your-ga-tracking-id

# Social Login OAuth (optional)
# VITE_GOOGLE_CLIENT_ID=your-google-client-id
# VITE_FACEBOOK_APP_ID=your-facebook-app-id
```

## Notes

- Never commit `.env` file to version control
- Use `.env.local` for local overrides (gitignored)
- In production, set these via your hosting platform's environment variables
- All `VITE_` prefixed variables are exposed to the client-side code
- After creating `.env` file, restart the development server

## Quick Start

1. Copy the content above
2. Create a new file named `.env` in the `client-app` directory
3. Paste the content and update values as needed
4. Restart the dev server: `npm run dev`
