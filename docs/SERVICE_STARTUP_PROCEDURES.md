# Service Startup Procedures

This document describes the procedures for starting all services in the CMEETRADING platform.

## Prerequisites

- Docker and Docker Compose installed
- All environment variables configured in `.env.production`
- Sufficient system resources (CPU, memory, disk)

## Standard Startup

### Start All Services

```bash
cd /root/forexxx
docker compose -f docker-compose.yml up -d
```

### Start Individual Services

```bash
# Start database
docker compose up -d postgres redis

# Start backend (after database is healthy)
docker compose up -d backend

# Start frontend applications
docker compose up -d client-app admin-app

# Start nginx proxy
docker compose up -d nginx-proxy
```

## Verification

After starting services, verify they are running:

```bash
# Check container status
docker compose ps

# Check health
./scripts/verify-deployment.sh

# Check logs
docker compose logs -f
```

## Service Dependencies

Services start in the following order:

1. **PostgreSQL** - Database service
2. **Redis** - Cache service
3. **Backend API** - Depends on PostgreSQL and Redis
4. **Client App** - Depends on Backend
5. **Admin App** - Depends on Backend
6. **Nginx Proxy** - Depends on all services

## Troubleshooting

### Services Not Starting

1. Check logs: `docker compose logs <service-name>`
2. Verify dependencies are healthy
3. Check system resources: `docker stats`
4. Review restart policies in `docker-compose.yml`

### Database Connection Issues

1. Verify PostgreSQL is running: `docker compose ps postgres`
2. Check connection: `docker exec digital_utopia_postgres pg_isready -U postgres`
3. Review database logs: `docker compose logs postgres`

### Backend Health Check Failing

1. Check backend logs: `docker compose logs backend`
2. Verify database and Redis connectivity
3. Review health endpoint: `curl http://localhost:8000/api/health`

## High Availability Startup

For HA setup:

```bash
docker compose -f docker-compose.yml -f docker-compose.ha.yml up -d
```

See `scripts/setup-ha.sh` for detailed HA setup procedures.
