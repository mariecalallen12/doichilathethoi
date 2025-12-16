"""
Client Endpoints - DB-based
Bao gồm: dashboard, wallet-balances, transactions, exchange-rates, crypto-deposit-address, generate-vietqr
"""

from fastapi import APIRouter, Depends, Request, HTTPException, status, Query, Response
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from decimal import Decimal
import json

from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc

from app.schemas.client import (
    DashboardResponse,
    WalletBalanceResponse,
    TransactionsResponse,
    ExchangeRatesResponse,
    CryptoDepositAddressRequest,
    CryptoDepositAddressResponse,
    GenerateVietQRRequest,
    VietQRResponse,
    ClientErrorResponse,
    ValidationErrorResponse,
    TransactionHistory,
    WalletBalance,
    ExchangeRate as ExchangeRateSchema,
)
from app.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.financial import WalletBalance as WalletBalanceModel, Transaction, ExchangeRate
from app.models.audit import AuditLog
from app.middleware.auth import get_client_ip
from app.core.two_factor import generate_totp_secret, build_otpauth_uri, verify_totp

router = APIRouter(tags=["client"])


def map_wallet_balances(user: User, db: Session) -> List[WalletBalance]:
    balances: List[WalletBalance] = []
    records = (
        db.query(WalletBalanceModel)
        .filter(WalletBalanceModel.user_id == user.id)
        .order_by(WalletBalanceModel.asset.asc())
        .all()
    )
    for rec in records:
        # Normalize currency code: trim whitespace and convert to uppercase
        asset = (rec.asset or '').strip().upper()
        if not asset:
            continue  # Skip invalid currency codes
        
        total = rec.total_balance
        balances.append(
            WalletBalance(
                userId=str(user.id),
                asset=asset,
                totalBalance=float(total),
                availableBalance=float(rec.available_balance or 0),
                lockedBalance=float(rec.locked_balance or 0),
                pendingBalance=float(rec.pending_balance or 0),
                reservedBalance=float(rec.reserved_balance or 0),
                lastUpdated=rec.updated_at or rec.created_at or datetime.utcnow(),
            )
        )
    return balances


def map_transactions(user: User, db: Session, limit: int = 50) -> List[TransactionHistory]:
    txs = (
        db.query(Transaction)
        .filter(Transaction.user_id == user.id)
        .order_by(Transaction.created_at.desc())
        .limit(limit)
        .all()
    )
    result: List[TransactionHistory] = []
    for tx in txs:
        amount = float(tx.amount or 0)
        fee = float(tx.fee or 0)
        net_amount = float(tx.net_amount or (tx.amount or 0) - (tx.fee or 0))
        result.append(
            TransactionHistory(
                id=str(tx.id),
                userId=str(tx.user_id),
                type=tx.transaction_type,
                category=tx.category or "",
                status=tx.status,
                amount=amount,
                currency=tx.asset.upper(),
                fee=fee,
                netAmount=net_amount,
                description=tx.description,
                reference=tx.reference_id,
                externalReference=tx.external_id,
                paymentMethod=tx.transaction_metadata.get("method") if tx.transaction_metadata else None,
                fromAddress=tx.from_address,
                toAddress=tx.to_address,
                bankDetails={
                    "bank_name": tx.bank_name,
                    "bank_account": tx.bank_account,
                }
                if tx.bank_name or tx.bank_account
                else None,
                blockchainNetwork=tx.network,
                confirmations=tx.confirmations,
                requiredConfirmations=None,
                metadata=tx.transaction_metadata or {},
                relatedId=None,
                adminNotes=None,
                createdAt=tx.created_at or datetime.utcnow(),
                updatedAt=tx.updated_at,
                completedAt=tx.completed_at,
            )
        )
    return result


def get_usd_equivalent(asset: str, amount: Decimal, db: Session) -> float:
    """Ước lượng giá trị USD dựa trên bảng exchange_rates (nếu có)"""
    # Normalize currency code: trim whitespace and convert to uppercase
    normalized_asset = (asset or '').strip().upper()
    if not normalized_asset:
        return float(amount)  # Return as-is if invalid currency
    
    if normalized_asset == "USD":
        return float(amount)

    rate = (
        db.query(ExchangeRate)
        .filter(
            and_(
                ExchangeRate.base_asset == asset,
                ExchangeRate.target_asset == "USD",
                ExchangeRate.is_active == True,
            )
        )
        .order_by(ExchangeRate.priority.desc())
        .first()
    )
    if rate:
        return float(amount * rate.rate)
    return float(amount)


# ========== DASHBOARD ENDPOINT ==========

@router.get(
    "/dashboard",
    response_model=DashboardResponse,
    responses={
        200: {"model": DashboardResponse, "description": "Lấy dữ liệu dashboard thành công"},
        401: {"model": ClientErrorResponse, "description": "Không tìm thấy token xác thực"},
        404: {"model": ClientErrorResponse, "description": "Không tìm thấy thông tin người dùng"},
        500: {"model": ClientErrorResponse, "description": "Lỗi hệ thống"},
    },
)
async def get_dashboard(
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Lấy dữ liệu dashboard từ dữ liệu thực trong DB
    """
    try:
        user = (
            db.query(User)
            .filter(User.id == current_user.id)
            .first()
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy thông tin người dùng",
            )

        # Balances
        balances = map_wallet_balances(user, db)

        # Recent transactions
        recent_transactions = map_transactions(user, db, limit=20)

        # Tổng quan (tính dựa trên availableBalance quy đổi USD)
        total_balance_usd = 0.0
        available_balance_usd = 0.0
        locked_balance_usd = 0.0
        pending_deposits = 0.0
        pending_withdrawals = 0.0

        for b in balances:
            asset_amount = Decimal(str(b.availableBalance))
            total_amount = Decimal(str(b.totalBalance))
            locked_amount = Decimal(str(b.lockedBalance))

            total_balance_usd += get_usd_equivalent(b.asset, total_amount, db)
            available_balance_usd += get_usd_equivalent(b.asset, asset_amount, db)
            locked_balance_usd += get_usd_equivalent(b.asset, locked_amount, db)

        pending_deposits = sum(
            t.amount
            for t in recent_transactions
            if t.type == "deposit" and t.status == "pending"
        )
        pending_withdrawals = sum(
            t.amount
            for t in recent_transactions
            if t.type == "withdrawal" and t.status == "pending"
        )

        # Stats
        deposits = [t for t in recent_transactions if t.type == "deposit"]
        withdrawals = [t for t in recent_transactions if t.type == "withdrawal"]

        total_deposits = sum(t.amount for t in deposits)
        total_withdrawals = sum(t.amount for t in withdrawals)
        deposit_count = len(deposits)
        withdrawal_count = len(withdrawals)

        largest_deposit = max((t.amount for t in deposits), default=0.0)
        largest_withdrawal = max((t.amount for t in withdrawals), default=0.0)

        average_deposit = total_deposits / deposit_count if deposit_count > 0 else 0.0
        average_withdrawal = (
            total_withdrawals / withdrawal_count if withdrawal_count > 0 else 0.0
        )

        last_deposit_at = deposits[0].createdAt if deposits else None
        last_withdrawal_at = withdrawals[0].createdAt if withdrawals else None

        # Risk & compliance (sơ bộ dựa trên trạng thái KYC)
        kyc_status = user.kyc_status or "pending"
        risk_score = 50
        if kyc_status == "verified":
            risk_score += 20
        if len(recent_transactions) > 10:
            risk_score += 10

        # Exchange rates (lấy từ bảng exchange_rates)
        rate_records = (
            db.query(ExchangeRate)
            .filter(ExchangeRate.is_active == True)
            .order_by(ExchangeRate.priority.desc())
            .all()
        )
        exchange_rates: Dict[str, float] = {}
        for r in rate_records:
            key = f"{r.base_asset}_{r.target_asset}"
            exchange_rates[key] = float(r.rate)

        dashboard_data = {
            "userId": str(user.id),
            "overview": {
                "totalBalance": total_balance_usd,
                "availableBalance": available_balance_usd,
                "lockedBalance": locked_balance_usd,
                "pendingDeposits": pending_deposits,
                "pendingWithdrawals": pending_withdrawals,
                "recentActivity": recent_transactions,
            },
            "balances": balances,
            "recentTransactions": recent_transactions,
            "stats": {
                "totalDeposits": total_deposits,
                "totalWithdrawals": total_withdrawals,
                "netFlow": total_deposits - total_withdrawals,
                "activeAssets": len(balances),
                "largestDeposit": largest_deposit,
                "largestWithdrawal": largest_withdrawal,
                "averageDeposit": average_deposit,
                "averageWithdrawal": average_withdrawal,
                "depositCount": deposit_count,
                "withdrawalCount": withdrawal_count,
                "lastDepositAt": last_deposit_at,
                "lastWithdrawalAt": last_withdrawal_at,
            },
            "riskScore": risk_score,
            "complianceStatus": kyc_status,
            # 2FA status: sử dụng phone_verified như proxy cho 2FA đã bật
            "twoFactorEnabled": bool(user.phone_verified),
            "lastUpdated": datetime.utcnow(),
        }

        return DashboardResponse(
            success=True,
            data=dashboard_data,
            exchangeRates=exchange_rates,
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Dashboard error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy dữ liệu dashboard",
        )


# ========== WALLET BALANCES ENDPOINT ==========

@router.get(
    "/wallet-balances",
    response_model=WalletBalanceResponse,
    responses={
        200: {"model": WalletBalanceResponse, "description": "Lấy số dư ví thành công"},
        401: {"model": ClientErrorResponse, "description": "Không tìm thấy token xác thực"},
    },
)
async def get_wallet_balances(
    request: Request,
    user_id: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Lấy số dư ví từ bảng wallet_balances
    """
    try:
        target_user_id = int(user_id) if user_id is not None else current_user.id
        user = db.query(User).filter(User.id == target_user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy người dùng",
            )

        balances = map_wallet_balances(user, db)

        return WalletBalanceResponse(success=True, data=balances)

    except HTTPException:
        raise
    except Exception as e:
        print(f"Wallet balances error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy số dư ví",
        )


# ========== TRANSACTIONS ENDPOINT ==========

@router.get(
    "/transactions",
    response_model=TransactionsResponse,
    responses={
        200: {"model": TransactionsResponse, "description": "Lấy danh sách giao dịch thành công"},
        401: {"model": ClientErrorResponse, "description": "Không tìm thấy token xác thực"},
    },
)
async def get_transactions(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    transaction_type: Optional[str] = Query(None, alias="type"),
    status_filter: Optional[str] = Query(None, alias="status"),
    currency: Optional[str] = Query(None, alias="currency"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Lấy danh sách giao dịch từ bảng transactions
    """
    try:
        query = db.query(Transaction).filter(Transaction.user_id == current_user.id)

        if transaction_type:
            query = query.filter(Transaction.transaction_type == transaction_type)

        if status_filter:
            query = query.filter(Transaction.status == status_filter)

        if currency:
            # Normalize currency code: trim whitespace and convert to uppercase
            normalized_currency = (currency or '').strip().upper()
            if normalized_currency:
                query = query.filter(Transaction.asset == normalized_currency)

        total_items = query.count()
        offset = (page - 1) * limit
        items = (
            query.order_by(Transaction.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        history = []
        for tx in items:
            amount = float(tx.amount or 0)
            fee = float(tx.fee or 0)
            net_amount = float(tx.net_amount or (tx.amount or 0) - (tx.fee or 0))
            history.append(
                TransactionHistory(
                    id=str(tx.id),
                    userId=str(tx.user_id),
                    type=tx.transaction_type,
                    category=tx.category or "",
                    status=tx.status,
                    amount=amount,
                    currency=(tx.asset or '').strip().upper(),
                    fee=fee,
                    netAmount=net_amount,
                    description=tx.description,
                    reference=tx.reference_id,
                    externalReference=tx.external_id,
                    paymentMethod=tx.transaction_metadata.get("method") if tx.transaction_metadata else None,
                    fromAddress=tx.from_address,
                    toAddress=tx.to_address,
                    bankDetails={
                        "bank_name": tx.bank_name,
                        "bank_account": tx.bank_account,
                    }
                    if tx.bank_name or tx.bank_account
                    else None,
                    blockchainNetwork=tx.network,
                    confirmations=tx.confirmations,
                    requiredConfirmations=None,
                    metadata=tx.transaction_metadata or {},
                    relatedId=None,
                    adminNotes=None,
                    createdAt=tx.created_at or datetime.utcnow(),
                    updatedAt=tx.updated_at,
                    completedAt=tx.completed_at,
                )
            )

        pagination = {
            "page": page,
            "limit": limit,
            "total": total_items,
            "pages": (total_items + limit - 1) // limit,
            "hasNext": offset + limit < total_items,
            "hasPrev": page > 1,
        }

        return TransactionsResponse(
            success=True,
            data=history,
            pagination=pagination,
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Transactions error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy danh sách giao dịch",
        )


# ========== EXCHANGE RATES ENDPOINT ==========

@router.get(
    "/exchange-rates",
    response_model=ExchangeRatesResponse,
    responses={
        200: {"model": ExchangeRatesResponse, "description": "Lấy tỷ giá hối đoái thành công"}
    },
)
async def get_exchange_rates(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Lấy tỷ giá hối đoái từ bảng exchange_rates
    """
    try:
        rate_records = (
            db.query(ExchangeRate)
            .filter(ExchangeRate.is_active == True)
            .order_by(ExchangeRate.priority.desc())
            .all()
        )

        exchange_rates: List[ExchangeRateSchema] = [
            ExchangeRateSchema(
                id=str(r.id),
                baseAsset=(r.base_asset or '').strip().upper(),
                targetAsset=(r.target_asset or '').strip().upper(),
                rate=float(r.rate),
                isActive=r.is_active,
                priority=r.priority,
                lastUpdated=r.updated_at or r.created_at or datetime.utcnow(),
                metadata={"source": r.source} if r.source else {},
            )
            for r in rate_records
            if r.base_asset and r.target_asset  # Skip invalid rates
        ]

        return ExchangeRatesResponse(success=True, data=exchange_rates)

    except Exception as e:
        print(f"Exchange rates error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy tỷ giá hối đoái",
        )


# ========== CRYPTO DEPOSIT ADDRESS & VIETQR ==========

@router.post(
    "/crypto-deposit-address",
    response_model=CryptoDepositAddressResponse,
    responses={
        200: {
            "model": CryptoDepositAddressResponse,
            "description": "Tạo địa chỉ nạp crypto thành công",
        },
        400: {"model": ValidationErrorResponse, "description": "Dữ liệu đầu vào không hợp lệ"},
        401: {"model": ClientErrorResponse, "description": "Không tìm thấy token xác thực"},
    },
)
async def create_crypto_deposit_address(
    request: Request,
    crypto_request: CryptoDepositAddressRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Tạo địa chỉ nạp crypto
    Endpoint này chỉ làm nhiệm vụ sinh địa chỉ và QR, ghi transaction do module financial xử lý.
    """
    try:
        # Tạo địa chỉ giả lập nhưng duy nhất (ở production sẽ tích hợp ví thực)
        import secrets

        # Normalize currency code: trim whitespace and convert to uppercase
        currency = (crypto_request.currency or '').strip().upper()
        if not currency:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Currency code không hợp lệ",
            )
        if currency == "BTC":
            address = f"bc1q{secrets.token_hex(16)}"
        elif currency in ("ETH", "USDT"):
            address = f"0x{secrets.token_hex(20)}"
        else:
            address = f"addr_{secrets.token_hex(16)}"

        from base64 import b64encode

        qr_content = f"{currency}:{address}"
        qr_code = b64encode(qr_content.encode()).decode()

        expires_at = datetime.utcnow() + timedelta(hours=24)

        return CryptoDepositAddressResponse(
            success=True,
            data={
                "address": address,
                "currency": currency,
                "network": crypto_request.network or "mainnet",
                "qrCode": qr_code,
                "memo": None,
                "createdAt": datetime.utcnow(),
                "expiresAt": expires_at,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Crypto deposit address error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể tạo địa chỉ nạp crypto",
        )


@router.post(
    "/generate-vietqr",
    response_model=VietQRResponse,
    responses={
        200: {"model": VietQRResponse, "description": "Tạo VietQR thành công"},
        400: {"model": ValidationErrorResponse, "description": "Dữ liệu đầu vào không hợp lệ"},
        401: {"model": ClientErrorResponse, "description": "Không tìm thấy token xác thực"},
    },
)
async def generate_vietqr(
    request: Request,
    qr_request: GenerateVietQRRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Tạo QR code thanh toán VietQR
    (ở production sẽ tích hợp với VietQR API, ở đây chỉ encode dữ liệu cơ bản)
    """
    try:
        from base64 import b64encode
        import json

        payment_id = f"VQR{current_user.id}{int(datetime.utcnow().timestamp())}"

        qr_data = {
            "paymentId": payment_id,
            "amount": qr_request.amount,
            "description": qr_request.description,
            "orderId": qr_request.orderId,
            "bankCode": "970436",
            "accountNumber": current_user.customer_payment_id or "0000000000",
            "accountName": "DIGITAL UTOPIA",
        }

        qr_content = json.dumps(qr_data, separators=(",", ":"))
        qr_code = b64encode(qr_content.encode()).decode()
        payment_url = f"https://vietqr.net/pay/{payment_id}"

        return VietQRResponse(
            success=True,
            data={
                **qr_data,
                "qrCode": qr_code,
                "paymentUrl": payment_url,
                "createdAt": datetime.utcnow().isoformat(),
                "expiresAt": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
            },
            qrCode=qr_code,
            paymentUrl=payment_url,
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"VietQR generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể tạo VietQR",
        )


# ========== PROFILE ENDPOINTS ==========

@router.get("/profile")
async def get_client_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get client profile information"""
    try:
        profile = current_user.profile
        
        if not profile:
            # Create empty profile if doesn't exist
            from app.models.user import UserProfile
            profile = UserProfile(
                user_id=current_user.id,
                full_name=current_user.email.split('@')[0],
                display_name=current_user.email.split('@')[0]
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)
        
        return {
            "success": True,
            "data": {
                "id": str(current_user.id),
                "email": current_user.email,
                "full_name": profile.full_name,
                "display_name": profile.display_name,
                "phone": profile.phone,
                "date_of_birth": profile.date_of_birth.isoformat() if profile.date_of_birth else None,
                "address": profile.address,
                "country": profile.country,
                "city": profile.city,
                "postal_code": profile.postal_code,
                "avatar_url": profile.avatar_url,
                "id_type": profile.id_type,
                "id_verified": profile.id_verified,
                "bank_account_name": profile.bank_account_name,
                "bank_account_number": profile.bank_account_number,
                "bank_name": profile.bank_name,
                "emergency_contact_name": profile.emergency_contact_name,
                "emergency_contact_phone": profile.emergency_contact_phone,
                "preferences": profile.preferences or {},
                "notification_settings": profile.notification_settings or {},
                "created_at": profile.created_at.isoformat(),
                "updated_at": profile.updated_at.isoformat()
            }
        }
        
    except Exception as e:
        print(f"Get client profile error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy thông tin profile"
        )


@router.put("/profile")
async def update_client_profile(
    request: Request,
    full_name: Optional[str] = None,
    display_name: Optional[str] = None,
    phone: Optional[str] = None,
    date_of_birth: Optional[str] = None,
    address: Optional[str] = None,
    country: Optional[str] = None,
    city: Optional[str] = None,
    postal_code: Optional[str] = None,
    emergency_contact_name: Optional[str] = None,
    emergency_contact_phone: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update client profile information"""
    try:
        profile = current_user.profile
        
        if not profile:
            # Create profile if doesn't exist
            from app.models.user import UserProfile
            profile = UserProfile(user_id=current_user.id)
            db.add(profile)
        
        # Update fields
        if full_name is not None:
            profile.full_name = full_name
        if display_name is not None:
            profile.display_name = display_name
        if phone is not None:
            profile.phone = phone
        if date_of_birth is not None:
            from datetime import datetime
            profile.date_of_birth = datetime.fromisoformat(date_of_birth.replace('Z', '+00:00')).date()
        if address is not None:
            profile.address = address
        if country is not None:
            profile.country = country
        if city is not None:
            profile.city = city
        if postal_code is not None:
            profile.postal_code = postal_code
        if emergency_contact_name is not None:
            profile.emergency_contact_name = emergency_contact_name
        if emergency_contact_phone is not None:
            profile.emergency_contact_phone = emergency_contact_phone
        
        db.commit()
        db.refresh(profile)
        
        # Log audit
        from app.models.audit import AuditLog
        try:
            client_ip = get_client_ip(request)
        except:
            client_ip = None
        audit_log = AuditLog(
            user_id=current_user.id,
            action="update_profile",
            resource_type="user_profile",
            resource_id=str(profile.id),
            ip_address=client_ip,
            user_agent=request.headers.get("user-agent"),
            result="success",
            category="client"
        )
        db.add(audit_log)
        db.commit()
        
        return {
            "success": True,
            "message": "Cập nhật profile thành công",
            "data": {
                "id": str(current_user.id),
                "full_name": profile.full_name,
                "display_name": profile.display_name,
                "phone": profile.phone,
                "updated_at": profile.updated_at.isoformat()
            }
        }
        
    except Exception as e:
        print(f"Update client profile error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể cập nhật profile"
        )


@router.get("/settings")
async def get_client_settings(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get client settings"""
    try:
        profile = current_user.profile
        
        if not profile:
            from app.models.user import UserProfile
            profile = UserProfile(
                user_id=current_user.id,
                notification_settings={
                    "email": True,
                    "sms": False,
                    "push": True
                }
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)
        
        return {
            "success": True,
            "data": {
                "notifications": profile.notification_settings or {
                    "email": True,
                    "sms": False,
                    "push": True
                },
                "language": profile.preferences.get("language", "en") if profile.preferences else "en",
                "timezone": profile.preferences.get("timezone", "UTC") if profile.preferences else "UTC",
                "theme": profile.preferences.get("theme", "light") if profile.preferences else "light"
            }
        }
        
    except Exception as e:
        print(f"Get client settings error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy cài đặt"
        )


@router.put("/settings")
async def update_client_settings(
    request: Request,
    notifications: Optional[Dict[str, Any]] = None,
    language: Optional[str] = None,
    timezone: Optional[str] = None,
    theme: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update client settings"""
    try:
        profile = current_user.profile
        
        if not profile:
            from app.models.user import UserProfile
            profile = UserProfile(user_id=current_user.id)
            db.add(profile)
        
        # Update notification settings
        if notifications is not None:
            if not profile.notification_settings:
                profile.notification_settings = {}
            profile.notification_settings.update(notifications)
        
        # Update preferences
        if not profile.preferences:
            profile.preferences = {}
        
        if language is not None:
            profile.preferences["language"] = language
        if timezone is not None:
            profile.preferences["timezone"] = timezone
        if theme is not None:
            profile.preferences["theme"] = theme
        
        db.commit()
        db.refresh(profile)
        
        return {
            "success": True,
            "message": "Cập nhật cài đặt thành công",
            "data": {
                "notifications": profile.notification_settings,
                "language": profile.preferences.get("language"),
                "timezone": profile.preferences.get("timezone"),
                "theme": profile.preferences.get("theme")
            }
        }
        
    except Exception as e:
        print(f"Update client settings error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể cập nhật cài đặt"
        )


@router.get("/preferences")
async def get_client_preferences(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get client preferences"""
    try:
        profile = current_user.profile
        
        if not profile:
            from app.models.user import UserProfile
            profile = UserProfile(user_id=current_user.id)
            db.add(profile)
            db.commit()
            db.refresh(profile)
        
        preferences = profile.preferences or {}
        
        return {
            "success": True,
            "data": {
                "trading_style": preferences.get("trading_style", "moderate"),
                "risk_tolerance": preferences.get("risk_tolerance", "medium"),
                "investment_goals": preferences.get("investment_goals", []),
                "preferred_assets": preferences.get("preferred_assets", []),
                "notification_preferences": preferences.get("notification_preferences", {})
            }
        }
        
    except Exception as e:
        print(f"Get client preferences error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy preferences"
        )


@router.put("/preferences")
async def update_client_preferences(
    request: Request,
    trading_style: Optional[str] = None,
    risk_tolerance: Optional[str] = None,
    investment_goals: Optional[List[str]] = None,
    preferred_assets: Optional[List[str]] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update client preferences"""
    try:
        profile = current_user.profile
        
        if not profile:
            from app.models.user import UserProfile
            profile = UserProfile(user_id=current_user.id)
            db.add(profile)
        
        if not profile.preferences:
            profile.preferences = {}
        
        if trading_style is not None:
            profile.preferences["trading_style"] = trading_style
        if risk_tolerance is not None:
            profile.preferences["risk_tolerance"] = risk_tolerance
        if investment_goals is not None:
            profile.preferences["investment_goals"] = investment_goals
        if preferred_assets is not None:
            profile.preferences["preferred_assets"] = preferred_assets
        
        db.commit()
        db.refresh(profile)
        
        return {
            "success": True,
            "message": "Cập nhật preferences thành công",
            "data": profile.preferences
        }
        
    except Exception as e:
        print(f"Update client preferences error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể cập nhật preferences"
        )


# ========== TWO-FACTOR AUTH (2FA TOTP) ==========


@router.post("/2fa/setup")
async def setup_two_factor_auth(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Khởi tạo 2FA TOTP cho người dùng hiện tại.

    Trả về:
    - secret: mã secret ở dạng Base32
    - otpauth_uri / qr_data: URI để tạo QR code trong ứng dụng xác thực
    """
    try:
        # Generate new secret and persist
        secret = generate_totp_secret()
        current_user.two_factor_secret = secret
        # Khi mới setup, chưa bật 2FA cho đến khi verify
        current_user.two_factor_enabled = False
        current_user.two_factor_backup_codes = []
        db.commit()
        db.refresh(current_user)

        # Build otpauth URI for Google Authenticator
        account_name = current_user.email or f"user-{current_user.id}"
        issuer = "CMEETRADING"
        otpauth_uri = build_otpauth_uri(secret, account_name=account_name, issuer=issuer)

        return {
            "success": True,
            "data": {
                "secret": secret,
                "otpauth_uri": otpauth_uri,
                "qr_data": otpauth_uri,
            },
        }
    except Exception as e:
        print(f"2FA setup error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể khởi tạo 2FA",
        )


@router.post("/2fa/verify")
async def verify_two_factor_auth(
    request: Request,
    code: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Xác thực mã TOTP và bật 2FA cho tài khoản.

    Body (form/json đơn giản):
    - code: mã 6 số từ ứng dụng xác thực
    """
    try:
        if not current_user.two_factor_secret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2FA chưa được khởi tạo",
            )

        if not verify_totp(code, current_user.two_factor_secret):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mã 2FA không hợp lệ",
            )

        # Generate backup codes
        import secrets
        backup_codes = [
            secrets.token_hex(4).upper() for _ in range(10)
        ]  # 8 hex chars mỗi mã

        current_user.two_factor_enabled = True
        current_user.two_factor_backup_codes = backup_codes
        db.commit()
        db.refresh(current_user)

        # Log audit
        try:
            audit_log = AuditLog(
                user_id=current_user.id,
                action="enable_2fa",
                resource_type="user",
                resource_id=str(current_user.id),
                ip_address=get_client_ip(request),
                user_agent=request.headers.get("user-agent"),
                result="success",
                category="authentication",
            )
            db.add(audit_log)
            db.commit()
        except Exception:
            pass

        return {
            "success": True,
            "data": {
                "enabled": True,
                "backup_codes": backup_codes,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"2FA verify error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể xác thực 2FA",
        )


@router.post("/2fa/disable")
async def disable_two_factor_auth(
    request: Request,
    code: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Tắt 2FA cho tài khoản.

    Body:
    - code: mã TOTP hiện tại hoặc một trong các backup code
    """
    try:
        if not current_user.two_factor_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2FA chưa được bật",
            )

        valid = False

        # Accept current TOTP code if secret is still set
        if current_user.two_factor_secret and verify_totp(code, current_user.two_factor_secret):
            valid = True

        # Or accept one of the backup codes
        backup_codes = current_user.two_factor_backup_codes or []
        if not valid and code in backup_codes:
            valid = True
            # One-time use: remove used code
            backup_codes = [c for c in backup_codes if c != code]
            current_user.two_factor_backup_codes = backup_codes

        if not valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mã 2FA không hợp lệ",
            )

        # Disable 2FA
        current_user.two_factor_enabled = False
        current_user.two_factor_secret = None
        if not valid:  # pragma: no cover - safety
            current_user.two_factor_backup_codes = []
        db.commit()
        db.refresh(current_user)

        # Log audit
        try:
            audit_log = AuditLog(
                user_id=current_user.id,
                action="disable_2fa",
                resource_type="user",
                resource_id=str(current_user.id),
                ip_address=get_client_ip(request),
                user_agent=request.headers.get("user-agent"),
                result="success",
                category="authentication",
            )
            db.add(audit_log)
            db.commit()
        except Exception:
            pass

        return {
            "success": True,
            "data": {
                "enabled": False,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"2FA disable error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể tắt 2FA",
        )


@router.get("/onboarding/status")
async def get_onboarding_status(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get client onboarding status"""
    try:
        # Check onboarding steps
        steps = {
            "profile_completion": False,
            "kyc_verification": False,
            "bank_account": False,
            "first_deposit": False,
            "trading_setup": False
        }
        
        profile = current_user.profile
        if profile:
            steps["profile_completion"] = bool(profile.full_name and profile.phone)
            steps["bank_account"] = bool(profile.bank_account_number)
        
        steps["kyc_verification"] = current_user.kyc_status == "verified"
        
        # Check first deposit
        from app.models.financial import Transaction
        first_deposit = db.query(Transaction).filter(
            and_(
                Transaction.user_id == current_user.id,
                Transaction.transaction_type == "deposit",
                Transaction.status == "completed"
            )
        ).first()
        steps["first_deposit"] = first_deposit is not None
        
        # Check trading setup
        from app.models.trading import TradingOrder
        first_trade = db.query(TradingOrder).filter(
            TradingOrder.user_id == current_user.id
        ).first()
        steps["trading_setup"] = first_trade is not None
        
        completed_steps = sum(1 for v in steps.values() if v)
        total_steps = len(steps)
        progress = (completed_steps / total_steps) * 100
        
        return {
            "success": True,
            "data": {
                "steps": steps,
                "progress": round(progress, 2),
                "completed_steps": completed_steps,
                "total_steps": total_steps,
                "is_complete": all(steps.values())
            }
        }
        
    except Exception as e:
        print(f"Get onboarding status error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy trạng thái onboarding"
        )


@router.post("/onboarding/complete")
async def complete_onboarding_step(
    request: Request,
    step: str = Query(..., description="Onboarding step to complete"),
    data: Optional[Dict[str, Any]] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Complete an onboarding step"""
    try:
        profile = current_user.profile
        
        if not profile:
            from app.models.user import UserProfile
            profile = UserProfile(user_id=current_user.id)
            db.add(profile)
        
        if step == "kyc_verification":
            if data and data.get("document_type"):
                # Update KYC document info
                profile.id_type = data.get("document_type")
                profile.id_number = data.get("document_number")
                # Note: Actual KYC verification would be handled by compliance module
                return {
                    "success": True,
                    "message": "Thông tin KYC đã được lưu. Vui lòng đợi xác minh.",
                    "data": {
                        "step": step,
                        "status": "pending_verification"
                    }
                }
        
        elif step == "profile_completion":
            if data:
                if data.get("full_name"):
                    profile.full_name = data.get("full_name")
                if data.get("phone"):
                    profile.phone = data.get("phone")
                if data.get("date_of_birth"):
                    from datetime import datetime
                    profile.date_of_birth = datetime.fromisoformat(data.get("date_of_birth").replace('Z', '+00:00')).date()
        
        elif step == "bank_account":
            if data:
                profile.bank_account_name = data.get("account_name")
                profile.bank_account_number = data.get("account_number")
                profile.bank_name = data.get("bank_name")
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Hoàn thành bước {step}",
            "data": {
                "step": step,
                "status": "completed"
            }
        }
        
    except Exception as e:
        print(f"Complete onboarding step error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể hoàn thành bước onboarding"
        )


# ========== REGISTRATION FIELDS CONFIG ENDPOINT ==========

from ...services.registration_fields_service import (
    get_registration_fields_config as get_config_service,
    DEFAULT_REGISTRATION_FIELDS
)


@router.get("/settings/registration-fields")
async def get_registration_fields_config(
    db: Session = Depends(get_db)
):
    """
    Lấy cấu hình các trường đăng ký - Public endpoint (không cần authentication)
    Returns config với version và updated_at để support real-time updates
    Set cache headers để prevent caching
    """
    try:
        config = get_config_service(db=db)
        
        # Create response with no-cache headers
        response_data = {
            "success": True,
            "data": config
        }
        
        # Set cache headers to prevent caching
        headers = {
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
            "ETag": f'"{config.get("version", 0)}"',  # Use version as ETag
        }
        
        return Response(
            content=json.dumps(response_data),
            media_type="application/json",
            headers=headers
        )
        
    except Exception as e:
        print(f"Get registration fields config error: {e}")
        # Return default config on error
        from datetime import datetime
        default_config = {
            **DEFAULT_REGISTRATION_FIELDS,
            "version": 0,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        return Response(
            content=json.dumps({
            "success": True,
                "data": default_config
            }),
            media_type="application/json",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
        }
        )
