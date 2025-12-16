# Smart Build & Deploy Scripts

Hệ thống build và deploy tự động với error handling, auto-fix, và real-time monitoring.

## Tổng Quan

Hệ thống bao gồm:

- **Smart Build**: Build tự động với error detection và auto-fix
- **Smart Deploy**: Deploy với retry logic và health checks
- **Error Handling**: Phát hiện và phân loại lỗi tự động
- **Auto-Fix**: Tự động sửa các lỗi phổ biến
- **Log Monitoring**: Real-time log monitoring và parsing
- **Status Monitoring**: Real-time service status updates

## Cấu Trúc

```
scripts/
├── lib/                    # Libraries
│   ├── error-handler.sh    # Error handling functions
│   ├── log-parser.sh       # Log parsing utilities
│   └── retry.sh           # Retry mechanism
├── config/                 # Configuration
│   ├── build-config.sh    # Build configuration
│   └── error-patterns.conf # Error patterns
├── run-all.sh              # Master script - chạy toàn bộ quy trình
├── smart-build.sh          # Smart build script
├── smart-deploy.sh         # Smart deploy script
├── monitor-logs.sh         # Log monitoring
├── error-detector.sh       # Error detection
├── auto-fix.sh            # Auto-fix strategies
└── status-monitor.sh      # Status monitoring
```

## Sử Dụng

### 🚀 Master Run Script (Khuyến nghị)

**Cách nhanh nhất để chạy toàn bộ quy trình:**

```bash
# Chạy từ thư mục gốc
./run-all.sh

# Hoặc từ thư mục scripts
./scripts/run-all.sh

# Với monitoring tự động sau khi deploy
./run-all.sh --monitor
```

**Script này sẽ tự động:**
1. ✅ Kiểm tra prerequisites (Docker, docker-compose, .env)
2. ✅ Chạy Smart Build cho tất cả services
3. ✅ Chạy Smart Deploy với health checks
4. ✅ Hiển thị summary và access URLs
5. ✅ (Optional) Bật monitoring nếu dùng flag `--monitor`

**Tính năng:**
- Pre-flight checks tự động
- Error handling và auto-fix
- Real-time progress tracking
- Comprehensive summary report
- Optional background monitoring

### Smart Build

Build với error handling và auto-fix:

```bash
# Build tất cả services
./scripts/smart-build.sh

# Build một service cụ thể
./scripts/smart-build.sh backend
```

**Tính năng:**
- Pre-build validation
- Resource checking
- Error detection trong quá trình build
- Auto-fix các lỗi có thể sửa
- Retry với exponential backoff
- Post-build verification

### Smart Deploy

Deploy với error handling và retry:

```bash
./scripts/smart-deploy.sh
```

**Tính năng:**
- Pre-deployment validation
- Dependency-aware deployment
- Real-time log monitoring
- Error detection và auto-fix
- Health checks cho mỗi service
- Retry failed deployments
- Post-deployment verification

### Monitor Logs

Monitor logs real-time:

```bash
# Monitor tất cả services
./scripts/monitor-logs.sh

# Monitor một service cụ thể
./scripts/monitor-logs.sh backend

# Monitor build logs
./scripts/monitor-logs.sh backend build
```

### Error Detection

Phát hiện và phân loại lỗi:

```bash
# Detect error từ text
./scripts/error-detector.sh detect "connection refused"

# Scan logs for errors
./scripts/error-detector.sh scan /path/to/logfile

# Get error suggestions
./scripts/error-detector.sh suggest "permission denied"
```

### Auto-Fix

Tự động sửa lỗi:

```bash
./scripts/auto-fix.sh "permission denied: /app/file"
```

**Các lỗi có thể auto-fix:**
- Permission errors
- Disk space issues
- Port conflicts
- Container conflicts
- Network issues
- Database connection issues
- Missing images

### Status Monitor

Monitor service status real-time:

```bash
# Monitor tất cả services
./scripts/status-monitor.sh monitor

# Get status một lần
./scripts/status-monitor.sh status

# Get status một service
./scripts/status-monitor.sh status backend
```

## Error Types

Hệ thống phân loại lỗi thành các loại:

- **BUILD**: Lỗi trong quá trình build
- **DEPLOY**: Lỗi trong quá trình deploy
- **NETWORK**: Lỗi mạng
- **DATABASE**: Lỗi database
- **CONFIG**: Lỗi cấu hình
- **PERMISSION**: Lỗi quyền truy cập
- **RESOURCE**: Lỗi tài nguyên (disk, memory)

## Error Severity

- **CRITICAL**: Lỗi nghiêm trọng, không thể tiếp tục
- **HIGH**: Lỗi cao, cần xử lý ngay
- **MEDIUM**: Lỗi trung bình, có thể retry
- **LOW**: Lỗi nhỏ, không ảnh hưởng nhiều

## Retry Mechanism

Hệ thống sử dụng exponential backoff:

- Initial delay: 2s
- Multiplier: 2x
- Max delay: 32s
- Max retries: 2-5 tùy loại operation

## Auto-Fix Strategies

### Build Auto-Fixes

1. **Missing dependencies**: Tự động install
2. **Permission issues**: Fix file permissions
3. **Network timeouts**: Retry với increased timeout
4. **Disk space**: Cleanup old images/containers
5. **Memory issues**: Adjust build resources

### Deployment Auto-Fixes

1. **Container conflicts**: Stop và remove conflicting containers
2. **Port conflicts**: Find alternative ports
3. **Database connection**: Wait và retry với backoff
4. **Migration errors**: Rollback và retry
5. **Configuration errors**: Validate và fix config

## Configuration

Cấu hình trong `scripts/config/build-config.sh`:

- Build settings (parallel, cache, timeout)
- Retry settings (max retries, delays)
- Resource limits (disk, memory, CPU)
- Service dependencies
- Health check intervals

## Error Patterns

Error patterns được định nghĩa trong `scripts/config/error-patterns.conf`:

- Build error patterns
- Network error patterns
- Database error patterns
- Permission error patterns
- Resource error patterns
- Config error patterns
- Deploy error patterns

## Logs

Logs được lưu tại:

- Build logs: `/tmp/build_<service>.log`
- Error log: `/tmp/build_errors.log`
- Monitor logs: Real-time output

## Troubleshooting

### Build Fails

1. Check error log: `cat /tmp/build_errors.log`
2. Check build logs: `cat /tmp/build_<service>.log`
3. Run error detector: `./scripts/error-detector.sh scan /tmp/build_<service>.log`
4. Try auto-fix: `./scripts/auto-fix.sh "<error message>"`

### Deploy Fails

1. Check service status: `./scripts/status-monitor.sh status`
2. Check logs: `docker-compose logs <service>`
3. Run health check: `./scripts/health-check.sh`
4. Monitor logs: `./scripts/monitor-logs.sh <service>`

### Services Not Healthy

1. Check dependencies: Ensure all dependencies are running
2. Check configuration: Verify .env file
3. Check resources: Disk space, memory
4. Check logs: `docker-compose logs <service>`

## Best Practices

1. **Always use smart-build.sh** thay vì build.sh cơ bản
2. **Always use smart-deploy.sh** thay vì deploy.sh cơ bản
3. **Monitor logs** trong quá trình build/deploy
4. **Check status** sau khi deploy
5. **Review error logs** nếu có lỗi
6. **Use auto-fix** trước khi manual fix

## Examples

### Full Build and Deploy

**Cách 1: Sử dụng Master Script (Khuyến nghị)**
```bash
# Chạy toàn bộ quy trình tự động
./run-all.sh

# Với monitoring
./run-all.sh --monitor
```

**Cách 2: Chạy từng bước thủ công**
```bash
# 1. Build
./scripts/smart-build.sh

# 2. Deploy
./scripts/smart-deploy.sh

# 3. Monitor status
./scripts/status-monitor.sh monitor
```

### Build với Monitoring

```bash
# Terminal 1: Build
./scripts/smart-build.sh

# Terminal 2: Monitor logs
./scripts/monitor-logs.sh
```

### Deploy với Error Handling

```bash
# Deploy với auto-fix
./scripts/smart-deploy.sh

# Nếu có lỗi, check và fix
./scripts/error-detector.sh scan /tmp/build_errors.log
./scripts/auto-fix.sh "<error message>"
```

## Support

Nếu gặp vấn đề:

1. Check logs: `/tmp/build_errors.log`
2. Run health check: `./scripts/health-check.sh`
3. Check status: `./scripts/status-monitor.sh status`
4. Review error patterns: `scripts/config/error-patterns.conf`

