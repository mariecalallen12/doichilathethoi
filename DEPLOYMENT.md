# Digital Utopia Platform - Hướng Dẫn Triển Khai

Tài liệu này hướng dẫn chi tiết cách triển khai Digital Utopia Platform trên Docker cho môi trường production.

**Status:** ✅ Production Ready - Version 2.0.0  
**Last Updated:** 2025-01-09

> **Note:** For complete production deployment guide, see [PRODUCTION_DEPLOYMENT_COMPLETE.md](PRODUCTION_DEPLOYMENT_COMPLETE.md)

## Yêu Cầu Hệ Thống

- Docker Engine 20.10+
- Docker Compose 2.0+
- Tối thiểu 4GB RAM
- Tối thiểu 20GB dung lượng ổ cứng
- Linux/Unix hoặc macOS

## Cấu Trúc Dự Án

```
/root/forexxx/
├── docker-compose.yml          # Main compose file
├── docker-compose.prod.yml     # Production overrides
├── env.example                 # Environment template
├── scripts/                    # Deployment scripts
│   ├── init-db.sh             # Database initialization
│   ├── run-migrations.sh      # Run Alembic migrations
│   ├── seed-data.sh           # Seed initial data
│   ├── build.sh               # Build all images
│   ├── deploy.sh              # Deploy stack
│   ├── verify-api.sh          # Verify API endpoints
│   └── health-check.sh        # Health check all services
├── backend/
│   ├── Dockerfile             # Backend container
│   ├── entrypoint.sh          # Entrypoint script
│   └── ...
├── client-app/
│   ├── Dockerfile             # Client app container
│   └── ...
└── Admin-app/
    ├── Dockerfile             # Admin app container
    └── ...
```

## Quy Trình Triển Khai

### Bước 1: Chuẩn Bị Môi Trường

1. **Tạo file .env từ template:**

```bash
cp env.example .env
nano .env
```

2. **Cập nhật các giá trị quan trọng trong .env:**

- `POSTGRES_PASSWORD`: Mật khẩu mạnh cho PostgreSQL
- `REDIS_PASSWORD`: Mật khẩu cho Redis (có thể để trống cho dev)
- `SECRET_KEY`: Generate một secret key ngẫu nhiên:
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
- `CORS_ORIGINS`: Các domain được phép truy cập API

### Bước 2: Build Docker Images

```bash
./scripts/build.sh
```

Hoặc build thủ công:

```bash
docker-compose build
```

### Bước 3: Triển Khai Services

Sử dụng script tự động (khuyến nghị):

```bash
./scripts/deploy.sh
```

Hoặc triển khai thủ công:

```bash
# 1. Start database services
docker-compose up -d postgres redis

# 2. Đợi databases sẵn sàng (30 giây)
sleep 30

# 3. Start backend
docker-compose up -d backend

# 4. Đợi backend sẵn sàng
sleep 20

# 5. Chạy migrations
./scripts/run-migrations.sh

# 6. Seed initial data (optional)
./scripts/seed-data.sh

# 7. Start frontend apps
docker-compose up -d client-app admin-app
```

### Bước 4: Kiểm Tra Triển Khai

1. **Health check:**

```bash
./scripts/health-check.sh
```

2. **Verify API:**

```bash
./scripts/verify-api.sh
```

3. **Kiểm tra thủ công:**

```bash
# Backend health
curl http://localhost:8000/api/health

# API Documentation
curl http://localhost:8000/docs

# Client app
curl http://localhost:3002

# Admin app
curl http://localhost:3001
```

## Các Lệnh Quản Lý

### Xem Logs

```bash
# Tất cả services
docker-compose logs -f

# Chỉ backend
docker-compose logs -f backend

# Chỉ database
docker-compose logs -f postgres
```

### Restart Services

```bash
# Restart tất cả
docker-compose restart

# Restart một service cụ thể
docker-compose restart backend
```

### Stop Services

```bash
# Stop nhưng giữ data
docker-compose down

# Stop và xóa volumes (CẨN THẬN - mất data)
docker-compose down -v
```

### Database Migrations

```bash
# Chạy migrations
./scripts/run-migrations.sh

# Hoặc thủ công
docker-compose exec backend alembic upgrade head

# Xem migration history
docker-compose exec backend alembic history

# Rollback migration
docker-compose exec backend alembic downgrade -1
```

### Seed Data

```bash
./scripts/seed-data.sh
```

## Triển Khai Production

### Production Deployment Checklist

Trước khi triển khai production, đảm bảo:

#### Pre-Deployment Checklist

- [ ] `.env.production` file đã được tạo và cấu hình đúng
- [ ] Tất cả passwords đã được thay đổi từ mặc định
- [ ] `SECRET_KEY` đã được generate (32+ ký tự ngẫu nhiên)
- [ ] Database backup đã được tạo
- [ ] Docker images đã được build với production config
- [ ] Database migrations đã được kiểm tra
- [ ] Health checks đã được test
- [ ] SSL certificates đã được cấu hình (nếu dùng HTTPS)
- [ ] Firewall rules đã được cấu hình
- [ ] Monitoring tools đã được setup

#### Deployment Steps

1. **Build production images:**
   ```bash
   ./scripts/build-production.sh --service=all --version=v2.0.0
   ```

2. **Run pre-deployment checks:**
   ```bash
   ./scripts/deploy-production.sh --dry-run
   ```

3. **Deploy to production:**
   ```bash
   ./scripts/deploy-production.sh --service=all --version=v2.0.0
   ```

4. **Verify deployment:**
   ```bash
   ./scripts/health-check.sh
   curl http://localhost:8000/api/health
   ```

**Lưu ý Production:**

1. **Bảo mật:**
   - Đổi tất cả passwords mặc định
   - Generate SECRET_KEY mạnh
   - Không expose database ports ra ngoài
   - Sử dụng reverse proxy (Nginx) với SSL
   - Rate limiting đã được cấu hình (1000 requests/min)

2. **Monitoring:**
   - Thiết lập log rotation
   - Cấu hình monitoring tools
   - Thiết lập alerts

3. **Backup:**
   - Backup database định kỳ
   - Backup Redis data nếu cần
   - Test restore procedure

### Rollback Procedures

#### Automatic Rollback

Deployment script tự động rollback nếu health check fails:

```bash
# Script sẽ tự động rollback nếu deployment fails
./scripts/deploy-production.sh --service=backend
```

#### Manual Rollback

1. **List available backups:**
   ```bash
   docker images | grep backup-
   ```

2. **Rollback to specific version:**
   ```bash
   ./scripts/deploy-production.sh --rollback=backup-20251211-120000
   ```

3. **Rollback specific service:**
   ```bash
   # Rollback backend
   docker tag digital_utopia_backend:backup-YYYYMMDD-HHMMSS digital_utopia_backend:latest
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d backend
   
   # Rollback client-app
   docker tag digital_utopia_client:backup-YYYYMMDD-HHMMSS digital_utopia_client:latest
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d client-app
   
   # Rollback admin-app
   docker tag digital_utopia_admin:backup-YYYYMMDD-HHMMSS digital_utopia_admin:latest
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d admin-app
   ```

4. **Database rollback (if needed):**
   ```bash
   ./scripts/restore-database.sh ./backups/backup_YYYYMMDD_HHMMSS.dump
   ```

#### Rollback Verification

Sau khi rollback, verify:

```bash
# Check service health
curl http://localhost:8000/api/health
curl http://localhost:3002/health
curl http://localhost:3001/health

# Check logs
docker-compose logs --tail=50 backend
```

### Monitoring Setup Guide

#### 1. Log Monitoring

**View logs:**
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend

# Since specific time
docker-compose logs --since 30m backend
```

**Log rotation:**
- Configured in `docker-compose.prod.yml`
- Max size: 10MB per file
- Max files: 3 for backend, 2 for frontend

#### 2. Health Monitoring

**Health check endpoints:**
- Backend: `http://localhost:8000/api/health`
- Client-app: `http://localhost:3002/health`
- Admin-app: `http://localhost:3001/health`

**Automated health checks:**
```bash
# Run health check script
./scripts/health-check.sh

# Or manually
curl -f http://localhost:8000/api/health && echo "Backend OK" || echo "Backend FAILED"
```

#### 3. Resource Monitoring

**Container stats:**
```bash
# Real-time stats
docker stats

# Specific container
docker stats digital_utopia_backend
```

**Disk usage:**
```bash
# Docker disk usage
docker system df

# Volume sizes
docker volume ls
docker volume inspect digital_utopia_postgres_data
```

#### 4. Database Monitoring

**Connection monitoring:**
```bash
# Active connections
docker exec digital_utopia_postgres psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"

# Database size
docker exec digital_utopia_postgres psql -U postgres -c "SELECT pg_size_pretty(pg_database_size('digital_utopia'));"
```

#### 5. Application Monitoring

**API monitoring:**
```bash
# Test API response time
time curl -s http://localhost:8000/api/health

# Check API documentation
curl http://localhost:8000/docs
```

**WebSocket monitoring:**
```bash
# Check WebSocket connections (if monitoring tool available)
# Or check backend logs for WebSocket activity
docker-compose logs backend | grep websocket
```

#### 6. Alerting Setup

**Example alert script:**
```bash
#!/bin/bash
# scripts/check-health.sh

ALERT_EMAIL="admin@example.com"

# Check backend
if ! curl -f -s http://localhost:8000/api/health > /dev/null; then
  echo "Backend health check failed!" | mail -s "Alert: Backend Down" $ALERT_EMAIL
fi

# Check disk space
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 80 ]; then
  echo "Disk usage is ${DISK_USAGE}%!" | mail -s "Alert: High Disk Usage" $ALERT_EMAIL
fi
```

**Cron job for monitoring:**
```bash
# Add to crontab
*/5 * * * * /path/to/scripts/check-health.sh
```

#### 7. Performance Monitoring

**Key metrics to monitor:**
- Response time (API endpoints)
- Error rate
- Database query performance
- Memory usage
- CPU usage
- Disk I/O
- Network traffic

**Tools recommendation:**
- Prometheus + Grafana for metrics
- ELK Stack for log aggregation
- Sentry for error tracking
- New Relic / Datadog for APM

## Troubleshooting

### Database Connection Issues

```bash
# Kiểm tra PostgreSQL logs
docker-compose logs postgres

# Test connection từ backend
docker-compose exec backend python -c "from app.db.session import check_db_connection; print(check_db_connection())"
```

### Migration Failures

```bash
# Xem migration status
docker-compose exec backend alembic current

# Xem migration history
docker-compose exec backend alembic history

# Rollback nếu cần
docker-compose exec backend alembic downgrade -1
```

### Backend Không Khởi Động

```bash
# Xem logs
docker-compose logs backend

# Kiểm tra environment variables
docker-compose exec backend env | grep POSTGRES

# Test database connection
docker-compose exec backend psql -h postgres -U postgres -d digital_utopia -c "SELECT 1"
```

### Redis Connection Issues

```bash
# Test Redis connection
docker-compose exec redis redis-cli ping

# Với password
docker-compose exec redis redis-cli -a YOUR_PASSWORD ping
```

## URLs Sau Khi Triển Khai

- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Client App:** http://localhost:3002
- **Admin App:** http://localhost:3001

## Verification Checklist

Sau khi triển khai, kiểm tra:

- [ ] PostgreSQL container running
- [ ] Redis container running
- [ ] Backend container running
- [ ] Database migrations completed
- [ ] All tables created (45+ tables)
- [ ] Backend health endpoint returns 200
- [ ] Swagger docs accessible
- [ ] Client app accessible
- [ ] Admin app accessible
- [ ] No errors in logs

## Hỗ Trợ

Nếu gặp vấn đề, kiểm tra:

1. Logs của các services
2. Environment variables trong .env
3. Network connectivity giữa containers
4. Database và Redis connections

## Tài Liệu Tham Khảo

- [DIGITAL_UTOPIA_DATABASE_SCHEMA.md](DIGITAL_UTOPIA_DATABASE_SCHEMA.md) - Database schema
- [README.md](README.md) - Tổng quan dự án
- [backend/app/core/config.py](backend/app/core/config.py) - Configuration

