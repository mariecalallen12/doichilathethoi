"""add_timescaledb_support

Revision ID: 20250109_001_add_timescaledb_support
Revises: 20250108_002_add_auto_approve_fields
Create Date: 2025-01-09 12:00:00.000000

Migration để:
1. Enable TimescaleDB extension
2. Convert market_data_history thành hypertable
3. Tạo bảng price_tick cho tick data storage
4. Tạo continuous aggregates cho OHLCV
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20250109_001_add_timescaledb_support'
down_revision: Union[str, None] = '20250108_002_add_auto_approve_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Enable TimescaleDB và tạo các bảng/time-series structures
    """
    
    # 1. Enable TimescaleDB extension
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;")
    
    # 2. Tạo bảng price_tick cho tick data
    op.create_table(
        'price_tick',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('symbol', sa.String(20), nullable=False),
        sa.Column('price', sa.DECIMAL(20, 8), nullable=False),
        sa.Column('volume', sa.DECIMAL(20, 8), nullable=False, server_default='0'),
        sa.Column('ts', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('source', sa.String(50), nullable=True, server_default='simulator'),
        sa.PrimaryKeyConstraint('id', 'ts'),  # Include ts in primary key for TimescaleDB
        sa.Index('ix_price_tick_symbol_ts', 'symbol', 'ts'),
        sa.Index('ix_price_tick_ts', 'ts'),
    )
    
    # 3. Convert price_tick thành hypertable (partition theo time)
    op.execute("""
        SELECT create_hypertable('price_tick', 'ts', 
            chunk_time_interval => INTERVAL '1 day',
            if_not_exists => TRUE
        );
    """)
    
    # 4. Convert market_data_history thành hypertable nếu chưa phải
    # Kiểm tra xem đã là hypertable chưa
    # Note: Chỉ convert nếu primary key đã bao gồm timestamp
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM timescaledb_information.hypertables 
                WHERE hypertable_name = 'market_data_history'
            ) THEN
                -- Kiểm tra xem primary key có chứa timestamp không
                IF EXISTS (
                    SELECT 1 FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu 
                        ON tc.constraint_name = kcu.constraint_name
                    WHERE tc.table_name = 'market_data_history' 
                        AND tc.constraint_type = 'PRIMARY KEY'
                        AND kcu.column_name = 'timestamp'
                ) THEN
                    PERFORM create_hypertable(
                        'market_data_history', 
                        'timestamp',
                        chunk_time_interval => INTERVAL '7 days',
                        if_not_exists => TRUE
                    );
                END IF;
            END IF;
        END $$;
    """)
    
    # 5. Tạo continuous aggregates cho OHLCV (1m, 5m, 15m, 1h, 4h, 1d)
    # 1-minute candles
    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS ohlcv_1m
        WITH (timescaledb.continuous) AS
        SELECT 
            time_bucket('1 minute', ts) AS bucket,
            symbol,
            FIRST(price, ts) AS open,
            MAX(price) AS high,
            MIN(price) AS low,
            LAST(price, ts) AS close,
            SUM(volume) AS volume,
            COUNT(*) AS tick_count
        FROM price_tick
        GROUP BY bucket, symbol
        WITH NO DATA;
    """)
    
    # Tạo index cho continuous aggregate
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_ohlcv_1m_symbol_bucket 
        ON ohlcv_1m (symbol, bucket DESC);
    """)
    
    # 5-minute candles
    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS ohlcv_5m
        WITH (timescaledb.continuous) AS
        SELECT 
            time_bucket('5 minutes', ts) AS bucket,
            symbol,
            FIRST(price, ts) AS open,
            MAX(price) AS high,
            MIN(price) AS low,
            LAST(price, ts) AS close,
            SUM(volume) AS volume,
            COUNT(*) AS tick_count
        FROM price_tick
        GROUP BY bucket, symbol
        WITH NO DATA;
    """)
    
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_ohlcv_5m_symbol_bucket 
        ON ohlcv_5m (symbol, bucket DESC);
    """)
    
    # 15-minute candles
    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS ohlcv_15m
        WITH (timescaledb.continuous) AS
        SELECT 
            time_bucket('15 minutes', ts) AS bucket,
            symbol,
            FIRST(price, ts) AS open,
            MAX(price) AS high,
            MIN(price) AS low,
            LAST(price, ts) AS close,
            SUM(volume) AS volume,
            COUNT(*) AS tick_count
        FROM price_tick
        GROUP BY bucket, symbol
        WITH NO DATA;
    """)
    
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_ohlcv_15m_symbol_bucket 
        ON ohlcv_15m (symbol, bucket DESC);
    """)
    
    # 1-hour candles
    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS ohlcv_1h
        WITH (timescaledb.continuous) AS
        SELECT 
            time_bucket('1 hour', ts) AS bucket,
            symbol,
            FIRST(price, ts) AS open,
            MAX(price) AS high,
            MIN(price) AS low,
            LAST(price, ts) AS close,
            SUM(volume) AS volume,
            COUNT(*) AS tick_count
        FROM price_tick
        GROUP BY bucket, symbol
        WITH NO DATA;
    """)
    
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_ohlcv_1h_symbol_bucket 
        ON ohlcv_1h (symbol, bucket DESC);
    """)
    
    # 4-hour candles
    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS ohlcv_4h
        WITH (timescaledb.continuous) AS
        SELECT 
            time_bucket('4 hours', ts) AS bucket,
            symbol,
            FIRST(price, ts) AS open,
            MAX(price) AS high,
            MIN(price) AS low,
            LAST(price, ts) AS close,
            SUM(volume) AS volume,
            COUNT(*) AS tick_count
        FROM price_tick
        GROUP BY bucket, symbol
        WITH NO DATA;
    """)
    
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_ohlcv_4h_symbol_bucket 
        ON ohlcv_4h (symbol, bucket DESC);
    """)
    
    # 1-day candles
    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS ohlcv_1d
        WITH (timescaledb.continuous) AS
        SELECT 
            time_bucket('1 day', ts) AS bucket,
            symbol,
            FIRST(price, ts) AS open,
            MAX(price) AS high,
            MIN(price) AS low,
            LAST(price, ts) AS close,
            SUM(volume) AS volume,
            COUNT(*) AS tick_count
        FROM price_tick
        GROUP BY bucket, symbol
        WITH NO DATA;
    """)
    
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_ohlcv_1d_symbol_bucket 
        ON ohlcv_1d (symbol, bucket DESC);
    """)
    
    # Add refresh policies cho continuous aggregates
    # Refresh mỗi 1 phút cho 1m candles
    op.execute("""
        SELECT add_continuous_aggregate_policy('ohlcv_1m',
            start_offset => INTERVAL '1 hour',
            end_offset => INTERVAL '1 minute',
            schedule_interval => INTERVAL '1 minute',
            if_not_exists => TRUE
        );
    """)
    
    # Refresh mỗi 5 phút cho 5m candles
    op.execute("""
        SELECT add_continuous_aggregate_policy('ohlcv_5m',
            start_offset => INTERVAL '1 day',
            end_offset => INTERVAL '5 minutes',
            schedule_interval => INTERVAL '5 minutes',
            if_not_exists => TRUE
        );
    """)


def downgrade() -> None:
    """
    Xóa TimescaleDB structures
    """
    # Drop continuous aggregates
    op.execute("DROP MATERIALIZED VIEW IF EXISTS ohlcv_1d CASCADE;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS ohlcv_4h CASCADE;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS ohlcv_1h CASCADE;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS ohlcv_15m CASCADE;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS ohlcv_5m CASCADE;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS ohlcv_1m CASCADE;")
    
    # Drop price_tick table (hypertable sẽ tự drop)
    op.drop_table('price_tick')
    
    # Note: Không drop TimescaleDB extension vì có thể được dùng bởi các bảng khác

