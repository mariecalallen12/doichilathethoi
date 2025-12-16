"""
Alert Rules API Endpoints
Digital Utopia Platform

API endpoints cho Alert Rules CRUD operations
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from ...middleware import get_current_user_optional
from ...models.user import User
from ...models.alert_rules import AlertRule, AlertHistory
from ...schemas.alert_rules import (
    AlertRuleCreate,
    AlertRuleUpdate,
    AlertRuleResponse,
    AlertHistoryResponse,
    AlertRuleListResponse,
    AlertHistoryListResponse,
)
from ...db.session import get_db

router = APIRouter(tags=["alert-rules"])


# ========== ALERT RULES ENDPOINTS ==========

@router.post("/alert-rules", response_model=AlertRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_alert_rule(
    rule_data: AlertRuleCreate,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    """
    Tạo alert rule mới
    
    - **name**: Tên của alert rule
    - **description**: Mô tả rule
    - **conditions**: Điều kiện để trigger (JSON)
    - **thresholds**: Ngưỡng để trigger (JSON)
    - **actions**: Actions khi trigger (JSON)
    - **enabled**: Rule có được bật không
    - **priority**: Độ ưu tiên (1-10)
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    try:
        # Set user_id from current user if not provided
        user_id = rule_data.user_id if rule_data.user_id else current_user.id
        
        # Check if user has permission to create system-wide rules
        if rule_data.user_id is None and not (hasattr(current_user, 'is_admin') and current_user.is_admin):
            user_id = current_user.id  # Regular users can only create their own rules
        
        rule = AlertRule(
            name=rule_data.name,
            description=rule_data.description,
            user_id=user_id,
            conditions=rule_data.conditions,
            thresholds=rule_data.thresholds,
            actions=rule_data.actions,
            enabled=rule_data.enabled,
            priority=rule_data.priority,
        )
        
        db.add(rule)
        db.commit()
        db.refresh(rule)
        
        return AlertRuleResponse.from_orm(rule)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create alert rule: {str(e)}"
        )


@router.get("/alert-rules", response_model=AlertRuleListResponse)
async def get_alert_rules(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    enabled: Optional[bool] = Query(None, description="Filter by enabled status"),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    """
    Lấy danh sách alert rules
    
    - **skip**: Số records bỏ qua
    - **limit**: Số records tối đa
    - **user_id**: Lọc theo user ID
    - **enabled**: Lọc theo enabled status
    """
    try:
        query = db.query(AlertRule)
        
        # Filter by user_id
        if user_id is not None:
            if current_user:
                # Users can only see their own rules or system-wide rules
                if user_id == current_user.id or (hasattr(current_user, 'is_admin') and current_user.is_admin):
                    query = query.filter(
                        (AlertRule.user_id == user_id) | (AlertRule.user_id.is_(None))
                    )
                else:
                    query = query.filter(AlertRule.user_id == current_user.id)
            else:
                # Anonymous users can only see system-wide rules
                query = query.filter(AlertRule.user_id.is_(None))
        elif current_user:
            # Authenticated users see their own rules + system-wide rules
            query = query.filter(
                (AlertRule.user_id == current_user.id) | (AlertRule.user_id.is_(None))
            )
        else:
            # Anonymous users only see system-wide rules
            query = query.filter(AlertRule.user_id.is_(None))
        
        # Filter by enabled
        if enabled is not None:
            query = query.filter(AlertRule.enabled == enabled)
        
        # Get total count
        total = query.count()
        
        # Order by priority desc, then by created_at desc
        query = query.order_by(desc(AlertRule.priority), desc(AlertRule.created_at))
        
        # Pagination
        rules = query.offset(skip).limit(limit).all()
        
        return AlertRuleListResponse(
            rules=[AlertRuleResponse.from_orm(r) for r in rules],
            total=total,
            page=skip // limit + 1,
            page_size=limit,
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch alert rules: {str(e)}"
        )


@router.get("/alert-rules/{rule_id}", response_model=AlertRuleResponse)
async def get_alert_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    """
    Lấy chi tiết một alert rule
    
    - **rule_id**: ID của alert rule
    """
    try:
        rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
        
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert rule not found"
            )
        
        # Check permissions
        if current_user:
            if rule.user_id != current_user.id and rule.user_id is not None:
                if not (hasattr(current_user, 'is_admin') and current_user.is_admin):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="You don't have permission to view this rule"
                    )
        else:
            # Anonymous users can only see system-wide rules
            if rule.user_id is not None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Authentication required"
                )
        
        return AlertRuleResponse.from_orm(rule)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch alert rule: {str(e)}"
        )


@router.put("/alert-rules/{rule_id}", response_model=AlertRuleResponse)
async def update_alert_rule(
    rule_id: int,
    rule_data: AlertRuleUpdate,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    """
    Cập nhật alert rule
    
    - **rule_id**: ID của alert rule
    - **rule_data**: Dữ liệu cập nhật
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    try:
        rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
        
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert rule not found"
            )
        
        # Check permissions
        if rule.user_id != current_user.id:
            if not (hasattr(current_user, 'is_admin') and current_user.is_admin):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to update this rule"
                )
        
        # Update fields
        update_data = rule_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(rule, field, value)
        
        db.commit()
        db.refresh(rule)
        
        return AlertRuleResponse.from_orm(rule)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update alert rule: {str(e)}"
        )


@router.delete("/alert-rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    """
    Xóa alert rule
    
    - **rule_id**: ID của alert rule
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    try:
        rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
        
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert rule not found"
            )
        
        # Check permissions
        if rule.user_id != current_user.id:
            if not (hasattr(current_user, 'is_admin') and current_user.is_admin):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to delete this rule"
                )
        
        db.delete(rule)
        db.commit()
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete alert rule: {str(e)}"
        )


# ========== ALERT HISTORY ENDPOINTS ==========

@router.get("/alert-history", response_model=AlertHistoryListResponse)
async def get_alert_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    rule_id: Optional[int] = Query(None, description="Filter by alert rule ID"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    resolved: Optional[bool] = Query(None, description="Filter by resolved status"),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    """
    Lấy lịch sử alerts
    
    - **skip**: Số records bỏ qua
    - **limit**: Số records tối đa
    - **rule_id**: Lọc theo alert rule ID
    - **user_id**: Lọc theo user ID
    - **severity**: Lọc theo severity
    - **resolved**: Lọc theo resolved status
    """
    try:
        query = db.query(AlertHistory)
        
        # Filter by rule_id
        if rule_id:
            query = query.filter(AlertHistory.alert_rule_id == rule_id)
        
        # Filter by user_id
        if user_id is not None:
            if current_user:
                # Users can only see their own alerts or system-wide alerts
                if user_id == current_user.id or (hasattr(current_user, 'is_admin') and current_user.is_admin):
                    query = query.filter(
                        (AlertHistory.user_id == user_id) | (AlertHistory.user_id.is_(None))
                    )
                else:
                    query = query.filter(AlertHistory.user_id == current_user.id)
            else:
                query = query.filter(AlertHistory.user_id.is_(None))
        elif current_user:
            # Authenticated users see their own alerts + system-wide alerts
            query = query.filter(
                (AlertHistory.user_id == current_user.id) | (AlertHistory.user_id.is_(None))
            )
        else:
            # Anonymous users only see system-wide alerts
            query = query.filter(AlertHistory.user_id.is_(None))
        
        # Filter by severity
        if severity:
            query = query.filter(AlertHistory.severity == severity)
        
        # Filter by resolved
        if resolved is not None:
            if resolved:
                query = query.filter(AlertHistory.resolved_at.isnot(None))
            else:
                query = query.filter(AlertHistory.resolved_at.is_(None))
        
        # Get total count
        total = query.count()
        
        # Order by triggered_at desc
        query = query.order_by(desc(AlertHistory.triggered_at))
        
        # Pagination
        alerts = query.offset(skip).limit(limit).all()
        
        return AlertHistoryListResponse(
            alerts=[AlertHistoryResponse.from_orm(a) for a in alerts],
            total=total,
            page=skip // limit + 1,
            page_size=limit,
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch alert history: {str(e)}"
        )


@router.post("/alert-history/{alert_id}/acknowledge", response_model=AlertHistoryResponse)
async def acknowledge_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    """
    Acknowledge một alert
    
    - **alert_id**: ID của alert
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    try:
        alert = db.query(AlertHistory).filter(AlertHistory.id == alert_id).first()
        
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )
        
        # Check permissions
        if alert.user_id != current_user.id:
            if not (hasattr(current_user, 'is_admin') and current_user.is_admin):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to acknowledge this alert"
                )
        
        # Update acknowledged_by if not already set
        if alert.acknowledged_by is None:
            alert.acknowledged_by = current_user.id
            db.commit()
            db.refresh(alert)
        
        return AlertHistoryResponse.from_orm(alert)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to acknowledge alert: {str(e)}"
        )


@router.post("/alert-history/{alert_id}/resolve", response_model=AlertHistoryResponse)
async def resolve_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    """
    Resolve một alert
    
    - **alert_id**: ID của alert
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    try:
        alert = db.query(AlertHistory).filter(AlertHistory.id == alert_id).first()
        
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )
        
        # Check permissions
        if alert.user_id != current_user.id:
            if not (hasattr(current_user, 'is_admin') and current_user.is_admin):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to resolve this alert"
                )
        
        # Update resolved_at if not already resolved
        if alert.resolved_at is None:
            from datetime import datetime
            alert.resolved_at = datetime.utcnow()
            db.commit()
            db.refresh(alert)
        
        return AlertHistoryResponse.from_orm(alert)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resolve alert: {str(e)}"
        )

