"""
Cấu hình ứng dụng - Application Configuration
CMEETRADING

Quản lý tất cả cấu hình môi trường cho PostgreSQL, Redis, JWT, và các dịch vụ khác
"""

from pydantic_settings import BaseSettings
from typing import Optional, List
from functools import lru_cache
import os


class Settings(BaseSettings):
    """
    Cấu hình ứng dụng chính
    Đọc từ biến môi trường hoặc file .env
    """
    
    # =============== Cấu hình ứng dụng ===============
    APP_NAME: str = "CMEETRADING"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # =============== Cấu hình API ===============
    API_V1_STR: str = "/api"
    # QUAN TRỌNG: Phải thay đổi SECRET_KEY trong production thông qua biến môi trường
    SECRET_KEY: str = "CHANGE-THIS-IN-PRODUCTION-USE-ENV-VAR"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # =============== Cấu hình PostgreSQL ===============
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "digital_utopia"
    
    @property
    def DATABASE_URL(self) -> str:
        """Tạo URL kết nối PostgreSQL"""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def DATABASE_URL_ASYNC(self) -> str:
        """Tạo URL kết nối PostgreSQL cho async"""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # =============== Cấu hình Redis ===============
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    
    # Redis cache TTL settings (seconds)
    REDIS_SESSION_TTL: int = 86400  # 24 hours
    REDIS_CACHE_TTL: int = 300  # 5 minutes
    REDIS_RATE_LIMIT_TTL: int = 3600  # 1 hour
    REDIS_MARKET_DATA_TTL: int = 5  # 5 seconds for real-time data
    
    @property
    def REDIS_URL(self) -> str:
        """Tạo URL kết nối Redis"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # =============== Cấu hình CORS ===============
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:5173,http://localhost:5174,http://localhost:8080,https://cmeetrading.com,http://cmeetrading.com"
    
    @property
    def CORS_ORIGINS_LIST(self) -> List[str]:
        """Parse CORS_ORIGINS string thành list"""
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        return self.CORS_ORIGINS if isinstance(self.CORS_ORIGINS, list) else []
    
    # =============== Cấu hình Email ===============
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: str = "noreply@digitalutopia.com"
    EMAILS_FROM_NAME: str = "CMEETRADING"
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")  # Frontend URL for email links
    
    # =============== Cấu hình File Upload ===============
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "pdf", "doc", "docx"]
    
    # =============== Cấu hình Rate Limiting ===============
    RATE_LIMIT_PER_MINUTE: int = 1000  # 1000 requests per minute per IP
    RATE_LIMIT_PER_HOUR: int = 60000  # 60000 requests per hour (1000 * 60)
    
    # =============== Cấu hình Logging ===============
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    # Production logging format (JSON for log aggregation)
    LOG_FORMAT_JSON: bool = False  # Set to True in production for JSON logs
    LOG_FILE: Optional[str] = None  # Optional log file path
    LOG_ROTATION: str = "10 MB"  # Log rotation size
    LOG_RETENTION: str = "7 days"  # Log retention period
    
    # =============== Production Settings ===============
    # Worker configuration
    UVICORN_WORKERS: int = 4  # Number of uvicorn workers (2 * CPU cores + 1)
    UVICORN_TIMEOUT_KEEP_ALIVE: int = 65  # Keep-alive timeout in seconds
    
    # Performance settings
    MAX_CONCURRENT_REQUESTS: int = 1000  # Max concurrent requests
    REQUEST_TIMEOUT: int = 30  # Request timeout in seconds
    
    # Security settings
    ALLOWED_HOSTS: List[str] = ["*"]  # Allowed hosts (use specific domains in production)
    TRUSTED_PROXIES: List[str] = ["127.0.0.1", "::1"]  # Trusted proxy IPs
    
    # Database connection pool settings
    DB_POOL_SIZE: int = 20  # Connection pool size
    DB_MAX_OVERFLOW: int = 10  # Max overflow connections
    DB_POOL_TIMEOUT: int = 30  # Pool timeout in seconds
    DB_POOL_RECYCLE: int = 3600  # Connection recycle time in seconds
    
    # Redis connection pool settings
    REDIS_POOL_SIZE: int = 50  # Redis connection pool size
    REDIS_SOCKET_TIMEOUT: int = 5  # Socket timeout in seconds
    REDIS_SOCKET_CONNECT_TIMEOUT: int = 5  # Connection timeout in seconds
    
    # =============== OPEX Core Configuration ===============
    OPEX_API_URL: str = os.getenv("OPEX_API_URL", "http://core-main-api-1:8080")  # OPEX API service URL
    OPEX_MARKET_URL: str = os.getenv("OPEX_MARKET_URL", "http://core-main-market-1:8080")  # OPEX Market service URL
    OPEX_API_KEY: Optional[str] = os.getenv("OPEX_API_KEY", None)  # OPEX API key for authentication
    OPEX_API_SECRET: Optional[str] = os.getenv("OPEX_API_SECRET", None)  # OPEX API secret for X-API-SECRET auth
    OPEX_TIMEOUT: int = int(os.getenv("OPEX_TIMEOUT", "30"))  # OPEX API request timeout in seconds
    OPEX_WS_URL: str = os.getenv("OPEX_WS_URL", "ws://core-main-api-1:8080/ws")  # OPEX WebSocket URL
    
    # Monitoring and health check
    HEALTH_CHECK_INTERVAL: int = 30  # Health check interval in seconds
    METRICS_ENABLED: bool = True  # Enable metrics collection
    
    # =============== Nguồn dữ liệu thị trường ===============
    # external | opex (OPEX integration is primary, external APIs as fallback)
    MARKET_DATA_SOURCE: str = "external"  # Changed from "simulator" - simulator removed, using OPEX + external APIs
    ALLOW_EXTERNAL_FEEDS: bool = True
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.ENVIRONMENT.lower() == "development"
    
    @property
    def log_config(self) -> dict:
        """Get logging configuration based on environment"""
        if self.is_production and self.LOG_FORMAT_JSON:
            return {
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    "json": {
                        "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                        "format": "%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d"
                    }
                },
                "handlers": {
                    "console": {
                        "class": "logging.StreamHandler",
                        "formatter": "json",
                        "stream": "ext://sys.stdout"
                    }
                },
                "root": {
                    "level": self.LOG_LEVEL,
                    "handlers": ["console"]
                }
            }
        else:
            return {
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    "default": {
                        "format": self.LOG_FORMAT
                    }
                },
                "handlers": {
                    "console": {
                        "class": "logging.StreamHandler",
                        "formatter": "default",
                        "stream": "ext://sys.stdout"
                    }
                },
                "root": {
                    "level": self.LOG_LEVEL,
                    "handlers": ["console"]
                }
            }
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Allow extra fields from environment without validation errors


@lru_cache()
def get_settings() -> Settings:
    """
    Lấy instance settings (cached)
    Sử dụng lru_cache để tránh đọc file .env nhiều lần
    """
    return Settings()


# Global settings instance
settings = get_settings()
