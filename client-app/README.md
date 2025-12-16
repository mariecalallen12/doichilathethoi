# Client App - Vue 3 + Vite (LuxeTrade)

**Version**: 2.0.0  
**Status**: Production Ready  
**Last Updated**: 2025-01-08

---

## Overview

This is the client-facing application for the Digital Utopia Platform, built with Vue 3 and Vite. The application provides a modern, responsive interface for trading, market analysis, education, and personal account management.

---

## Features

- 🏠 **Homepage** - Landing page with navigation and login
- 📊 **Market View** - Real-time market data and analysis
- 💹 **Trading Dashboard** - Advanced trading interface
- 📚 **Education** - Trading education and resources
- 📈 **Analysis** - Technical and fundamental analysis tools
- 👤 **Personal Area** - Account management, deposits, withdrawals, wallet

---

## Prerequisites

- **Node.js**: 18.x or 20.x
- **npm**: 8.x or higher
- **Docker**: 20.x or higher (for containerized deployment)

---

## Quick Start

### Local Development

1. **Clone and navigate to client-app**
   ```bash
   cd client-app
   ```

2. **Install dependencies**
   ```bash
   npm install --legacy-peer-deps
   ```

3. **Create environment file**
   ```bash
   cp ENV_EXAMPLE.md .env
   # Edit .env with your configuration
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

5. **Open in browser**
   ```
   http://localhost:3002
   ```

### Docker Development

1. **Build and run with docker-compose**
   ```bash
   docker-compose up -d client-app
   ```

2. **Access application**
   ```
   http://localhost:3002
   ```

---

## Environment Variables

### Required Variables

Create a `.env` file in the `client-app` directory with the following variables:

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000

# WebSocket Configuration
VITE_WS_URL=ws://localhost:8000/ws
```

### Production Variables

For production deployment, set these via Docker build arguments or your hosting platform:

```bash
# Docker build with production URLs
docker build \
  --build-arg VITE_API_BASE_URL=https://api.example.com \
  --build-arg VITE_WS_URL=wss://api.example.com/ws \
  -t client-app:latest .
```

### Available Variables

See [ENV_EXAMPLE.md](./ENV_EXAMPLE.md) for a complete list of available environment variables.

**Important Notes**:
- All variables must start with `VITE_` prefix to be accessible in the browser
- Variables are replaced at build time, not runtime
- After changing `.env`, restart the dev server or rebuild the application
- Never commit `.env` file to version control

---

## Development

### Project Structure

```
client-app/
├── public/              # Static assets
├── src/
│   ├── assets/         # Images, fonts, icons
│   ├── components/     # Vue components
│   │   ├── shared/     # Shared components (LoginModal, etc.)
│   │   ├── market/     # Market-related components
│   │   ├── trading/    # Trading-related components
│   │   ├── education/  # Education components
│   │   └── personal/   # Personal area components
│   ├── layouts/        # Layout components
│   ├── router/         # Vue Router configuration
│   ├── services/       # API and WebSocket services
│   │   ├── api/        # API service files
│   │   └── websocket.js # WebSocket service
│   ├── stores/         # Pinia stores (state management)
│   ├── views/          # Page components
│   └── main.js         # Application entry point
├── scripts/            # Utility scripts
├── Dockerfile          # Docker build configuration
├── vite.config.js      # Vite configuration
└── package.json        # Dependencies and scripts
```

### Available Scripts

```bash
# Development
npm run dev                      # Start development server
npm run build                    # Build for production
npm run preview                  # Preview production build

# API Integration Testing
node scripts/test-client-api.mjs       # Test client→backend API (local/staging)
node scripts/test-production-api.mjs   # Test API integration (production URLs)
```

### Key Files

- **Router**: `src/router/index.js` - Route configuration
- **API Services**: `src/services/api/` - API integration
- **WebSocket**: `src/services/websocket.js` - Real-time updates
- **Homepage**: `src/views/HomePage.vue` - Landing page with navigation
- **Login Modal**: `src/components/shared/LoginModal.vue` - Login component

---

## Production Deployment

### Docker Deployment

1. **Build production image**
   ```bash
   docker build \
     --build-arg VITE_API_BASE_URL=https://api.example.com \
     --build-arg VITE_WS_URL=wss://api.example.com/ws \
     -t client-app:latest ./client-app
   ```

2. **Run container**
   ```bash
   docker run -d \
     -p 3002:80 \
     --name client-app \
     client-app:latest
   ```

### Docker Compose

1. **Set environment variables in `.env`**
   ```env
   CLIENT_API_BASE_URL=https://api.example.com
   CLIENT_WS_URL=wss://api.example.com/ws
   ```

2. **Deploy with docker-compose**
   ```bash
   docker-compose up -d client-app
   ```

### Production Checklist

- [ ] Environment variables set correctly
- [ ] API URL points to production backend
- [ ] WebSocket URL uses `wss://` (secure)
- [ ] CORS configured on backend
- [ ] SSL/TLS certificates configured
- [ ] Health checks configured
- [ ] Monitoring and logging setup
- [ ] Backup strategy in place

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for detailed deployment instructions.

---

## Testing

### Manual Testing

Use the [TESTING_CHECKLIST.md](./TESTING_CHECKLIST.md) for comprehensive testing scenarios, bao gồm:
- Login → overview → Mini Wallet
- Nạp/rút (crypto, VietQR)
- Trading CTA & đồng bộ số dư
- Tỷ giá & portfolio analytics
- 2FA cho các thao tác nhạy cảm

### API Integration Testing

Test API integration with production URLs:

```bash
node scripts/test-production-api.mjs \
  --api-url=https://api.example.com \
  --ws-url=wss://api.example.com/ws
```

### User Acceptance Testing

Follow the scenarios in [UAT_TEST_SCENARIOS.md](./UAT_TEST_SCENARIOS.md) for UAT.

---

## Troubleshooting

### Common Issues

1. **Navigation links not working**
   - Check router configuration
   - Verify routes are defined
   - See [TROUBLESHOOTING_GUIDE.md](./TROUBLESHOOTING_GUIDE.md)

2. **Login redirect issues**
   - Verify redirect logic in LoginModal
   - Check browser console for errors
   - See [TROUBLESHOOTING_GUIDE.md](./TROUBLESHOOTING_GUIDE.md)

3. **API connection failures**
   - Verify `VITE_API_BASE_URL` is set correctly
   - Check CORS configuration
   - Verify backend is running
   - See [TROUBLESHOOTING_GUIDE.md](./TROUBLESHOOTING_GUIDE.md)

4. **Environment variables not working**
   - Variables must start with `VITE_` prefix
   - Rebuild after changing variables
   - Check Docker build args
   - See [TROUBLESHOOTING_GUIDE.md](./TROUBLESHOOTING_GUIDE.md)

For detailed troubleshooting, see [TROUBLESHOOTING_GUIDE.md](./TROUBLESHOOTING_GUIDE.md).

---

## Recent Fixes

### Version 2.0.0 (2025-01-08)

1. **Desktop Navigation Links Fix**
   - Replaced `<a>` tags with `<router-link>` components
   - Added active state highlighting
   - Fixed navigation routing

2. **Login Redirect Fix**
   - Resolved double redirect issue
   - Centralized redirect logic in LoginModal
   - Improved login flow

3. **Environment Variables Verification**
   - Verified Dockerfile configuration
   - Documented environment setup
   - Added fallback values

See [BAO_CAO_TRIEN_KHAI_FIXES.md](../BAO_CAO_TRIEN_KHAI_FIXES.md) for detailed fix report.

---

## Documentation

- [ENV_EXAMPLE.md](./ENV_EXAMPLE.md) - Environment variables reference
- [TESTING_CHECKLIST.md](./TESTING_CHECKLIST.md) - Testing scenarios
- [UAT_TEST_SCENARIOS.md](./UAT_TEST_SCENARIOS.md) - User acceptance testing
- [TROUBLESHOOTING_GUIDE.md](./TROUBLESHOOTING_GUIDE.md) - Troubleshooting guide
- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) - Production deployment guide

---

## Support

For issues and questions:
1. Check [TROUBLESHOOTING_GUIDE.md](./TROUBLESHOOTING_GUIDE.md)
2. Review browser console for errors
3. Check server logs
4. Contact development team

---

## License

MIT License

---

**Last Updated**: 2025-01-08
