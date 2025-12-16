"""
Education module endpoints for FastAPI.
"""

from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ...dependencies import get_current_user
from ...db.session import get_db
from ...models.user import User
from ...schemas.education import (
    VideoListRequest, VideoListResponse, VideoResponse,
    EbookListRequest, EbookListResponse, EbookResponse,
    CalendarRequest, CalendarResponse, CalendarEventResponse,
    ReportListRequest, ReportListResponse, ReportResponse,
    ProgressUpdateRequest, ProgressResponse, ApiResponse, ApiError
)
from ...services.education_service import EducationService

router = APIRouter()


# ========== Video Endpoints ==========

@router.get("/videos", response_model=VideoListResponse)
async def get_videos(
    category: Optional[str] = Query(None),
    language: Optional[str] = Query(None),
    is_featured: Optional[bool] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get list of education videos"""
    try:
        service = EducationService(db)
        result = service.get_videos(
            category=category,
            language=language,
            is_featured=is_featured,
            limit=limit,
            offset=offset,
            search=search
        )
        
        videos = [VideoResponse.from_orm(v) for v in result["videos"]]
        
        return VideoListResponse(
            success=True,
            data=videos,
            total=result["total"],
            limit=result["limit"],
            offset=result["offset"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching videos: {str(e)}"
        )


@router.get("/videos/{video_id}", response_model=ApiResponse)
async def get_video_by_id(
    video_id: int = Path(..., description="Video ID"),
    db: Session = Depends(get_db)
):
    """Get video by ID"""
    try:
        service = EducationService(db)
        video = service.get_video_by_id(video_id)
        
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video not found"
            )
        
        return ApiResponse(
            success=True,
            data=VideoResponse.from_orm(video)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching video: {str(e)}"
        )


# ========== Ebook Endpoints ==========

@router.get("/ebooks", response_model=EbookListResponse)
async def get_ebooks(
    category: Optional[str] = Query(None),
    language: Optional[str] = Query(None),
    is_featured: Optional[bool] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get list of education ebooks"""
    try:
        service = EducationService(db)
        result = service.get_ebooks(
            category=category,
            language=language,
            is_featured=is_featured,
            limit=limit,
            offset=offset,
            search=search
        )
        
        ebooks = [EbookResponse.from_orm(e) for e in result["ebooks"]]
        
        return EbookListResponse(
            success=True,
            data=ebooks,
            total=result["total"],
            limit=result["limit"],
            offset=result["offset"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching ebooks: {str(e)}"
        )


@router.get("/ebooks/{ebook_id}", response_model=ApiResponse)
async def get_ebook_by_id(
    ebook_id: int = Path(..., description="Ebook ID"),
    db: Session = Depends(get_db)
):
    """Get ebook by ID"""
    try:
        service = EducationService(db)
        ebook = service.get_ebook_by_id(ebook_id)
        
        if not ebook:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ebook not found"
            )
        
        return ApiResponse(
            success=True,
            data=EbookResponse.from_orm(ebook)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching ebook: {str(e)}"
        )


# ========== Calendar Endpoints ==========

@router.get("/calendar", response_model=CalendarResponse)
async def get_calendar(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    country: Optional[str] = Query(None),
    currency: Optional[str] = Query(None),
    impact: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get economic calendar events"""
    try:
        service = EducationService(db)
        result = service.get_calendar(
            start_date=start_date,
            end_date=end_date,
            country=country,
            currency=currency,
            impact=impact,
            category=category,
            limit=limit,
            offset=offset
        )
        
        events = [CalendarEventResponse.from_orm(e) for e in result["events"]]
        
        return CalendarResponse(
            success=True,
            data=events,
            total=result["total"],
            limit=result["limit"],
            offset=result["offset"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching calendar: {str(e)}"
        )


# ========== Report Endpoints ==========

@router.get("/reports", response_model=ReportListResponse)
async def get_reports(
    category: Optional[str] = Query(None),
    language: Optional[str] = Query(None),
    is_featured: Optional[bool] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get list of market reports"""
    try:
        service = EducationService(db)
        result = service.get_reports(
            category=category,
            language=language,
            is_featured=is_featured,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
            search=search
        )
        
        reports = [ReportResponse.from_orm(r) for r in result["reports"]]
        
        return ReportListResponse(
            success=True,
            data=reports,
            total=result["total"],
            limit=result["limit"],
            offset=result["offset"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching reports: {str(e)}"
        )


@router.get("/reports/{report_id}", response_model=ApiResponse)
async def get_report_by_id(
    report_id: int = Path(..., description="Report ID"),
    db: Session = Depends(get_db)
):
    """Get report by ID"""
    try:
        service = EducationService(db)
        report = service.get_report_by_id(report_id)
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        return ApiResponse(
            success=True,
            data=ReportResponse.from_orm(report)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching report: {str(e)}"
        )


# ========== Progress Endpoints ==========

@router.post("/progress", response_model=ApiResponse)
async def update_progress(
    request: ProgressUpdateRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user progress"""
    try:
        service = EducationService(db)
        progress = service.update_progress(
            user_id=current_user.id,
            item_id=request.item_id,
            item_type=request.item_type,
            progress_percent=request.progress_percent,
            time_spent=request.time_spent,
            last_position=request.last_position,
            is_completed=request.is_completed,
            rating=request.rating,
            feedback=request.feedback,
            meta_data=request.meta_data
        )
        
        return ApiResponse(
            success=True,
            data=ProgressResponse.from_orm(progress)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating progress: {str(e)}"
        )

