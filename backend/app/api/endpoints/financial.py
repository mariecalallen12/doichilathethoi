"""
Financial Endpoints - DB-based
Bao gồm: deposits, withdrawals với đầy đủ validation logic và DB integration
"""

from fastapi import APIRouter, Depends, Request, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from decimal import Decimal
import secrets
try:
    import qrcode
    import io
    import base64
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False

# Import schemas
from ...schemas.financial import (
    CreateDepositRequest,
    DepositRecord,
    Invoice,
    DepositResponse,
    DepositsListResponse,
    CreateWithdrawalRequest,
    WithdrawalRecord,
    WithdrawalLimits,
    WithdrawalResponse,
    WithdrawalsListResponse,
    FinancialErrorResponse,
    FinancialValidationErrorResponse
)

# Import dependencies
from ...dependencies import get_current_user, get_financial_service
from ...db.session import get_db
from ...models.user import User
from ...models.financial import Transaction, WalletBalance
from ...models.audit import AuditLog
from ...services.financial_service import FinancialService
from ...middleware.auth import get_client_ip

router = APIRouter(tags=["financial"])


# ========== HELPER FUNCTIONS ==========

def log_audit(
    db: Session,
    user_id: int,
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    result: str = "success"
):
    """Log audit trail"""
    try:
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            result=result,
            category="financial"
        )
        db.add(audit_log)
        db.commit()
    except Exception as e:
        print(f"Audit logging error: {e}")


def generate_deposit_address(asset: str, user_id: int) -> str:
    """Generate deposit address - integrate with crypto service"""
    # In production, integrate with crypto wallet service
    if asset.upper() == "BTC":
        return f"bc1q{secrets.token_hex(16)}"
    elif asset.upper() == "ETH":
        return f"0x{secrets.token_hex(20)}"
    elif asset.upper() == "USDT":
        return f"0x{secrets.token_hex(20)}"  # ERC20
    return f"address_{secrets.token_hex(16)}"


def generate_qr_code(data: str) -> str:
    """Generate QR code base64 string"""
    if not QRCODE_AVAILABLE:
        # Raise error if QR code library not available - no placeholder
        raise ValueError("QR code generation library not available")
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"


# ========== DEPOSIT ENDPOINTS ==========

@router.post(
    "/deposits",
    response_model=DepositResponse,
    responses={
        201: {"model": DepositResponse, "description": "Tạo deposit request thành công"},
        400: {"model": FinancialValidationErrorResponse, "description": "Dữ liệu đầu vào không hợp lệ"},
        401: {"model": FinancialErrorResponse, "description": "Không tìm thấy token xác thực"},
        403: {"model": FinancialErrorResponse, "description": "Tài khoản không hoạt động"}
    }
)
async def create_deposit(
    request: Request,
    deposit_data: CreateDepositRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    financial_service: FinancialService = Depends(get_financial_service)
):
    """Tạo yêu cầu nạp tiền - DB-based"""
    
    try:
        # Check account status
        if user.status != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tài khoản không hoạt động"
            )
        
        client_ip = get_client_ip(request)
        asset = deposit_data.currency.value.upper()
        amount = Decimal(str(deposit_data.amount))
        
        # Validate minimum deposit
        min_deposit = Decimal("10.0")  # Can be configurable
        if amount < min_deposit:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Số tiền nạp tối thiểu là {min_deposit} {asset}"
            )
        
        # Handle different deposit methods
        if deposit_data.method.value == "crypto_deposit":
            # Crypto deposit
            deposit_address = generate_deposit_address(asset, user.id)
            
            # Create transaction
            transaction = financial_service.create_transaction(
                user_id=user.id,
                transaction_type="deposit",
                category="crypto_deposit",
                asset=asset,
                amount=amount,
                fee=Decimal("0"),  # No fee for crypto deposits
                description=f"Crypto deposit {amount} {asset}",
                metadata={
                    "method": "crypto",
                    "wallet_address": deposit_address,
                    "network": "mainnet"  # Can be configurable
                }
            )
            
            # Log audit
            log_audit(
                db, user.id, "create_deposit", "transaction",
                resource_id=str(transaction.id),
                ip_address=client_ip,
                user_agent=request.headers.get("user-agent")
            )
            
            return DepositResponse(
                success=True,
                message="Tạo yêu cầu nạp tiền thành công",
                data={
                    "deposit": {
                        "id": str(transaction.id),
                        "amount": float(amount),
                        "currency": asset.lower(),
                        "method": "crypto_deposit",
                        "status": "pending",
                        "wallet_address": deposit_address,
                        "network": "mainnet",
                        "min_confirmations": 3
                    },
                    "qr_code": generate_qr_code(deposit_address),
                    "warnings": {
                        "network": "Chỉ gửi {asset} trên mạng chính (Mainnet)",
                        "minimum": f"Số tiền nạp tối thiểu: {min_deposit} {asset}",
                        "fee": "Không có phí nạp tiền"
                    }
                }
            )
        
        elif deposit_data.method.value == "bank_transfer":
            # VietQR deposit
            if not user.customer_payment_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Không tìm thấy customer_payment_id"
                )
            
            # Create transaction
            transaction = financial_service.create_transaction(
                user_id=user.id,
                transaction_type="deposit",
                category="vietqr",
                asset=asset,
                amount=amount,
                fee=Decimal("0"),
                description=f"VietQR deposit {amount} {asset}",
                metadata={
                    "method": "vietqr",
                    "customer_payment_id": user.customer_payment_id,
                    "bank_account": deposit_data.bankAccount.dict() if deposit_data.bankAccount else None
                }
            )
            
            # Generate QR code data
            qr_data = f"{user.customer_payment_id}|{amount}|{asset}"
            qr_code = generate_qr_code(qr_data)
            
            # Log audit
            log_audit(
                db, user.id, "create_deposit", "transaction",
                resource_id=str(transaction.id),
                ip_address=client_ip,
                user_agent=request.headers.get("user-agent")
            )
            
            return DepositResponse(
                success=True,
                message="Tạo yêu cầu nạp tiền thành công",
                data={
                    "deposit": {
                        "id": str(transaction.id),
                        "amount": float(amount),
                        "currency": asset.lower(),
                        "method": "bank_transfer",
                        "status": "pending",
                        "customer_payment_id": user.customer_payment_id,
                        "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat()
                    },
                    "qr_code": qr_code,
                    "warnings": {
                        "expiry": "QR code có hiệu lực trong 24 giờ",
                        "minimum": f"Số tiền nạp tối thiểu: {min_deposit} {asset}",
                        "fee": "Không có phí nạp tiền"
                    }
                }
            )
        
        elif deposit_data.method.value == "card":
            # Online payment - Coming soon
            return DepositResponse(
                success=True,
                message="Thanh toán online đang được phát triển",
                data={
                    "deposit": {
                        "id": None,
                        "status": "coming_soon"
                    },
                    "message": "Tính năng thanh toán online sẽ sớm được ra mắt"
                }
            )
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phương thức thanh toán không hợp lệ"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Create deposit error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể tạo yêu cầu nạp tiền"
        )


@router.get(
    "/deposits",
    response_model=DepositsListResponse,
    responses={
        200: {"model": DepositsListResponse, "description": "Lấy danh sách deposits thành công"},
        401: {"model": FinancialErrorResponse, "description": "Không tìm thấy token xác thực"}
    }
)
async def get_deposits(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    currency: Optional[str] = Query(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    financial_service: FinancialService = Depends(get_financial_service)
):
    """Lấy danh sách deposits - DB-based"""
    
    try:
        # Get transactions from DB
        query = db.query(Transaction).filter(
            and_(
                Transaction.user_id == user.id,
                Transaction.transaction_type == "deposit"
            )
        )
        
        if status_filter:
            query = query.filter(Transaction.status == status_filter)
        if currency:
            query = query.filter(Transaction.asset == currency.upper())
        
        # Get total count
        total_count = query.count()
        
        # Pagination
        offset = (page - 1) * limit
        transactions = query.order_by(desc(Transaction.created_at)).offset(offset).limit(limit).all()
        
        # Format response
        deposits_data = []
        for tx in transactions:
            deposits_data.append({
                "id": str(tx.id),
                "userId": str(tx.user_id),
                "userEmail": user.email,
                "amount": float(tx.amount),
                "currency": tx.asset.lower(),
                "method": tx.category or "unknown",
                "status": tx.status,
                "fees": float(tx.fee or 0),
                "netAmount": float(tx.net_amount),
                "walletAddress": tx.to_address,
                "transactionId": tx.transaction_hash,
                "createdAt": tx.created_at.isoformat(),
                "updatedAt": tx.updated_at.isoformat(),
                "processedAt": tx.completed_at.isoformat() if tx.completed_at else None
            })
        
        return DepositsListResponse(
            success=True,
            data={
                "deposits": deposits_data,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total_count,
                    "totalPages": (total_count + limit - 1) // limit
                }
            }
        )
        
    except Exception as e:
        print(f"Get deposits error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy danh sách nạp tiền"
        )


# ========== WITHDRAWAL ENDPOINTS ==========

@router.post(
    "/withdrawals",
    response_model=WithdrawalResponse,
    responses={
        201: {"model": WithdrawalResponse, "description": "Tạo withdrawal request thành công"},
        400: {"model": FinancialValidationErrorResponse, "description": "Dữ liệu đầu vào không hợp lệ"},
        401: {"model": FinancialErrorResponse, "description": "Không tìm thấy token xác thực"},
        403: {"model": FinancialErrorResponse, "description": "Cần xác minh KYC hoặc tài khoản không hoạt động"}
    }
)
async def create_withdrawal(
    request: Request,
    withdrawal_data: CreateWithdrawalRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    financial_service: FinancialService = Depends(get_financial_service)
):
    """Tạo yêu cầu rút tiền - DB-based"""
    
    try:
        # Check account status
        if user.status != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tài khoản không hoạt động"
            )
        
        # Check KYC status
        if user.kyc_status != "verified":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vui lòng xác minh KYC trước khi rút tiền"
            )

        # Require 2FA (sử dụng xác thực số điện thoại như 2FA tối thiểu)
        if not user.phone_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vui lòng bật xác thực 2 yếu tố (2FA) trước khi rút tiền"
            )

        client_ip = get_client_ip(request)
        asset = withdrawal_data.currency.value.upper()
        amount = Decimal(str(withdrawal_data.amount))

        # Nếu người dùng đã bật 2FA TOTP, yêu cầu mã 2FA hợp lệ
        if getattr(user, "two_factor_enabled", False):
            from ...core.two_factor import verify_totp
            code = (withdrawal_data.twoFactorCode or "").strip()
            if not code:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Vui lòng nhập mã 2FA để rút tiền"
                )
            if not user.two_factor_secret or not verify_totp(code, user.two_factor_secret):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Mã 2FA không hợp lệ"
                )
        
        # Get balance
        balance = financial_service.get_balance(user.id, asset)
        if not balance or balance.available_balance < amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Số dư {asset} không đủ để rút tiền"
            )
        
        # Calculate fee (2% for withdrawals)
        fee_rate = Decimal("0.02")
        fee = amount * fee_rate
        required_amount = amount + fee
        
        if balance.available_balance < required_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Số dư {asset} không đủ (cần {required_amount} bao gồm phí {fee})"
            )
        
        # Check withdrawal limits
        withdrawal_limits = WithdrawalLimits(daily=10000, monthly=100000)
        
        # Get withdrawals for current period
        start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_of_day = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        monthly_total = db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.user_id == user.id,
                Transaction.transaction_type == "withdrawal",
                Transaction.status == "completed",
                Transaction.asset == asset,
                Transaction.completed_at >= start_of_month
            )
        ).scalar() or Decimal("0")
        
        daily_total = db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.user_id == user.id,
                Transaction.transaction_type == "withdrawal",
                Transaction.status == "completed",
                Transaction.asset == asset,
                Transaction.completed_at >= start_of_day
            )
        ).scalar() or Decimal("0")
        
        if monthly_total + amount > Decimal(str(withdrawal_limits.monthly)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vượt quá hạn mức rút tiền hàng tháng"
            )
        
        if daily_total + amount > Decimal(str(withdrawal_limits.daily)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vượt quá hạn mức rút tiền hàng ngày"
            )
        
        # Lock balance
        if not financial_service.lock_balance(user.id, asset, required_amount):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không thể khóa số dư"
            )
        
        # Create transaction
        transaction = financial_service.create_transaction(
            user_id=user.id,
            transaction_type="withdrawal",
            category=withdrawal_data.method.value,
            asset=asset,
            amount=amount,
            fee=fee,
            description=f"Withdrawal {amount} {asset}",
            metadata={
                "method": withdrawal_data.method.value,
                "bank_account": withdrawal_data.bankAccount.dict() if withdrawal_data.bankAccount else None,
                "wallet_address": withdrawal_data.walletAddress
            }
        )
        
        # Log audit
        log_audit(
            db, user.id, "create_withdrawal", "transaction",
            resource_id=str(transaction.id),
            ip_address=client_ip,
            user_agent=request.headers.get("user-agent")
        )
        
        return WithdrawalResponse(
            success=True,
            message="Tạo yêu cầu rút tiền thành công. Đang chờ phê duyệt từ quản trị viên.",
            data={
                "withdrawal": {
                    "id": str(transaction.id),
                    "amount": float(amount),
                    "currency": asset.lower(),
                    "fee": float(fee),
                    "netAmount": float(amount),
                    "status": "pending"
                },
                "limits": {
                    "remainingDaily": float(withdrawal_limits.daily - (daily_total + amount)),
                    "remainingMonthly": float(withdrawal_limits.monthly - (monthly_total + amount))
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Create withdrawal error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể tạo yêu cầu rút tiền"
        )


@router.get(
    "/withdrawals",
    response_model=WithdrawalsListResponse,
    responses={
        200: {"model": WithdrawalsListResponse, "description": "Lấy danh sách withdrawals thành công"},
        401: {"model": FinancialErrorResponse, "description": "Không tìm thấy token xác thực"}
    }
)
async def get_withdrawals(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    currency: Optional[str] = Query(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    financial_service: FinancialService = Depends(get_financial_service)
):
    """Lấy danh sách withdrawals - DB-based"""
    
    try:
        # Get transactions from DB
        query = db.query(Transaction).filter(
            and_(
                Transaction.user_id == user.id,
                Transaction.transaction_type == "withdrawal"
            )
        )
        
        if status_filter:
            query = query.filter(Transaction.status == status_filter)
        if currency:
            query = query.filter(Transaction.asset == currency.upper())
        
        # Get total count
        total_count = query.count()
        
        # Pagination
        offset = (page - 1) * limit
        transactions = query.order_by(desc(Transaction.created_at)).offset(offset).limit(limit).all()
        
        # Format response
        withdrawals_data = []
        for tx in transactions:
            withdrawals_data.append({
                "id": str(tx.id),
                "userId": str(tx.user_id),
                "userEmail": user.email,
                "amount": float(tx.amount),
                "currency": tx.asset.lower(),
                "method": tx.category or "unknown",
                "fee": float(tx.fee or 0),
                "netAmount": float(tx.net_amount),
                "status": tx.status,
                "bankAccount": tx.transaction_metadata.get("bank_account") if tx.transaction_metadata else None,
                "walletAddress": tx.to_address,
                "createdAt": tx.created_at.isoformat(),
                "updatedAt": tx.updated_at.isoformat(),
                "processedAt": tx.completed_at.isoformat() if tx.completed_at else None,
                "rejectReason": tx.failed_reason
            })
        
        return WithdrawalsListResponse(
            success=True,
            data={
                "withdrawals": withdrawals_data,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total_count,
                    "totalPages": (total_count + limit - 1) // limit
                }
            }
        )
        
    except Exception as e:
        print(f"Get withdrawals error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy danh sách rút tiền"
        )


# ========== BALANCE ENDPOINT ==========

@router.get("/balance")
async def get_balance(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    financial_service: FinancialService = Depends(get_financial_service)
):
    """Lấy số dư ví - DB-based"""
    
    try:
        balances = financial_service.get_all_balances(user.id)
        
        balance_dict = {}
        for balance in balances:
            balance_dict[balance.asset.lower()] = {
                "available": float(balance.available_balance),
                "locked": float(balance.locked_balance),
                "pending": float(balance.pending_balance),
                "total": float(balance.total_balance)
            }
        
        return {
            "success": True,
            "data": {
                "balances": balance_dict,
                "currencies": list(balance_dict.keys())
            }
        }
        
    except Exception as e:
        print(f"Get balance error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy số dư"
        )


# ========== TRANSACTIONS ENDPOINT ==========

@router.get("/transactions")
async def get_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    type_filter: Optional[str] = Query(None, alias="type"),
    status_filter: Optional[str] = Query(None, alias="status"),
    asset: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    financial_service: FinancialService = Depends(get_financial_service)
):
    """Lấy lịch sử giao dịch - DB-based"""
    
    try:
        query = db.query(Transaction).filter(
            Transaction.user_id == user.id
        )
        
        if type_filter:
            query = query.filter(Transaction.transaction_type == type_filter)
        if status_filter:
            query = query.filter(Transaction.status == status_filter)
        if asset:
            query = query.filter(Transaction.asset == asset.upper())
        if start_date:
            query = query.filter(Transaction.created_at >= start_date)
        if end_date:
            query = query.filter(Transaction.created_at <= end_date)
        
        # Get total count
        total_count = query.count()
        
        # Pagination
        offset = (page - 1) * limit
        transactions = query.order_by(desc(Transaction.created_at)).offset(offset).limit(limit).all()
        
        # Format response
        transactions_data = []
        for tx in transactions:
            transactions_data.append({
                "id": str(tx.id),
                "type": tx.transaction_type,
                "category": tx.category,
                "asset": tx.asset,
                "amount": float(tx.amount),
                "fee": float(tx.fee or 0),
                "net_amount": float(tx.net_amount),
                "status": tx.status,
                "description": tx.description,
                "reference_id": tx.reference_id,
                "created_at": tx.created_at.isoformat(),
                "completed_at": tx.completed_at.isoformat() if tx.completed_at else None
            })
        
        return {
            "success": True,
            "data": {
                "transactions": transactions_data,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total_count,
                    "totalPages": (total_count + limit - 1) // limit
                }
            }
        }
        
    except Exception as e:
        print(f"Get transactions error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy lịch sử giao dịch"
        )


# ========== CURRENCY EXCHANGE ENDPOINT ==========

@router.post("/exchange")
async def currency_exchange(
    request: Request,
    from_currency: str = Query(..., description="Source currency"),
    to_currency: str = Query(..., description="Target currency"),
    amount: float = Query(..., gt=0, description="Amount to exchange"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    financial_service: FinancialService = Depends(get_financial_service)
):
    """Exchange currency - DB-based"""
    
    try:
        # Check account status
        if user.status != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tài khoản không hoạt động"
            )
        
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        
        if from_currency == to_currency:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không thể đổi cùng loại tiền tệ"
            )
        
        # Get exchange rate
        from app.models.financial import ExchangeRate
        exchange_rate = db.query(ExchangeRate).filter(
            and_(
                ExchangeRate.base_asset == from_currency,
                ExchangeRate.target_asset == to_currency,
                ExchangeRate.is_active == True
            )
        ).first()
        
        if not exchange_rate:
            # Try inverse rate
            exchange_rate = db.query(ExchangeRate).filter(
                and_(
                    ExchangeRate.base_asset == to_currency,
                    ExchangeRate.target_asset == from_currency,
                    ExchangeRate.is_active == True
                )
            ).first()
            
            if exchange_rate and exchange_rate.inverse_rate:
                rate = float(exchange_rate.inverse_rate)
            else:
                # Default rate (1:1 for same base, or fetch from external API)
                rate = 1.0
        else:
            rate = float(exchange_rate.rate)
        
        # Calculate exchanged amount
        exchanged_amount = Decimal(str(amount)) * Decimal(str(rate))
        
        # Calculate fee (0.1% for exchange)
        fee_rate = Decimal("0.001")
        fee = exchanged_amount * fee_rate
        net_amount = exchanged_amount - fee
        
        # Check balance
        from_balance = financial_service.get_balance(user.id, from_currency)
        if not from_balance or from_balance.available_balance < Decimal(str(amount)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Số dư {from_currency} không đủ"
            )
        
        # Lock balance
        if not financial_service.lock_balance(user.id, from_currency, Decimal(str(amount))):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không thể khóa số dư"
            )
        
        # Create transactions
        # Debit from currency
        debit_tx = financial_service.create_transaction(
            user_id=user.id,
            transaction_type="exchange",
            category="currency_exchange",
            asset=from_currency,
            amount=Decimal(str(amount)),
            fee=Decimal("0"),
            description=f"Exchange {amount} {from_currency} to {to_currency}",
            metadata={
                "exchange_type": "currency_exchange",
                "to_currency": to_currency,
                "exchange_rate": float(rate),
                "exchanged_amount": float(exchanged_amount),
                "fee": float(fee)
            }
        )
        
        # Credit to currency
        credit_tx = financial_service.create_transaction(
            user_id=user.id,
            transaction_type="exchange",
            category="currency_exchange",
            asset=to_currency,
            amount=net_amount,
            fee=fee,
            description=f"Exchange {amount} {from_currency} to {to_currency}",
            metadata={
                "exchange_type": "currency_exchange",
                "from_currency": from_currency,
                "exchange_rate": float(rate),
                "original_amount": float(amount),
                "fee": float(fee)
            }
        )
        
        # Update balances
        from_balance.available_balance -= Decimal(str(amount))
        from_balance.locked_balance -= Decimal(str(amount))
        
        to_balance = financial_service.get_balance(user.id, to_currency)
        if not to_balance:
            # Create new balance record
            from app.models.financial import WalletBalance
            to_balance = WalletBalance(
                user_id=user.id,
                asset=to_currency,
                available_balance=net_amount,
                locked_balance=Decimal("0"),
                pending_balance=Decimal("0"),
                reserved_balance=Decimal("0")
            )
            db.add(to_balance)
        else:
            to_balance.available_balance += net_amount
        
        db.commit()
        
        # Log audit
        log_audit(
            db, user.id, "currency_exchange", "transaction",
            resource_id=str(debit_tx.id),
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent")
        )
        
        return {
            "success": True,
            "message": "Đổi tiền thành công",
            "data": {
                "from_currency": from_currency,
                "to_currency": to_currency,
                "amount": float(amount),
                "exchange_rate": float(rate),
                "exchanged_amount": float(exchanged_amount),
                "fee": float(fee),
                "net_amount": float(net_amount),
                "transaction_id": str(credit_tx.id)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Currency exchange error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể thực hiện đổi tiền"
        )


# ========== PAYMENT PROCESSING ENDPOINT ==========

@router.post("/payments/process")
async def process_payment(
    request: Request,
    payment_id: str = Query(..., description="Payment transaction ID"),
    action: str = Query(..., description="Action: approve, reject, cancel"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    financial_service: FinancialService = Depends(get_financial_service)
):
    """Process payment (approve/reject/cancel) - Admin only"""
    
    try:
        # Check if user is admin
        if not user.role or user.role.name not in ["admin", "owner"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chỉ quản trị viên mới có quyền xử lý thanh toán"
            )
        
        # Get transaction
        transaction = db.query(Transaction).filter(
            Transaction.id == int(payment_id)
        ).first()
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy giao dịch"
            )
        
        if action == "approve":
            if transaction.status != "pending":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Giao dịch không ở trạng thái pending"
                )
            
            # Update transaction status
            transaction.status = "completed"
            transaction.completed_at = datetime.utcnow()
            
            # Update balance for deposits
            if transaction.transaction_type == "deposit":
                balance = financial_service.get_balance(transaction.user_id, transaction.asset)
                if balance:
                    balance.available_balance += transaction.net_amount
                    balance.pending_balance -= transaction.amount
                else:
                    # Create new balance
                    from app.models.financial import WalletBalance
                    balance = WalletBalance(
                        user_id=transaction.user_id,
                        asset=transaction.asset,
                        available_balance=transaction.net_amount,
                        locked_balance=Decimal("0"),
                        pending_balance=Decimal("0"),
                        reserved_balance=Decimal("0")
                    )
                    db.add(balance)
            
            # Unlock balance for withdrawals
            elif transaction.transaction_type == "withdrawal":
                balance = financial_service.get_balance(transaction.user_id, transaction.asset)
                if balance:
                    balance.locked_balance -= (transaction.amount + transaction.fee)
            
            db.commit()
            
            message = "Phê duyệt thanh toán thành công"
            
        elif action == "reject":
            if transaction.status not in ["pending", "processing"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Giao dịch không thể từ chối"
                )
            
            transaction.status = "failed"
            transaction.failed_reason = "Rejected by admin"
            
            # Unlock balance
            if transaction.transaction_type == "withdrawal":
                balance = financial_service.get_balance(transaction.user_id, transaction.asset)
                if balance:
                    balance.locked_balance -= (transaction.amount + transaction.fee)
                    balance.available_balance += (transaction.amount + transaction.fee)
            
            db.commit()
            message = "Từ chối thanh toán thành công"
            
        elif action == "cancel":
            if transaction.status != "pending":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Giao dịch không thể hủy"
                )
            
            transaction.status = "cancelled"
            transaction.cancelled_at = datetime.utcnow()
            
            # Unlock balance
            if transaction.transaction_type == "withdrawal":
                balance = financial_service.get_balance(transaction.user_id, transaction.asset)
                if balance:
                    balance.locked_balance -= (transaction.amount + transaction.fee)
                    balance.available_balance += (transaction.amount + transaction.fee)
            
            db.commit()
            message = "Hủy thanh toán thành công"
            
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hành động không hợp lệ"
            )
        
        # Log audit
        log_audit(
            db, user.id, f"process_payment_{action}", "transaction",
            resource_id=str(transaction.id),
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent")
        )
        
        return {
            "success": True,
            "message": message,
            "data": {
                "transaction_id": str(transaction.id),
                "status": transaction.status,
                "action": action
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Process payment error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể xử lý thanh toán"
        )


# ========== FINANCIAL REPORTS ENDPOINT ==========

@router.get("/reports")
async def get_financial_reports(
    report_type: str = Query("summary", description="Report type: summary, transactions, deposits, withdrawals"),
    period: str = Query("monthly", description="Period: daily, weekly, monthly, yearly"),
    start_date: Optional[datetime] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="End date (ISO format)"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    financial_service: FinancialService = Depends(get_financial_service)
):
    """Get financial reports - DB-based"""
    
    try:
        # Set date range
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            if period == "daily":
                start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
            elif period == "weekly":
                start_date = end_date - timedelta(days=7)
            elif period == "monthly":
                start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            elif period == "yearly":
                start_date = end_date.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                start_date = end_date - timedelta(days=30)
        
        # Query transactions
        query = db.query(Transaction).filter(
            and_(
                Transaction.user_id == user.id,
                Transaction.created_at >= start_date,
                Transaction.created_at <= end_date
            )
        )
        
        transactions = query.all()
        
        # Calculate statistics
        total_deposits = sum(float(tx.amount) for tx in transactions if tx.transaction_type == "deposit" and tx.status == "completed")
        total_withdrawals = sum(float(tx.amount) for tx in transactions if tx.transaction_type == "withdrawal" and tx.status == "completed")
        total_fees = sum(float(tx.fee or 0) for tx in transactions)
        total_transactions = len(transactions)
        
        # Group by currency
        currency_stats = {}
        for tx in transactions:
            asset = tx.asset
            if asset not in currency_stats:
                currency_stats[asset] = {
                    "deposits": 0,
                    "withdrawals": 0,
                    "fees": 0,
                    "transactions": 0
                }
            
            if tx.transaction_type == "deposit" and tx.status == "completed":
                currency_stats[asset]["deposits"] += float(tx.amount)
            elif tx.transaction_type == "withdrawal" and tx.status == "completed":
                currency_stats[asset]["withdrawals"] += float(tx.amount)
            
            currency_stats[asset]["fees"] += float(tx.fee or 0)
            currency_stats[asset]["transactions"] += 1
        
        # Format response based on report type
        if report_type == "summary":
            return {
                "success": True,
                "report_type": "summary",
                "period": period,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "data": {
                    "total_deposits": round(total_deposits, 2),
                    "total_withdrawals": round(total_withdrawals, 2),
                    "total_fees": round(total_fees, 2),
                    "net_flow": round(total_deposits - total_withdrawals, 2),
                    "total_transactions": total_transactions,
                    "currency_breakdown": currency_stats
                }
            }
        
        elif report_type == "transactions":
            transactions_data = []
            for tx in transactions:
                transactions_data.append({
                    "id": str(tx.id),
                    "type": tx.transaction_type,
                    "asset": tx.asset,
                    "amount": float(tx.amount),
                    "fee": float(tx.fee or 0),
                    "status": tx.status,
                    "created_at": tx.created_at.isoformat(),
                    "completed_at": tx.completed_at.isoformat() if tx.completed_at else None
                })
            
            return {
                "success": True,
                "report_type": "transactions",
                "period": period,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "data": {
                    "transactions": transactions_data,
                    "total": len(transactions_data)
                }
            }
        
        elif report_type in ["deposits", "withdrawals"]:
            filtered_txs = [tx for tx in transactions if tx.transaction_type == report_type[:-1]]  # Remove 's'
            
            return {
                "success": True,
                "report_type": report_type,
                "period": period,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "data": {
                    "total_amount": round(sum(float(tx.amount) for tx in filtered_txs if tx.status == "completed"), 2),
                    "total_count": len(filtered_txs),
                    "completed": len([tx for tx in filtered_txs if tx.status == "completed"]),
                    "pending": len([tx for tx in filtered_txs if tx.status == "pending"]),
                    "failed": len([tx for tx in filtered_txs if tx.status == "failed"])
                }
            }
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Loại báo cáo không hợp lệ"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get financial reports error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy báo cáo tài chính"
        )
