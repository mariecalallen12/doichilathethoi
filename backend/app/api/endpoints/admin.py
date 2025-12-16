"""
Admin Endpoints - DB-based
Bao gồm: users, customers, deposits, withdrawals, platform stats, analytics, logs, settings
"""

from fastapi import APIRouter, Depends, Request, HTTPException, status, Query, Path, Body
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta, timezone
from decimal import Decimal

# Import schemas
from ...schemas.admin import (
    GetUsersRequest,
    UpdateUserRequest,
    UsersResponse,
    UserResponse,
    AdminUser,
    GetCustomersRequest,
    CustomersResponse,
    AdminCustomer,
    DepositDetailRequest,
    DepositDetailResponse,
    AdminDeposit,
    PlatformStatsResponse,
    PlatformStats,
    AdminErrorResponse,
    AdminValidationErrorResponse,
    UserRole,
    UserStatus,
    KYCStatus,
    CustomerWalletBalance,
    CustomerWalletBalancesResponse,
)

# Import dependencies
from ...dependencies import get_current_user, require_role, get_financial_service, get_user_service, rate_limit, get_cache_service
from ...services.cache_service import CacheService
from ...db.session import get_db
from ...models.user import User, UserProfile, Role
from ...models.financial import Transaction, WalletBalance, Invoice, Payment, ExchangeRate
from ...models.trading import TradingOrder, PortfolioPosition
from ...models.audit import AuditLog
from ...models.system import ScheduledReport, TradingAdjustment, SystemSetting
from ...services.user_service import UserService
from ...services.financial_service import FinancialService
# from ...services.market_display_config_service import (
#     get_market_display_config,
#     save_market_display_config,
#     validate_market_display_config,
# )  # Service doesn't exist - commenting out
# from ...services.market_scenario_service import (
#     get_scenarios as get_market_scenarios,
#     save_scenarios as save_market_scenarios,
#     validate_scenarios as validate_market_scenarios,
# )  # Service doesn't exist - commenting out
from ...services.simulator_session_service import (
    get_sessions as get_sim_sessions,
    get_session as get_sim_session,
    start_session as start_sim_session,
    stop_session as stop_sim_session,
    reset_sessions as reset_sim_sessions,
    replay_session as replay_sim_session,
)
from ...middleware.auth import get_client_ip, require_admin_role

router = APIRouter(tags=["admin"])


# ========== HELPER FUNCTIONS ==========

def format_admin_user(user: User, db: Session) -> Dict[str, Any]:
    """Format User to AdminUser response"""
    # Get balances
    balances = db.query(WalletBalance).filter(WalletBalance.user_id == user.id).all()
    balance_dict = {}
    for bal in balances:
        balance_dict[bal.asset.lower()] = float(bal.total_balance)
    
    return {
        "id": str(user.id),
        "email": user.email,
        "displayName": user.profile.display_name if user.profile else None,
        "role": user.role.name if user.role else "customer",
        "status": user.status,
        "kycStatus": user.kyc_status,
        "isActive": user.status == "active",
        "phoneNumber": user.profile.phone if user.profile else None,
        "emailVerified": user.email_verified,
        "phoneVerified": user.phone_verified,
        "balance": balance_dict,
        "lastLoginAt": user.last_login_at.isoformat() if user.last_login_at else None,
        "createdAt": user.created_at.isoformat(),
        "updatedAt": user.updated_at.isoformat()
    }


def log_audit(
    db: Session,
    admin_user_id: int,
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    result: str = "success"
):
    """Log admin audit trail"""
    try:
        audit_log = AuditLog(
            user_id=admin_user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            result=result,
            category="admin"
        )
        db.add(audit_log)
        db.commit()
    except Exception as e:
        print(f"Audit logging error: {e}")


# ========== USER MANAGEMENT ENDPOINTS ==========

@router.get(
    "/users",
    response_model=UsersResponse,
    responses={
        200: {"model": UsersResponse, "description": "Lấy danh sách users thành công"},
        401: {"model": AdminErrorResponse, "description": "Không có quyền truy cập"},
        403: {"model": AdminErrorResponse, "description": "Cần quyền admin"}
    }
)
async def get_users(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    kyc_status: Optional[str] = Query(None, alias="kycStatus"),
    sort_by: str = Query("createdAt", alias="sortBy"),
    sort_order: str = Query("desc", alias="sortOrder"),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Lấy danh sách users - DB-based"""
    
    try:
        # Build query
        query = db.query(User).join(UserProfile, User.id == UserProfile.user_id, isouter=True)
        
        # Apply filters
        if search:
            query = query.filter(
                or_(
                    User.email.ilike(f"%{search}%"),
                    UserProfile.full_name.ilike(f"%{search}%"),
                    UserProfile.display_name.ilike(f"%{search}%")
                )
            )
        
        if role:
            role_obj = db.query(Role).filter(Role.name == role).first()
            if role_obj:
                query = query.filter(User.role_id == role_obj.id)
        
        # Handle status filter: 'all' means no filter, otherwise filter by status
        if status_filter and status_filter.lower() != 'all':
            query = query.filter(User.status == status_filter)
        
        # Handle kyc_status filter: 'all' means no filter, otherwise filter by kyc_status
        if kyc_status and kyc_status.lower() != 'all':
            query = query.filter(User.kyc_status == kyc_status)
        
        # Get total count
        total_count = query.count()
        
        # Sort
        if sort_by == "email":
            order_by = User.email
        elif sort_by == "createdAt":
            order_by = User.created_at
        elif sort_by == "lastLoginAt":
            order_by = User.last_login_at
        else:
            order_by = User.created_at
        
        if sort_order.lower() == "desc":
            query = query.order_by(desc(order_by))
        else:
            query = query.order_by(order_by)
        
        # Pagination
        offset = (page - 1) * limit
        users = query.offset(offset).limit(limit).all()
        
        # Format response
        users_data = [format_admin_user(user, db) for user in users]
        
        log_audit(
            db, admin_user.id, "get_users", "admin",
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent")
        )
        
        return UsersResponse(
            success=True,
            data={
                "users": users_data
            },
            pagination={
                "page": page,
                "limit": limit,
                "total": total_count,
                "totalPages": (total_count + limit - 1) // limit
            }
        )
        
    except Exception as e:
        print(f"Get users error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy danh sách người dùng"
        )


@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    responses={
        200: {"model": UserResponse, "description": "Lấy thông tin user thành công"},
        404: {"model": AdminErrorResponse, "description": "Không tìm thấy user"}
    }
)
async def get_user_by_id(
    request: Request,
    user_id: int = Path(...),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Lấy thông tin chi tiết user - DB-based"""
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy người dùng"
            )
        
        # Get statistics
        total_deposits = db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.transaction_type == "deposit",
                Transaction.status == "completed"
            )
        ).scalar() or Decimal("0")
        
        total_withdrawals = db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.transaction_type == "withdrawal",
                Transaction.status == "completed"
            )
        ).scalar() or Decimal("0")
        
        total_orders = db.query(func.count(TradingOrder.id)).filter(
            TradingOrder.user_id == user_id
        ).scalar() or 0
        
        total_positions = db.query(func.count(PortfolioPosition.id)).filter(
            PortfolioPosition.user_id == user_id
        ).scalar() or 0
        
        user_data = format_admin_user(user, db)
        user_data.update({
            "statistics": {
                "totalDeposits": float(total_deposits),
                "totalWithdrawals": float(total_withdrawals),
                "totalOrders": total_orders,
                "totalPositions": total_positions
            }
        })
        
        return UserResponse(
            success=True,
            data=user_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get user by id error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy thông tin người dùng"
        )


@router.put(
    "/users/{user_id}",
    response_model=UserResponse,
    responses={
        200: {"model": UserResponse, "description": "Cập nhật user thành công"},
        404: {"model": AdminErrorResponse, "description": "Không tìm thấy user"}
    }
)
async def update_user(
    request: Request,
    user_id: int = Path(...),
    update_data: UpdateUserRequest = None,
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db),
    user_service: UserService = Depends(get_user_service)
):
    """Cập nhật thông tin user - DB-based"""
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy người dùng"
            )
        
        updated_fields = []
        
        # Update role
        if update_data.role:
            role_obj = db.query(Role).filter(Role.name == update_data.role.value).first()
            if role_obj:
                user.role_id = role_obj.id
                updated_fields.append("role")
        
        # Update status
        if update_data.status:
            user.status = update_data.status.value
            updated_fields.append("status")
        
        # Update KYC status
        if update_data.kycStatus:
            user.kyc_status = update_data.kycStatus.value
            updated_fields.append("kycStatus")
        
        # Update isActive (via status)
        if update_data.isActive is not None:
            if update_data.isActive:
                user.status = "active"
            else:
                user.status = "suspended"
            updated_fields.append("isActive")
        
        db.commit()
        db.refresh(user)
        
        # Log audit
        log_audit(
            db, admin_user.id, "update_user", "user",
            resource_id=str(user_id),
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent")
        )
        
        return UserResponse(
            success=True,
            message="Cập nhật thông tin người dùng thành công",
            data=format_admin_user(user, db),
            updatedFields=updated_fields
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Update user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể cập nhật thông tin người dùng"
        )


@router.get(
    "/customers",
    response_model=CustomersResponse,
    responses={
        200: {"model": CustomersResponse, "description": "Lấy danh sách customers thành công"}
    }
)
async def get_customers(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    kyc_status: Optional[str] = Query(None, alias="kycStatus"),
    is_active: Optional[bool] = Query(None, alias="isActive"),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Lấy danh sách customers - DB-based"""
    
    try:
        # Get customer role
        customer_role = db.query(Role).filter(Role.name == "customer").first()
        if not customer_role:
            return CustomersResponse(
                success=True,
                data=[],
                pagination={"page": 1, "limit": limit, "total": 0, "totalPages": 0}
            )
        
        # Build query
        query = db.query(User).filter(User.role_id == customer_role.id)
        
        # Apply filters
        if search:
            query = query.join(UserProfile).filter(
                or_(
                    User.email.ilike(f"%{search}%"),
                    UserProfile.full_name.ilike(f"%{search}%")
                )
            )
        
        if kyc_status:
            query = query.filter(User.kyc_status == kyc_status)
        
        if is_active is not None:
            query = query.filter(User.status == "active" if is_active else User.status != "active")
        
        # Get total count
        total_count = query.count()
        
        # Pagination
        offset = (page - 1) * limit
        users = query.order_by(desc(User.created_at)).offset(offset).limit(limit).all()
        
        # Format response with statistics
        customers_data = []
        for user in users:
            # Get deposit/withdrawal totals
            total_deposits = db.query(func.sum(Transaction.amount)).filter(
                and_(
                    Transaction.user_id == user.id,
                    Transaction.transaction_type == "deposit",
                    Transaction.status == "completed"
                )
            ).scalar() or Decimal("0")
            
            total_withdrawals = db.query(func.sum(Transaction.amount)).filter(
                and_(
                    Transaction.user_id == user.id,
                    Transaction.transaction_type == "withdrawal",
                    Transaction.status == "completed"
                )
            ).scalar() or Decimal("0")
            
            customers_data.append({
                "id": str(user.id),
                "userId": str(user.id),
                "email": user.email,
                "displayName": user.profile.display_name if user.profile else None,
                "phoneNumber": user.profile.phone if user.profile else None,
                "registrationDate": user.created_at,
                "totalDeposits": float(total_deposits),
                "totalWithdrawals": float(total_withdrawals),
                "kycStatus": user.kyc_status,
                "isActive": user.status == "active",
                "lastActivity": user.last_login_at
            })
        
        return CustomersResponse(
            success=True,
            data=customers_data,
            pagination={
                "page": page,
                "limit": limit,
                "total": total_count,
                "totalPages": (total_count + limit - 1) // limit
            }
        )
        
    except Exception as e:
        print(f"Get customers error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy danh sách khách hàng"
        )


# ========== DASHBOARD ENDPOINT ==========

@router.get("/dashboard")
async def get_dashboard(
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db),
    cache_service: CacheService = Depends(get_cache_service)
):
    """Lấy thống kê dashboard - DB-based với caching"""
    
    # Try cache first
    cache_key = "admin:dashboard:stats"
    cached_data = cache_service.get(cache_key)
    if cached_data:
        return cached_data
    
    try:
        # Total users
        total_users = db.query(func.count(User.id)).scalar() or 0
        active_users = db.query(func.count(User.id)).filter(User.status == "active").scalar() or 0
        
        # Total deposits/withdrawals
        total_deposits = db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.transaction_type == "deposit",
                Transaction.status == "completed"
            )
        ).scalar() or Decimal("0")
        
        total_withdrawals = db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.transaction_type == "withdrawal",
                Transaction.status == "completed"
            )
        ).scalar() or Decimal("0")
        
        # Trading volume
        trading_volume = db.query(func.sum(TradingOrder.quantity * TradingOrder.filled_price)).filter(
            TradingOrder.status == "filled"
        ).scalar() or Decimal("0")
        
        # KYC pending
        kyc_pending = db.query(func.count(User.id)).filter(User.kyc_status == "pending").scalar() or 0
        
        # Recent activities (last 10 audit logs)
        recent_activities = db.query(AuditLog).order_by(desc(AuditLog.created_at)).limit(10).all()
        
        activities_data = []
        for log in recent_activities:
            activities_data.append({
                "id": str(log.id),
                "action": log.action,
                "user_id": log.user_id,
                "resource_type": log.resource_type,
                "created_at": log.created_at.isoformat()
            })
        
        result = {
            "success": True,
            "data": {
                "stats": {
                    "totalUsers": total_users,
                    "activeUsers": active_users,
                    "totalDeposits": float(total_deposits),
                    "totalWithdrawals": float(total_withdrawals),
                    "tradingVolume": float(trading_volume),
                    "kycPending": kyc_pending
                },
                "recentActivities": activities_data
            }
        }
        
        # Cache for 5 minutes
        cache_service.set(cache_key, result, ttl=300)
        return result
        
    except Exception as e:
        print(f"Get dashboard error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy thống kê dashboard"
        )


# ========== PLATFORM STATS ENDPOINT ==========

@router.get("/platform-stats", response_model=PlatformStatsResponse)
async def get_platform_stats(
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Lấy thống kê platform - DB-based với risk metrics và top performers"""
    
    try:
        # Aggregate stats from DB
        total_users = db.query(func.count(User.id)).scalar() or 0
        active_users = db.query(func.count(User.id)).filter(User.status == "active").scalar() or 0
        
        total_deposits = db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.transaction_type == "deposit",
                Transaction.status == "completed"
            )
        ).scalar() or Decimal("0")
        
        total_withdrawals = db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.transaction_type == "withdrawal",
                Transaction.status == "completed"
            )
        ).scalar() or Decimal("0")
        
        # Average deposits/withdrawals
        deposit_count = db.query(func.count(Transaction.id)).filter(
            and_(
                Transaction.transaction_type == "deposit",
                Transaction.status == "completed"
            )
        ).scalar() or 0
        
        withdrawal_count = db.query(func.count(Transaction.id)).filter(
            and_(
                Transaction.transaction_type == "withdrawal",
                Transaction.status == "completed"
            )
        ).scalar() or 0
        
        avg_deposit = float(total_deposits / deposit_count) if deposit_count > 0 else 0
        avg_withdrawal = float(total_withdrawals / withdrawal_count) if withdrawal_count > 0 else 0
        
        # New users
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        month_start = today.replace(day=1)
        
        new_users_today = db.query(func.count(User.id)).filter(
            User.created_at >= today
        ).scalar() or 0
        
        new_users_month = db.query(func.count(User.id)).filter(
            User.created_at >= month_start
        ).scalar() or 0
        
        # KYC stats
        verified_kyc = db.query(func.count(User.id)).filter(User.kyc_status == "verified").scalar() or 0
        pending_kyc = db.query(func.count(User.id)).filter(User.kyc_status == "pending").scalar() or 0
        
        # Trading volume
        transaction_volume = db.query(func.sum(Transaction.amount)).filter(
            Transaction.status == "completed"
        ).scalar() or Decimal("0")
        
        # Total positions
        total_positions = db.query(func.count(PortfolioPosition.id)).scalar() or 0
        
        # Risk Metrics
        # High risk users (users with large losses or high leverage)
        high_risk_positions = db.query(PortfolioPosition).filter(
            PortfolioPosition.realized_pnl < Decimal("-1000")
        ).all()
        high_risk_user_ids = set([pos.user_id for pos in high_risk_positions])
        high_risk_users = len(high_risk_user_ids)
        
        # Average leverage (simplified - would need leverage data)
        # For now, calculate based on position sizes vs balances
        positions_with_leverage = db.query(PortfolioPosition).filter(
            PortfolioPosition.leverage.isnot(None)
        ).all()
        if positions_with_leverage:
            leverage_values = [float(pos.leverage) for pos in positions_with_leverage if pos.leverage is not None]
            avg_leverage = sum(leverage_values) / len(leverage_values) if leverage_values else 1.0
        else:
            avg_leverage = 1.0
        
        # Margin call risk (simplified - positions close to liquidation)
        margin_call_risk = 0.0  # Placeholder - would need margin calculation
        
        # Top Performers
        user_performance = {}
        for user in db.query(User).all():
            user_orders = db.query(TradingOrder).filter(
                and_(
                    TradingOrder.user_id == user.id,
                    TradingOrder.status == "filled"
                )
            ).all()
            
            if user_orders:
                winning_trades = 0
                for order in user_orders:
                    if order.side == "buy" and order.filled_price and order.price and order.filled_price <= order.price:
                        winning_trades += 1
                    elif order.side == "sell" and order.filled_price and order.price and order.filled_price >= order.price:
                        winning_trades += 1
                
                win_rate = (winning_trades / len(user_orders) * 100) if user_orders else 0
                user_performance[user.id] = {
                    "user_id": user.id,
                    "win_rate": win_rate,
                    "trades": len(user_orders)
                }
        
        # Sort by win rate and get top 10
        top_performers_list = sorted(
            user_performance.values(),
            key=lambda x: x["win_rate"],
            reverse=True
        )[:10]
        
        stats = PlatformStats(
            totalUsers=total_users,
            activeUsers=active_users,
            totalDeposits=float(total_deposits),
            totalWithdrawals=float(total_withdrawals),
            averageDeposit=avg_deposit,
            averageWithdrawal=avg_withdrawal,
            newUsersToday=new_users_today,
            newUsersThisMonth=new_users_month,
            verifiedKycUsers=verified_kyc,
            pendingKycUsers=pending_kyc,
            totalRevenue=float(total_deposits - total_withdrawals),  # Simplified
            transactionVolume=float(transaction_volume)
        )
        
        # Add risk_metrics and top_performers to response
        response_data = stats.dict() if hasattr(stats, 'dict') else {
            "total_users": stats.totalUsers,
            "active_users": stats.activeUsers,
            "total_deposits": stats.totalDeposits,
            "total_withdrawals": stats.totalWithdrawals,
            "average_deposit": stats.averageDeposit,
            "average_withdrawal": stats.averageWithdrawal,
            "new_users_today": stats.newUsersToday,
            "new_users_this_month": stats.newUsersThisMonth,
            "verified_kyc_users": stats.verifiedKycUsers,
            "pending_kyc_users": stats.pendingKycUsers,
            "total_revenue": stats.totalRevenue,
            "transaction_volume": stats.transactionVolume,
            "total_positions": total_positions,
            "risk_metrics": {
                "high_risk_users": high_risk_users,
                "average_leverage": round(avg_leverage, 2),
                "margin_call_risk": round(margin_call_risk, 2)
            },
            "top_performers": top_performers_list,
            "average_win_rate": sum([p["win_rate"] for p in top_performers_list]) / len(top_performers_list) if top_performers_list else 0,
            "platform_volume": float(transaction_volume)
        }
        
        return {
            "success": True,
            "data": response_data
        }
        
    except Exception as e:
        print(f"Get platform stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy thống kê platform"
        )


# Alias route for /platform/stats (with slash) to maintain compatibility
@router.get("/platform/stats", response_model=PlatformStatsResponse)
async def get_platform_stats_alias(
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Alias endpoint for /platform/stats - redirects to platform-stats handler"""
    return await get_platform_stats(admin_user=admin_user, db=db)


# ========== DEPOSITS MANAGEMENT ENDPOINTS ==========

@router.get("/deposits")
async def get_deposits(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    currency: Optional[str] = Query(None),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Lấy danh sách deposits - DB-based"""
    
    try:
        query = db.query(Transaction).filter(Transaction.transaction_type == "deposit")
        
        if status_filter:
            query = query.filter(Transaction.status == status_filter)
        if currency:
            query = query.filter(Transaction.asset == currency.upper())
        
        total_count = query.count()
        offset = (page - 1) * limit
        transactions = query.order_by(desc(Transaction.created_at)).offset(offset).limit(limit).all()
        
        deposits_data = []
        for tx in transactions:
            user = db.query(User).filter(User.id == tx.user_id).first()
            deposits_data.append({
                "id": str(tx.id),
                "userId": str(tx.user_id),
                "customerEmail": user.email if user else "",
                "amount": float(tx.amount),
                "currency": tx.asset.lower(),
                "status": tx.status,
                "paymentMethod": tx.category or "unknown",
                "transactionHash": tx.transaction_hash,
                "createdAt": tx.created_at.isoformat(),
                "processedAt": tx.completed_at.isoformat() if tx.completed_at else None
            })
        
        return {
            "success": True,
            "data": {
                "deposits": deposits_data,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total_count,
                    "totalPages": (total_count + limit - 1) // limit
                }
            }
        }
        
    except Exception as e:
        print(f"Get deposits error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy danh sách nạp tiền"
        )


@router.get("/deposits/{deposit_id}")
async def get_deposit_detail(
    request: Request,
    deposit_id: int = Path(...),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Lấy chi tiết deposit - DB-based"""
    
    try:
        transaction = db.query(Transaction).filter(
            and_(
                Transaction.id == deposit_id,
                Transaction.transaction_type == "deposit"
            )
        ).first()
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy giao dịch nạp tiền"
            )
        
        user = db.query(User).filter(User.id == transaction.user_id).first()
        
        deposit_data = {
            "id": str(transaction.id),
            "userId": str(transaction.user_id),
            "customerEmail": user.email if user else "",
            "amount": float(transaction.amount),
            "currency": transaction.asset.lower(),
            "status": transaction.status,
            "paymentMethod": transaction.category or "unknown",
            "transactionHash": transaction.transaction_hash,
            "bankReference": transaction.reference_id,
            "adminNotes": transaction.description,
            "processedAt": transaction.completed_at.isoformat() if transaction.completed_at else None,
            "createdAt": transaction.created_at.isoformat()
        }
        
        return DepositDetailResponse(
            success=True,
            data=deposit_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get deposit detail error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy chi tiết giao dịch nạp tiền"
        )


@router.post("/deposits/{deposit_id}/approve")
async def approve_deposit(
    request: Request,
    deposit_id: int = Path(...),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db),
    financial_service: FinancialService = Depends(get_financial_service)
):
    """Duyệt deposit - DB-based"""
    
    try:
        transaction = db.query(Transaction).filter(
            and_(
                Transaction.id == deposit_id,
                Transaction.transaction_type == "deposit",
                Transaction.status == "pending"
            )
        ).first()
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy giao dịch nạp tiền hoặc đã được xử lý"
            )
        
        # Complete transaction (updates balance)
        completed_tx = financial_service.complete_transaction(deposit_id)
        
        if not completed_tx:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không thể hoàn tất giao dịch"
            )
        
        # Log audit
        log_audit(
            db, admin_user.id, "approve_deposit", "transaction",
            resource_id=str(deposit_id),
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent")
        )
        
        return {
            "success": True,
            "message": "Duyệt nạp tiền thành công"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Approve deposit error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể duyệt nạp tiền"
        )


@router.post("/deposits/{deposit_id}/reject")
async def reject_deposit(
    request: Request,
    deposit_id: int = Path(...),
    reason: str = Query(..., description="Lý do từ chối"),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db),
    financial_service: FinancialService = Depends(get_financial_service)
):
    """Từ chối deposit - DB-based"""
    
    try:
        transaction = db.query(Transaction).filter(
            and_(
                Transaction.id == deposit_id,
                Transaction.transaction_type == "deposit",
                Transaction.status == "pending"
            )
        ).first()
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy giao dịch nạp tiền hoặc đã được xử lý"
            )
        
        # Cancel transaction
        cancelled_tx = financial_service.cancel_transaction(deposit_id, reason)
        
        if not cancelled_tx:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không thể hủy giao dịch"
            )
        
        # Log audit
        log_audit(
            db, admin_user.id, "reject_deposit", "transaction",
            resource_id=str(deposit_id),
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent")
        )
        
        return {
            "success": True,
            "message": "Từ chối nạp tiền thành công"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Reject deposit error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể từ chối nạp tiền"
        )


# ========== WITHDRAWALS MANAGEMENT ENDPOINTS ==========

@router.get("/withdrawals")
async def get_withdrawals(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    currency: Optional[str] = Query(None),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Lấy danh sách withdrawals - DB-based"""
    
    try:
        query = db.query(Transaction).filter(Transaction.transaction_type == "withdrawal")
        
        if status_filter:
            query = query.filter(Transaction.status == status_filter)
        if currency:
            query = query.filter(Transaction.asset == currency.upper())
        
        total_count = query.count()
        offset = (page - 1) * limit
        transactions = query.order_by(desc(Transaction.created_at)).offset(offset).limit(limit).all()
        
        withdrawals_data = []
        for tx in transactions:
            user = db.query(User).filter(User.id == tx.user_id).first()
            withdrawals_data.append({
                "id": str(tx.id),
                "userId": str(tx.user_id),
                "customerEmail": user.email if user else "",
                "amount": float(tx.amount),
                "currency": tx.asset.lower(),
                "fee": float(tx.fee or 0),
                "netAmount": float(tx.net_amount),
                "status": tx.status,
                "createdAt": tx.created_at.isoformat(),
                "processedAt": tx.completed_at.isoformat() if tx.completed_at else None,
                "rejectReason": tx.failed_reason
            })
        
        return {
            "success": True,
            "data": {
                "withdrawals": withdrawals_data,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total_count,
                    "totalPages": (total_count + limit - 1) // limit
                }
            }
        }
        
    except Exception as e:
        print(f"Get withdrawals error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy danh sách rút tiền"
        )


@router.get("/withdrawals/{withdrawal_id}")
async def get_withdrawal_detail(
    request: Request,
    withdrawal_id: int = Path(...),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Lấy chi tiết withdrawal - DB-based"""
    
    try:
        transaction = db.query(Transaction).filter(
            and_(
                Transaction.id == withdrawal_id,
                Transaction.transaction_type == "withdrawal"
            )
        ).first()
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy giao dịch rút tiền"
            )
        
        user = db.query(User).filter(User.id == transaction.user_id).first()
        
        withdrawal_data = {
            "id": str(transaction.id),
            "userId": str(transaction.user_id),
            "customerEmail": user.email if user else "",
            "amount": float(transaction.amount),
            "currency": transaction.asset.lower(),
            "fee": float(transaction.fee or 0),
            "netAmount": float(transaction.net_amount),
            "status": transaction.status,
            "bankAccount": transaction.transaction_metadata.get("bank_account") if transaction.transaction_metadata else None,
            "walletAddress": transaction.to_address,
            "createdAt": transaction.created_at.isoformat(),
            "processedAt": transaction.completed_at.isoformat() if transaction.completed_at else None,
            "rejectReason": transaction.failed_reason
        }
        
        return {
            "success": True,
            "data": withdrawal_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get withdrawal detail error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy chi tiết giao dịch rút tiền"
        )


@router.post("/withdrawals/{withdrawal_id}/approve")
async def approve_withdrawal(
    request: Request,
    withdrawal_id: int = Path(...),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db),
    financial_service: FinancialService = Depends(get_financial_service)
):
    """Duyệt withdrawal - DB-based"""
    
    try:
        transaction = db.query(Transaction).filter(
            and_(
                Transaction.id == withdrawal_id,
                Transaction.transaction_type == "withdrawal",
                Transaction.status == "pending"
            )
        ).first()
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy giao dịch rút tiền hoặc đã được xử lý"
            )
        
        # Complete transaction (deducts from locked balance)
        completed_tx = financial_service.complete_transaction(withdrawal_id)
        
        if not completed_tx:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không thể hoàn tất giao dịch"
            )
        
        # Log audit
        log_audit(
            db, admin_user.id, "approve_withdrawal", "transaction",
            resource_id=str(withdrawal_id),
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent")
        )
        
        return {
            "success": True,
            "message": "Duyệt rút tiền thành công"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Approve withdrawal error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể duyệt rút tiền"
        )


@router.post("/withdrawals/{withdrawal_id}/reject")
async def reject_withdrawal(
    request: Request,
    withdrawal_id: int = Path(...),
    reason: str = Query(..., description="Lý do từ chối"),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db),
    financial_service: FinancialService = Depends(get_financial_service)
):
    """Từ chối withdrawal - DB-based"""
    
    try:
        transaction = db.query(Transaction).filter(
            and_(
                Transaction.id == withdrawal_id,
                Transaction.transaction_type == "withdrawal",
                Transaction.status == "pending"
            )
        ).first()
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy giao dịch rút tiền hoặc đã được xử lý"
            )
        
        # Cancel transaction (unlocks balance)
        cancelled_tx = financial_service.cancel_transaction(withdrawal_id, reason)
        
        if not cancelled_tx:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không thể hủy giao dịch"
            )
        
        # Log audit
        log_audit(
            db, admin_user.id, "reject_withdrawal", "transaction",
            resource_id=str(withdrawal_id),
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent")
        )
        
        return {
            "success": True,
            "message": "Từ chối rút tiền thành công"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Reject withdrawal error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể từ chối rút tiền"
        )


# ========== ANALYTICS ENDPOINT ==========

@router.get("/analytics")
async def get_analytics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Lấy analytics data - DB-based với đầy đủ KPIs, charts, và insights"""
    
    try:
        # Default to last 30 days
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Previous period for comparison
        period_days = (end_date - start_date).days
        prev_start_date = start_date - timedelta(days=period_days)
        prev_end_date = start_date
        
        # KPIs
        # Total Revenue
        total_revenue = db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.transaction_type == "deposit",
                Transaction.status == "completed",
                Transaction.created_at >= start_date,
                Transaction.created_at <= end_date
            )
        ).scalar() or Decimal("0")
        
        prev_revenue = db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.transaction_type == "deposit",
                Transaction.status == "completed",
                Transaction.created_at >= prev_start_date,
                Transaction.created_at <= prev_end_date
            )
        ).scalar() or Decimal("0")
        
        revenue_change = ((total_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
        
        # Active Users
        active_users = db.query(func.count(func.distinct(User.id))).filter(
            and_(
                User.status == "active",
                User.last_login_at >= start_date
            )
        ).scalar() or 0
        
        prev_active_users = db.query(func.count(func.distinct(User.id))).filter(
            and_(
                User.status == "active",
                User.last_login_at >= prev_start_date,
                User.last_login_at < prev_end_date
            )
        ).scalar() or 0
        
        active_users_change = ((active_users - prev_active_users) / prev_active_users * 100) if prev_active_users > 0 else 0
        
        # Total Trades
        total_trades = db.query(func.count(TradingOrder.id)).filter(
            and_(
                TradingOrder.created_at >= start_date,
                TradingOrder.created_at <= end_date
            )
        ).scalar() or 0
        
        prev_trades = db.query(func.count(TradingOrder.id)).filter(
            and_(
                TradingOrder.created_at >= prev_start_date,
                TradingOrder.created_at <= prev_end_date
            )
        ).scalar() or 0
        
        trades_change = ((total_trades - prev_trades) / prev_trades * 100) if prev_trades > 0 else 0
        
        # Conversion Rate (simplified - registered users who made a deposit)
        total_registered = db.query(func.count(User.id)).filter(
            User.created_at >= start_date
        ).scalar() or 0
        
        converted = db.query(func.count(func.distinct(Transaction.user_id))).filter(
            and_(
                Transaction.transaction_type == "deposit",
                Transaction.status == "completed",
                Transaction.created_at >= start_date
            )
        ).scalar() or 0
        
        conversion_rate = (converted / total_registered * 100) if total_registered > 0 else 0
        
        prev_converted = db.query(func.count(func.distinct(Transaction.user_id))).filter(
            and_(
                Transaction.transaction_type == "deposit",
                Transaction.status == "completed",
                Transaction.created_at >= prev_start_date,
                Transaction.created_at <= prev_end_date
            )
        ).scalar() or 0
        
        prev_registered = db.query(func.count(User.id)).filter(
            User.created_at >= prev_start_date,
            User.created_at <= prev_end_date
        ).scalar() or 0
        
        prev_conversion_rate = (prev_converted / prev_registered * 100) if prev_registered > 0 else 0
        conversion_change = conversion_rate - prev_conversion_rate
        
        # Top Assets
        top_assets_query = db.query(
            TradingOrder.symbol,
            func.sum(TradingOrder.quantity * TradingOrder.filled_price).label("volume"),
            func.count(TradingOrder.id).label("trades")
        ).filter(
            and_(
                TradingOrder.status == "filled",
                TradingOrder.created_at >= start_date,
                TradingOrder.created_at <= end_date
            )
        ).group_by(TradingOrder.symbol).order_by(desc("volume")).limit(10).all()
        
        top_assets = []
        for symbol, volume, trades in top_assets_query:
            prev_volume = db.query(func.sum(TradingOrder.quantity * TradingOrder.filled_price)).filter(
                and_(
                    TradingOrder.symbol == symbol,
                    TradingOrder.status == "filled",
                    TradingOrder.created_at >= prev_start_date,
                    TradingOrder.created_at <= prev_end_date
                )
            ).scalar() or Decimal("0")
            
            change = ((volume - prev_volume) / prev_volume * 100) if prev_volume > 0 else 0
            
            top_assets.append({
                "symbol": symbol,
                "volume": float(volume or 0),
                "trades": trades,
                "change": round(change, 2)
            })
        
        # User Insights
        # Average Session Time (simplified - based on login frequency)
        avg_session_time = "15m 30s"  # Placeholder - would come from analytics events
        
        # Retention Rate (users who logged in this period and previous period)
        retained_users = db.query(func.count(func.distinct(User.id))).filter(
            and_(
                User.last_login_at >= start_date,
                User.last_login_at <= end_date,
                User.created_at < start_date
            )
        ).scalar() or 0
        
        total_previous_users = db.query(func.count(User.id)).filter(
            User.created_at < start_date
        ).scalar() or 0
        
        retention_rate = (retained_users / total_previous_users * 100) if total_previous_users > 0 else 0
        
        # Churn Rate
        churned_users = db.query(func.count(User.id)).filter(
            and_(
                User.status == "active",
                User.last_login_at < start_date - timedelta(days=30),
                User.created_at < start_date
            )
        ).scalar() or 0
        
        churn_rate = (churned_users / total_previous_users * 100) if total_previous_users > 0 else 0
        
        # Charts
        # User Growth Chart
        user_growth_query = db.query(
            func.date(User.created_at).label("date"),
            func.count(User.id).label("count")
        ).filter(
            and_(
                User.created_at >= start_date,
                User.created_at <= end_date
            )
        ).group_by(func.date(User.created_at)).order_by("date").all()
        
        user_growth_labels = []
        user_growth_data = []
        for date, count in user_growth_query:
            user_growth_labels.append(date.strftime("%Y-%m-%d"))
            user_growth_data.append(count)
        
        # Trading Volume Chart
        trading_volume_query = db.query(
            func.date(TradingOrder.created_at).label("date"),
            func.sum(TradingOrder.quantity * TradingOrder.filled_price).label("volume")
        ).filter(
            and_(
                TradingOrder.status == "filled",
                TradingOrder.created_at >= start_date,
                TradingOrder.created_at <= end_date
            )
        ).group_by(func.date(TradingOrder.created_at)).order_by("date").all()
        
        trading_volume_labels = []
        trading_volume_data = []
        for date, volume in trading_volume_query:
            trading_volume_labels.append(date.strftime("%Y-%m-%d"))
            trading_volume_data.append(float(volume or 0))
        
        # Revenue Trends Chart
        revenue_trends_query = db.query(
            func.date(Transaction.created_at).label("date"),
            func.sum(Transaction.amount).label("revenue")
        ).filter(
            and_(
                Transaction.transaction_type == "deposit",
                Transaction.status == "completed",
                Transaction.created_at >= start_date,
                Transaction.created_at <= end_date
            )
        ).group_by(func.date(Transaction.created_at)).order_by("date").all()
        
        revenue_trends_labels = []
        revenue_trends_data = []
        for date, revenue in revenue_trends_query:
            revenue_trends_labels.append(date.strftime("%Y-%m-%d"))
            revenue_trends_data.append(float(revenue or 0))
        
        return {
            "success": True,
            "data": {
                "kpis": {
                    "total_revenue": {
                        "value": float(total_revenue),
                        "change": round(revenue_change, 2)
                    },
                    "active_users": {
                        "value": active_users,
                        "change": round(active_users_change, 2)
                    },
                    "total_trades": {
                        "value": total_trades,
                        "change": round(trades_change, 2)
                    },
                    "conversion_rate": {
                        "value": round(conversion_rate, 2),
                        "change": round(conversion_change, 2)
                    }
                },
                "top_assets": top_assets,
                "user_insights": {
                    "average_session_time": avg_session_time,
                    "retention_rate": round(retention_rate, 2),
                    "churn_rate": round(churn_rate, 2),
                    "conversion_rate": round(conversion_rate, 2)
                },
                "user_growth_chart": {
                    "labels": user_growth_labels,
                    "data": user_growth_data
                },
                "trading_volume_chart": {
                    "labels": trading_volume_labels,
                    "data": trading_volume_data
                },
                "revenue_trends_chart": {
                    "labels": revenue_trends_labels,
                    "data": revenue_trends_data
                },
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                }
            }
        }
        
    except Exception as e:
        print(f"Get analytics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy analytics"
        )


# ========== REPORTS ENDPOINT ==========

@router.get("/reports")
async def get_reports(
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Lấy danh sách reports - DB-based"""
    
    try:
        # Generate reports from DB
        # This is a simplified version - can be expanded
        return {
            "success": True,
            "data": {
                "reports": [
                    {
                        "id": "daily_report",
                        "name": "Báo cáo hàng ngày",
                        "status": "available"
                    },
                    {
                        "id": "monthly_report",
                        "name": "Báo cáo hàng tháng",
                        "status": "available"
                    }
                ]
            }
        }
        
    except Exception as e:
        print(f"Get reports error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy danh sách báo cáo"
        )


# ========== LOGS ENDPOINT ==========

@router.get("/logs")
async def get_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    action: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Lấy audit logs - DB-based"""
    
    try:
        query = db.query(AuditLog)
        
        if action:
            query = query.filter(AuditLog.action == action)
        if category:
            query = query.filter(AuditLog.category == category)
        
        total_count = query.count()
        offset = (page - 1) * limit
        logs = query.order_by(desc(AuditLog.created_at)).offset(offset).limit(limit).all()
        
        logs_data = []
        for log in logs:
            logs_data.append({
                "id": str(log.id),
                "user_id": log.user_id,
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "category": log.category,
                "result": log.result,
                "ip_address": str(log.ip_address) if log.ip_address else None,
                "created_at": log.created_at.isoformat()
            })
        
        return {
            "success": True,
            "data": {
                "logs": logs_data,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total_count,
                    "totalPages": (total_count + limit - 1) // limit
                }
            }
        }
        
    except Exception as e:
        print(f"Get logs error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy audit logs"
        )


# ========== SETTINGS ENDPOINT ==========

@router.get("/settings")
async def get_settings(
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Lấy system settings - Config-based"""
    
    try:
        # In production, can be stored in DB
        return {
            "success": True,
            "data": {
                "maintenanceMode": False,
                "tradingFee": 0.001,  # 0.1%
                "minDeposit": 10.0,
                "maxDeposit": 1000000.0,
                "minWithdraw": 20.0,
                "maxWithdraw": 100000.0,
                "dailyWithdrawLimit": 10000.0,
                "monthlyWithdrawLimit": 100000.0
            }
        }
        
    except Exception as e:
        print(f"Get settings error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy cài đặt hệ thống"
        )


# ========== MARKET DISPLAY CONFIG ==========


@router.get("/settings/market-display")
async def get_market_display_settings(
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db),
):
    """Lấy cấu hình hiển thị Market (spread, candle style, volume, market cap)."""
    try:
        config = get_market_display_config(db)
        return {
            "success": True,
            "data": config,
        }
    except Exception as e:
        print(f"Get market display config error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy cấu hình hiển thị Market",
        )


@router.put("/settings/market-display")
async def update_market_display_settings(
    request: Request,
    config_data: Dict[str, Any],
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db),
):
    """Cập nhật cấu hình hiển thị Market và áp dụng cho TradingDataSimulator."""
    try:
        is_valid, error = validate_market_display_config(config_data)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error,
            )

        saved = save_market_display_config(config_data, db)

        # Áp dụng ngay cho simulator nếu đang chạy
        try:
            from ...services.trading_data_simulator import get_trading_data_simulator

            sim = get_trading_data_simulator()
            sim.apply_display_config(saved)
        except Exception as sim_err:
            print(f"Apply market display config to simulator failed: {sim_err}")

        log_audit(
            db,
            admin_user.id,
            "update_market_display_settings",
            "system",
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent"),
        )
        return {
            "success": True,
            "message": "Cập nhật cấu hình hiển thị Market thành công",
            "data": saved,
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Update market display config error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể cập nhật cấu hình hiển thị Market",
        )

# ========== CHART DISPLAY CONFIG (CANDLE COLORS) ==========


@router.get("/settings/chart-display")
async def get_chart_display_settings(
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db),
):
    """Lấy cấu hình hiển thị Chart (màu nến, màu bấc, theme)."""
    try:
        # Get from system_settings
        setting = db.query(SystemSetting).filter(
            SystemSetting.key == "chart_display_config"
        ).first()
        
        default_config = {
            "upColor": "#10B981",
            "downColor": "#EF4444",
            "wickUpColor": "#10B981",
            "wickDownColor": "#EF4444",
            "borderVisible": False,
            "shadowStyle": "normal",
            "backgroundColor": "#1e293b",
            "gridColor": "#334155",
            "textColor": "#e2e8f0",
        }
        
        if setting and setting.value:
            import json
            try:
                config = json.loads(setting.value) if isinstance(setting.value, str) else setting.value
                return {"success": True, "data": {**default_config, **config}}
            except:
                pass
        
        return {"success": True, "data": default_config}
    except Exception as e:
        print(f"Get chart display config error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy cấu hình hiển thị Chart",
        )


@router.patch("/config/candle")
async def update_candle_config(
    request: Request,
    config_data: Dict[str, Any],
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db),
):
    """Cập nhật cấu hình màu nến và bấc nến (theo yêu cầu kỹ thuật section 3.2)."""
    import json
    
    try:
        # Validate required fields
        valid_fields = [
            "upColor", "downColor", "wickUpColor", "wickDownColor",
            "borderVisible", "shadowStyle", "backgroundColor", "gridColor", "textColor"
        ]
        
        # Filter only valid fields
        filtered_config = {k: v for k, v in config_data.items() if k in valid_fields}
        
        # Get existing config
        setting = db.query(SystemSetting).filter(
            SystemSetting.key == "chart_display_config"
        ).first()
        
        if setting:
            existing = json.loads(setting.value) if isinstance(setting.value, str) else setting.value
            merged_config = {**existing, **filtered_config}
            setting.value = json.dumps(merged_config)
            setting.updated_at = datetime.utcnow()
        else:
            setting = SystemSetting(
                key="chart_display_config",
                value=json.dumps(filtered_config),
                description="Cấu hình hiển thị Chart (màu nến, bấc, theme)",
            )
            db.add(setting)
        
        db.commit()
        
        log_audit(
            db,
            admin_user.id,
            "update_candle_config",
            "system",
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent"),
        )
        
        return {
            "success": True,
            "message": "Cập nhật cấu hình màu nến thành công",
            "data": filtered_config,
        }
    except Exception as e:
        print(f"Update candle config error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể cập nhật cấu hình màu nến",
        )


# ========== MARKET SCENARIO BUILDER (GOD MODE) ==========


@router.get("/settings/market-scenarios")
async def get_market_scenarios_settings(
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db),
):
    """Lấy danh sách kịch bản Market (God Mode)."""
    try:
        scenarios = get_market_scenarios(db)
        return {
            "success": True,
            "data": scenarios,
        }
    except Exception as e:
        print(f"Get market scenarios error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy kịch bản market",
        )


@router.put("/settings/market-scenarios")
async def update_market_scenarios_settings(
    request: Request,
    payload: Dict[str, Any],
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db),
):
    """Cập nhật danh sách kịch bản Market và áp dụng cho simulator."""
    try:
        scenarios = payload.get("scenarios", [])
        is_valid, error = validate_market_scenarios(scenarios)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error,
            )

        saved = save_market_scenarios(scenarios, db)

        # Áp dụng cho simulator nếu đang chạy
        try:
            from ...services.trading_data_simulator import get_trading_data_simulator
            from ...api.websocket import broadcast_sim_event

            sim = get_trading_data_simulator()
            import asyncio
            loop = asyncio.get_event_loop()
            loop.create_task(sim.set_scenarios_from_dicts(saved))
            
            # Broadcast scenario_changed event to all clients
            from datetime import datetime
            loop.create_task(broadcast_sim_event(
                "scenario_changed",
                "scenario_changed",
                {
                    "scenarios": saved,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ))
        except Exception as sim_err:
            print(f"Apply market scenarios to simulator failed: {sim_err}")

        log_audit(
            db,
            admin_user.id,
            "update_market_scenarios",
            "system",
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent"),
        )

        return {
            "success": True,
            "message": "Cập nhật kịch bản Market thành công",
            "data": saved,
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Update market scenarios error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể cập nhật kịch bản Market",
        )

        return {
            "success": True,
            "message": "Cập nhật cấu hình hiển thị Market thành công",
            "data": saved,
        }


# ========== SESSION MANAGER & MONITORING HUB ==========


@router.get("/simulator/sessions")
async def list_simulator_sessions(
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db),
):
    """Lấy danh sách session đã lưu của simulator."""
    sessions = get_sim_sessions(db)
    return {"success": True, "data": sessions}


@router.post("/simulator/sessions/start")
async def start_simulator_session(
    request: Request,
    payload: Dict[str, Any],
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db),
):
    """
    Bắt đầu một phiên mô phỏng mới:
    - Reset simulator state
    - Áp dụng kịch bản hiện tại
    - Lưu session vào system_settings
    """
    try:
        name = payload.get("name") or "New Session"
        note = payload.get("note")
        current_scenarios = get_market_scenarios(db)
        session, sessions = start_sim_session(
            name=name, note=note, db=db, scenarios_snapshot=current_scenarios
        )

        # Reset simulator và apply lại kịch bản
        try:
            from ...services.trading_data_simulator import get_trading_data_simulator
            import asyncio

            sim = get_trading_data_simulator()
            await sim.reset_state()
            loop = asyncio.get_event_loop()
            loop.create_task(sim.set_scenarios_from_dicts(current_scenarios))
        except Exception as sim_err:
            print(f"Reset/apply scenarios to simulator failed: {sim_err}")

        log_audit(
            db,
            admin_user.id,
            "start_simulator_session",
            "system",
            resource_id=session.get("id"),
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent"),
        )

        return {"success": True, "data": session, "sessions": sessions}
    except Exception as e:
        print(f"Start simulator session error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể bắt đầu session",
        )


@router.post("/simulator/sessions/stop")
async def stop_simulator_session(
    request: Request,
    payload: Dict[str, Any],
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db),
):
    session_id = payload.get("session_id")
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Thiếu session_id",
        )
    result = payload.get("result")
    session, sessions = stop_sim_session(session_id, db, result=result)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session không tồn tại",
        )

    log_audit(
        db,
        admin_user.id,
        "stop_simulator_session",
        "system",
        resource_id=session_id,
        ip_address=get_client_ip(request),
        user_agent=request.headers.get("user-agent"),
    )
    return {"success": True, "data": session, "sessions": sessions}


@router.post("/simulator/sessions/reset")
async def reset_simulator_sessions(
    request: Request,
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db),
):
    """
    Xóa lịch sử session và reset simulator về trạng thái mặc định.
    """
    try:
        from ...services.trading_data_simulator import get_trading_data_simulator
        import asyncio

        saved_sessions = reset_sim_sessions(db)
        sim = get_trading_data_simulator()
        await sim.reset_state()
        scenarios = get_market_scenarios(db)
        loop = asyncio.get_event_loop()
        loop.create_task(sim.set_scenarios_from_dicts(scenarios))

        log_audit(
            db,
            admin_user.id,
            "reset_simulator_sessions",
            "system",
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent"),
        )

        return {
            "success": True,
            "message": "Đã reset simulator và xóa lịch sử session",
            "sessions": saved_sessions,
        }
    except Exception as e:
        print(f"Reset simulator sessions error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể reset simulator",
        )


@router.post("/simulator/sessions/replay")
async def replay_simulator_session(
    request: Request,
    payload: Dict[str, Any],
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db),
):
    """
    Replay một session: áp dụng lại snapshot kịch bản đã lưu cho simulator.
    """
    session_id = payload.get("session_id")
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Thiếu session_id",
        )
    try:
        from ...services.trading_data_simulator import get_trading_data_simulator
        import asyncio

        session = get_sim_session(session_id, db)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session không tồn tại",
            )
        scenarios_snapshot = session.get("scenarios_snapshot") or []
        if not scenarios_snapshot:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session không có snapshot để replay",
            )

        replayed, sessions = replay_sim_session(session_id, db)

        sim = get_trading_data_simulator()
        await sim.reset_state()
        loop = asyncio.get_event_loop()
        loop.create_task(sim.set_scenarios_from_dicts(scenarios_snapshot))

        log_audit(
            db,
            admin_user.id,
            "replay_simulator_session",
            "system",
            resource_id=session_id,
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent"),
        )
        return {
            "success": True,
            "message": "Đã replay session và áp dụng kịch bản",
            "data": replayed,
            "sessions": sessions,
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Replay simulator session error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể replay session",
        )


@router.get("/simulator/monitoring")
async def get_simulator_monitoring(
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db),
):
    """
    Trả về metrics nhanh cho Monitoring/Educational Hub.
    """
    try:
        from ...services.trading_data_simulator import get_trading_data_simulator

        sim = get_trading_data_simulator()
        snapshot = await sim.get_snapshot()
        metrics = await sim.get_metrics()
        return {
            "success": True,
            "data": {
                "metrics": metrics,
                "snapshot": {
                    "prices": {k: v.price for k, v in snapshot.prices.items()},
                    "trades": {k: len(v) for k, v in snapshot.trades.items()},
                    "candles": {k: len(v) for k, v in snapshot.candles.items()},
                    "positions": {k: len(v) for k, v in snapshot.positions.items()},
                },
            },
        }
    except Exception as e:
        print(f"Get simulator monitoring error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy dữ liệu monitoring",
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Update market display config error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể cập nhật cấu hình hiển thị Market",
        )


@router.put("/settings")
async def update_settings(
    request: Request,
    settings_data: Dict[str, Any],
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Cập nhật system settings - Config-based"""
    
    try:
        # Validate settings
        if "maintenanceMode" in settings_data:
            maintenance_mode = settings_data["maintenanceMode"]
            # Can update in DB or config file
        
        if "tradingFee" in settings_data:
            fee = settings_data["tradingFee"]
            if fee < 0 or fee > 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Trading fee phải trong khoảng 0-1"
                )
        
        # Log audit
        log_audit(
            db, admin_user.id, "update_settings", "system",
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent")
        )
        
        return {
            "success": True,
            "message": "Cập nhật cài đặt hệ thống thành công"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Update settings error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể cập nhật cài đặt hệ thống"
        )


# ========== REGISTRATION FIELDS CONFIG ENDPOINTS ==========

from ...services.registration_fields_service import (
    get_registration_fields_config as get_config_service,
    save_registration_fields_config as save_config_service,
    validate_registration_fields_config
)


@router.get("/settings/registration-fields")
async def get_registration_fields_config(
    request: Request,
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Lấy cấu hình các trường đăng ký"""
    
    try:
        config = get_config_service(db=db)
        
        return {
            "success": True,
            "data": config
        }
        
    except Exception as e:
        print(f"Get registration fields config error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy cấu hình trường đăng ký"
        )


@router.put("/settings/registration-fields")
async def update_registration_fields_config(
    request: Request,
    config_data: Dict[str, Any] = Body(...),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Cập nhật cấu hình các trường đăng ký"""
    
    try:
        # Validate config
        # Additional validation: reject attempts to enable locked fields
        locked_fields = ["country", "tradingExperience", "referralCode"]
        for field in config_data.get("fields", []):
            if field.get("key") in locked_fields:
                if field.get("enabled", False):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Trường '{field.get('key')}' đã bị khóa và không thể được bật. Giá trị mặc định được set tự động ở backend."
                    )
        
        is_valid, error_message = validate_registration_fields_config(config_data)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )
        
        # Save config to database
        saved_config = save_config_service(config_data, db=db)
        
        # Log audit
        log_audit(
            db, admin_user.id, "update_registration_fields_config", "system",
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent")
        )
        
        return {
            "success": True,
            "message": "Đã cập nhật cấu hình trường đăng ký thành công",
            "data": saved_config
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Update registration fields config error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể cập nhật cấu hình trường đăng ký"
        )


# ========== TRADING MANAGEMENT ENDPOINTS ==========

@router.get("/trades")
async def get_admin_trades(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    symbol: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db),
    _: None = Depends(rate_limit(100, 60))  # 100 requests per minute
):
    """Lấy danh sách trading orders cho admin - DB-based"""
    
    try:
        query = db.query(TradingOrder)
        
        # Apply filters
        if symbol:
            query = query.filter(TradingOrder.symbol == symbol)
        
        if status:
            query = query.filter(TradingOrder.status == status)
        
        if user_id:
            query = query.filter(TradingOrder.user_id == user_id)
        
        if date_from:
            query = query.filter(TradingOrder.created_at >= date_from)
        
        if date_to:
            query = query.filter(TradingOrder.created_at <= date_to)
        
        # Get total count
        total_count = query.count()
        
        # Pagination
        offset = (page - 1) * limit
        orders = query.order_by(desc(TradingOrder.created_at)).offset(offset).limit(limit).all()
        
        # Format orders
        trades_data = []
        for order in orders:
            trades_data.append({
                "id": str(order.id),
                "trade_id": f"TRD-{order.id:06d}",
                "user_id": str(order.user_id),
                "symbol": order.symbol,
                "side": order.side,
                "type": order.order_type,
                "quantity": float(order.quantity),
                "price": float(order.price) if order.price else None,
                "stop_price": float(order.stop_price) if order.stop_price else None,
                "value": float(order.quantity * (order.price or order.filled_price or 0)),
                "status": order.status,
                "executed_quantity": float(order.filled_quantity or 0),
                "executed_price": float(order.filled_price) if order.filled_price else None,
                "created_at": order.created_at.isoformat(),
                "updated_at": order.updated_at.isoformat(),
            })
        
        # Calculate stats
        pending_count = db.query(func.count(TradingOrder.id)).filter(
            TradingOrder.status == "pending"
        ).scalar() or 0
        
        today = datetime.utcnow().date()
        approved_today = db.query(func.count(TradingOrder.id)).filter(
            and_(
                TradingOrder.status == "filled",
                func.date(TradingOrder.updated_at) == today
            )
        ).scalar() or 0
        
        total_volume = db.query(func.sum(TradingOrder.quantity * TradingOrder.filled_price)).filter(
            TradingOrder.status == "filled"
        ).scalar() or Decimal("0")
        
        total_trades = db.query(func.count(TradingOrder.id)).scalar() or 0
        
        log_audit(
            db, admin_user.id, "get_admin_trades", "admin",
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent")
        )
        
        return {
            "success": True,
            "data": {
                "trades": trades_data,
                "stats": {
                    "total_trades": total_trades,
                    "pending_trades": pending_count,
                    "approved_today": approved_today,
                    "total_volume": float(total_volume)
                },
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total_count,
                    "totalPages": (total_count + limit - 1) // limit
                }
            }
        }
        
    except Exception as e:
        print(f"Get admin trades error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy danh sách giao dịch"
        )


@router.post("/trades/{trade_id}/approve")
async def approve_trade(
    request: Request,
    trade_id: int = Path(..., ge=1),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db),
    _: None = Depends(rate_limit(50, 60))  # 50 requests per minute
):
    """Phê duyệt trading order - DB-based"""
    
    try:
        order = db.query(TradingOrder).filter(TradingOrder.id == trade_id).first()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy giao dịch"
            )
        
        if order.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Giao dịch đã ở trạng thái {order.status}, không thể phê duyệt"
            )
        
        # Update order status to approved/filled
        order.status = "filled"
        order.filled_at = datetime.utcnow()
        if not order.filled_price:
            order.filled_price = order.price or Decimal("0")
        if not order.filled_quantity:
            order.filled_quantity = order.quantity
        
        db.commit()
        db.refresh(order)
        
        log_audit(
            db, admin_user.id, "approve_trade", "trading",
            resource_id=str(trade_id),
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent")
        )
        
        return {
            "success": True,
            "message": "Đã phê duyệt giao dịch thành công",
            "data": {
                "id": str(order.id),
                "status": order.status
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Approve trade error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể phê duyệt giao dịch"
        )


@router.post("/trades/{trade_id}/reject")
async def reject_trade(
    request: Request,
    trade_id: int = Path(..., ge=1),
    reason: Optional[str] = Body(None, max_length=500),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db),
    _: None = Depends(rate_limit(50, 60))  # 50 requests per minute
):
    """Từ chối trading order - DB-based"""
    
    try:
        order = db.query(TradingOrder).filter(TradingOrder.id == trade_id).first()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy giao dịch"
            )
        
        if order.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Giao dịch đã ở trạng thái {order.status}, không thể từ chối"
            )
        
        # Update order status to rejected
        order.status = "rejected"
        db.commit()
        db.refresh(order)
        
        log_audit(
            db, admin_user.id, "reject_trade", "trading",
            resource_id=str(trade_id),
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent"),
            result=f"rejected: {reason or 'No reason provided'}"
        )
        
        return {
            "success": True,
            "message": "Đã từ chối giao dịch thành công",
            "data": {
                "id": str(order.id),
                "status": order.status,
                "reason": reason
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Reject trade error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể từ chối giao dịch"
        )


@router.post("/trades/batch-approve")
async def batch_approve_trades(
    request: Request,
    data: Dict[str, Any] = Body(...),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Phê duyệt hàng loạt trading orders - DB-based"""
    
    try:
        trade_ids = data.get("trade_ids") or data.get("tradeIds", [])
        
        if not trade_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Danh sách trade_ids không được rỗng"
            )
        
        orders = db.query(TradingOrder).filter(
            and_(
                TradingOrder.id.in_(trade_ids),
                TradingOrder.status == "pending"
            )
        ).all()
        
        if not orders:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy giao dịch chờ phê duyệt"
            )
        
        approved_count = 0
        for order in orders:
            order.status = "filled"
            order.filled_at = datetime.utcnow()
            if not order.filled_price:
                order.filled_price = order.price or Decimal("0")
            if not order.filled_quantity:
                order.filled_quantity = order.quantity
            approved_count += 1
        
        db.commit()
        
        log_audit(
            db, admin_user.id, "batch_approve_trades", "trading",
            resource_id=f"{len(orders)} trades",
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent")
        )
        
        return {
            "success": True,
            "message": f"Đã phê duyệt {approved_count} giao dịch thành công",
            "data": {
                "approved_count": approved_count,
                "total_requested": len(trade_ids)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Batch approve trades error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể phê duyệt hàng loạt giao dịch"
        )


# ========== TRADING ADJUSTMENTS ENDPOINTS ==========

@router.post("/trading-adjustments/win-rate")
async def set_win_rate(
    request: Request,
    data: Dict[str, Any] = Body(...),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db),
    _: None = Depends(rate_limit(30, 60))  # 30 requests per minute
):
    """Thiết lập win rate cho user - DB-based"""
    
    try:
        user_id = data.get("user_id") or data.get("userId")
        target_win_rate = data.get("target_win_rate") or data.get("targetWinRate")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user_id là bắt buộc"
            )
        
        # Validate target_win_rate
        try:
            target_win_rate = float(target_win_rate)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="target_win_rate phải là số"
            )
        
        if target_win_rate < 0 or target_win_rate > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="target_win_rate phải trong khoảng 0-100"
            )
        
        # Find user
        user = db.query(User).filter(User.id == int(user_id)).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy người dùng"
            )
        
        # Create adjustment record
        adjustment = TradingAdjustment(
            admin_user_id=admin_user.id,
            user_id=int(user_id),
            adjustment_type="win_rate",
            target_value=str(target_win_rate),
            result=f"Win rate set to {target_win_rate}%"
        )
        db.add(adjustment)
        db.commit()
        
        log_audit(
            db, admin_user.id, "set_win_rate", "trading_adjustment",
            resource_id=user_id,
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent"),
            result=f"target_win_rate: {target_win_rate}%"
        )
        
        return {
            "success": True,
            "message": f"Đã thiết lập win rate {target_win_rate}% cho user {user_id}",
            "data": {
                "user_id": user_id,
                "target_win_rate": target_win_rate
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Set win rate error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể thiết lập win rate"
        )


@router.post("/trading-adjustments/position-override")
async def override_position(
    request: Request,
    data: Dict[str, Any] = Body(...),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db),
    _: None = Depends(rate_limit(30, 60))  # 30 requests per minute
):
    """Ghi đè kết quả vị thế - DB-based"""
    
    try:
        position_id = data.get("position_id") or data.get("positionId")
        outcome = data.get("outcome")
        amount = data.get("amount")
        
        if not position_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="position_id là bắt buộc"
            )
        
        if outcome not in ["profit", "loss"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="outcome phải là 'profit' hoặc 'loss'"
            )
        
        # Validate amount
        try:
            amount = float(amount)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="amount phải là số"
            )
        
        if amount < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="amount phải >= 0"
            )
        
        # Validate position_id
        try:
            position_id = int(position_id)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="position_id phải là số nguyên"
            )
        
        # Find position
        position = db.query(PortfolioPosition).filter(PortfolioPosition.id == int(position_id)).first()
        
        if not position:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy vị thế"
            )
        
        # Update position based on outcome
        if outcome == "profit":
            position.realized_pnl = Decimal(str(amount))
        else:
            position.realized_pnl = Decimal(str(-amount))
        
        position.is_closed = True
        position.closed_at = datetime.utcnow()
        if not position.closed_price:
            position.closed_price = position.average_price
        
        db.commit()
        db.refresh(position)
        
        log_audit(
            db, admin_user.id, "override_position", "trading_adjustment",
            resource_id=position_id,
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent"),
            result=f"{outcome}: {amount}"
        )
        
        return {
            "success": True,
            "message": f"Đã ghi đè vị thế {position_id} với kết quả {outcome}",
            "data": {
                "position_id": position_id,
                "outcome": outcome,
                "amount": amount,
                "realized_pnl": float(position.realized_pnl)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Override position error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể ghi đè vị thế"
        )


# ========== INVOICES MANAGEMENT ENDPOINTS ==========

@router.get("/invoices")
async def get_invoices(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Lấy danh sách invoices - DB-based"""
    
    try:
        query = db.query(Invoice)
        
        if status and status != "all":
            query = query.filter(Invoice.status == status)
        if user_id:
            query = query.filter(Invoice.user_id == user_id)
        if date_from:
            query = query.filter(Invoice.created_at >= date_from)
        if date_to:
            query = query.filter(Invoice.created_at <= date_to)
        
        total_count = query.count()
        offset = (page - 1) * limit
        invoices = query.order_by(desc(Invoice.created_at)).offset(offset).limit(limit).all()
        
        invoices_data = []
        for inv in invoices:
            user = db.query(User).filter(User.id == inv.user_id).first()
            invoices_data.append({
                "id": str(inv.id),
                "invoice_number": inv.invoice_number,
                "user_id": str(inv.user_id),
                "user_email": user.email if user else "",
                "amount": float(inv.amount),
                "currency": inv.currency,
                "description": inv.description,
                "due_date": inv.due_date.isoformat() if inv.due_date else None,
                "status": inv.status,
                "items": inv.items or [],
                "created_at": inv.created_at.isoformat(),
                "updated_at": inv.updated_at.isoformat(),
            })
        
        return {
            "success": True,
            "data": {
                "invoices": invoices_data,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total_count,
                    "totalPages": (total_count + limit - 1) // limit
                }
            }
        }
    except Exception as e:
        print(f"Get invoices error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy danh sách hóa đơn"
        )


@router.get("/invoices/{invoice_id}")
async def get_invoice_detail(
    request: Request,
    invoice_id: int = Path(...),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Lấy chi tiết invoice - DB-based"""
    
    try:
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy hóa đơn"
            )
        
        user = db.query(User).filter(User.id == invoice.user_id).first()
        
        invoice_data = {
            "id": str(invoice.id),
            "invoice_number": invoice.invoice_number,
            "user_id": str(invoice.user_id),
            "user_email": user.email if user else "",
            "amount": float(invoice.amount),
            "currency": invoice.currency,
            "description": invoice.description,
            "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
            "status": invoice.status,
            "items": invoice.items or [],
            "metadata": invoice.extra_metadata or {},
            "created_at": invoice.created_at.isoformat(),
            "updated_at": invoice.updated_at.isoformat(),
        }
        
        return {
            "success": True,
            "data": invoice_data
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get invoice detail error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy chi tiết hóa đơn"
        )


@router.post("/invoices")
async def create_invoice(
    request: Request,
    data: Dict[str, Any] = Body(...),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Tạo invoice mới - DB-based"""
    
    try:
        user_id = data.get("user_id") or data.get("userId")
        amount = data.get("amount")
        description = data.get("description", "")
        due_date = data.get("due_date") or data.get("dueDate")
        items = data.get("items", [])
        currency = data.get("currency", "USD")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user_id là bắt buộc"
            )
        
        if not amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="amount là bắt buộc"
            )
        
        # Validate user exists
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy người dùng"
            )
        
        # Generate invoice number
        invoice_count = db.query(func.count(Invoice.id)).scalar() or 0
        invoice_number = f"INV-{datetime.utcnow().strftime('%Y%m%d')}-{invoice_count + 1:06d}"
        
        # Parse due_date if provided
        due_date_obj = None
        if due_date:
            if isinstance(due_date, str):
                due_date_obj = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            else:
                due_date_obj = due_date
        
        invoice = Invoice(
            user_id=int(user_id),
            invoice_number=invoice_number,
            amount=Decimal(str(amount)),
            currency=currency,
            description=description,
            due_date=due_date_obj,
            status="draft",
            items=items
        )
        
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        
        log_audit(
            db, admin_user.id, "create_invoice", "invoice",
            resource_id=str(invoice.id),
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent")
        )
        
        return {
            "success": True,
            "message": "Đã tạo hóa đơn thành công",
            "data": {
                "id": str(invoice.id),
                "invoice_number": invoice.invoice_number,
                "amount": float(invoice.amount),
                "status": invoice.status
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Create invoice error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể tạo hóa đơn"
        )


@router.put("/invoices/{invoice_id}")
async def update_invoice(
    request: Request,
    invoice_id: int = Path(...),
    data: Dict[str, Any] = Body(...),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Cập nhật invoice - DB-based"""
    
    try:
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy hóa đơn"
            )
        
        # Update fields
        if "amount" in data:
            invoice.amount = Decimal(str(data["amount"]))
        if "description" in data:
            invoice.description = data["description"]
        if "due_date" in data:
            due_date = data["due_date"]
            if isinstance(due_date, str):
                invoice.due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            else:
                invoice.due_date = due_date
        if "items" in data:
            invoice.items = data["items"]
        if "status" in data:
            invoice.status = data["status"]
        
        db.commit()
        db.refresh(invoice)
        
        log_audit(
            db, admin_user.id, "update_invoice", "invoice",
            resource_id=str(invoice_id),
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent")
        )
        
        return {
            "success": True,
            "message": "Đã cập nhật hóa đơn thành công",
            "data": {
                "id": str(invoice.id),
                "invoice_number": invoice.invoice_number,
                "status": invoice.status
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Update invoice error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể cập nhật hóa đơn"
        )


@router.delete("/invoices/{invoice_id}")
async def delete_invoice(
    request: Request,
    invoice_id: int = Path(...),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Xóa invoice - DB-based"""
    
    try:
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy hóa đơn"
            )
        
        db.delete(invoice)
        db.commit()
        
        log_audit(
            db, admin_user.id, "delete_invoice", "invoice",
            resource_id=str(invoice_id),
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent")
        )
        
        return {
            "success": True,
            "message": "Đã xóa hóa đơn thành công"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Delete invoice error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể xóa hóa đơn"
        )


@router.post("/invoices/{invoice_id}/approve")
async def approve_invoice(
    request: Request,
    invoice_id: int = Path(...),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Phê duyệt invoice - DB-based"""
    
    try:
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy hóa đơn"
            )
        
        invoice.status = "paid"
        db.commit()
        db.refresh(invoice)
        
        log_audit(
            db, admin_user.id, "approve_invoice", "invoice",
            resource_id=str(invoice_id),
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent")
        )
        
        return {
            "success": True,
            "message": "Đã phê duyệt hóa đơn thành công"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Approve invoice error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể phê duyệt hóa đơn"
        )


@router.post("/invoices/{invoice_id}/reject")
async def reject_invoice(
    request: Request,
    invoice_id: int = Path(...),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Từ chối invoice - DB-based"""
    
    try:
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy hóa đơn"
            )
        
        invoice.status = "cancelled"
        db.commit()
        db.refresh(invoice)
        
        log_audit(
            db, admin_user.id, "reject_invoice", "invoice",
            resource_id=str(invoice_id),
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent")
        )
        
        return {
            "success": True,
            "message": "Đã từ chối hóa đơn thành công"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Reject invoice error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể từ chối hóa đơn"
        )


# ========== PAYMENTS MANAGEMENT ENDPOINTS ==========

@router.get("/payments")
async def get_payments(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None),
    payment_method: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Lấy danh sách payments - DB-based"""
    
    try:
        query = db.query(Payment)
        
        if status and status != "all":
            query = query.filter(Payment.status == status)
        if payment_method and payment_method != "all":
            query = query.filter(Payment.payment_method == payment_method)
        if user_id:
            query = query.filter(Payment.user_id == user_id)
        if date_from:
            query = query.filter(Payment.created_at >= date_from)
        if date_to:
            query = query.filter(Payment.created_at <= date_to)
        
        total_count = query.count()
        offset = (page - 1) * limit
        payments = query.order_by(desc(Payment.created_at)).offset(offset).limit(limit).all()
        
        payments_data = []
        for pay in payments:
            user = db.query(User).filter(User.id == pay.user_id).first()
            payments_data.append({
                "id": str(pay.id),
                "user_id": str(pay.user_id),
                "user_email": user.email if user else "",
                "invoice_id": str(pay.invoice_id) if pay.invoice_id else None,
                "transaction_id": str(pay.transaction_id) if pay.transaction_id else None,
                "amount": float(pay.amount),
                "currency": pay.currency,
                "payment_method": pay.payment_method,
                "status": pay.status,
                "payment_reference": pay.payment_reference,
                "payment_provider": pay.payment_provider,
                "processed_at": pay.processed_at.isoformat() if pay.processed_at else None,
                "failed_reason": pay.failed_reason,
                "created_at": pay.created_at.isoformat(),
                "updated_at": pay.updated_at.isoformat(),
            })
        
        return {
            "success": True,
            "data": {
                "payments": payments_data,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total_count,
                    "totalPages": (total_count + limit - 1) // limit
                }
            }
        }
    except Exception as e:
        print(f"Get payments error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy danh sách thanh toán"
        )


@router.get("/payments/{payment_id}")
async def get_payment_detail(
    request: Request,
    payment_id: int = Path(...),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Lấy chi tiết payment - DB-based"""
    
    try:
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy thanh toán"
            )
        
        user = db.query(User).filter(User.id == payment.user_id).first()
        
        payment_data = {
            "id": str(payment.id),
            "user_id": str(payment.user_id),
            "user_email": user.email if user else "",
            "invoice_id": str(payment.invoice_id) if payment.invoice_id else None,
            "transaction_id": str(payment.transaction_id) if payment.transaction_id else None,
            "amount": float(payment.amount),
            "currency": payment.currency,
            "payment_method": payment.payment_method,
            "status": payment.status,
            "payment_reference": payment.payment_reference,
            "payment_provider": payment.payment_provider,
            "metadata": payment.extra_metadata or {},
            "processed_at": payment.processed_at.isoformat() if payment.processed_at else None,
            "failed_reason": payment.failed_reason,
            "created_at": payment.created_at.isoformat(),
            "updated_at": payment.updated_at.isoformat(),
        }
        
        return {
            "success": True,
            "data": payment_data
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get payment detail error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy chi tiết thanh toán"
        )


@router.post("/payments/{payment_id}/process")
async def process_payment(
    request: Request,
    payment_id: int = Path(...),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Xử lý payment - DB-based"""
    
    try:
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy thanh toán"
            )
        
        if payment.status == "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Thanh toán đã được xử lý"
            )
        
        payment.status = "processing"
        db.commit()
        db.refresh(payment)
        
        # Simulate processing - in real system, this would integrate with payment gateway
        payment.status = "completed"
        payment.processed_at = datetime.utcnow()
        db.commit()
        db.refresh(payment)
        
        log_audit(
            db, admin_user.id, "process_payment", "payment",
            resource_id=str(payment_id),
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent")
        )
        
        return {
            "success": True,
            "message": "Đã xử lý thanh toán thành công"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Process payment error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể xử lý thanh toán"
        )


@router.post("/payments/{payment_id}/refund")
async def refund_payment(
    request: Request,
    payment_id: int = Path(...),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Hoàn tiền payment - DB-based"""
    
    try:
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy thanh toán"
            )
        
        if payment.status != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chỉ có thể hoàn tiền thanh toán đã hoàn thành"
            )
        
        payment.status = "refunded"
        db.commit()
        db.refresh(payment)
        
        log_audit(
            db, admin_user.id, "refund_payment", "payment",
            resource_id=str(payment_id),
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent")
        )
        
        return {
            "success": True,
            "message": "Đã hoàn tiền thành công"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Refund payment error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể hoàn tiền"
        )


# ========== USER PERFORMANCE ENDPOINT ==========

@router.get("/users/{user_id}/performance")
async def get_user_performance(
    request: Request,
    user_id: int = Path(...),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Lấy thông tin hiệu suất giao dịch của user - DB-based"""
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy người dùng"
            )
        
        # Calculate win rate from trading orders
        total_orders = db.query(func.count(TradingOrder.id)).filter(
            TradingOrder.user_id == user_id
        ).scalar() or 0
        
        filled_orders = db.query(TradingOrder).filter(
            and_(
                TradingOrder.user_id == user_id,
                TradingOrder.status == "filled"
            )
        ).all()
        
        # Calculate win rate (simplified - based on filled orders with profit)
        winning_trades = 0
        total_volume = Decimal("0")
        profit_loss = Decimal("0")
        
        for order in filled_orders:
            if order.filled_price and order.price:
                # Simple win calculation: if filled price is better than order price for buy, or vice versa for sell
                if order.side == "buy" and order.filled_price <= order.price:
                    winning_trades += 1
                elif order.side == "sell" and order.filled_price >= order.price:
                    winning_trades += 1
            
            if order.filled_price and order.filled_quantity:
                total_volume += Decimal(str(order.filled_price)) * Decimal(str(order.filled_quantity))
        
        win_rate = (winning_trades / len(filled_orders) * 100) if filled_orders else 0
        
        # Get positions for P/L calculation
        positions = db.query(PortfolioPosition).filter(
            PortfolioPosition.user_id == user_id
        ).all()
        
        for pos in positions:
            if pos.realized_pnl:
                profit_loss += Decimal(str(pos.realized_pnl))
        
        # Check for current win rate override (from trading adjustments)
        current_win_rate = win_rate
        latest_adjustment = db.query(TradingAdjustment).filter(
            and_(
                TradingAdjustment.user_id == user_id,
                TradingAdjustment.adjustment_type == "win_rate"
            )
        ).order_by(desc(TradingAdjustment.created_at)).first()
        
        if latest_adjustment and latest_adjustment.target_value:
            try:
                current_win_rate = float(latest_adjustment.target_value)
            except (ValueError, TypeError):
                pass
        
        return {
            "success": True,
            "data": {
                "user_id": str(user_id),
                "win_rate": round(win_rate, 2),
                "current_win_rate": round(current_win_rate, 2),
                "total_trades": total_orders,
                "total_volume": float(total_volume),
                "profit_loss": float(profit_loss)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get user performance error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy thông tin hiệu suất người dùng"
        )


# ========== TRADING ADJUSTMENTS ENDPOINTS ==========

@router.post("/trading-adjustments/reset-win-rate")
async def reset_win_rate(
    request: Request,
    data: Dict[str, Any] = Body(...),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Reset win rate về mặc định cho user - DB-based"""
    
    try:
        user_id = data.get("user_id") or data.get("userId")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user_id là bắt buộc"
            )
        
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy người dùng"
            )
        
        # Create adjustment record
        adjustment = TradingAdjustment(
            admin_user_id=admin_user.id,
            user_id=int(user_id),
            adjustment_type="reset_win_rate",
            target_value="reset",
            result="Win rate reset to default"
        )
        db.add(adjustment)
        db.commit()
        
        log_audit(
            db, admin_user.id, "reset_win_rate", "trading_adjustment",
            resource_id=user_id,
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent")
        )
        
        return {
            "success": True,
            "message": f"Đã reset win rate về mặc định cho user {user_id}"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Reset win rate error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể reset win rate"
        )


@router.get("/trading-adjustments/history")
async def get_trading_adjustments_history(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    action_type: Optional[str] = Query(None),
    admin_user_id: Optional[int] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Lấy lịch sử điều chỉnh giao dịch - DB-based"""
    
    try:
        query = db.query(TradingAdjustment)
        
        if action_type:
            query = query.filter(TradingAdjustment.adjustment_type == action_type)
        if admin_user_id:
            query = query.filter(TradingAdjustment.admin_user_id == admin_user_id)
        if date_from:
            query = query.filter(TradingAdjustment.created_at >= date_from)
        if date_to:
            query = query.filter(TradingAdjustment.created_at <= date_to)
        
        total_count = query.count()
        offset = (page - 1) * limit
        adjustments = query.order_by(desc(TradingAdjustment.created_at)).offset(offset).limit(limit).all()
        
        adjustments_data = []
        for adj in adjustments:
            admin_user_obj = db.query(User).filter(User.id == adj.admin_user_id).first() if adj.admin_user_id else None
            target_user = db.query(User).filter(User.id == adj.user_id).first() if adj.user_id else None
            
            adjustments_data.append({
                "id": str(adj.id),
                "date": adj.created_at.isoformat(),
                "admin_user": admin_user_obj.email if admin_user_obj else None,
                "admin_user_id": str(adj.admin_user_id) if adj.admin_user_id else None,
                "action_type": adj.adjustment_type,
                "target": str(adj.user_id) if adj.user_id else (str(adj.position_id) if adj.position_id else None),
                "target_type": "user" if adj.user_id else ("position" if adj.position_id else None),
                "details": {
                    "target_value": adj.target_value,
                    "previous_value": adj.previous_value,
                    "result": adj.result
                }
            })
        
        return {
            "success": True,
            "data": {
                "adjustments": adjustments_data,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total_count,
                    "totalPages": (total_count + limit - 1) // limit
                }
            }
        }
    except Exception as e:
        print(f"Get trading adjustments history error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy lịch sử điều chỉnh"
        )


# ========== ANALYTICS ENHANCEMENT ==========

@router.get("/analytics/performance")
async def get_analytics_performance(
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Lấy dữ liệu performance report - DB-based"""
    
    try:
        # System Performance
        # Calculate uptime (simplified - based on recent activity)
        recent_logs = db.query(AuditLog).order_by(desc(AuditLog.created_at)).limit(1000).all()
        error_count = sum(1 for log in recent_logs if log.result == "error")
        error_rate = (error_count / len(recent_logs) * 100) if recent_logs else 0
        
        # Calculate average response time (simplified)
        # In real system, this would come from monitoring/metrics
        response_time = 85.5  # Placeholder - would come from metrics
        
        uptime = 99.9 - error_rate  # Simplified calculation
        
        # Trading Metrics
        filled_orders = db.query(TradingOrder).filter(
            TradingOrder.status == "filled"
        ).all()
        
        winning_trades = 0
        total_trade_size = Decimal("0")
        total_profit = Decimal("0")
        total_loss = Decimal("0")
        
        for order in filled_orders:
            if order.filled_price and order.filled_quantity:
                trade_size = Decimal(str(order.filled_price)) * Decimal(str(order.filled_quantity))
                total_trade_size += trade_size
                
                # Simplified win/loss calculation
                if order.side == "buy" and order.filled_price <= (order.price or order.filled_price):
                    winning_trades += 1
                    total_profit += trade_size * Decimal("0.01")  # Simplified
                else:
                    total_loss += trade_size * Decimal("0.005")  # Simplified
        
        win_rate = (winning_trades / len(filled_orders) * 100) if filled_orders else 0
        avg_trade_size = float(total_trade_size / len(filled_orders)) if filled_orders else 0
        profit_loss_ratio = float(total_profit / total_loss) if total_loss > 0 else 0
        
        # Financial Health
        total_deposits = db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.transaction_type == "deposit",
                Transaction.status == "completed"
            )
        ).scalar() or Decimal("0")
        
        total_withdrawals = db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.transaction_type == "withdrawal",
                Transaction.status == "completed"
            )
        ).scalar() or Decimal("0")
        
        cash_flow = total_deposits - total_withdrawals
        
        # Revenue growth (simplified - compare last 30 days vs previous 30 days)
        now = datetime.utcnow()
        last_30_days_start = now - timedelta(days=60)
        last_30_days_end = now - timedelta(days=30)
        prev_30_days_start = now - timedelta(days=90)
        
        recent_revenue = db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.transaction_type == "deposit",
                Transaction.status == "completed",
                Transaction.created_at >= last_30_days_end,
                Transaction.created_at <= now
            )
        ).scalar() or Decimal("0")
        
        prev_revenue = db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.transaction_type == "deposit",
                Transaction.status == "completed",
                Transaction.created_at >= prev_30_days_start,
                Transaction.created_at <= last_30_days_end
            )
        ).scalar() or Decimal("0")
        
        revenue_growth = ((recent_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
        
        profit_margin = (float(cash_flow / total_deposits * 100)) if total_deposits > 0 else 0
        
        # Generate chart data (last 30 days)
        chart_labels = []
        uptime_data = []
        win_rate_data = []
        cash_flow_data = []
        
        for i in range(30, 0, -1):
            date = now - timedelta(days=i)
            chart_labels.append(date.strftime("%Y-%m-%d"))
            uptime_data.append(99.5 + (i % 3) * 0.1)  # Simplified
            win_rate_data.append(win_rate + (i % 5) - 2)  # Simplified
            cash_flow_data.append(float(cash_flow / 30) + (i % 10) * 100)  # Simplified
        
        return {
            "success": True,
            "data": {
                "system_performance": {
                    "uptime": round(uptime, 2),
                    "response_time": response_time,
                    "error_rate": round(error_rate, 2),
                    "chart": {
                        "labels": chart_labels,
                        "uptime_data": uptime_data
                    }
                },
                "trading_metrics": {
                    "win_rate": round(win_rate, 2),
                    "avg_trade_size": round(avg_trade_size, 2),
                    "profit_loss_ratio": round(profit_loss_ratio, 2),
                    "chart": {
                        "labels": chart_labels,
                        "win_rate_data": win_rate_data
                    }
                },
                "financial_health": {
                    "cash_flow": float(cash_flow),
                    "revenue_growth": round(revenue_growth, 2),
                    "profit_margin": round(profit_margin, 2),
                    "chart": {
                        "labels": chart_labels,
                        "cash_flow_data": cash_flow_data
                    }
                }
            }
        }
    except Exception as e:
        print(f"Get analytics performance error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy dữ liệu hiệu suất"
        )


# ========== SCHEDULED REPORTS ENDPOINTS ==========

@router.get("/reports/scheduled")
async def get_scheduled_reports(
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Lấy danh sách scheduled reports - DB-based"""
    
    try:
        reports = db.query(ScheduledReport).order_by(desc(ScheduledReport.created_at)).all()
        
        reports_data = []
        for report in reports:
            reports_data.append({
                "id": str(report.id),
                "report_type": report.report_type,
                "frequency": report.frequency,
                "status": report.status,
                "last_run": report.last_run.isoformat() if report.last_run else None,
                "next_run": report.next_run.isoformat() if report.next_run else None,
                "config": report.config or {},
                "created_at": report.created_at.isoformat(),
                "updated_at": report.updated_at.isoformat(),
            })
        
        return {
            "success": True,
            "data": {
                "reports": reports_data,
                "scheduled_reports": reports_data
            }
        }
    except Exception as e:
        print(f"Get scheduled reports error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy danh sách báo cáo đã lên lịch"
        )


@router.patch("/reports/scheduled/{report_id}")
async def update_scheduled_report(
    request: Request,
    report_id: int = Path(...),
    data: Dict[str, Any] = Body(...),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Cập nhật scheduled report - DB-based"""
    
    try:
        report = db.query(ScheduledReport).filter(ScheduledReport.id == report_id).first()
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy báo cáo đã lên lịch"
            )
        
        if "status" in data:
            report.status = data["status"]
        if "frequency" in data:
            report.frequency = data["frequency"]
        if "config" in data:
            report.config = data["config"]
        if "next_run" in data:
            next_run = data["next_run"]
            if isinstance(next_run, str):
                report.next_run = datetime.fromisoformat(next_run.replace('Z', '+00:00'))
            else:
                report.next_run = next_run
        
        db.commit()
        db.refresh(report)
        
        log_audit(
            db, admin_user.id, "update_scheduled_report", "scheduled_report",
            resource_id=str(report_id),
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent")
        )
        
        return {
            "success": True,
            "message": "Đã cập nhật báo cáo đã lên lịch thành công"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Update scheduled report error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể cập nhật báo cáo đã lên lịch"
        )


@router.delete("/reports/scheduled/{report_id}")
async def delete_scheduled_report(
    request: Request,
    report_id: int = Path(...),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Xóa scheduled report - DB-based"""
    
    try:
        report = db.query(ScheduledReport).filter(ScheduledReport.id == report_id).first()
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy báo cáo đã lên lịch"
            )
        
        db.delete(report)
        db.commit()
        
        log_audit(
            db, admin_user.id, "delete_scheduled_report", "scheduled_report",
            resource_id=str(report_id),
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent")
        )
        
        return {
            "success": True,
            "message": "Đã xóa báo cáo đã lên lịch thành công"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Delete scheduled report error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể xóa báo cáo đã lên lịch"
        )


# ========== CORS ORIGINS MANAGEMENT ==========

@router.get("/settings/cors-origins")
async def get_cors_origins(
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Lấy danh sách CORS origins - DB-based"""
    
    try:
        # Get from system_settings
        cors_setting = db.query(SystemSetting).filter(SystemSetting.key == "cors_origins").first()
        
        if cors_setting and cors_setting.value:
            origins = cors_setting.value if isinstance(cors_setting.value, list) else []
        else:
            origins = []
        
        return {
            "success": True,
            "data": {
                "origins": origins
            }
        }
    except Exception as e:
        print(f"Get CORS origins error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy danh sách CORS origins"
        )


@router.post("/settings/cors-origins")
async def add_cors_origin(
    request: Request,
    data: Dict[str, Any] = Body(...),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Thêm CORS origin - DB-based"""
    
    try:
        origin = data.get("origin")
        
        if not origin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="origin là bắt buộc"
            )
        
        # Get or create cors_origins setting
        cors_setting = db.query(SystemSetting).filter(SystemSetting.key == "cors_origins").first()
        
        if cors_setting:
            origins = cors_setting.value if isinstance(cors_setting.value, list) else []
        else:
            origins = []
            cors_setting = SystemSetting(
                key="cors_origins",
                value=[],
                description="CORS allowed origins"
            )
            db.add(cors_setting)
        
        # Add origin if not exists
        if origin not in origins:
            origins.append(origin)
            cors_setting.value = origins
            db.commit()
        
        log_audit(
            db, admin_user.id, "add_cors_origin", "system",
            resource_id=origin,
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent")
        )
        
        return {
            "success": True,
            "message": "Đã thêm CORS origin thành công",
            "data": {
                "origins": origins
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Add CORS origin error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể thêm CORS origin"
        )


@router.delete("/settings/cors-origins")
async def remove_cors_origin(
    request: Request,
    origin: str = Query(...),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Xóa CORS origin - DB-based"""
    
    try:
        cors_setting = db.query(SystemSetting).filter(SystemSetting.key == "cors_origins").first()
        
        if not cors_setting or not cors_setting.value:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy CORS origin"
            )
        
        origins = cors_setting.value if isinstance(cors_setting.value, list) else []
        
        if origin not in origins:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy CORS origin"
            )
        
        origins.remove(origin)
        cors_setting.value = origins
        db.commit()
        
        log_audit(
            db, admin_user.id, "remove_cors_origin", "system",
            resource_id=origin,
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent")
        )
        
        return {
            "success": True,
            "message": "Đã xóa CORS origin thành công",
            "data": {
                "origins": origins
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Remove CORS origin error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể xóa CORS origin"
        )


# ========== BULK UPDATE USERS ==========

@router.post("/users/bulk-update")
async def bulk_update_users(
    request: Request,
    data: Dict[str, Any] = Body(...),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Cập nhật hàng loạt users - DB-based"""
    
    try:
        user_ids = data.get("user_ids") or data.get("userIds", [])
        update_data = data.get("update_data") or data.get("updateData", {})
        
        if not user_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user_ids không được rỗng"
            )
        
        updated_count = 0
        
        for user_id in user_ids:
            try:
                user = db.query(User).filter(User.id == int(user_id)).first()
                if not user:
                    continue
                
                # Update status
                if "status" in update_data:
                    user.status = update_data["status"]
                
                # Update role
                if "role" in update_data:
                    role_obj = db.query(Role).filter(Role.name == update_data["role"]).first()
                    if role_obj:
                        user.role_id = role_obj.id
                
                # Update KYC status
                if "kyc_status" in update_data or "kycStatus" in update_data:
                    kyc_status = update_data.get("kyc_status") or update_data.get("kycStatus")
                    user.kyc_status = kyc_status
                
                updated_count += 1
            except Exception as e:
                print(f"Error updating user {user_id}: {e}")
                continue
        
        db.commit()
        
        log_audit(
            db, admin_user.id, "bulk_update_users", "user",
            resource_id=f"{len(user_ids)} users",
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent")
        )
        
        return {
            "success": True,
            "message": f"Đã cập nhật {updated_count} người dùng thành công",
            "data": {
                "updated_count": updated_count,
                "total_requested": len(user_ids)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Bulk update users error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể cập nhật hàng loạt người dùng"
        )


# ========== AUTO APPROVE REGISTRATION SETTINGS ==========

@router.get("/settings/auto-approve-registration")
async def get_auto_approve_registration_setting(
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Lấy cấu hình auto approve registration"""
    
    try:
        setting = db.query(SystemSetting).filter(
            SystemSetting.key == "auto_approve_registration"
        ).first()
        
        if setting and setting.value:
            enabled = setting.value.get("enabled", False) if isinstance(setting.value, dict) else bool(setting.value)
        else:
            enabled = False  # Default: không auto approve
        
        return {
            "success": True,
            "data": {
                "enabled": enabled
            }
        }
    except Exception as e:
        print(f"Get auto approve setting error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy cấu hình auto approve"
        )


@router.put("/settings/auto-approve-registration")
async def update_auto_approve_registration_setting(
    request: Request,
    enabled: bool = Body(..., embed=True),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Cập nhật cấu hình auto approve registration"""
    
    try:
        setting = db.query(SystemSetting).filter(
            SystemSetting.key == "auto_approve_registration"
        ).first()
        
        if setting:
            setting.value = {"enabled": enabled}
        else:
            setting = SystemSetting(
                key="auto_approve_registration",
                value={"enabled": enabled},
                description="Tự động phê duyệt đăng ký người dùng mới",
                is_public=False
            )
            db.add(setting)
        
        db.commit()
        db.refresh(setting)
        
        # Log audit
        log_audit(
            db, admin_user.id, "update_auto_approve_registration", "system",
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent"),
            result="success"
        )
        
        return {
            "success": True,
            "message": f"Đã {'bật' if enabled else 'tắt'} tự động phê duyệt đăng ký",
            "data": {
                "enabled": enabled
            }
        }
    except Exception as e:
        db.rollback()
        print(f"Update auto approve setting error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể cập nhật cấu hình auto approve"
        )


# ========== REGISTRATION APPROVAL ==========

@router.get("/registrations")
async def get_pending_registrations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, description="Filter by status: pending, approved"),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Lấy danh sách đăng ký chờ duyệt"""
    
    try:
        query = db.query(User).join(UserProfile).filter(
            User.role_id == db.query(Role.id).filter(Role.name == "customer").scalar_subquery()
        )
        
        # Filter by status
        if status_filter == "pending":
            query = query.filter(User.is_approved == False, User.status == "pending")
        elif status_filter == "approved":
            query = query.filter(User.is_approved == True)
        
        # Count total
        total = query.count()
        
        # Pagination
        offset = (page - 1) * page_size
        users = query.order_by(User.created_at.desc()).offset(offset).limit(page_size).all()
        
        registrations = []
        for user in users:
            registrations.append({
                "id": user.id,
                "email": user.email,
                "phone": user.profile.phone if user.profile else None,
                "display_name": user.profile.display_name if user.profile else None,
                "status": user.status,
                "is_approved": user.is_approved,
                "approved_at": user.approved_at.isoformat() if user.approved_at else None,
                "created_at": user.created_at.isoformat() if user.created_at else None,
            })
        
        return {
            "success": True,
            "data": {
                "registrations": registrations,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": total,
                    "total_pages": (total + page_size - 1) // page_size
                }
            }
        }
    except Exception as e:
        print(f"Get pending registrations error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy danh sách đăng ký"
        )


@router.post("/registrations/{registration_id}/approve")
async def approve_registration(
    request: Request,
    registration_id: int = Path(..., description="User ID to approve"),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Phê duyệt đăng ký người dùng"""
    
    try:
        user = db.query(User).filter(User.id == registration_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy người dùng"
            )
        
        if user.is_approved:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Người dùng đã được phê duyệt"
            )
        
        # Approve user
        user.is_approved = True
        user.status = "active"
        user.approved_at = datetime.now(timezone.utc)
        user.approved_by = admin_user.id
        
        db.commit()
        db.refresh(user)
        
        # Log audit
        log_audit(
            db, admin_user.id, "approve_registration", "user",
            resource_id=str(user.id),
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent"),
            result="success"
        )
        
        return {
            "success": True,
            "message": "Đã phê duyệt đăng ký thành công",
            "data": {
                "user_id": user.id,
                "email": user.email,
                "approved_at": user.approved_at.isoformat(),
                "approved_by": admin_user.id
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Approve registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể phê duyệt đăng ký"
        )


# ========== CUSTOMER WALLET BALANCES ENDPOINT ==========

@router.get(
    "/customers/wallet-balances",
    response_model=CustomerWalletBalancesResponse,
    responses={
        200: {"model": CustomerWalletBalancesResponse, "description": "Lấy số dư ví khách hàng thành công"},
        401: {"model": AdminErrorResponse, "description": "Không có quyền truy cập"},
        403: {"model": AdminErrorResponse, "description": "Cần quyền admin"}
    }
)
async def get_customer_wallet_balances(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    currency: Optional[str] = Query(None),
    min_balance: Optional[float] = Query(None),
    max_balance: Optional[float] = Query(None),
    sort_by: str = Query("totalBalanceUSD", alias="sortBy"),
    sort_order: str = Query("desc", alias="sortOrder"),
    admin_user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """
    Lấy số dư ví của tất cả khách hàng đã đăng ký thành công
    """
    try:
        # Query only active customers (status = "active" and role = "customer")
        query = (
            db.query(User)
            .join(Role)
            .filter(
                User.status == "active",
                Role.name == "customer"
            )
        )
        
        # Search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    User.email.ilike(search_term),
                    UserProfile.display_name.ilike(search_term),
                    UserProfile.full_name.ilike(search_term)
                )
            )
        
        # Get total count before pagination
        total_items = query.count()
        
        # Apply sorting
        if sort_by == "totalBalanceUSD":
            # We'll sort after calculating balances
            pass
        elif sort_by == "email":
            if sort_order == "asc":
                query = query.order_by(User.email.asc())
            else:
                query = query.order_by(User.email.desc())
        elif sort_by == "createdAt":
            if sort_order == "asc":
                query = query.order_by(User.created_at.asc())
            else:
                query = query.order_by(User.created_at.desc())
        else:
            query = query.order_by(User.created_at.desc())
        
        # Apply pagination
        offset = (page - 1) * limit
        users = query.offset(offset).limit(limit).all()
        
        if not users:
            # Return empty response if no users
            return CustomerWalletBalancesResponse(
                success=True,
                data=[],
                pagination={
                    "page": page,
                    "limit": limit,
                    "total": 0,
                    "pages": 0,
                    "hasNext": False,
                    "hasPrev": False,
                },
                summary={
                    "totalCustomers": 0,
                    "totalBalanceUSD": 0.0,
                    "averageBalanceUSD": 0.0,
                    "currencies": []
                }
            )
        
        # Optimize: Load all wallet balances for all users in one query
        user_ids = [user.id for user in users]
        all_balances = (
            db.query(WalletBalance)
            .filter(WalletBalance.user_id.in_(user_ids))
            .all()
        )
        
        # Group balances by user_id
        balances_by_user: Dict[int, List[WalletBalance]] = {}
        for bal in all_balances:
            if bal.user_id not in balances_by_user:
                balances_by_user[bal.user_id] = []
            balances_by_user[bal.user_id].append(bal)
        
        # Optimize: Load all exchange rates in one query
        all_rates = (
            db.query(ExchangeRate)
            .filter(
                and_(
                    ExchangeRate.target_asset == "USD",
                    ExchangeRate.is_active == True,
                )
            )
            .order_by(ExchangeRate.base_asset, ExchangeRate.priority.desc())
            .all()
        )
        
        # Create exchange rate lookup dict (base_asset -> rate)
        exchange_rates: Dict[str, float] = {}
        for rate in all_rates:
            base_asset = (rate.base_asset or '').strip().upper()
            if base_asset and base_asset not in exchange_rates:
                exchange_rates[base_asset] = float(rate.rate)
        
        # Get wallet balances for each user
        customer_balances: List[CustomerWalletBalance] = []
        total_balance_usd_all = 0.0
        
        for user in users:
            # Get balances for this user (from pre-loaded dict)
            balances = balances_by_user.get(user.id, [])
            
            # Build balances dictionary
            balances_dict: Dict[str, float] = {}
            total_balance_usd = 0.0
            
            for bal in balances:
                asset = (bal.asset or '').strip().upper()
                if not asset:
                    continue
                
                total_bal = float(bal.total_balance or 0)
                balances_dict[asset] = total_bal
                
                # Convert to USD equivalent using exchange rates (from pre-loaded dict)
                if asset == "USD":
                    total_balance_usd += total_bal
                else:
                    # Get exchange rate from pre-loaded dict
                    rate = exchange_rates.get(asset)
                    if rate:
                        total_balance_usd += float(total_bal * rate)
                    else:
                        # Fallback: assume 1:1 for unknown currencies
                        total_balance_usd += total_bal
            
            # Apply currency filter if specified
            if currency:
                normalized_currency = currency.strip().upper()
                if normalized_currency not in balances_dict:
                    continue  # Skip users without this currency
            
            # Apply min/max balance filters
            if min_balance is not None and total_balance_usd < min_balance:
                continue
            if max_balance is not None and total_balance_usd > max_balance:
                continue
            
            # Get user profile
            profile = user.profile
            
            customer_balances.append(
                CustomerWalletBalance(
                    userId=str(user.id),
                    email=user.email,
                    displayName=profile.display_name if profile else None,
                    balances=balances_dict,
                    totalBalanceUSD=total_balance_usd,
                    createdAt=user.created_at,
                    lastUpdated=max([bal.updated_at or bal.created_at for bal in balances], default=user.updated_at) if balances else user.updated_at
                )
            )
            
            total_balance_usd_all += total_balance_usd
        
        # Sort by totalBalanceUSD if requested
        if sort_by == "totalBalanceUSD":
            customer_balances.sort(
                key=lambda x: x.totalBalanceUSD,
                reverse=(sort_order == "desc")
            )
        
        # Calculate summary statistics
        summary = {
            "totalCustomers": len(customer_balances),
            "totalBalanceUSD": total_balance_usd_all,
            "averageBalanceUSD": total_balance_usd_all / len(customer_balances) if customer_balances else 0.0,
            "currencies": list(set(
                currency
                for cb in customer_balances
                for currency in cb.balances.keys()
            ))
        }
        
        pagination = {
            "page": page,
            "limit": limit,
            "total": total_items,
            "pages": (total_items + limit - 1) // limit,
            "hasNext": offset + limit < total_items,
            "hasPrev": page > 1,
        }
        
        # Log audit
        log_audit(
            db, admin_user.id, "view_customer_wallet_balances", "wallet_balances",
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent"),
            result="success"
        )
        
        return CustomerWalletBalancesResponse(
            success=True,
            data=customer_balances,
            pagination=pagination,
            summary=summary
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get customer wallet balances error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy số dư ví khách hàng"
        )


# ========== MARKET PREVIEW ENDPOINTS ==========

@router.get("/market-preview/{symbol}")
async def get_market_preview(
    symbol: str = Path(..., description="Symbol để preview (ví dụ: BTCUSDT)"),
    admin_user: User = Depends(require_role(["admin", "owner"])),
):
    """Lấy market data cho preview - Market Scenario Builder"""
    
    try:
        from ...services.market_data_service import get_market_data_service
        
        market_service = get_market_data_service()
        market_data = await market_service.get_market_data(symbol)
        
        return {
            "success": True,
            "data": market_data
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        print(f"Get market preview error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy market data preview"
        )


@router.get("/market-preview")
async def get_multiple_market_preview(
    symbols: str = Query(..., description="List symbols separated by commas (ví dụ: BTCUSDT,ETHUSDT)"),
    admin_user: User = Depends(require_role(["admin", "owner"])),
):
    """Lấy market data cho nhiều symbols - Market Scenario Builder"""
    
    try:
        from ...services.market_data_service import get_market_data_service
        
        # Parse symbols
        symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
        
        if not symbol_list:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vui lòng cung cấp ít nhất một symbol"
            )
        
        market_service = get_market_data_service()
        market_data_dict = await market_service.get_multiple_market_data(symbol_list)
        
        return {
            "success": True,
            "data": market_data_dict
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get multiple market preview error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy market data preview"
        )
