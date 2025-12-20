# CI/CD Guide - Forexxx Trading Platform

## 📋 Overview

Dự án sử dụng GitHub Actions để tự động hóa quy trình build, test, và deployment. Tất cả workflows được cấu hình để đảm bảo chất lượng code và tính ổn định của hệ thống trước khi deploy.

## 🔄 Workflows

### 1. **CI - Full Stack Build & Test** (`ci-full-stack.yml`)
**Trigger:** Push/PR vào develop, staging, main  
**Mục đích:** Build và test tất cả services

**Jobs:**
- ✅ Backend Tests - Build và lint backend service
- ✅ Core-Main Tests - Build và lint core-main service  
- ✅ Client-App Tests - Build và lint frontend client
- ✅ Admin-App Tests - Build và lint admin dashboard
- 🐳 Docker Build Test - Verify tất cả Docker images build thành công

**Thời gian:** ~10-15 phút

---

### 2. **Integration Tests** (`integration-tests.yml`)
**Trigger:** Push/PR vào develop, staging, main  
**Mục đích:** Test tích hợp toàn bộ hệ thống

**Steps:**
1. Khởi động PostgreSQL & Redis
2. Chạy database migrations
3. Khởi động Backend & Core-Main services
4. Kiểm tra health endpoints
5. Chạy integration test suite
6. Thu thập logs nếu có lỗi

**Thời gian:** ~20-30 phút

---

### 3. **Code Quality & Security** (`code-quality.yml`)
**Trigger:** Push/PR vào develop, staging, main + Hàng tuần (Monday)  
**Mục đích:** Đảm bảo chất lượng code và bảo mật

**Checks:**
- 📝 ESLint cho tất cả services
- 🔒 NPM Security Audit
- 🐳 Dockerfile Linting (Hadolint)
- 📦 Dependency Review (trên PRs)
- 📊 Outdated Dependencies Report

**Thời gian:** ~8-12 phút

---

### 4. **Staging Deployment** (`staging.yml`)
**Trigger:** Push vào develop/staging hoặc manual dispatch  
**Mục đích:** Deploy lên môi trường staging

**Pipeline:**
1. **Test Phase** - Chạy tests và build
2. **Build Phase** - Build và push Docker images với tag `staging`
3. **Deploy Phase** - Deploy lên staging environment

**Môi trường:** Staging Server  
**Thời gian:** ~15-20 phút

---

### 5. **Production Deployment** (`production.yml`)
**Trigger:** Push vào main/master hoặc manual dispatch  
**Mục đích:** Deploy lên production

**Pipeline:**
1. **Test Phase** - Chạy full test suite
2. **Security Scan** - NPM audit với strict mode
3. **Build Phase** - Build và push Docker images với tags:
   - `latest`
   - `production-{sha}`
   - Custom version (nếu manual trigger)
4. **Deploy Phase** - Deploy với approval gate

**Môi trường:** Production (requires approval)  
**Thời gian:** ~20-30 phút

---

### 6. **Deployment Validation** (`deploy-validation.yml`)
**Trigger:** Sau khi staging/production deployment hoàn thành  
**Mục đích:** Validate deployment thành công

**Validation Checks:**
- ✅ Backend health endpoint
- ✅ Core-Main health endpoint
- 🔌 WebSocket connection test
- 📊 Trading data endpoints
- 📈 Real-time data stream
- ⚡ Performance test (response time < 2s)
- 💾 Database connection
- 🔴 Redis connection

**Thời gian:** ~3-5 phút

---

### 7. **Health Monitoring** (`health-monitoring.yml`)
**Trigger:** Mỗi 30 phút hoặc manual dispatch  
**Mục đích:** Giám sát sức khỏe hệ thống 24/7

**Monitors:**
- Production environment health
- Staging environment health
- Trading data flow
- Alert on failures

**Thời gian:** ~2-3 phút

---

### 8. **Data Validation** (`data-validation.yml`)
**Trigger:** Push/PR vào develop, staging, main  
**Mục đích:** Validate data integrity

**Checks:**
- Database schema verification
- Data integrity checks
- Data consistency validation

**Thời gian:** ~10-15 phút

---

### 9. **Automated Tests** (`tests.yml`)
**Trigger:** Push/PR vào develop, staging, main  
**Mục đích:** Run test suite

**Jobs:**
- Unit tests
- Smoke tests
- Build validation
- Linting
- Security audit

**Thời gian:** ~10-15 phút

---

## 🎯 Workflow Strategy

### Branch Strategy
```
main/master (production)
    ↑
staging (pre-production)
    ↑
develop (development)
    ↑
feature/* (feature branches)
```

### Workflow Execution per Branch

| Branch | Workflows Triggered |
|--------|-------------------|
| `feature/*` | Tests, Linting, Code Quality |
| `develop` | All CI + Integration Tests + Data Validation |
| `staging` | All CI + Staging Deployment + Validation |
| `main` | All CI + Production Deployment + Validation + Monitoring |

---

## 🔐 Required GitHub Secrets

Để workflows hoạt động, cần cấu hình các secrets sau trong GitHub repository:

### Docker Registry
- `DOCKER_REGISTRY` - Docker registry URL
- `DOCKER_USERNAME` - Registry username
- `DOCKER_PASSWORD` - Registry password/token

### Staging Environment
- `STAGING_URL` - Staging server URL
- `STAGING_API_BASE_URL` - API base URL
- `STAGING_WS_URL` - WebSocket URL

### Production Environment
- `PRODUCTION_URL` - Production server URL
- `PRODUCTION_API_BASE_URL` - API base URL
- `PRODUCTION_WS_URL` - WebSocket URL

---

## 🚀 Manual Deployment

### Staging Deployment
```bash
# Via GitHub CLI
gh workflow run staging.yml

# Via GitHub UI
Actions → Staging Deployment → Run workflow
```

### Production Deployment
```bash
# With version tag
gh workflow run production.yml -f version=v1.2.3

# Via GitHub UI
Actions → Production Deployment → Run workflow → Input version
```

---

## 📊 Monitoring Deployment

### Check Workflow Status
```bash
# List recent workflow runs
gh run list --workflow=production.yml

# Watch specific run
gh run watch <run-id>

# View logs
gh run view <run-id> --log
```

### Validate Deployment
```bash
# Trigger validation manually
gh workflow run deploy-validation.yml -f environment=production
```

---

## 🐛 Troubleshooting

### Build Failures
1. Check logs: `gh run view <run-id> --log`
2. Verify dependencies are up to date
3. Check Docker build context
4. Verify environment variables

### Test Failures
1. Review test logs in workflow output
2. Run tests locally: `npm test`
3. Check database/Redis connectivity
4. Verify test data setup

### Deployment Failures
1. Check deployment logs
2. Verify secrets are configured
3. Check server connectivity
4. Review health check endpoints

### Health Check Failures
1. Check service logs: `docker-compose logs <service>`
2. Verify database connectivity
3. Check Redis connection
4. Review environment variables

---

## 📈 Best Practices

### Before Pushing
```bash
# Run local tests
npm test

# Run linting
npm run lint

# Build locally
npm run build

# Test Docker build
docker-compose build
```

### Pull Request Guidelines
- Ensure all checks pass ✅
- Review code quality reports
- Check security audit results
- Verify integration tests pass
- Add meaningful commit messages

### Deployment Checklist
- [ ] All tests passing
- [ ] Code reviewed and approved
- [ ] No security vulnerabilities
- [ ] Database migrations ready
- [ ] Environment variables configured
- [ ] Rollback plan prepared
- [ ] Monitoring alerts configured

---

## 🔄 Rollback Procedure

### Staging Rollback
```bash
# Redeploy previous version
gh workflow run staging.yml

# Or use Docker tag
docker pull registry/client-app:staging-<previous-sha>
```

### Production Rollback
```bash
# Redeploy specific version
gh workflow run production.yml -f version=<previous-version>

# Or manual Docker rollback
docker pull registry/client-app:production-<previous-sha>
docker-compose up -d
```

---

## 📞 Support

Nếu gặp vấn đề với CI/CD:
1. Check workflow logs
2. Review documentation
3. Check GitHub Actions status
4. Contact DevOps team

---

## 📝 Changelog

### Latest Updates
- ✅ Added comprehensive CI/CD workflows
- ✅ Integrated health monitoring
- ✅ Added deployment validation
- ✅ Implemented code quality checks
- ✅ Added security auditing
- ✅ Configured multi-environment deployment
