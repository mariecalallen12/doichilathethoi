"""
Notification Service
Digital Utopia Platform

Service để gửi và quản lý notifications
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging
import json
import os

from ..models.notifications import Notification, NotificationPreference
from ..models.user import User
from .email_service import get_email_service

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service để gửi và quản lý notifications
    
    Features:
    - Create và send notifications
    - Manage notification preferences
    - Track read/unread status
    - Auto-expire notifications
    """
    
    def __init__(self, db: Session):
        """
        Khởi tạo NotificationService
        
        Args:
            db: SQLAlchemy session
        """
        self.db = db
    
    def create_notification(
        self,
        user_id: int,
        type: str,
        category: str,
        severity: str,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        link_url: Optional[str] = None,
        expires_in_hours: Optional[int] = None,
    ) -> Notification:
        """
        Tạo và lưu notification mới
        
        Args:
            user_id: ID của user nhận notification
            type: Loại notification (alert, info, warning, success)
            category: Category (diagnostic, trading, system, etc.)
            severity: Mức độ nghiêm trọng (low, medium, high, critical)
            title: Tiêu đề notification
            message: Nội dung notification
            data: Dữ liệu bổ sung (optional)
            link_url: URL để navigate khi click (optional)
            expires_in_hours: Số giờ để expire (optional)
            
        Returns:
            Notification instance
        """
        try:
            expires_at = None
            if expires_in_hours:
                expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
            
            notification = Notification(
                user_id=user_id,
                type=type,
                category=category,
                severity=severity,
                title=title,
                message=message,
                data=data,
                link_url=link_url,
                expires_at=expires_at,
            )
            
            self.db.add(notification)
            self.db.commit()
            self.db.refresh(notification)
            
            logger.info(f"Notification created: id={notification.id}, user_id={user_id}, type={type}, severity={severity}")
            
            return notification
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating notification: {e}", exc_info=True)
            raise
    
    def send_alert_notification(
        self,
        user_id: int,
        alert_rule_id: int,
        health_status: Dict[str, Any],
        conditions_met: Dict[str, Any],
    ) -> Notification:
        """
        Gửi alert notification khi alert rule được trigger
        
        Args:
            user_id: ID của user nhận notification
            alert_rule_id: ID của alert rule đã trigger
            health_status: Health status khi trigger
            conditions_met: Conditions đã được thỏa mãn
            
        Returns:
            Notification instance
        """
        # Determine severity from health status
        severity = 'medium'
        if health_status.get('status') == 'unhealthy':
            severity = 'high'
        elif health_status.get('status') == 'degraded':
            severity = 'medium'
        
        # Get issues for message
        issues = health_status.get('issues', [])
        issue_messages = [issue.get('message', '') for issue in issues[:3]]
        
        title = f"Alert: Trading Dashboard Health Issue"
        message = f"Health status: {health_status.get('status', 'unknown')}. "
        if issue_messages:
            message += "Issues: " + "; ".join(issue_messages)
        
        data = {
            'alert_rule_id': alert_rule_id,
            'health_status': health_status,
            'conditions_met': conditions_met,
        }
        
        return self.create_notification(
            user_id=user_id,
            type='alert',
            category='diagnostic',
            severity=severity,
            title=title,
            message=message,
            data=data,
            link_url='/trading',  # Link to trading dashboard
            expires_in_hours=24,  # Expire after 24 hours
        )
    
    def get_user_notifications(
        self,
        user_id: int,
        unread_only: bool = False,
        category: Optional[str] = None,
        limit: int = 50,
    ) -> List[Notification]:
        """
        Lấy notifications của user
        
        Args:
            user_id: ID của user
            unread_only: Chỉ lấy unread notifications
            category: Lọc theo category (optional)
            limit: Số lượng tối đa
            
        Returns:
            List of Notification instances
        """
        try:
            query = self.db.query(Notification).filter(Notification.user_id == user_id)
            
            # Filter unread only
            if unread_only:
                query = query.filter(Notification.read_at.is_(None))
            
            # Filter by category
            if category:
                query = query.filter(Notification.category == category)
            
            # Filter expired
            query = query.filter(
                (Notification.expires_at.is_(None)) | 
                (Notification.expires_at > datetime.utcnow())
            )
            
            # Order by created_at desc
            query = query.order_by(Notification.created_at.desc())
            
            # Limit
            notifications = query.limit(limit).all()
            
            return notifications
            
        except Exception as e:
            logger.error(f"Error getting user notifications: {e}", exc_info=True)
            return []
    
    def mark_as_read(
        self,
        notification_id: int,
        user_id: int,
    ) -> Optional[Notification]:
        """
        Đánh dấu notification là đã đọc
        
        Args:
            notification_id: ID của notification
            user_id: ID của user (để verify ownership)
            
        Returns:
            Notification instance nếu thành công, None nếu không tìm thấy
        """
        try:
            notification = self.db.query(Notification).filter(
                Notification.id == notification_id,
                Notification.user_id == user_id,
            ).first()
            
            if not notification:
                return None
            
            if notification.read_at is None:
                notification.read_at = datetime.utcnow()
                self.db.commit()
                self.db.refresh(notification)
            
            return notification
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error marking notification as read: {e}", exc_info=True)
            return None
    
    def mark_all_as_read(
        self,
        user_id: int,
        category: Optional[str] = None,
    ) -> int:
        """
        Đánh dấu tất cả notifications của user là đã đọc
        
        Args:
            user_id: ID của user
            category: Lọc theo category (optional)
            
        Returns:
            Số lượng notifications đã được đánh dấu
        """
        try:
            query = self.db.query(Notification).filter(
                Notification.user_id == user_id,
                Notification.read_at.is_(None),
            )
            
            if category:
                query = query.filter(Notification.category == category)
            
            count = query.update({'read_at': datetime.utcnow()})
            self.db.commit()
            
            return count
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error marking all notifications as read: {e}", exc_info=True)
            return 0
    
    def dismiss_notification(
        self,
        notification_id: int,
        user_id: int,
    ) -> Optional[Notification]:
        """
        Dismiss một notification
        
        Args:
            notification_id: ID của notification
            user_id: ID của user (để verify ownership)
            
        Returns:
            Notification instance nếu thành công, None nếu không tìm thấy
        """
        try:
            notification = self.db.query(Notification).filter(
                Notification.id == notification_id,
                Notification.user_id == user_id,
            ).first()
            
            if not notification:
                return None
            
            if notification.dismissed_at is None:
                notification.dismissed_at = datetime.utcnow()
                self.db.commit()
                self.db.refresh(notification)
            
            return notification
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error dismissing notification: {e}", exc_info=True)
            return None
    
    def get_unread_count(
        self,
        user_id: int,
        category: Optional[str] = None,
    ) -> int:
        """
        Lấy số lượng unread notifications
        
        Args:
            user_id: ID của user
            category: Lọc theo category (optional)
            
        Returns:
            Số lượng unread notifications
        """
        try:
            query = self.db.query(Notification).filter(
                Notification.user_id == user_id,
                Notification.read_at.is_(None),
                Notification.dismissed_at.is_(None),
            )
            
            if category:
                query = query.filter(Notification.category == category)
            
            # Filter expired
            query = query.filter(
                (Notification.expires_at.is_(None)) | 
                (Notification.expires_at > datetime.utcnow())
            )
            
            return query.count()
            
        except Exception as e:
            logger.error(f"Error getting unread count: {e}", exc_info=True)
            return 0
    
    def get_user_preferences(
        self,
        user_id: int,
    ) -> Dict[str, Dict[str, bool]]:
        """
        Lấy notification preferences của user
        
        Args:
            user_id: ID của user
            
        Returns:
            Dict với preferences theo category
        """
        try:
            preferences = self.db.query(NotificationPreference).filter(
                NotificationPreference.user_id == user_id
            ).all()
            
            result = {}
            for pref in preferences:
                result[pref.category] = {
                    'email_enabled': pref.email_enabled,
                    'in_app_enabled': pref.in_app_enabled,
                    'push_enabled': pref.push_enabled,
                    'webhook_url': pref.webhook_url,
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting user preferences: {e}", exc_info=True)
            return {}
    
    def update_preferences(
        self,
        user_id: int,
        category: str,
        email_enabled: Optional[bool] = None,
        in_app_enabled: Optional[bool] = None,
        push_enabled: Optional[bool] = None,
        webhook_url: Optional[str] = None,
    ) -> NotificationPreference:
        """
        Cập nhật notification preferences
        
        Args:
            user_id: ID của user
            category: Category của notification
            email_enabled: Cho phép email (optional)
            in_app_enabled: Cho phép in-app (optional)
            push_enabled: Cho phép push (optional)
            webhook_url: Webhook URL (optional)
            
        Returns:
            NotificationPreference instance
        """
        try:
            preference = self.db.query(NotificationPreference).filter(
                NotificationPreference.user_id == user_id,
                NotificationPreference.category == category,
            ).first()
            
            if not preference:
                preference = NotificationPreference(
                    user_id=user_id,
                    category=category,
                    email_enabled=email_enabled if email_enabled is not None else True,
                    in_app_enabled=in_app_enabled if in_app_enabled is not None else True,
                    push_enabled=push_enabled if push_enabled is not None else False,
                    webhook_url=webhook_url,
                )
                self.db.add(preference)
            else:
                if email_enabled is not None:
                    preference.email_enabled = email_enabled
                if in_app_enabled is not None:
                    preference.in_app_enabled = in_app_enabled
                if push_enabled is not None:
                    preference.push_enabled = push_enabled
                if webhook_url is not None:
                    preference.webhook_url = webhook_url
            
            self.db.commit()
            self.db.refresh(preference)
            
            return preference
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating preferences: {e}", exc_info=True)
            raise
    
    def should_send_notification(
        self,
        user_id: int,
        category: str,
        notification_type: str,
    ) -> bool:
        """
        Kiểm tra xem có nên gửi notification không dựa trên preferences
        
        Args:
            user_id: ID của user
            category: Category của notification
            notification_type: Loại notification (in_app, email, etc.)
            
        Returns:
            True nếu nên gửi, False nếu không
        """
        try:
            preference = self.db.query(NotificationPreference).filter(
                NotificationPreference.user_id == user_id,
                NotificationPreference.category == category,
            ).first()
            
            if not preference:
                # Default: allow in_app, email enabled
                return notification_type in ['in_app', 'email']
            
            if notification_type == 'in_app':
                return preference.in_app_enabled
            elif notification_type == 'email':
                return preference.email_enabled
            elif notification_type == 'push':
                return preference.push_enabled
            elif notification_type == 'webhook':
                return preference.webhook_url is not None
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking notification preferences: {e}", exc_info=True)
            # Default to True on error
            return True

