"""
Portfolio module endpoints for FastAPI.
Migrated from Next.js portfolio API routes with full business logic preservation.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Literal
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ...dependencies import get_current_user
from ...db.session import get_db
from ...models.user import User
from ...models.trading import PortfolioPosition, TradingOrder
from ...models.financial import WalletBalance, Transaction
from ...services.portfolio_service import PortfolioService
from app.schemas.portfolio import (
    # Analytics schemas
    PortfolioAnalyticsRequest,
    PortfolioReportRequest,
    PortfolioAnalyticsResponse,
    PortfolioReportResponse,
    PortfolioAnalytics,
    
    # Metrics schemas
    PortfolioMetricsResponse,
    PortfolioMetrics,
    RecalculateMetricsRequest,
    
    # Position close schemas
    PositionCloseResponse,
    PositionCloseRequest,
    
    # Rebalancing schemas
    RebalancingRequest,
    RebalancingResponse,
    RebalancingRecommendationsResponse,
    
    # Trading bots schemas
    TradingBotsResponse,
    TradingBotResponse,
    CreateTradingBotRequest,
    UpdateTradingBotRequest,
    DeleteTradingBotRequest,
    TradingBotsQuery,
    
    # Watchlist schemas
    WatchlistResponse,
    AddToWatchlistRequest,
    RemoveFromWatchlistRequest,
    
    # Generic schemas
    ApiResponse,
    ApiError
)

router = APIRouter()


# ============================================================================
# PORTFOLIO ANALYTICS ENDPOINTS
# ============================================================================

@router.get("/analytics", response_model=PortfolioAnalyticsResponse)
async def get_portfolio_analytics(
    period: Literal['1D', '7D', '30D', '90D', '1Y', 'ALL'] = Query(default='30D', description="Analysis period"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get portfolio analytics for specified period from real database data
    GET /api/portfolio/analytics
    """
    try:
        from datetime import datetime, timedelta
        from app.models.trading import TradingOrder, PortfolioPosition
        from app.models.financial import WalletBalance, Transaction
        
        # Calculate date range based on period
        end_date = datetime.utcnow()
        if period == '1D':
            start_date = end_date - timedelta(days=1)
        elif period == '7D':
            start_date = end_date - timedelta(days=7)
        elif period == '30D':
            start_date = end_date - timedelta(days=30)
        elif period == '90D':
            start_date = end_date - timedelta(days=90)
        elif period == '1Y':
            start_date = end_date - timedelta(days=365)
        else:  # ALL
            start_date = None
        
        # Get portfolio positions
        positions_query = db.query(PortfolioPosition).filter(
            PortfolioPosition.user_id == current_user.id
        )
        if start_date:
            positions_query = positions_query.filter(
                PortfolioPosition.created_at >= start_date
            )
        positions = positions_query.all()
        
        # Get wallet balances
        balances = db.query(WalletBalance).filter(
            WalletBalance.user_id == current_user.id
        ).all()
        
        # Get transactions for performance history
        transactions_query = db.query(Transaction).filter(
            Transaction.user_id == current_user.id,
            Transaction.transaction_type.in_(['deposit', 'withdrawal', 'trading'])
        )
        if start_date:
            transactions_query = transactions_query.filter(
                Transaction.created_at >= start_date
            )
        transactions = transactions_query.order_by(Transaction.created_at.asc()).all()
        
        # Calculate current portfolio value
        total_balance = sum(float(b.available_balance or 0) + float(b.locked_balance or 0) for b in balances)
        total_market_value = sum(float(p.market_value or 0) for p in positions if not p.is_closed)
        total_value = total_balance + total_market_value
        
        # Build performance history from transactions
        performance_history = []
        running_balance = 0
        for tx in transactions:
            if tx.transaction_type == 'deposit':
                running_balance += float(tx.amount or 0)
            elif tx.transaction_type == 'withdrawal':
                running_balance -= float(tx.amount or 0)
            # For trading transactions, calculate based on P&L if available
            performance_history.append({
                'date': tx.created_at.isoformat() if tx.created_at else datetime.utcnow().isoformat(),
                'value': running_balance
            })
        
        # If no transactions, use current value
        if not performance_history:
            performance_history = [{
                'date': datetime.utcnow().isoformat(),
                'value': total_value
            }]
        
        # Calculate returns
        if len(performance_history) > 1:
            initial_value = performance_history[0]['value']
            final_value = performance_history[-1]['value']
            total_return = ((final_value - initial_value) / initial_value * 100) if initial_value > 0 else 0
        else:
            total_return = 0
        
        analytics_data = {
            "period": period,
            "total_value": total_value,
            "total_balance": total_balance,
            "total_market_value": total_market_value,
            "total_return": round(total_return, 2),
            "performance_history": performance_history[-30:] if len(performance_history) > 30 else performance_history,  # Last 30 data points
            "position_count": len([p for p in positions if not p.is_closed]),
            "total_positions": len(positions)
        }
        
        return PortfolioAnalyticsResponse(
            success=True,
            data=PortfolioAnalytics(**analytics_data)
        )

    except HTTPException:
        raise
    except Exception as error:
        print(f"Portfolio Analytics Error: {error}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi lấy dữ liệu analytics: {str(error)}"
        )


@router.post("/analytics/report", response_model=PortfolioReportResponse)
async def generate_portfolio_report(
    request: PortfolioReportRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate comprehensive portfolio report
    POST /api/portfolio/analytics/report
    """
    try:
        raise HTTPException(
            status_code=501,
            detail="Portfolio report chưa được triển khai trên dữ liệu lịch sử thực tế"
        )

    except HTTPException:
        raise
    except Exception as error:
        print(f"Generate Portfolio Report Error: {error}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi tạo báo cáo: {str(error)}"
        )


# ============================================================================
# PORTFOLIO METRICS ENDPOINTS
# ============================================================================

@router.get("/metrics", response_model=PortfolioMetricsResponse)
async def get_portfolio_metrics(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get portfolio metrics (DB-based)
    GET /api/portfolio/metrics
    """
    try:
        user_id = current_user.id

        service = PortfolioService(db)

        # Lấy summary và metrics thực tế từ DB
        summary = service.get_portfolio_summary(user_id)
        metrics_raw = service.get_portfolio_metrics(user_id)

        # Lấy balances để tách available / locked
        balances = db.query(WalletBalance).filter(WalletBalance.user_id == user_id).all()
        available_balance = sum(float(b.available_balance or 0) for b in balances)
        locked_balance = sum(float(b.locked_balance or 0) for b in balances)

        total_balance = available_balance + locked_balance
        total_pnl = float(summary.get("total_pnl", 0.0))
        total_pnl_percent = (total_pnl / total_balance * 100) if total_balance > 0 else 0.0

        # Chuẩn hoá phân bổ theo symbol từ summary.position_breakdown
        position_breakdown = summary.get("position_breakdown", {}) or {}
        total_market_value = float(summary.get("total_market_value", 0.0))

        assets: Dict[str, Any] = {}
        for symbol, info in position_breakdown.items():
            value = float(info.get("market_value", 0.0))
            pnl = float(info.get("unrealized_pnl", 0.0))
            allocation = (value / total_market_value * 100) if total_market_value > 0 else 0.0
            pnl_percent = (pnl / value * 100) if value > 0 else 0.0
            assets[symbol] = {
                "balance": float(info.get("quantity", 0.0)),
                "value": value,
                "allocation": allocation,
                "pnl": pnl,
                "pnl_percent": pnl_percent,
            }

        # Tính thêm các chỉ số hiệu suất dựa trên positions đã đóng
        closed_positions = (
            db.query(PortfolioPosition)
            .filter(PortfolioPosition.user_id == user_id, PortfolioPosition.is_closed == True)
            .all()
        )
        wins = [float(p.realized_pnl or 0) for p in closed_positions if float(p.realized_pnl or 0) > 0]
        losses = [float(p.realized_pnl or 0) for p in closed_positions if float(p.realized_pnl or 0) < 0]

        avg_win = (sum(wins) / len(wins)) if wins else 0.0
        avg_loss = (sum(losses) / len(losses)) if losses else 0.0
        profit_factor = (sum(wins) / abs(sum(losses))) if losses and sum(losses) != 0 else 0.0

        performance = {
            "total_return": total_pnl,
            "total_return_percent": total_pnl_percent,
            "max_drawdown": float(metrics_raw.get("max_drawdown", 0.0)),
            "sharpe_ratio": 0.0,
            "win_rate": float(metrics_raw.get("win_rate", 0.0)),
            "average_win": round(avg_win, 2),
            "average_loss": round(avg_loss, 2),
            "profit_factor": round(profit_factor, 2) if profit_factor else 0.0,
        }

        risk = {
            "var95": 0.0,
            "var99": 0.0,
            "beta": 0.0,
            "correlation": {},
        }

        metrics = PortfolioMetrics(
            total_balance=total_balance,
            available_balance=available_balance,
            used_margin=locked_balance,
            total_pnl=total_pnl,
            total_pnl_percent=total_pnl_percent,
            daily_pnl=0.0,
            daily_pnl_percent=0.0,
            assets=assets,
            performance=performance,
            risk=risk,
            updated_at=datetime.now(),
        )

        return PortfolioMetricsResponse(
            success=True,
            data=metrics,
            metadata={
                "timestamp": datetime.now(),
                "source": "db"
            }
        )

    except HTTPException:
        raise
    except Exception as error:
        print(f"Get Portfolio Metrics Error: {error}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi lấy dữ liệu metrics: {str(error)}"
        )


@router.post("/metrics/recalculate", response_model=PortfolioMetricsResponse)
async def recalculate_portfolio_metrics(
    request: RecalculateMetricsRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Recalculate portfolio metrics
    POST /api/portfolio/metrics/recalculate
    """
    try:
        # Hiện tại metrics luôn lấy trực tiếp từ DB, nên recalculate chỉ gọi lại get_portfolio_metrics
        return await get_portfolio_metrics(current_user=current_user, db=db)

    except HTTPException:
        raise
    except Exception as error:
        print(f"Recalculate Portfolio Metrics Error: {error}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi tính lại metrics: {str(error)}"
        )


# ============================================================================
# POSITION CLOSE ENDPOINT
# ============================================================================

@router.post("/positions/{position_id}/close", response_model=PositionCloseResponse)
async def close_portfolio_position(
    position_id: int = Path(..., description="Position ID to close"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Close a portfolio position
    POST /api/portfolio/positions/{positionId}/close
    """
    try:
        user_id = current_user.id

        # Lấy position thực tế từ DB
        position = (
            db.query(PortfolioPosition)
            .filter(
                PortfolioPosition.id == position_id,
                PortfolioPosition.user_id == user_id,
                PortfolioPosition.is_closed == False,
            )
            .first()
        )

        if not position:
            raise HTTPException(status_code=404, detail="Không tìm thấy vị thế đang mở")

        # Xác định giá hiện tại: ưu tiên market_value / quantity, fallback về average_price
        if position.market_value and position.quantity:
            current_price = float(position.market_value) / float(position.quantity)
        else:
            current_price = float(position.average_price)

        size = float(position.quantity)
        entry_price = float(position.average_price)
        is_long = position.position_type == "long"

        if is_long:
            pnl = (current_price - entry_price) * size
        else:
            pnl = (entry_price - current_price) * size

        # Đóng position trong DB
        position.is_closed = True
        position.closed_at = datetime.utcnow()
        position.closed_price = current_price
        position.closed_reason = "manual"
        position.realized_pnl = pnl
        db.commit()
        db.refresh(position)

        close_result = {
            "position_id": str(position.id),
            "symbol": position.symbol,
            "side": position.position_type,
            "size": size,
            "entry_price": entry_price,
            "close_price": current_price,
            "pnl": pnl,
            "pnl_percent": pnl / (entry_price * size) if entry_price * size != 0 else 0.0,
            "close_time": position.closed_at.isoformat() if position.closed_at else datetime.utcnow().isoformat(),
        }

        return PositionCloseResponse(
            success=True,
            message="Đóng vị thế thành công",
            data=close_result
        )

    except HTTPException:
        raise
    except Exception as error:
        print(f"Close position error: {error}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi đóng vị thế: {str(error)}"
        )


# ============================================================================
# PORTFOLIO REBALANCING ENDPOINTS
# ============================================================================

@router.post("/rebalancing", response_model=RebalancingResponse)
async def create_rebalancing_order(
    request: RebalancingRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Create portfolio rebalancing order
    POST /api/portfolio/rebalancing
    """
    try:
        # Chưa có engine thực thi rebalancing trên DB
        raise HTTPException(
            status_code=501,
            detail="Portfolio rebalancing chưa được triển khai trên dữ liệu thực tế"
        )

    except HTTPException:
        raise
    except Exception as error:
        print(f"Create Rebalancing Order Error: {error}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi tạo lệnh rebalancing: {str(error)}"
        )


@router.get("/rebalancing/recommendations", response_model=RebalancingRecommendationsResponse)
async def get_rebalancing_recommendations(current_user: dict = Depends(get_current_user)):
    """
    Get rebalancing recommendations
    GET /api/portfolio/rebalancing/recommendations
    """
    try:
        raise HTTPException(
            status_code=501,
            detail="Portfolio rebalancing recommendations chưa được triển khai trên dữ liệu thực tế"
        )

    except HTTPException:
        raise
    except Exception as error:
        print(f"Get Rebalancing Recommendations Error: {error}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi lấy khuyến nghị: {str(error)}"
        )


# ============================================================================
# TRADING BOTS ENDPOINTS
# ============================================================================

@router.get("/trading-bots", response_model=TradingBotsResponse)
async def get_trading_bots(
    status: Optional[Literal['STARTED', 'PAUSED', 'STOPPED']] = Query(None),
    limit: int = Query(default=50, ge=1, le=100),
    page: int = Query(default=1, ge=1),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's trading bots
    GET /api/portfolio/trading-bots
    """
    try:
        user_id = current_user.id

        service = PortfolioService(db)
        bots = service.get_user_bots(user_id)

        # Áp dụng phân trang đơn giản phía server
        total = len(bots)
        start = (page - 1) * limit
        end = start + limit
        bots_page = bots[start:end]

        def map_bot(bot) -> Dict[str, Any]:
            return {
                "bot_id": str(bot.id),
                "user_id": str(bot.user_id),
                "name": bot.name,
                "strategy": {
                    "strategy_id": bot.strategy_id or "",
                    "user_id": str(bot.user_id),
                    "name": bot.strategy_name or bot.name,
                    "description": bot.description or "",
                    "strategy_type": "custom",
                    "parameters": bot.strategy_parameters or {},
                    "performance": {},
                    "status": bot.status,
                    "created_at": bot.created_at,
                    "updated_at": bot.updated_at,
                },
                "status": bot.status or "PAUSED",
                "config": {
                    "symbols": bot.symbols or [],
                    "base_amount": float(bot.base_amount or 0),
                    "leverage": int(bot.leverage or 1),
                    "max_concurrent_orders": int(bot.max_positions or 5),
                    "risk_management": {
                        "risk_per_trade": float(bot.risk_per_trade or 1),
                    },
                },
                "performance": {
                    "total_trades": int(bot.total_trades or 0),
                    "success_rate": (
                        (float(bot.winning_trades or 0) / float(bot.total_trades or 1) * 100)
                        if bot.total_trades
                        else 0.0
                    ),
                    "total_pnl": float(bot.total_pnl or 0),
                    "total_pnl_percent": 0.0,
                    "average_trade_time": 0.0,
                    "max_drawdown": float(bot.max_drawdown or 0),
                },
                "logs": bot.logs or [],
                "created_at": bot.created_at,
                "updated_at": bot.updated_at,
            }

        data = [map_bot(b) for b in bots_page]

        return TradingBotsResponse(
            success=True,
            data=data,
            metadata={
                "timestamp": datetime.now(),
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "has_next": end < total,
                    "has_prev": page > 1,
                },
            },
        )

    except HTTPException:
        raise
    except Exception as error:
        print(f"Get Trading Bots Error: {error}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi lấy danh sách bot: {str(error)}"
        )


@router.post("/trading-bots", response_model=TradingBotResponse)
async def create_trading_bot(
    request: CreateTradingBotRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create trading bot
    POST /api/portfolio/trading-bots
    """
    try:
        user_id = current_user.id

        if not request.name or not request.strategy or not request.config:
            raise HTTPException(status_code=400, detail="Thiếu tham số bắt buộc")

        strategy_name = request.strategy.get("name", f"{request.name} Strategy")
        symbols = request.config.get("symbols", [])
        base_amount = request.config.get("base_amount", 0)

        service = PortfolioService(db)
        bot = service.create_trading_bot(
            user_id=user_id,
            name=request.name,
            strategy_name=strategy_name,
            symbols=symbols,
            base_amount=base_amount,
            strategy_parameters=request.strategy.get("parameters", {}),
        )

        data = {
            "bot_id": str(bot.id),
            "user_id": str(bot.user_id),
            "name": bot.name,
            "strategy": {
                "strategy_id": bot.strategy_id or "",
                "user_id": str(bot.user_id),
                "name": bot.strategy_name or bot.name,
                "description": bot.description or "",
                "strategy_type": "custom",
                "parameters": bot.strategy_parameters or {},
                "performance": {},
                "status": bot.status,
                "created_at": bot.created_at,
                "updated_at": bot.updated_at,
            },
            "status": "STARTED" if request.start_immediately else bot.status,
            "config": request.config,
            "performance": {
                "total_trades": int(bot.total_trades or 0),
                "success_rate": 0.0,
                "total_pnl": float(bot.total_pnl or 0),
                "total_pnl_percent": 0.0,
                "average_trade_time": 0.0,
                "max_drawdown": float(bot.max_drawdown or 0),
            },
            "logs": bot.logs or [],
            "created_at": bot.created_at,
            "updated_at": bot.updated_at,
        }

        return TradingBotResponse(
            success=True,
            data=data,
            metadata={
                "timestamp": datetime.now()
            }
        )

    except HTTPException:
        raise
    except Exception as error:
        print(f"Create Trading Bot Error: {error}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi tạo bot: {str(error)}"
        )


@router.patch("/trading-bots", response_model=TradingBotResponse)
async def update_trading_bot(
    request: UpdateTradingBotRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update trading bot
    PATCH /api/portfolio/trading-bots
    """
    try:
        user_id = current_user.id

        if not request.bot_id:
            raise HTTPException(status_code=400, detail="Bot ID là bắt buộc")

        service = PortfolioService(db)

        # Lấy bot và verify ownership
        try:
            bot_id_int = int(request.bot_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Bot ID không hợp lệ")

        bots = service.get_user_bots(user_id)
        bot = next((b for b in bots if b.id == bot_id_int), None)
        if not bot:
            raise HTTPException(status_code=404, detail="Không tìm thấy bot")

        # Cập nhật các trường
        if request.name is not None:
            bot.name = request.name
        if request.strategy is not None:
            bot.strategy_name = request.strategy.get("name", bot.strategy_name)
            bot.strategy_parameters = request.strategy.get("parameters", bot.strategy_parameters)
        if request.config is not None:
            bot.symbols = request.config.get("symbols", bot.symbols)
            bot.base_amount = request.config.get("base_amount", bot.base_amount)
            bot.leverage = request.config.get("leverage", bot.leverage)

        if request.status is not None:
            # dùng service để cập nhật status (log, timestamps,…)
            bot = service.update_bot_status(bot_id_int, user_id, request.status)
        else:
            db.commit()
            db.refresh(bot)

        data = {
            "bot_id": str(bot.id),
            "user_id": str(bot.user_id),
            "status": bot.status,
            "name": bot.name,
            "config": {
                "symbols": bot.symbols or [],
                "base_amount": float(bot.base_amount or 0),
                "leverage": int(bot.leverage or 1),
                "max_concurrent_orders": int(bot.max_positions or 5),
                "risk_management": {
                    "risk_per_trade": float(bot.risk_per_trade or 1),
                },
            },
            "strategy": {
                "strategy_id": bot.strategy_id or "",
                "user_id": str(bot.user_id),
                "name": bot.strategy_name or bot.name,
                "description": bot.description or "",
                "strategy_type": "custom",
                "parameters": bot.strategy_parameters or {},
                "performance": {},
                "status": bot.status,
                "created_at": bot.created_at,
                "updated_at": bot.updated_at,
            },
            "updated_at": bot.updated_at or datetime.utcnow(),
        }

        return TradingBotResponse(
            success=True,
            data=data,
            metadata={
                "timestamp": datetime.now()
            }
        )

    except HTTPException:
        raise
    except Exception as error:
        print(f"Update Trading Bot Error: {error}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi cập nhật bot: {str(error)}"
        )


@router.delete("/trading-bots", response_model=TradingBotResponse)
async def delete_trading_bot(
    request: DeleteTradingBotRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete trading bot
    DELETE /api/portfolio/trading-bots
    """
    try:
        user_id = current_user.id

        if not request.bot_id:
            raise HTTPException(status_code=400, detail="Bot ID là bắt buộc")

        try:
            bot_id_int = int(request.bot_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Bot ID không hợp lệ")

        service = PortfolioService(db)
        deleted = service.delete_bot(bot_id_int, user_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Không tìm thấy bot hoặc không có quyền xoá")

        return TradingBotResponse(
            success=True,
            data={"bot_id": request.bot_id, "status": "DELETED"},
            metadata={
                "timestamp": datetime.now()
            }
        )

    except HTTPException:
        raise
    except Exception as error:
        print(f"Delete Trading Bot Error: {error}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi xóa bot: {str(error)}"
        )


# ============================================================================
# WATCHLIST ENDPOINTS
# ============================================================================

@router.get("/watchlist", response_model=WatchlistResponse)
async def get_watchlist(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's watchlist
    GET /api/portfolio/watchlist
    """
    try:
        user_id = current_user.id

        service = PortfolioService(db)
        watchlists = service.get_user_watchlist(user_id)

        # Lấy watchlist default nếu có, nếu không trả về list trống
        default_watchlist = next((w for w in watchlists if w.is_default), None)
        symbols = default_watchlist.symbols if default_watchlist else []

        return WatchlistResponse(
            success=True,
            data={
                "symbols": symbols,
                "is_default": True if default_watchlist else False
            }
        )

    except HTTPException:
        raise
    except Exception as error:
        print(f"Get watchlist error: {error}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi lấy danh sách theo dõi: {str(error)}"
        )


@router.post("/watchlist", response_model=WatchlistResponse)
async def add_to_watchlist(
    request: AddToWatchlistRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add symbol to watchlist
    POST /api/portfolio/watchlist
    """
    try:
        user_id = current_user.id

        if not request.symbol:
            raise HTTPException(status_code=400, detail="Symbol là bắt buộc")

        symbol_upper = request.symbol.upper().strip()

        # Validate symbol format
        import re
        symbol_regex = r'^[A-Z]{3,10}(USDT|USD|EUR|JPY|GBP|CAD|AUD|CHF)?$'
        if not re.match(symbol_regex, symbol_upper):
            raise HTTPException(status_code=400, detail="Định dạng symbol không hợp lệ")

        service = PortfolioService(db)
        watchlist = service.add_to_watchlist(user_id=user_id, symbol=symbol_upper)

        return WatchlistResponse(
            success=True,
            data={
                "symbol": symbol_upper,
                "watchlist": (watchlist.symbols or []) if watchlist else []
            }
        )

    except HTTPException:
        raise
    except Exception as error:
        print(f"Add to watchlist error: {error}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi thêm symbol: {str(error)}"
        )


@router.delete("/watchlist/{symbol}", response_model=WatchlistResponse)
async def remove_from_watchlist(
    symbol: str = Path(..., description="Symbol to remove from watchlist"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove symbol from watchlist
    DELETE /api/portfolio/watchlist/{symbol}
    """
    try:
        user_id = current_user.id

        if not symbol:
            raise HTTPException(status_code=400, detail="Symbol là bắt buộc")

        symbol_upper = symbol.upper().strip()

        service = PortfolioService(db)
        watchlist = service.remove_from_watchlist(user_id=user_id, symbol=symbol_upper)

        return WatchlistResponse(
            success=True,
            data={
                "symbol": symbol_upper,
                "watchlist": (watchlist.symbols or []) if watchlist else []
            }
        )

    except HTTPException:
        raise
    except Exception as error:
        print(f"Remove from watchlist error: {error}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi xóa symbol: {str(error)}"
        )


#
