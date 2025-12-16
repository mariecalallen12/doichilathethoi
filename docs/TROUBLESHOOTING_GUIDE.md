# Troubleshooting Guide

Common issues and solutions for the CMEETRADING platform.

## Container Issues

### Container Not Starting

**Symptoms:**
- Container status shows "Exited" or "Created"
- Service not accessible

**Solutions:**
1. Check logs: `docker compose logs <service-name>`
2. Verify restart policy: `docker inspect <container-name> | grep RestartPolicy`
3. Check resource limits: `docker stats`
4. Review dependencies: Ensure dependent services are healthy

### Container Restarting Continuously

**Symptoms:**
- Container keeps restarting
- High restart count

**Solutions:**
1. Check application logs for errors
2. Verify health check configuration
3. Check resource constraints (memory, CPU)
4. Review startup scripts for issues

## Database Issues

### Database Connection Failed

**Symptoms:**
- Backend cannot connect to database
- Connection timeout errors

**Solutions:**
1. Verify PostgreSQL is running: `docker compose ps postgres`
2. Check database logs: `docker compose logs postgres`
3. Verify connection string in environment variables
4. Test connection: `docker exec digital_utopia_postgres pg_isready -U postgres`

### Database Performance Issues

**Symptoms:**
- Slow queries
- High connection count

**Solutions:**
1. Check active connections: `docker exec digital_utopia_postgres psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"`
2. Review slow queries: Check PostgreSQL logs
3. Optimize database indexes
4. Consider connection pooling

## Backend Issues

### Backend Health Check Failing

**Symptoms:**
- Health endpoint returns error
- Container marked as unhealthy

**Solutions:**
1. Check backend logs: `docker compose logs backend`
2. Verify database and Redis connectivity
3. Test health endpoint: `curl http://localhost:8000/api/health`
4. Review health check configuration in `docker-compose.yml`

### API Endpoints Not Responding

**Symptoms:**
- 404 or 500 errors
- Timeout errors

**Solutions:**
1. Check backend logs for errors
2. Verify route configuration
3. Check CORS settings
4. Review nginx proxy configuration

## Frontend Issues

### Client/Admin App Not Loading

**Symptoms:**
- White screen
- 404 errors
- Assets not loading

**Solutions:**
1. Check container logs: `docker compose logs client-app`
2. Verify nginx configuration
3. Check API base URL configuration
4. Review browser console for errors

## Network Issues

### Services Cannot Communicate

**Symptoms:**
- Connection refused errors
- Network timeout

**Solutions:**
1. Verify all containers are on the same network: `docker network inspect digital_utopia_network`
2. Check service names match docker-compose configuration
3. Review network configuration
4. Test connectivity: `docker exec <container> ping <other-container>`

## Performance Issues

### High CPU Usage

**Symptoms:**
- System slow
- High load average

**Solutions:**
1. Check resource usage: `docker stats`
2. Identify resource-intensive containers
3. Review application code for optimization
4. Consider scaling services

### High Memory Usage

**Symptoms:**
- Out of memory errors
- Containers being killed

**Solutions:**
1. Check memory usage: `free -h` and `docker stats`
2. Review memory limits in docker-compose.yml
3. Configure swap space: `./scripts/configure-swap.sh`
4. Optimize application memory usage

## Monitoring and Logs

### Viewing Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend

# Last 100 lines
docker compose logs --tail 100 backend
```

### Health Checks

```bash
# Run verification script
./scripts/verify-deployment.sh

# Check individual service health
curl http://localhost:8000/api/health
```

### Monitoring

- Access Prometheus: http://localhost:9090
- Access Grafana: http://localhost:3000
- View monitoring dashboards

## Getting Help

If issues persist:

1. Collect logs: `docker compose logs > logs.txt`
2. Run diagnostics: `./scripts/investigate-service-stoppage.sh`
3. Check system resources
4. Review recent changes to configuration
