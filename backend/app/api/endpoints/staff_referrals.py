"""
Staff Referral Management API Endpoints
DB-based implementation using ReferralService
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.schemas.staff_referrals import (
    StaffReferralsResponse,
    GenerateLinkRequest,
    GenerateLinkResponse,
    ReferralStatus,
    StaffInfo,
    ReferralCode as ReferralCodeSchema,
    ReferralAnalytics,
    ReferralLink,
)
from app.dependencies import require_role
from app.db.session import get_db
from app.db.redis_client import get_redis, RedisCache
from app.models.user import User
from app.models.referral import ReferralCode, ReferralRegistration
from app.services.referral_service import ReferralService

router = APIRouter()


def get_referral_service(
    db: Session = Depends(get_db),
    cache: RedisCache = Depends(get_redis),
) -> ReferralService:
    """Dependency helper for ReferralService"""
    return ReferralService(db, cache)


@router.get(
    "/referrals",
    response_model=StaffReferralsResponse,
    status_code=status.HTTP_200_OK,
    summary="Lấy thông tin referrals của staff",
    tags=["staff-referrals"]
)
async def get_staff_referrals(
    request: Request,
    staff_user: User = Depends(require_role(["staff"])),
    db: Session = Depends(get_db),
    referral_service: ReferralService = Depends(get_referral_service),
):
    """
    Lấy thông tin mã giới thiệu của staff
    
    Bao gồm:
    - Referral analytics (tổng lượt, thành công, conversion rate)
    - Referral codes của staff (từ DB)
    - Thông tin staff (từ bảng users)
    """
    try:
        staff_id = staff_user.id

        # Lấy referral codes từ DB
        codes: List[ReferralCode] = referral_service.get_staff_codes(staff_id)

        # Lấy registrations của staff để tính analytics
        registrations: List[ReferralRegistration] = referral_service.get_staff_registrations(
            staff_id
        )

        total_referrals = len(registrations)
        successful_referrals = len(
            [r for r in registrations if r.status in ("verified", "rewarded")]
        )
        conversion_rate = (
            float(successful_referrals) / float(total_referrals) * 100.0
            if total_referrals > 0
            else 0.0
        )
        total_rewards = sum(
            float(r.commission_amount or 0)
            for r in registrations
            if r.commission_paid
        )

        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_30_days = now - timedelta(days=30)

        this_month = len(
            [r for r in registrations if r.created_at and r.created_at >= month_start]
        )
        last_30_days_count = len(
            [r for r in registrations if r.created_at and r.created_at >= last_30_days]
        )

        analytics = ReferralAnalytics(
            totalReferrals=total_referrals,
            successfulReferrals=successful_referrals,
            conversionRate=conversion_rate,
            totalRewards=total_rewards,
            thisMonth=this_month,
            last30Days=last_30_days_count,
        )

        referral_codes = [
            ReferralCodeSchema(
                id=str(code.id),
                code=code.code,
                status=ReferralStatus(code.status),
                usageCount=code.used_count or 0,
                createdAt=code.created_at,
                staffId=str(code.staff_id),
            )
            for code in codes
        ]

        staff_info = StaffInfo(
            staffId=str(staff_user.id),
            displayName=staff_user.profile.display_name if staff_user.profile else "",
            email=staff_user.email,
        )

        return StaffReferralsResponse(
            analytics=analytics,
            referralCodes=referral_codes,
            staffInfo=staff_info,
        )
        
    except HTTPException:
        raise
    except Exception as error:
        print("Get staff referrals error:", error)
        
        error_message = str(error) if error else "Không thể lấy thông tin mã giới thiệu"
        
        if "Unauthorized" in error_message:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Không tìm thấy token xác thực",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_message
        )


@router.post(
    "/referrals/generate-link",
    response_model=GenerateLinkResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo link giới thiệu mới",
    tags=["staff-referrals"]
)
async def generate_referral_link_endpoint(
    request: Request,
    generate_request: GenerateLinkRequest,
    staff_user: User = Depends(require_role(["staff"])),
    referral_service: ReferralService = Depends(get_referral_service),
):
    """
    Tạo link giới thiệu mới cho staff
    
    Args:
        expiryDays: Số ngày hết hạn (1-365, mặc định 30)
    
    Returns:
        Link giới thiệu với URL và thời hạn hết hạn
    """
    try:
        staff_id = staff_user.id

        # Lấy hoặc tạo referral code active cho staff
        codes = referral_service.get_staff_codes(staff_id)
        active_code = next((c for c in codes if c.status == "active"), None)

        if not active_code:
            active_code = referral_service.create_referral_code(
                staff_id=staff_id,
                max_uses=None,
                expires_days=generate_request.expiryDays,
            )

        base_url = "https://app.digitalutopia.com/ref"
        link_url = f"{base_url}/{active_code.token}"
        expires_at = datetime.utcnow() + timedelta(days=generate_request.expiryDays)

        referral_link = ReferralLink(
            url=link_url,
            code=active_code.code,
            expiresAt=expires_at,
        )

        return GenerateLinkResponse(
            message="Tạo link giới thiệu thành công",
            data=referral_link,
        )
        
    except HTTPException:
        raise
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dữ liệu đầu vào không hợp lệ",
            headers={"X-Error": str(error)}
        )
    except Exception as error:
        print("Generate referral link error:", error)
        
        error_message = str(error) if error else "Không thể tạo link giới thiệu"
        
        if "Unauthorized" in error_message:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Không tìm thấy token xác thực",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_message
        )


@router.get(
    "/referrals/links",
    response_model=List[dict],
    status_code=status.HTTP_200_OK,
    summary="Lấy danh sách links đã tạo",
    tags=["staff-referrals"]
)
async def get_staff_referral_links(
    request: Request,
    staff_user: User = Depends(require_role(["staff"])),
    referral_service: ReferralService = Depends(get_referral_service),
):
    """
    Lấy danh sách tất cả referral links đã tạo cho staff
    """
    try:
        staff_id = staff_user.id
        codes = referral_service.get_staff_codes(staff_id)
        base_url = "https://app.digitalutopia.com/ref"
        
        # Represent each active code as a link entry
        staff_links = []
        for code in codes:
            staff_links.append({
                "id": str(code.id),
                "url": f"{base_url}/{code.token}",
                "code": code.code,
                "expiresAt": code.expires_at.isoformat() if code.expires_at else None,
                "staffId": staff_id,
                "createdAt": code.created_at.isoformat() if code.created_at else None,
                "clicks": 0,
                "conversions": 0,
                "status": code.status,
            })
        
        return staff_links
        
    except Exception as error:
        print("Get referral links error:", error)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy danh sách links giới thiệu"
        )


@router.delete(
    "/referrals/links/{link_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa referral link",
    tags=["staff-referrals"]
)
async def delete_referral_link(
    link_id: str,
    request: Request,
    staff_user: User = Depends(require_role(["staff"])),
    referral_service: ReferralService = Depends(get_referral_service),
):
    """
    Xóa referral link (vô hiệu hóa)
    """
    try:
        staff_id = staff_user.id
        
        # Ở phiên bản DB-based, sử dụng link_id như referral code ID
        try:
            code_id = int(link_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="link_id không hợp lệ"
            )
        
        updated = referral_service.deactivate_code(code_id=code_id, staff_id=staff_id)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mã giới thiệu không tồn tại hoặc không thuộc về staff hiện tại"
            )
        
        return None
        
    except HTTPException:
        raise
    except Exception as error:
        print("Delete referral link error:", error)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể xóa link giới thiệu"
        )
