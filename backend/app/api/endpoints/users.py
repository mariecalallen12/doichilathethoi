"""
User Management API Endpoints
User profile management và account operations (DB-based)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.schemas.users import (
    UserProfileResponse,
    UpdateProfileRequest,
    UpdateProfileResponse,
    DeleteAccountResponse,
    UserProfile as UserProfileSchema,
    UserStatus,
    UserActivity,
    UserPreferences,
)
from app.dependencies import get_current_user, get_current_active_user
from app.db.session import get_db
from app.models.user import User, UserProfile
from app.models.trading import PortfolioPosition
from app.models.audit import AuditLog

router = APIRouter(tags=["users"])


def map_user_to_profile_schema(user: dict) -> UserProfileSchema:
    """Helper: map User + UserProfile model sang UserProfile schema"""
    profile = user.profile

    status_value = user.status if user.status in UserStatus._value2member_map_ else "active"

    return UserProfileSchema(
        id=str(user.id),
        email=user.email,
        displayName=profile.display_name if profile and profile.display_name else user.email,
        phoneNumber=profile.phone if profile else None,
        avatar=profile.avatar_url if profile else None,
        status=UserStatus(status_value),
        role="admin" if user.role and user.role.name == "admin" else "user",
        isActive=user.status == "active",
        firstName=None,
        lastName=None,
        dateOfBirth=profile.date_of_birth if profile else None,
        address=profile.address if profile else None,
        city=profile.city if profile else None,
        country=profile.country if profile else None,
        emailVerified=user.email_verified,
        phoneVerified=user.phone_verified,
        # Sử dụng trạng thái xác thực số điện thoại như 2FA đơn giản
        twoFactorEnabled=bool(user.phone_verified),
        createdAt=user.created_at,
        updatedAt=user.updated_at,
        lastLoginAt=user.last_login_at,
        deletedAt=None,
    )


@router.get(
    "/api/users",
    response_model=UserProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Lấy thông tin user profile",
)
async def get_user_profile_endpoint(
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Lấy thông tin profile của user hiện tại (DB-based)
    """
    try:
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user or user.status == "deleted":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tài khoản đã bị xóa",
            )

        if user.status == "suspended":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tài khoản đã bị tạm dừng",
            )

        return UserProfileResponse(
            success=True,
            data=map_user_to_profile_schema(user),
        )

    except HTTPException:
        raise
    except Exception as error:
        print("Get user profile error:", error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy thông tin người dùng",
        )


@router.put(
    "/api/users",
    response_model=UpdateProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Cập nhật user profile",
)
async def update_user_profile_endpoint(
    request: Request,
    update_request: UpdateProfileRequest,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Cập nhật thông tin profile của user (DB-based)
    """
    try:
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user or user.status == "deleted":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tài khoản không tồn tại hoặc đã bị xóa",
            )

        profile = user.profile
        if not profile:
            profile = UserProfile(user_id=user.id)
            db.add(profile)

        updated_fields: List[str] = []

        if update_request.displayName is not None:
            profile.display_name = update_request.displayName
            updated_fields.append("displayName")

        if update_request.phoneNumber is not None:
            profile.phone = update_request.phoneNumber
            updated_fields.append("phoneNumber")

        if update_request.avatar is not None:
            profile.avatar_url = update_request.avatar
            updated_fields.append("avatar")

        if update_request.firstName is not None:
            # full_name có thể ghép first/last; ở đây chỉ lưu vào full_name
            profile.full_name = (update_request.firstName or "") + (
                f" {update_request.lastName}" if update_request.lastName else ""
            )
            updated_fields.append("firstName")

        if update_request.lastName is not None and "firstName" not in updated_fields:
            # Nếu chỉ cập nhật lastName, nối vào full_name hiện tại
            current_name = profile.full_name or ""
            profile.full_name = f"{current_name} {update_request.lastName}".strip()
            updated_fields.append("lastName")

        if update_request.address is not None:
            profile.address = update_request.address
            updated_fields.append("address")

        if update_request.city is not None:
            profile.city = update_request.city
            updated_fields.append("city")

        if update_request.country is not None:
            profile.country = update_request.country
            updated_fields.append("country")

        profile.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(profile)

        # Log vào audit_logs
        audit_log = AuditLog(
            user_id=user.id,
            action="profile_updated",
            resource_type="user_profile",
            resource_id=str(user.id),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            category="user",
        )
        db.add(audit_log)
        db.commit()

        return UpdateProfileResponse(
            success=True,
            message="Cập nhật thông tin thành công",
            data={
                "updatedFields": updated_fields,
                "updatedAt": profile.updated_at.isoformat(),
            },
        )

    except HTTPException:
        raise
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dữ liệu đầu vào không hợp lệ",
            headers={"X-Error": str(error)},
        )
    except Exception as error:
        print("Update user profile error:", error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể cập nhật thông tin",
        )


@router.delete(
    "/api/users",
    response_model=DeleteAccountResponse,
    status_code=status.HTTP_200_OK,
    summary="Xóa tài khoản người dùng",
)
async def delete_user_account_endpoint(
    request: Request,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Xóa tài khoản người dùng (soft delete) - DB-based
    
    Kiểm tra:
    - Không có vị thế giao dịch đang mở
    - Tài khoản đang active
    """
    try:
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user or user.status == "deleted":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tài khoản đã bị xóa trước đó",
            )

        # Kiểm tra vị thế giao dịch đang mở
        open_positions = (
            db.query(PortfolioPosition)
            .filter(
                and_(
                    PortfolioPosition.user_id == user.id,
                    PortfolioPosition.is_closed == False,
                )
            )
            .count()
        )
        if open_positions > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không thể xóa tài khoản khi còn vị thế giao dịch chưa đóng",
            )

        # Soft delete
        user.status = "deleted"
        user.updated_at = datetime.utcnow()
        db.commit()

        # Ghi audit log
        audit_log = AuditLog(
            user_id=user.id,
            action="account_deleted",
            resource_type="user",
            resource_id=str(user.id),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            category="user",
        )
        db.add(audit_log)
        db.commit()

        return DeleteAccountResponse(
            success=True,
            message="Tài khoản đã được xóa thành công",
        )

    except HTTPException:
        raise
    except Exception as error:
        print("Delete user account error:", error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể xóa tài khoản",
        )


@router.get(
    "/api/users/preferences",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Lấy user preferences",
)
async def get_user_preferences_endpoint(
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Lấy preferences và settings của user từ user_profiles.preferences
    """
    try:
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user or user.status == "deleted":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tài khoản đã bị xóa",
            )

        profile = user.profile
        if not profile or not profile.preferences:
            # Trả về default preferences nếu chưa có
            return UserPreferences().dict()

        return profile.preferences

    except Exception as error:
        print("Get user preferences error:", error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy preferences",
        )


@router.get(
    "/api/users/activity",
    response_model=List[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="Lấy user activity history",
)
async def get_user_activity_endpoint(
    request: Request,
    limit: Optional[int] = Query(50, ge=1, le=100, description="Số lượng records"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Lấy lịch sử hoạt động của user từ audit_logs
    """
    try:
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user or user.status == "deleted":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tài khoản đã bị xóa",
            )

        logs = (
            db.query(AuditLog)
            .filter(AuditLog.user_id == user.id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .all()
        )

        activities: List[Dict[str, Any]] = []
        for log in logs:
            activity = UserActivity(
                action=log.action,
                timestamp=log.created_at or datetime.utcnow(),
                details={"resource_type": log.resource_type, "resource_id": log.resource_id},
                ipAddress=str(log.ip_address) if log.ip_address else None,
                userAgent=log.user_agent,
            )
            activities.append(activity.dict())

        return activities

    except Exception as error:
        print("Get user activity error:", error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy lịch sử hoạt động",
        )
