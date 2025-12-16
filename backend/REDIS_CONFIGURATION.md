# Redis Configuration Documentation

## Tổng Quan

Redis được sử dụng trong Digital Utopia Platform cho:
- **Caching**: Cache dữ liệu user, portfolio, market data
- **Session Management**: Quản lý session của users
- **Rate Limiting**: Giới hạn số lượng requests
- **Real-time Updates**: Publish/Subscribe cho real-time notifications

## Cấu Hình

### Environment Variables

Redis configuration được quản lý qua các environment variables:

```bash
REDIS_HOST=redis              # Redis server hostname
REDIS_PORT=6379              # Redis server port
REDIS_PASSWORD=              # Redis password (optional)
REDIS_DB=0                   # Redis database number (0-15)
```

### Docker Compose Configuration

Trong `docker-compose.yml`, Redis được cấu hình như sau:

```yaml
redis:
  image: redis:7-alpine
  command: redis-server --requirepass ${REDIS_PASSWORD:-} --appendonly yes
```

**Lưu ý quan trọng:**
- Nếu `REDIS_PASSWORD` không được set (empty), Redis sẽ **KHÔNG** yêu cầu authentication
- Nếu `REDIS_PASSWORD` được set, Redis sẽ yêu cầu password cho tất cả operations
- `--appendonly yes` enables AOF (Append Only File) persistence

### Authentication

#### Khi Redis KHÔNG có password (Development)

1. Set `REDIS_PASSWORD` empty hoặc không set:
   ```bash
   REDIS_PASSWORD=
   ```

2. Redis sẽ chấp nhận connections mà không cần authentication

#### Khi Redis CÓ password (Production)

1. Set `REDIS_PASSWORD` trong environment:
   ```bash
   REDIS_PASSWORD=your-secure-password-here
   ```

2. Redis client sẽ tự động authenticate khi connect:
   ```python
   redis.Redis(
       host=settings.REDIS_HOST,
       port=settings.REDIS_PORT,
       password=settings.REDIS_PASSWORD,  # Auto authenticate
       db=settings.REDIS_DB
   )
   ```

### Connection Handling

Redis client trong `app/db/redis_client.py` xử lý authentication tự động:

```python
def connect(self) -> bool:
    try:
        self._client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,  # None nếu không có password
            db=settings.REDIS_DB,
            decode_responses=True,
            socket_timeout=5,
            socket_connect_timeout=5,
            retry_on_timeout=True
        )
        self._client.ping()  # Test connection
        return True
    except redis.ConnectionError:
        # Fallback to in-memory mode
        return False
```

**Behavior:**
- Nếu `REDIS_PASSWORD` là empty/None, client sẽ connect mà không authenticate
- Nếu `REDIS_PASSWORD` có giá trị, client sẽ authenticate tự động
- Nếu connection fails, application sẽ chạy ở "in-memory mode" (không có cache)

## Troubleshooting

### Lỗi "NOAUTH Authentication required"

**Nguyên nhân:** Redis server yêu cầu password nhưng client không cung cấp.

**Giải pháp:**
1. Kiểm tra `REDIS_PASSWORD` trong environment variables
2. Đảm bảo `REDIS_PASSWORD` được set đúng trong `docker-compose.yml` hoặc `.env` file
3. Restart Redis container sau khi thay đổi password

### Lỗi "Connection refused"

**Nguyên nhân:** Redis server không chạy hoặc không accessible.

**Giải pháp:**
1. Kiểm tra Redis container đang chạy:
   ```bash
   docker ps | grep redis
   ```

2. Kiểm tra Redis logs:
   ```bash
   docker logs digital_utopia_redis
   ```

3. Kiểm tra network connectivity:
   ```bash
   docker exec digital_utopia_backend ping redis
   ```

### Redis không cache dữ liệu

**Nguyên nhân:** Connection failed và application đang chạy ở in-memory mode.

**Giải pháp:**
1. Kiểm tra Redis connection status trong application logs
2. Verify Redis configuration trong `app/core/config.py`
3. Test Redis connection manually:
   ```bash
   docker exec -it digital_utopia_redis redis-cli ping
   ```

## Best Practices

### Development Environment

- **Không set password** để dễ dàng development và testing
- Sử dụng separate Redis database (db=1) để tránh conflict với production data

### Production Environment

- **Luôn set password** để bảo mật
- Sử dụng strong password (ít nhất 32 characters)
- Enable AOF persistence (`--appendonly yes`)
- Set up Redis backup strategy
- Monitor Redis memory usage

### Security

1. **Password Management:**
   - Store password trong environment variables, không hardcode
   - Use secrets management (AWS Secrets Manager, HashiCorp Vault, etc.)
   - Rotate passwords định kỳ

2. **Network Security:**
   - Redis chỉ accessible trong internal network
   - Không expose Redis port ra ngoài internet
   - Use firewall rules để restrict access

3. **Data Protection:**
   - Enable AOF persistence
   - Regular backups
   - Encrypt sensitive data trước khi cache

## Testing Redis Connection

### Manual Test

```bash
# Test từ backend container
docker exec -it digital_utopia_backend python -c "
from app.db.redis_client import init_redis
result = init_redis()
print('Redis connected:', result)
"
```

### Test với redis-cli

```bash
# Connect without password
docker exec -it digital_utopia_redis redis-cli

# Connect with password
docker exec -it digital_utopia_redis redis-cli -a your-password

# Test operations
> PING
PONG
> SET test "hello"
OK
> GET test
"hello"
```

## Configuration Files

- **Redis Client:** `backend/app/db/redis_client.py`
- **Docker Compose:** `docker-compose.yml`
- **Environment Config:** `backend/app/core/config.py`

## References

- [Redis Documentation](https://redis.io/docs/)
- [Redis Python Client](https://redis-py.readthedocs.io/)
- [Docker Redis Image](https://hub.docker.com/_/redis)

