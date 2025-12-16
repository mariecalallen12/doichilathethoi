"""
Authentication Endpoints - DB-based
Bao gồm: login, register, logout, refresh token, verify token, password reset, email/phone verification
"""

from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import secrets
import hashlib

# Import schemas
from ...schemas.auth import (
    LoginRequest,
    RegisterRequest,
    LoginResponse,
    RegisterResponse,
    LogoutResponse,
    RefreshTokenResponse,
    VerifyTokenResponse,
    AuthErrorResponse,
    ValidationErrorResponse,
    UserData
)

# Import dependencies
from ...db.session import get_db
from ...db.redis_client import get_redis, RedisCache
from ...core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_access_token,
    verify_refresh_token
)
from ...middleware.auth import (
    get_client_ip,
    rate_limit,
    authenticate_user,
    AuthenticationError,
    RateLimitError
)
from ...models.user import User, UserProfile, Role, RefreshToken
from ...services.user_service import UserService
from ...models.audit import AuditLog

router = APIRouter(tags=["authentication"])


# ========== HELPER FUNCTIONS ==========

def generate_customer_payment_id(db: Session) -> str:
    """Generate unique customer_payment_id"""
    while True:
        # Generate 10-digit number
        payment_id = ''.join([str(secrets.randbelow(10)) for _ in range(10)])
        # Check if exists
        existing = db.query(User).filter(User.customer_payment_id == payment_id).first()
        if not existing:
            return payment_id


def get_user_permissions(user: User, db: Session) -> list:
    """Get user permissions from role"""
    if not user.role_id:
        return []
    
    role = db.query(Role).filter(Role.id == user.role_id).first()
    if not role or not role.permissions:
        return []
    
    return [perm.name for perm in role.permissions]


def format_user_response(user: User, db: Session, include_permissions: bool = True) -> Dict[str, Any]:
    """Format user data for response"""
    role_name = user.role.name if user.role else "customer"
    permissions = get_user_permissions(user, db) if include_permissions else []
    
    return {
        "id": str(user.id),
        "email": user.email,
        "role": role_name,
        "permissions": permissions,
        "kyc_status": user.kyc_status,
        "email_verified": user.email_verified,
        "phone_verified": user.phone_verified,
        "status": user.status,
        "display_name": user.profile.display_name if user.profile else None,
        "avatar_url": user.profile.avatar_url if user.profile else None,
    }


def log_audit(
    db: Session,
    user_id: Optional[int],
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    result: str = "success",
    error_message: Optional[str] = None
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
            error_message=error_message,
            category="authentication"
        )
        db.add(audit_log)
        db.commit()
    except Exception as e:
        # Don't fail if audit logging fails
        print(f"Audit logging error: {e}")


# ========== LOGIN ENDPOINT ==========

@router.post(
    "/login",
    response_model=LoginResponse,
    responses={
        200: {"model": LoginResponse, "description": "Đăng nhập thành công"},
        400: {"model": ValidationErrorResponse, "description": "Dữ liệu đầu vào không hợp lệ"},
        401: {"model": AuthErrorResponse, "description": "Đăng nhập thất bại"},
        429: {"model": AuthErrorResponse, "description": "Quá nhiều yêu cầu"}
    }
)
async def login(
    request: Request,
    login_data: LoginRequest,
    db: Session = Depends(get_db),
    cache: RedisCache = Depends(get_redis)
):
    """Đăng nhập người dùng - DB-based"""
    
    try:
        # Apply rate limiting
        client_ip = get_client_ip(request)
        await rate_limit(client_ip, "login", cache)
        
        # Authenticate user
        user = await authenticate_user(login_data.email, login_data.password, db)
        
        if not user:
            # Log failed attempt
            log_audit(
                db, None, "login_failed", "user",
                ip_address=client_ip,
                user_agent=request.headers.get("user-agent"),
                result="failure",
                error_message="Invalid credentials"
            )
            await rate_limit(client_ip, "login_failed", cache)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email hoặc mật khẩu không đúng"
            )
        
        # Check account status
        if user.status == "pending":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tài khoản đang chờ phê duyệt"
            )
        
        if user.status == "suspended":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tài khoản đã bị tạm khóa"
            )
        
        # Create tokens
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.name if user.role else "customer",
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        # Store refresh token in DB
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        expires_at = datetime.utcnow() + timedelta(days=7)  # 7 days
        
        refresh_token_record = RefreshToken(
            user_id=user.id,
            token=refresh_token,
            token_hash=token_hash,
            expires_at=expires_at,
            ip_address=client_ip,
            user_agent=request.headers.get("user-agent")
        )
        db.add(refresh_token_record)
        db.commit()
        
        # Format user response
        user_data = format_user_response(user, db)
        
        # Log successful login
        log_audit(
            db, user.id, "login", "user",
            ip_address=client_ip,
            user_agent=request.headers.get("user-agent"),
            result="success"
        )
        
        return LoginResponse(
            success=True,
            message="Đăng nhập thành công",
            data={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": user_data,
                "expires_in": 1800  # 30 minutes
            }
        )
        
    except RateLimitError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi hệ thống. Vui lòng thử lại sau."
        )


# ========== REGISTER ENDPOINT ==========

@router.post(
    "/register",
    response_model=RegisterResponse,
    responses={
        201: {"model": RegisterResponse, "description": "Đăng ký thành công"},
        400: {"model": ValidationErrorResponse, "description": "Dữ liệu đầu vào không hợp lệ"},
        429: {"model": AuthErrorResponse, "description": "Quá nhiều yêu cầu"}
    }
)
async def register(
    request: Request,
    register_data: RegisterRequest,
    db: Session = Depends(get_db),
    cache: RedisCache = Depends(get_redis)
):
    """Đăng ký tài khoản mới - DB-based"""
    
    try:
        # Apply rate limiting
        client_ip = get_client_ip(request)
        await rate_limit(client_ip, "register", cache)
        
        # Check if email already exists
        user_service = UserService(db, cache)
        existing_user = user_service.get_by_email(register_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email đã được sử dụng"
            )
        
        # Validate referral code if provided
        referral_code_id = None
        if register_data.referralCode:
            from ...models.referral import ReferralCode
            ref_code = db.query(ReferralCode).filter(
                ReferralCode.code == register_data.referralCode,
                ReferralCode.status == "active"
            ).first()
            if not ref_code:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Mã giới thiệu không hợp lệ"
                )
            referral_code_id = ref_code.id
        
        # Generate customer_payment_id
        customer_payment_id = generate_customer_payment_id(db)
        
        # Create user
        user = user_service.create(
            email=register_data.email,
            password=register_data.password,
            role_name="customer",
            referral_code=register_data.referralCode
        )
        
        # Set customer_payment_id
        user.customer_payment_id = customer_payment_id
        user.terms_accepted_at = datetime.utcnow()
        
        # Update profile
        if user.profile:
            user.profile.display_name = register_data.displayName
            if register_data.phoneNumber:
                user.profile.phone = register_data.phoneNumber
        
        db.commit()
        db.refresh(user)
        
        # Create referral registration if applicable
        if referral_code_id:
            from ...models.referral import ReferralRegistration
            reg = ReferralRegistration(
                referral_code_id=referral_code_id,
                referred_user_id=user.id,
                source_type="code",
                ip_address=client_ip,
                user_agent=request.headers.get("user-agent")
            )
            db.add(reg)
            db.commit()
        
        # Log audit
        log_audit(
            db, user.id, "register", "user",
            ip_address=client_ip,
            user_agent=request.headers.get("user-agent"),
            result="success"
        )
        
        return RegisterResponse(
            success=True,
            message="Đăng ký thành công. Tài khoản của bạn đang chờ phê duyệt từ quản trị viên.",
            data={
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "display_name": register_data.displayName,
                    "approval_status": "pending",
                }
            },
            needsApproval=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Register error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Đăng ký thất bại. Vui lòng thử lại."
        )


# ========== REFRESH TOKEN ENDPOINT ==========

@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    responses={
        200: {"model": RefreshTokenResponse, "description": "Token đã được làm mới"},
        401: {"model": AuthErrorResponse, "description": "Không thể làm mới token"}
    }
)
async def refresh_token(
    request: Request,
    db: Session = Depends(get_db)
):
    """Làm mới access token"""
    
    try:
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Không tìm thấy refresh token"
            )
        
        refresh_token = auth_header.split(" ")[1]
        
        # Verify refresh token
        payload = verify_refresh_token(refresh_token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token không hợp lệ"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token không chứa thông tin người dùng"
            )
        
        # Check if token exists in DB and not revoked
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        token_record = db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked == False,
            RefreshToken.expires_at > datetime.utcnow()
        ).first()
        
        if not token_record:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token không hợp lệ hoặc đã hết hạn"
            )
        
        # Get user
        user_service = UserService(db, None)
        user = user_service.get_by_id(int(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Người dùng không tồn tại"
            )
        
        # Create new access token
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.name if user.role else "customer",
        }
        new_access_token = create_access_token(token_data)
        
        return RefreshTokenResponse(
            success=True,
            message="Token đã được làm mới",
            data={
                "access_token": new_access_token,
                "expires_in": 1800
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Refresh token error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Không thể làm mới token. Vui lòng đăng nhập lại."
        )


# ========== LOGOUT ENDPOINT ==========

@router.post(
    "/logout",
    response_model=LogoutResponse,
    responses={
        200: {"model": LogoutResponse, "description": "Đăng xuất thành công"},
        401: {"model": AuthErrorResponse, "description": "Không tìm thấy token xác thực"}
    }
)
async def logout(
    request: Request,
    db: Session = Depends(get_db)
):
    """Đăng xuất người dùng"""
    
    try:
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            # Even if no token, consider logout successful
            return LogoutResponse(
                success=True,
                message="Đăng xuất thành công"
            )
        
        refresh_token = auth_header.split(" ")[1]
        
        # Revoke refresh token
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        token_record = db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash
        ).first()
        
        if token_record:
            token_record.revoked = True
            token_record.revoked_at = datetime.utcnow()
            db.commit()
        
        # Log audit
        payload = verify_refresh_token(refresh_token)
        user_id = payload.get("sub") if payload else None
        if user_id:
            log_audit(
                db, int(user_id), "logout", "user",
                ip_address=get_client_ip(request),
                user_agent=request.headers.get("user-agent"),
                result="success"
            )
        
        return LogoutResponse(
            success=True,
            message="Đăng xuất thành công"
        )
        
    except Exception as e:
        # Even if logout fails, return success
        print(f"Logout error: {e}")
        return LogoutResponse(
            success=True,
            message="Đăng xuất thành công"
        )


# ========== VERIFY TOKEN ENDPOINT ==========

@router.get(
    "/verify",
    response_model=VerifyTokenResponse,
    responses={
        200: {"model": VerifyTokenResponse, "description": "Token hợp lệ"},
        401: {"model": AuthErrorResponse, "description": "Token không hợp lệ"}
    }
)
async def verify_token_endpoint(
    request: Request,
    db: Session = Depends(get_db)
):
    """Verify access token và trả về user info"""
    
    try:
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Không tìm thấy token xác thực"
            )
        
        token = auth_header.split(" ")[1]
        payload = verify_access_token(token)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token không hợp lệ"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token không chứa thông tin người dùng"
            )
        
        # Get user from DB
        user_service = UserService(db, None)
        user = user_service.get_by_id(int(user_id))
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Người dùng không tồn tại"
            )
        
        user_data = format_user_response(user, db)
        
        return VerifyTokenResponse(
            success=True,
            data={
                "user": user_data
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Verify token error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ"
        )


# ========== FORGOT PASSWORD ENDPOINT ==========

@router.post(
    "/forgot-password",
    responses={
        200: {"description": "Email reset password đã được gửi"},
        400: {"model": ValidationErrorResponse, "description": "Email không hợp lệ"},
        404: {"model": AuthErrorResponse, "description": "Email không tồn tại"}
    }
)
async def forgot_password(
    request: Request,
    email: str,
    db: Session = Depends(get_db),
    cache: RedisCache = Depends(get_redis)
):
    """Gửi email reset password"""
    
    try:
        client_ip = get_client_ip(request)
        await rate_limit(client_ip, "general", cache)
        
        # Get user
        user_service = UserService(db, cache)
        user = user_service.get_by_email(email.lower())
        
        if not user:
            # Don't reveal if email exists
            return {
                "success": True,
                "message": "Nếu email tồn tại, chúng tôi đã gửi link reset password."
            }
        
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(reset_token.encode()).hexdigest()
        
        # Store in cache (24h expiration)
        if cache:
            cache.set(
                f"password_reset:{token_hash}",
                str(user.id),
                ex=86400  # 24 hours
            )
        else:
            # Fallback: store in DB (would need a password_reset_tokens table)
            pass
        
        # TODO: Send email with reset link
        # reset_link = f"https://digital-utopia.app/reset-password?token={reset_token}"
        # await send_email({
        #     "to": user.email,
        #     "template": "password_reset",
        #     "subject": "Đặt lại mật khẩu",
        #     "data": {"reset_link": reset_link}
        # })
        
        log_audit(
            db, user.id, "forgot_password", "user",
            ip_address=client_ip,
            user_agent=request.headers.get("user-agent"),
            result="success"
        )
        
        return {
            "success": True,
            "message": "Nếu email tồn tại, chúng tôi đã gửi link reset password."
        }
        
    except Exception as e:
        print(f"Forgot password error: {e}")
        return {
            "success": True,
            "message": "Nếu email tồn tại, chúng tôi đã gửi link reset password."
        }


# ========== RESET PASSWORD ENDPOINT ==========

@router.post(
    "/reset-password",
    responses={
        200: {"description": "Mật khẩu đã được đặt lại"},
        400: {"model": ValidationErrorResponse, "description": "Token hoặc mật khẩu không hợp lệ"},
        401: {"model": AuthErrorResponse, "description": "Token không hợp lệ hoặc đã hết hạn"}
    }
)
async def reset_password(
    request: Request,
    token: str,
    new_password: str,
    db: Session = Depends(get_db),
    cache: RedisCache = Depends(get_redis)
):
    """Đặt lại mật khẩu với token"""
    
    try:
        client_ip = get_client_ip(request)
        
        # Validate password strength
        if len(new_password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mật khẩu phải có ít nhất 6 ký tự"
            )
        
        # Verify token
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        user_id_str = None
        
        if cache:
            user_id_str = cache.get(f"password_reset:{token_hash}")
        
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token không hợp lệ hoặc đã hết hạn"
            )
        
        user_id = int(user_id_str)
        
        # Get user
        user_service = UserService(db, cache)
        user = user_service.get_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Người dùng không tồn tại"
            )
        
        # Update password
        user.password_hash = get_password_hash(new_password)
        db.commit()
        
        # Delete reset token
        if cache:
            cache.delete(f"password_reset:{token_hash}")
        
        log_audit(
            db, user.id, "reset_password", "user",
            ip_address=client_ip,
            user_agent=request.headers.get("user-agent"),
            result="success"
        )
        
        return {
            "success": True,
            "message": "Mật khẩu đã được đặt lại thành công"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Reset password error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Đặt lại mật khẩu thất bại"
        )


# ========== VERIFY EMAIL ENDPOINT ==========

@router.post(
    "/verify-email",
    responses={
        200: {"description": "Email đã được xác thực"},
        400: {"model": ValidationErrorResponse, "description": "Token không hợp lệ"},
        401: {"model": AuthErrorResponse, "description": "Token không hợp lệ hoặc đã hết hạn"}
    }
)
async def verify_email(
    request: Request,
    token: str,
    db: Session = Depends(get_db),
    cache: RedisCache = Depends(get_redis)
):
    """Xác thực email với token"""
    
    try:
        client_ip = get_client_ip(request)
        
        # Verify token (stored in cache or DB)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        user_id_str = None
        
        if cache:
            user_id_str = cache.get(f"email_verify:{token_hash}")
        
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token không hợp lệ hoặc đã hết hạn"
            )
        
        user_id = int(user_id_str)
        
        # Get user
        user_service = UserService(db, cache)
        user = user_service.get_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Người dùng không tồn tại"
            )
        
        # Update email verified
        user.email_verified = True
        db.commit()
        
        # Delete verification token
        if cache:
            cache.delete(f"email_verify:{token_hash}")
        
        log_audit(
            db, user.id, "verify_email", "user",
            ip_address=client_ip,
            user_agent=request.headers.get("user-agent"),
            result="success"
        )
        
        return {
            "success": True,
            "message": "Email đã được xác thực thành công"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Verify email error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Xác thực email thất bại"
        )


# ========== VERIFY PHONE ENDPOINT ==========

@router.post(
    "/verify-phone",
    responses={
        200: {"description": "Số điện thoại đã được xác thực"},
        400: {"model": ValidationErrorResponse, "description": "OTP không hợp lệ"},
        401: {"model": AuthErrorResponse, "description": "OTP không đúng hoặc đã hết hạn"}
    }
)
async def verify_phone(
    request: Request,
    otp: str,
    db: Session = Depends(get_db),
    cache: RedisCache = Depends(get_redis)
):
    """Xác thực số điện thoại với OTP"""
    
    try:
        # Get user from token (user must be logged in)
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Cần đăng nhập để xác thực số điện thoại"
            )
        
        token = auth_header.split(" ")[1]
        payload = verify_access_token(token)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token không hợp lệ"
            )
        
        user_id = int(payload.get("sub"))
        
        # Verify OTP
        if cache:
            stored_otp = cache.get(f"phone_verify_otp:{user_id}")
            if not stored_otp or stored_otp != otp:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="OTP không đúng hoặc đã hết hạn"
                )
        else:
            # Fallback: simple validation (in production, use proper OTP service)
            if len(otp) != 6 or not otp.isdigit():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="OTP không hợp lệ"
                )
        
        # Get user
        user_service = UserService(db, cache)
        user = user_service.get_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Người dùng không tồn tại"
            )
        
        # Update phone verified
        user.phone_verified = True
        db.commit()
        
        # Delete OTP
        if cache:
            cache.delete(f"phone_verify_otp:{user_id}")
        
        log_audit(
            db, user.id, "verify_phone", "user",
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent"),
            result="success"
        )
        
        return {
            "success": True,
            "message": "Số điện thoại đã được xác thực thành công"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Verify phone error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Xác thực số điện thoại thất bại"
        )

