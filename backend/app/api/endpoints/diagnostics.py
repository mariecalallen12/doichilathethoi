"""
Diagnostics module endpoints
Nhận và lưu trữ diagnostic reports từ Trading Dashboard
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ...middleware import get_current_user_optional
from ...models.user import User
from ...models.diagnostics import TradingDiagnosticReport
from ...db.session import get_db

router = APIRouter(tags=["diagnostics"])


# ========== SCHEMAS ==========

class DiagnosticReportRequest(BaseModel):
    """Request schema cho diagnostic report"""
    report: Dict[str, Any]
    timestamp: Optional[str] = None


class DiagnosticReportResponse(BaseModel):
    """Response schema cho diagnostic report"""
    id: int
    user_id: Optional[int]
    url: str
    overall_health: Optional[str]
    created_at: str
    report_id: Optional[int] = None  # Alias for id for compatibility


# ========== ENDPOINTS ==========

@router.post("/trading-report", response_model=DiagnosticReportResponse, status_code=status.HTTP_201_CREATED)
async def create_trading_diagnostic_report(
    request: DiagnosticReportRequest,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    """
    Nhận và lưu trữ diagnostic report từ Trading Dashboard
    
    - **report**: Diagnostic data từ frontend
    - **timestamp**: Timestamp của report (optional)
    
    Returns:
        DiagnosticReportResponse với report ID
    """
    try:
        report_data = request.report
        
        # Extract data từ report structure
        diagnostics = report_data.get('diagnostics', report_data)
        
        # Tạo report record
        report = TradingDiagnosticReport(
            user_id=current_user.id if current_user else None,
            url=diagnostics.get('url', ''),
            user_agent=diagnostics.get('userAgent', ''),
            auth_status=diagnostics.get('auth'),
            api_status=diagnostics.get('api'),
            ws_status=diagnostics.get('websocket'),
            component_status=diagnostics.get('components'),
            errors=diagnostics.get('console', {}).get('errors', []),
            warnings=diagnostics.get('console', {}).get('warnings', []),
            recommendations=diagnostics.get('recommendations', []),
            raw_data=report_data,
            overall_health=diagnostics.get('api', {}).get('overallHealth', 'unknown'),
            collection_duration_ms=diagnostics.get('collectionDuration'),
            sent_at=datetime.utcnow(),
        )
        
        db.add(report)
        db.commit()
        db.refresh(report)
        
        return DiagnosticReportResponse(
            id=report.id,
            report_id=report.id,  # Alias for compatibility
            user_id=report.user_id,
            url=report.url,
            overall_health=report.overall_health,
            created_at=report.created_at.isoformat() if report.created_at else datetime.utcnow().isoformat(),
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save diagnostic report: {str(e)}"
        )


@router.get("/trading-reports", response_model=List[Dict[str, Any]])
async def get_trading_diagnostic_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    health: Optional[str] = Query(None, description="Filter by health status"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    """
    Lấy danh sách diagnostic reports
    
    - **skip**: Số records bỏ qua
    - **limit**: Số records tối đa trả về
    - **health**: Lọc theo health status (healthy/degraded/unhealthy)
    - **user_id**: Lọc theo user ID (chỉ admin mới có thể filter theo user khác)
    
    Returns:
        List of diagnostic reports
    """
    try:
        query = db.query(TradingDiagnosticReport)
        
        # Filter by health status
        if health:
            query = query.filter(TradingDiagnosticReport.overall_health == health)
        
        # Filter by user_id
        if user_id is not None:
            # Chỉ admin hoặc chính user đó mới có thể xem reports của user khác
            if current_user and (current_user.id == user_id or hasattr(current_user, 'is_admin') and current_user.is_admin):
                query = query.filter(TradingDiagnosticReport.user_id == user_id)
            elif current_user:
                # User chỉ có thể xem reports của chính mình
                query = query.filter(TradingDiagnosticReport.user_id == current_user.id)
            else:
                # Chưa đăng nhập chỉ có thể xem reports không có user_id
                query = query.filter(TradingDiagnosticReport.user_id.is_(None))
        elif current_user:
            # Nếu có user đăng nhập nhưng không chỉ định user_id, chỉ show reports của chính họ
            query = query.filter(TradingDiagnosticReport.user_id == current_user.id)
        else:
            # Chưa đăng nhập chỉ có thể xem reports không có user_id
            query = query.filter(TradingDiagnosticReport.user_id.is_(None))
        
        # Order by created_at desc
        query = query.order_by(TradingDiagnosticReport.created_at.desc())
        
        # Pagination
        reports = query.offset(skip).limit(limit).all()
        
        return [report.to_dict() for report in reports]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch diagnostic reports: {str(e)}"
        )


@router.get("/trading-reports/{report_id}", response_model=Dict[str, Any])
async def get_trading_diagnostic_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    """
    Lấy chi tiết một diagnostic report
    
    - **report_id**: ID của report
    
    Returns:
        Diagnostic report details
    """
    try:
        report = db.query(TradingDiagnosticReport).filter(TradingDiagnosticReport.id == report_id).first()
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Diagnostic report not found"
            )
        
        # Kiểm tra quyền truy cập
        if current_user:
            # User chỉ có thể xem reports của chính mình hoặc admin có thể xem tất cả
            if report.user_id != current_user.id and not (hasattr(current_user, 'is_admin') and current_user.is_admin):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to view this report"
                )
        else:
            # Chưa đăng nhập chỉ có thể xem reports không có user_id
            if report.user_id is not None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Authentication required to view this report"
                )
        
        return report.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch diagnostic report: {str(e)}"
        )

