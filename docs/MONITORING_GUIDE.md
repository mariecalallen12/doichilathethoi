# Monitoring Guide

Comprehensive guide to monitoring the CMEETRADING platform.

## Monitoring Stack

### Components

- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboards
- **cAdvisor**: Container metrics
- **Node Exporter**: System metrics
- **Alertmanager**: Alert routing and notifications
- **Loki**: Log aggregation
- **Promtail**: Log collection

## Starting Monitoring Services

```bash
# Start monitoring stack
docker compose -f docker-compose.monitoring.yml up -d

# Start logging stack
docker compose -f docker-compose.logging.yml up -d
```

## Accessing Monitoring Tools

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)
- **cAdvisor**: http://localhost:8080
- **Node Exporter**: http://localhost:9100/metrics
- **Alertmanager**: http://localhost:9093

## Dashboards

### System Health Dashboard

- Container status
- CPU usage
- Memory usage
- Disk usage

### Application Performance Dashboard

- API response times (p95, p99)
- Request rates
- Error rates
- Database query performance
- Redis hit rate

### Business Metrics Dashboard

- Active users
- Total requests
- Success rate
- User activity over time

## Metrics to Monitor

### System Metrics

- CPU usage: Target < 70%
- Memory usage: Target < 80%
- Disk usage: Target < 85%
- Network traffic

### Application Metrics

- API response time: Target p95 < 500ms
- Error rate: Target < 1%
- Request rate
- Endpoint performance

### Database Metrics

- Connection pool usage
- Query performance
- Database size
- Replication lag (if applicable)

### Redis Metrics

- Memory usage
- Hit rate: Target > 80%
- Connection count
- Command latency

## Alerts

### Critical Alerts (P0)

- Service down
- Error rate > 5%
- Response time p95 > 2s
- Database connection failures
- Memory usage > 90%

### Warning Alerts (P1)

- Error rate > 2%
- Response time p95 > 1s
- CPU usage > 80%
- Disk usage > 85%
- Redis connection issues

### Medium Priority Alerts (P2)

- Error rate > 1%
- Response time p95 > 500ms
- CPU usage > 70%
- Unusual traffic patterns

## Log Monitoring

### Viewing Logs

```bash
# Container logs
docker compose logs -f

# Aggregated logs
./scripts/log-aggregation.sh

# Loki logs (via Grafana)
# Access Grafana and navigate to Explore > Loki
```

### Log Levels

- **ERROR**: Critical errors requiring immediate attention
- **WARN**: Warnings that may indicate issues
- **INFO**: General information about system operation
- **DEBUG**: Detailed debugging information

## Health Checks

### Automated Health Checks

```bash
# Run health check script
./scripts/health-check.sh

# 24-hour monitoring
./scripts/24h-monitoring.sh

# Verify deployment
./scripts/verify-deployment.sh
```

### Manual Health Checks

```bash
# Backend health
curl http://localhost:8000/api/health

# Client app
curl http://localhost:3002/health

# Admin app
curl http://localhost:3001/health
```

## Best Practices

1. **Regular Monitoring**: Check dashboards daily
2. **Alert Response**: Respond to alerts promptly
3. **Log Review**: Review logs regularly for anomalies
4. **Performance Baseline**: Establish performance baselines
5. **Capacity Planning**: Monitor resource usage trends

## Troubleshooting Monitoring

### Prometheus Not Collecting Metrics

1. Check Prometheus status: `docker compose ps prometheus`
2. Review Prometheus logs: `docker compose logs prometheus`
3. Verify scrape targets in Prometheus UI
4. Check network connectivity

### Grafana Dashboards Not Loading

1. Verify Prometheus datasource is configured
2. Check dashboard JSON files
3. Review Grafana logs: `docker compose logs grafana`
4. Verify metrics are available in Prometheus

### Alerts Not Firing

1. Check Alertmanager configuration
2. Verify alert rules in Prometheus
3. Test alert routing
4. Check notification channels
