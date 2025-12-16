"""
Audit Log Endpoints
Digital Utopia Platform

Endpoints để query và xem audit logs
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from typing import Optional, List
from datetime import datetime, timedelta

from ...models.audit import AuditLog
# from ...models.user import User  # Not needed - using dict type hint
from ...dependencies import get_current_user, require_role, get_db
from ...middleware.auth import require_admin_role

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/logs")
async def get_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    result: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: dict = Depends(require_admin_role),
    db: Session = Depends(get_db),
):
    """
    Lấy danh sách audit logs với filters và pagination
    """
    query = db.query(AuditLog)

    # Filters
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    
    if action:
        query = query.filter(AuditLog.action.ilike(f"%{action}%"))
    
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)
    
    if category:
        query = query.filter(AuditLog.category == category)
    
    if severity:
        query = query.filter(AuditLog.severity == severity)
    
    if result:
        query = query.filter(AuditLog.result == result)
    
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(AuditLog.created_at >= start_dt)
        except Exception:
            pass
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(AuditLog.created_at <= end_dt)
        except Exception:
            pass
    
    if search:
        # Search in action, resource_type, error_message
        query = query.filter(
            or_(
                AuditLog.action.ilike(f"%{search}%"),
                AuditLog.resource_type.ilike(f"%{search}%"),
                AuditLog.error_message.ilike(f"%{search}%"),
            )
        )

    # Get total count
    total = query.count()

    # Pagination
    offset = (page - 1) * page_size
    logs = query.order_by(desc(AuditLog.created_at)).offset(offset).limit(page_size).all()

    # Format response
    logs_data = []
    for log in logs:
        logs_data.append({
            "id": log.id,
            "user_id": log.user_id,
            "user_role": log.user_role,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "old_values": log.old_values,
            "new_values": log.new_values,
            "ip_address": str(log.ip_address) if log.ip_address else None,
            "user_agent": log.user_agent,
            "result": log.result,
            "error_message": log.error_message,
            "category": log.category,
            "severity": log.severity,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        })

    return {
        "data": logs_data,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size,
        },
    }


@router.get("/logs/stats")
async def get_audit_stats(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: dict = Depends(require_admin_role),
    db: Session = Depends(get_db),
):
    """
    Lấy thống kê audit logs
    """
    query = db.query(AuditLog)

    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(AuditLog.created_at >= start_dt)
        except Exception:
            pass
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(AuditLog.created_at <= end_dt)
        except Exception:
            pass

    # Stats by category
    category_stats = (
        db.query(AuditLog.category, func.count(AuditLog.id).label("count"))
        .filter(AuditLog.id.in_([log.id for log in query.all()]))
        .group_by(AuditLog.category)
        .all()
    )

    # Stats by severity
    severity_stats = (
        db.query(AuditLog.severity, func.count(AuditLog.id).label("count"))
        .filter(AuditLog.id.in_([log.id for log in query.all()]))
        .group_by(AuditLog.severity)
        .all()
    )

    # Stats by result
    result_stats = (
        db.query(AuditLog.result, func.count(AuditLog.id).label("count"))
        .filter(AuditLog.id.in_([log.id for log in query.all()]))
        .group_by(AuditLog.result)
        .all()
    )

    return {
        "data": {
            "total": query.count(),
            "by_category": {cat: count for cat, count in category_stats if cat},
            "by_severity": {sev: count for sev, count in severity_stats},
            "by_result": {res: count for res, count in result_stats},
        }
    }


@router.get("/logs/{log_id}")
async def get_audit_log_detail(
    log_id: int,
    current_user: dict = Depends(require_admin_role),
    db: Session = Depends(get_db),
):
    """
    Lấy chi tiết một audit log
    """
    log = db.query(AuditLog).filter(AuditLog.id == log_id).first()
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log không tồn tại"
        )

    return {
        "data": {
            "id": log.id,
            "user_id": log.user_id,
            "user_role": log.user_role,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "old_values": log.old_values,
            "new_values": log.new_values,
            "ip_address": str(log.ip_address) if log.ip_address else None,
            "user_agent": log.user_agent,
            "session_id": log.session_id,
            "result": log.result,
            "error_message": log.error_message,
            "category": log.category,
            "severity": log.severity,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }
    }

