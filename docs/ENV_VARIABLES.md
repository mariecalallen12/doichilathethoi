# Environment Variables Documentation

**Digital Utopia Platform**  
**Version:** 2.0.0  
**Last Updated:** 2025-12-20

---

## Overview

This document describes all environment variables used in the Digital Utopia Platform.

## Configuration Files

Located in `config/` directory:

- `.env.example` - Master template with all variables
- `.env.development` - Development defaults
- `.env.staging.template` - Staging template
- `.env.production.template` - Production template

## Required Variables

### Application

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ENV` | Environment name | `development` | ✅ |
| `DEBUG` | Debug mode | `true` | ✅ |
| `APP_NAME` | Application name | `Digital Utopia Platform` | ✅ |
| `APP_VERSION` | Application version | `2.0.0` | ✅ |
| `SECRET_KEY` | JWT secret key | - | ✅ |
| `ALGORITHM` | JWT algorithm | `HS256` | ✅ |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry | `30` | ✅ |

### Database (PostgreSQL)

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_NAME` | Database name | `digital_utopia` | ✅ |
| `DATABASE_USER` | Database user | `postgres` | ✅ |
| `DATABASE_PASSWORD` | Database password | - | ✅ |
| `DATABASE_HOST` | Database host | `localhost` | ✅ |
| `DATABASE_PORT` | Database port | `5432` | ✅ |
| `DATABASE_URL` | Full connection URL | (computed) | ✅ |

### Redis

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `REDIS_HOST` | Redis host | `localhost` | ✅ |
| `REDIS_PORT` | Redis port | `6379` | ✅ |
| `REDIS_PASSWORD` | Redis password | - | ✅ |
| `REDIS_URL` | Full connection URL | (computed) | ✅ |

### OPEX Core Integration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPEX_API_URL` | OPEX API endpoint | `http://localhost:8080` | ✅ |
| `OPEX_MARKET_URL` | Market service URL | `http://localhost:8081` | ✅ |
| `OPEX_WS_URL` | WebSocket URL | `ws://localhost:8080/ws` | ✅ |
| `OPEX_API_KEY` | API key | - | ✅ |
| `OPEX_API_SECRET` | API secret | - | ✅ |
| `OPEX_TIMEOUT` | Request timeout (seconds) | `30` | ❌ |
| `OPEX_PROFILE` | OPEX profile | `production` | ❌ |

### OPEX Database

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPEX_DATABASE_NAME` | OPEX database name | `opex_core` | ✅ |
| `OPEX_DATABASE_USER` | OPEX database user | `opex` | ✅ |
| `OPEX_DATABASE_PASSWORD` | OPEX database password | - | ✅ |
| `OPEX_DATABASE_URL` | Full connection URL | (computed) | ✅ |
| `OPEX_REDIS_URL` | OPEX Redis URL | - | ✅ |

### Ports

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `BACKEND_PORT` | Backend API port | `8000` | ❌ |
| `CLIENT_PORT` | Client app port | `3000` | ❌ |
| `ADMIN_PORT` | Admin app port | `3001` | ❌ |
| `NGINX_HTTP_PORT` | Nginx HTTP port | `80` | ❌ |
| `NGINX_HTTPS_PORT` | Nginx HTTPS port | `443` | ❌ |

### CORS

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `CORS_ORIGINS` | Allowed origins (comma-separated) | `http://localhost:3000,http://localhost:3001` | ✅ |

### Frontend API URLs

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `VITE_API_BASE_URL` | Backend API URL | `http://localhost:8000` | ✅ |
| `VITE_WS_URL` | WebSocket URL | `ws://localhost:8000/ws` | ✅ |
| `CLIENT_API_BASE_URL` | Client API base | `http://localhost:8000` | ✅ |
| `ADMIN_API_BASE_URL` | Admin API base | `http://localhost:8000` | ✅ |

### Monitoring

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PROMETHEUS_PORT` | Prometheus port | `9090` | ❌ |
| `GRAFANA_PORT` | Grafana port | `3333` | ❌ |
| `GRAFANA_USER` | Grafana username | `admin` | ✅ |
| `GRAFANA_PASSWORD` | Grafana password | - | ✅ |
| `LOKI_PORT` | Loki port | `3100` | ❌ |
| `ALERTMANAGER_PORT` | Alertmanager port | `9093` | ❌ |

### Email

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MAIL_SERVER` | SMTP server | `mailhog` (dev) | ✅ |
| `MAIL_PORT` | SMTP port | `1025` | ✅ |
| `MAIL_FROM` | From address | `noreply@digitalutopia.com` | ✅ |

### Domain (Production)

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DOMAIN` | Production domain | - | ✅ (prod) |
| `FRONTEND_URL` | Frontend URL | `https://${DOMAIN}` | ✅ (prod) |

### Security

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ALLOWED_HOSTS` | Allowed hosts | `localhost,127.0.0.1` | ✅ |
| `CSRF_TRUSTED_ORIGINS` | CSRF trusted origins | - | ✅ |

### Logging

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `LOG_LEVEL` | Logging level | `INFO` | ❌ |
| `LOG_FILE` | Log file path | `/var/log/app.log` | ❌ |

### Feature Flags

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ENABLE_OPEX` | Enable OPEX integration | `true` | ❌ |
| `ENABLE_MOCK_TRADING` | Enable mock trading | `true` | ❌ |
| `ENABLE_MONITORING` | Enable monitoring | `true` | ❌ |
| `ENABLE_WEBSOCKET` | Enable WebSocket | `true` | ❌ |

### Backup

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `BACKUP_RETENTION_DAYS` | Backup retention | `30` | ❌ |
| `BACKUP_PATH` | Backup directory | `/backups` | ❌ |

---

## Environment-Specific Values

### Development

```bash
ENV=development
DEBUG=true
ENABLE_OPEX=false
ENABLE_MOCK_TRADING=true
ENABLE_MONITORING=false
LOG_LEVEL=DEBUG
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours
```

### Staging

```bash
ENV=staging
DEBUG=false
ENABLE_OPEX=true
ENABLE_MOCK_TRADING=false
ENABLE_MONITORING=true
LOG_LEVEL=INFO
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Production

```bash
ENV=production
DEBUG=false
ENABLE_OPEX=true
ENABLE_MOCK_TRADING=false
ENABLE_MONITORING=true
LOG_LEVEL=WARNING
ACCESS_TOKEN_EXPIRE_MINUTES=15
```

---

## Security Best Practices

### Secret Key Generation

```bash
# Generate secure random key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Password Requirements

- **Development:** Any password (for convenience)
- **Staging:** Strong passwords (12+ chars, mixed case, numbers, symbols)
- **Production:** Very strong passwords (16+ chars, mixed case, numbers, symbols)

### Never Commit Secrets

❌ **Never commit these files:**
- `.env`
- `.env.local`
- `.env.production`
- Any file with actual secrets

✅ **Safe to commit:**
- `.env.example`
- `.env.*.template`
- `config/.env.example`

---

## Validation

Use the validation script to check required variables:

```bash
./scripts/validate/validate-env.sh
```

---

## Troubleshooting

### Missing Variable Error

```
Error: DATABASE_URL environment variable is required
```

**Solution:** Check `.env` file and ensure variable is set.

### Invalid Value

```
Error: REDIS_PORT must be a number
```

**Solution:** Verify variable value format matches expected type.

### Database Connection Failed

**Check:**
1. `DATABASE_HOST` is correct
2. `DATABASE_PORT` is correct
3. `DATABASE_USER` has permissions
4. `DATABASE_PASSWORD` is correct
5. Database is running

---

## Support

For issues, see:
- [Deployment Runbook](./deployment/DEPLOYMENT_RUNBOOK.md)
- [Quick Start Guide](./QUICK_START.md)
- [Architecture Overview](./architecture/ARCHITECTURE.md)
