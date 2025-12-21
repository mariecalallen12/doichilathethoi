# 🚀 Quick Start - Microservices Deployment

**Time to Deploy:** 7-10 minutes  
**Difficulty:** Easy (One command)

---

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 20GB disk space

---

## Step 1: Clone/Navigate to Project

```bash
cd /root/3/doichilathethoi
```

---

## Step 2: Deploy Everything

```bash
./deploy-microservices.sh
```

That's it! The script will:
1. ✅ Check/create .env file
2. ✅ Build Docker images
3. ✅ Start all services
4. ✅ Verify health
5. ✅ Display URLs

---

## Step 3: Access Services

### Main URLs

- **API Gateway:** http://localhost
- **Client App:** http://localhost:3002
- **Admin App:** http://localhost:3001

### API Endpoints

- **Backend:** http://localhost/api/*
- **Trading:** http://localhost/trading/*
- **WebSocket:** ws://localhost/ws

### Documentation

- **Backend Docs:** http://localhost:8000/docs
- **Trading Market:** http://localhost:8001/market/docs
- **Trading Features:** http://localhost:8001/trading/docs

---

## Quick Tests

```bash
# Test Gateway
curl http://localhost/health

# Test Backend
curl http://localhost/api/market/prices

# Test Trading API
curl http://localhost/trading/signals
```

---

## View Logs

```bash
# All services
docker-compose -f docker-compose.microservices.yml logs -f

# Specific service
docker-compose -f docker-compose.microservices.yml logs -f backend
```

---

## Stop Services

```bash
docker-compose -f docker-compose.microservices.yml down
```

---

## Troubleshooting

### Service not starting?

```bash
# Check status
docker-compose -f docker-compose.microservices.yml ps

# Check logs
docker-compose -f docker-compose.microservices.yml logs [service]

# Restart service
docker-compose -f docker-compose.microservices.yml restart [service]
```

### Port conflicts?

Edit `.env` file and change ports:
```bash
CLIENT_PORT=3003
ADMIN_PORT=3004
```

Then restart:
```bash
docker-compose -f docker-compose.microservices.yml up -d
```

---

## Need Help?

See complete documentation: `MICROSERVICES_INTEGRATION.md`
