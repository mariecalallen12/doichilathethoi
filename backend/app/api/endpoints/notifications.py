"""
Notifications API Endpoints
Digital Utopia Platform

API endpoints cho Notification management
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ...middleware import get_current_user_optional
from ...models.user import User
from ...models.notifications import Notification, NotificationPreference
from ...schemas.notifications import (
    NotificationCreate,
    NotificationResponse,
    NotificationListResponse,
    NotificationPreferenceResponse,
    NotificationPreferenceUpdate,
)
from ...services.notification_service import NotificationService
from ...db.session import get_db

router = APIRouter(tags=["notifications"])


# ========== NOTIFICATIONS ENDPOINTS ==========

@router.post("/notifications", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    notification_data: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    """
    Tạo notification mới (admin only hoặc system)
    
    - **user_id**: ID của user nhận notification
    - **type**: Loại notification (alert, info, warning, success)
    - **category**: Category (diagnostic, trading, system, etc.)
    - **severity**: Mức độ nghiêm trọng
    - **title**: Tiêu đề
    - **message**: Nội dung
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    # Only admins can create notifications for other users
    if notification_data.user_id != current_user.id:
        if not (hasattr(current_user, 'is_admin') and current_user.is_admin):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can create notifications for other users"
            )
    
    try:
        service = NotificationService(db)
        notification = service.create_notification(
            user_id=notification_data.user_id,
            type=notification_data.type,
            category=notification_data.category,
            severity=notification_data.severity,
            title=notification_data.title,
            message=notification_data.message,
            data=notification_data.data,
            link_url=notification_data.link_url,
            expires_in_hours=notification_data.expires_in_hours,
        )
        
        return NotificationResponse(
            id=notification.id,
            user_id=notification.user_id,
            type=notification.type,
            category=notification.category,
            severity=notification.severity,
            title=notification.title,
            message=notification.message,
            data=notification.data,
            link_url=notification.link_url,
            read_at=notification.read_at,
            dismissed_at=notification.dismissed_at,
            expires_at=notification.expires_at,
            created_at=notification.created_at,
            is_read=notification.is_read,
            is_dismissed=notification.is_dismissed,
            is_expired=notification.is_expired,
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create notification: {str(e)}"
        )


@router.get("/notifications", response_model=NotificationListResponse)
async def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    unread_only: bool = Query(False, description="Chỉ lấy unread notifications"),
    category: Optional[str] = Query(None, description="Lọc theo category"),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    """
    Lấy danh sách notifications của user hiện tại
    
    - **skip**: Số records bỏ qua
    - **limit**: Số records tối đa
    - **unread_only**: Chỉ lấy unread
    - **category**: Lọc theo category
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    try:
        service = NotificationService(db)
        notifications = service.get_user_notifications(
            user_id=current_user.id,
            unread_only=unread_only,
            category=category,
            limit=limit + skip,  # Get more to account for skip
        )
        
        # Apply skip manually (since we're using limit in service)
        notifications = notifications[skip:skip + limit]
        
        # Get total count
        total_query = db.query(Notification).filter(Notification.user_id == current_user.id)
        if category:
            total_query = total_query.filter(Notification.category == category)
        total = total_query.count()
        
        # Get unread count
        unread_count = service.get_unread_count(
            user_id=current_user.id,
            category=category,
        )
        
        return NotificationListResponse(
            notifications=[
                NotificationResponse(
                    id=n.id,
                    user_id=n.user_id,
                    type=n.type,
                    category=n.category,
                    severity=n.severity,
                    title=n.title,
                    message=n.message,
                    data=n.data,
                    link_url=n.link_url,
                    read_at=n.read_at,
                    dismissed_at=n.dismissed_at,
                    expires_at=n.expires_at,
                    created_at=n.created_at,
                    is_read=n.is_read,
                    is_dismissed=n.is_dismissed,
                    is_expired=n.is_expired,
                )
                for n in notifications
            ],
            total=total,
            unread_count=unread_count,
            page=skip // limit + 1,
            page_size=limit,
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch notifications: {str(e)}"
        )


@router.get("/notifications/unread-count", response_model=dict)
async def get_unread_count(
    category: Optional[str] = Query(None, description="Lọc theo category"),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    """
    Lấy số lượng unread notifications
    
    - **category**: Lọc theo category (optional)
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    try:
        service = NotificationService(db)
        count = service.get_unread_count(
            user_id=current_user.id,
            category=category,
        )
        
        return {
            'unread_count': count,
            'category': category,
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get unread count: {str(e)}"
        )


@router.post("/notifications/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    """
    Đánh dấu notification là đã đọc
    
    - **notification_id**: ID của notification
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    try:
        service = NotificationService(db)
        notification = service.mark_as_read(
            notification_id=notification_id,
            user_id=current_user.id,
        )
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        return NotificationResponse(
            id=notification.id,
            user_id=notification.user_id,
            type=notification.type,
            category=notification.category,
            severity=notification.severity,
            title=notification.title,
            message=notification.message,
            data=notification.data,
            link_url=notification.link_url,
            read_at=notification.read_at,
            dismissed_at=notification.dismissed_at,
            expires_at=notification.expires_at,
            created_at=notification.created_at,
            is_read=notification.is_read,
            is_dismissed=notification.is_dismissed,
            is_expired=notification.is_expired,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark notification as read: {str(e)}"
        )


@router.post("/notifications/mark-all-read", response_model=dict)
async def mark_all_notifications_read(
    category: Optional[str] = Query(None, description="Lọc theo category"),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    """
    Đánh dấu tất cả notifications là đã đọc
    
    - **category**: Lọc theo category (optional)
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    try:
        service = NotificationService(db)
        count = service.mark_all_as_read(
            user_id=current_user.id,
            category=category,
        )
        
        return {
            'marked_count': count,
            'category': category,
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark all notifications as read: {str(e)}"
        )


@router.post("/notifications/{notification_id}/dismiss", response_model=NotificationResponse)
async def dismiss_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    """
    Dismiss một notification
    
    - **notification_id**: ID của notification
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    try:
        service = NotificationService(db)
        notification = service.dismiss_notification(
            notification_id=notification_id,
            user_id=current_user.id,
        )
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        return NotificationResponse(
            id=notification.id,
            user_id=notification.user_id,
            type=notification.type,
            category=notification.category,
            severity=notification.severity,
            title=notification.title,
            message=notification.message,
            data=notification.data,
            link_url=notification.link_url,
            read_at=notification.read_at,
            dismissed_at=notification.dismissed_at,
            expires_at=notification.expires_at,
            created_at=notification.created_at,
            is_read=notification.is_read,
            is_dismissed=notification.is_dismissed,
            is_expired=notification.is_expired,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to dismiss notification: {str(e)}"
        )


# ========== NOTIFICATION PREFERENCES ENDPOINTS ==========

@router.get("/notification-preferences", response_model=List[NotificationPreferenceResponse])
async def get_notification_preferences(
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    """
    Lấy notification preferences của user hiện tại
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    try:
        preferences = db.query(NotificationPreference).filter(
            NotificationPreference.user_id == current_user.id
        ).all()
        
        return [
            NotificationPreferenceResponse(
                id=p.id,
                user_id=p.user_id,
                category=p.category,
                email_enabled=p.email_enabled,
                in_app_enabled=p.in_app_enabled,
                push_enabled=p.push_enabled,
                webhook_url=p.webhook_url,
                created_at=p.created_at,
                updated_at=p.updated_at,
            )
            for p in preferences
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch preferences: {str(e)}"
        )


@router.put("/notification-preferences/{category}", response_model=NotificationPreferenceResponse)
async def update_notification_preference(
    category: str,
    preference_data: NotificationPreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    """
    Cập nhật notification preference cho một category
    
    - **category**: Category của notification
    - **preference_data**: Dữ liệu cập nhật
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    try:
        service = NotificationService(db)
        preference = service.update_preferences(
            user_id=current_user.id,
            category=category,
            email_enabled=preference_data.email_enabled,
            in_app_enabled=preference_data.in_app_enabled,
            push_enabled=preference_data.push_enabled,
            webhook_url=preference_data.webhook_url,
        )
        
        return NotificationPreferenceResponse(
            id=preference.id,
            user_id=preference.user_id,
            category=preference.category,
            email_enabled=preference.email_enabled,
            in_app_enabled=preference.in_app_enabled,
            push_enabled=preference.push_enabled,
            webhook_url=preference.webhook_url,
            created_at=preference.created_at,
            updated_at=preference.updated_at,
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update preference: {str(e)}"
        )

