# Runbooks

Common operational procedures and solutions for the CMEETRADING platform.

## Service Restart

### Restart All Services

```bash
cd /root/forexxx
docker compose restart
```

### Restart Specific Service

```bash
docker compose restart <service-name>
```

### Graceful Restart

```bash
# Stop services gracefully
docker compose stop

# Start services
docker compose start
```

## Backup and Restore

### Create Backup

```bash
./scripts/automated-backup.sh
```

### List Available Backups

```bash
./scripts/restore-procedure.sh list
```

### Restore Database

```bash
./scripts/restore-procedure.sh database /path/to/backup.sql.gz
```

### Restore Redis

```bash
./scripts/restore-procedure.sh redis /path/to/backup.rdb
```

### Restore Configuration

```bash
./scripts/restore-procedure.sh config /path/to/backup.tar.gz
```

## Monitoring

### Check System Health

```bash
# Run health checks
./scripts/verify-deployment.sh

# 24-hour monitoring
./scripts/24h-monitoring.sh

# Check container status
docker compose ps
```

### View Metrics

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000
- cAdvisor: http://localhost:8080

## Failover Procedures

### Backend Failover

```bash
./scripts/failover.sh backend
```

### Database Failover

```bash
./scripts/failover.sh database
```

## Deployment

### Standard Deployment

```bash
# Build images
docker compose build

# Deploy services
docker compose up -d

# Verify deployment
./scripts/verify-deployment.sh
```

### High Availability Deployment

```bash
# Setup HA
./scripts/setup-ha.sh

# Deploy HA services
docker compose -f docker-compose.yml -f docker-compose.ha.yml up -d
```

## Maintenance

### Update Services

```bash
# Pull latest images
docker compose pull

# Rebuild and restart
docker compose up -d --build
```

### Clean Up

```bash
# Remove stopped containers
docker compose down

# Remove volumes (WARNING: deletes data)
docker compose down -v

# Clean up unused resources
docker system prune -a
```

## Emergency Procedures

### Service Down

1. Check status: `docker compose ps`
2. Check logs: `docker compose logs <service>`
3. Restart service: `docker compose restart <service>`
4. If persistent, investigate: `./scripts/investigate-service-stoppage.sh`

### Database Issues

1. Check database status: `docker compose ps postgres`
2. Check logs: `docker compose logs postgres`
3. Verify connectivity: `docker exec digital_utopia_postgres pg_isready -U postgres`
4. If needed, restore from backup

### Complete System Failure

1. Stop all services: `docker compose down`
2. Check system resources: `free -h`, `df -h`
3. Review logs: `docker compose logs`
4. Restore from backup if necessary
5. Restart services: `docker compose up -d`

## Testing

### Run Integration Tests

```bash
./scripts/run-tests.sh integration
```

### Run Performance Tests

```bash
./scripts/run-tests.sh performance
```

### Test Production URLs

```bash
./scripts/test-production-urls.sh
```

## Configuration Updates

### Update Environment Variables

1. Edit `.env.production`
2. Restart affected services: `docker compose restart <service>`

### Update Nginx Configuration

1. Edit `nginx/nginx.conf`
2. Reload nginx: `docker compose exec nginx-proxy nginx -s reload`

### Update Docker Compose

1. Edit `docker-compose.yml`
2. Apply changes: `docker compose up -d`
