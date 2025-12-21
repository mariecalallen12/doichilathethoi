"""
Database Session Management
Digital Utopia Platform

Quản lý SQLAlchemy engine, session, và kết nối PostgreSQL
"""

from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import QueuePool, AsyncAdaptedQueuePool
from typing import Generator, AsyncGenerator
from contextlib import asynccontextmanager
import logging

from ..core.config import settings

logger = logging.getLogger(__name__)

# =============== Tạo SQLAlchemy Engine ===============
# Sử dụng connection pooling để tối ưu hiệu suất

engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,  # Số kết nối cơ bản trong pool
    max_overflow=20,  # Số kết nối tối đa có thể tạo thêm
    pool_timeout=30,  # Thời gian chờ kết nối (giây)
    pool_recycle=1800,  # Tái tạo kết nối sau 30 phút
    pool_pre_ping=True,  # Kiểm tra kết nối trước khi sử dụng
    echo=settings.DEBUG,  # Log SQL queries trong debug mode
)

# =============== Tạo Async Engine ===============
# Convert postgresql:// to postgresql+asyncpg://
async_database_url = settings.DATABASE_URL.replace(
    "postgresql://", "postgresql+asyncpg://"
).replace(
    "postgres://", "postgresql+asyncpg://"
)

async_engine = create_async_engine(
    async_database_url,
    poolclass=AsyncAdaptedQueuePool,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

# =============== Tạo Session Factory ===============
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# =============== Tạo Async Session Factory ===============
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# =============== Base class cho models ===============
Base = declarative_base()


# =============== Event Listeners ===============
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """
    Cấu hình connection khi kết nối mới được tạo
    """
    logger.debug("New database connection established")


@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """
    Log khi connection được lấy từ pool
    """
    logger.debug("Connection checked out from pool")


@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_conn, connection_record):
    """
    Log khi connection được trả về pool
    """
    logger.debug("Connection returned to pool")


# =============== Dependency Injection ===============
def get_db() -> Generator[Session, None, None]:
    """
    Dependency để inject database session vào endpoints
    
    Sử dụng:
        @router.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency để inject async database session vào async endpoints
    
    Sử dụng:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_async_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    
    Yields:
        AsyncSession: SQLAlchemy async database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@asynccontextmanager
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager để sử dụng async session trong code
    
    Sử dụng:
        async with async_session() as db:
            result = await db.execute(select(User))
            users = result.scalars().all()
    
    Yields:
        AsyncSession: SQLAlchemy async database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def init_db():
    """
    Khởi tạo database - tạo tất cả các bảng
    Sử dụng trong startup của ứng dụng
    """
    # Import tất cả models để đảm bảo chúng được đăng ký với Base
    from ..models import (
        user, trading, financial, compliance, 
        portfolio, referral, audit
    )
    
    # Tạo tất cả bảng
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


def drop_db():
    """
    Xóa tất cả bảng trong database
    CHỈ SỬ DỤNG TRONG TESTING!
    """
    Base.metadata.drop_all(bind=engine)
    logger.warning("All database tables dropped!")


# =============== Health Check ===============
def check_db_connection(max_retries: int = 3, retry_delay: int = 2) -> bool:
    """
    Kiểm tra kết nối database với retry logic
    
    Args:
        max_retries: Số lần thử lại tối đa
        retry_delay: Thời gian chờ giữa các lần thử (giây)
    
    Returns:
        True nếu kết nối thành công
    """
    import time
    
    for attempt in range(1, max_retries + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info(f"Database connection successful (attempt {attempt})")
            return True
        except Exception as e:
            if attempt < max_retries:
                logger.warning(f"Database connection attempt {attempt} failed: {e}. Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                logger.error(f"Database connection failed after {max_retries} attempts: {e}")
                return False
    
    return False
