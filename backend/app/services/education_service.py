"""
Education Service
Digital Utopia Platform

Business logic cho Education operations
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from datetime import datetime
import logging

from ..models.education import (
    EducationVideo, EducationEbook, EconomicCalendar, 
    MarketReport, EducationProgress
)

logger = logging.getLogger(__name__)


class EducationService:
    """
    Service class cho Education operations
    
    Cung cấp business logic cho:
    - Video tutorials
    - Ebooks
    - Economic calendar
    - Market reports
    - Progress tracking
    """
    
    def __init__(self, db: Session):
        """
        Khởi tạo EducationService
        
        Args:
            db: SQLAlchemy session
        """
        self.db = db
    
    # =============== Videos ===============
    
    def get_videos(
        self,
        category: Optional[str] = None,
        language: Optional[str] = None,
        is_featured: Optional[bool] = None,
        limit: int = 20,
        offset: int = 0,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Lấy danh sách videos
        
        Args:
            category: Filter by category
            language: Filter by language
            is_featured: Filter by featured status
            limit: Number of results
            offset: Offset for pagination
            search: Search query
            
        Returns:
            Dict với videos và metadata
        """
        query = self.db.query(EducationVideo).filter(
            EducationVideo.is_published == True
        )
        
        if category:
            query = query.filter(EducationVideo.category == category)
        
        if language:
            query = query.filter(EducationVideo.language == language)
        
        if is_featured is not None:
            query = query.filter(EducationVideo.is_featured == is_featured)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    EducationVideo.title.ilike(search_pattern),
                    EducationVideo.description.ilike(search_pattern)
                )
            )
        
        total = query.count()
        
        videos = query.order_by(
            desc(EducationVideo.is_featured),
            desc(EducationVideo.sort_order),
            desc(EducationVideo.created_at)
        ).offset(offset).limit(limit).all()
        
        return {
            "videos": videos,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    
    def get_video_by_id(self, video_id: int) -> Optional[EducationVideo]:
        """
        Lấy video theo ID
        
        Args:
            video_id: Video ID
            
        Returns:
            EducationVideo object hoặc None
        """
        video = self.db.query(EducationVideo).filter(
            and_(
                EducationVideo.id == video_id,
                EducationVideo.is_published == True
            )
        ).first()
        
        if video:
            # Increment view count
            video.views_count = (video.views_count or 0) + 1
            self.db.commit()
        
        return video
    
    # =============== Ebooks ===============
    
    def get_ebooks(
        self,
        category: Optional[str] = None,
        language: Optional[str] = None,
        is_featured: Optional[bool] = None,
        limit: int = 20,
        offset: int = 0,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Lấy danh sách ebooks
        
        Args:
            category: Filter by category
            language: Filter by language
            is_featured: Filter by featured status
            limit: Number of results
            offset: Offset for pagination
            search: Search query
            
        Returns:
            Dict với ebooks và metadata
        """
        query = self.db.query(EducationEbook).filter(
            EducationEbook.is_published == True
        )
        
        if category:
            query = query.filter(EducationEbook.category == category)
        
        if language:
            query = query.filter(EducationEbook.language == language)
        
        if is_featured is not None:
            query = query.filter(EducationEbook.is_featured == is_featured)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    EducationEbook.title.ilike(search_pattern),
                    EducationEbook.description.ilike(search_pattern)
                )
            )
        
        total = query.count()
        
        ebooks = query.order_by(
            desc(EducationEbook.is_featured),
            desc(EducationEbook.sort_order),
            desc(EducationEbook.created_at)
        ).offset(offset).limit(limit).all()
        
        return {
            "ebooks": ebooks,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    
    def get_ebook_by_id(self, ebook_id: int) -> Optional[EducationEbook]:
        """
        Lấy ebook theo ID
        
        Args:
            ebook_id: Ebook ID
            
        Returns:
            EducationEbook object hoặc None
        """
        ebook = self.db.query(EducationEbook).filter(
            and_(
                EducationEbook.id == ebook_id,
                EducationEbook.is_published == True
            )
        ).first()
        
        if ebook:
            # Increment download count (when viewed)
            ebook.download_count = (ebook.download_count or 0) + 1
            self.db.commit()
        
        return ebook
    
    # =============== Economic Calendar ===============
    
    def get_calendar(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        country: Optional[str] = None,
        currency: Optional[str] = None,
        impact: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Lấy economic calendar events
        
        Args:
            start_date: Start date filter
            end_date: End date filter
            country: Filter by country
            currency: Filter by currency
            impact: Filter by impact level
            category: Filter by category
            limit: Number of results
            offset: Offset for pagination
            
        Returns:
            Dict với events và metadata
        """
        query = self.db.query(EconomicCalendar).filter(
            EconomicCalendar.is_published == True
        )
        
        if start_date:
            query = query.filter(EconomicCalendar.event_date >= start_date)
        
        if end_date:
            query = query.filter(EconomicCalendar.event_date <= end_date)
        
        if country:
            query = query.filter(EconomicCalendar.country == country)
        
        if currency:
            query = query.filter(EconomicCalendar.currency == currency)
        
        if impact:
            query = query.filter(EconomicCalendar.impact == impact)
        
        if category:
            query = query.filter(EconomicCalendar.category == category)
        
        total = query.count()
        
        events = query.order_by(
            EconomicCalendar.event_date.asc()
        ).offset(offset).limit(limit).all()
        
        return {
            "events": events,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    
    # =============== Market Reports ===============
    
    def get_reports(
        self,
        category: Optional[str] = None,
        language: Optional[str] = None,
        is_featured: Optional[bool] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 20,
        offset: int = 0,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Lấy danh sách market reports
        
        Args:
            category: Filter by category
            language: Filter by language
            is_featured: Filter by featured status
            start_date: Filter by start date
            end_date: Filter by end date
            limit: Number of results
            offset: Offset for pagination
            search: Search query
            
        Returns:
            Dict với reports và metadata
        """
        query = self.db.query(MarketReport).filter(
            MarketReport.is_published == True
        )
        
        if category:
            query = query.filter(MarketReport.category == category)
        
        if language:
            query = query.filter(MarketReport.language == language)
        
        if is_featured is not None:
            query = query.filter(MarketReport.is_featured == is_featured)
        
        if start_date:
            query = query.filter(MarketReport.report_date >= start_date)
        
        if end_date:
            query = query.filter(MarketReport.report_date <= end_date)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    MarketReport.title.ilike(search_pattern),
                    MarketReport.summary.ilike(search_pattern)
                )
            )
        
        total = query.count()
        
        reports = query.order_by(
            desc(MarketReport.is_featured),
            desc(MarketReport.report_date),
            desc(MarketReport.sort_order)
        ).offset(offset).limit(limit).all()
        
        return {
            "reports": reports,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    
    def get_report_by_id(self, report_id: int) -> Optional[MarketReport]:
        """
        Lấy report theo ID
        
        Args:
            report_id: Report ID
            
        Returns:
            MarketReport object hoặc None
        """
        report = self.db.query(MarketReport).filter(
            and_(
                MarketReport.id == report_id,
                MarketReport.is_published == True
            )
        ).first()
        
        if report:
            # Increment view count
            report.view_count = (report.view_count or 0) + 1
            self.db.commit()
        
        return report
    
    # =============== Progress Tracking ===============
    
    def update_progress(
        self,
        user_id: int,
        item_id: int,
        item_type: str,
        progress_percent: Optional[float] = None,
        time_spent: Optional[int] = None,
        last_position: Optional[str] = None,
        is_completed: Optional[bool] = None,
        rating: Optional[int] = None,
        feedback: Optional[str] = None,
        meta_data: Optional[Dict[str, Any]] = None
    ) -> EducationProgress:
        """
        Cập nhật progress của user
        
        Args:
            user_id: User ID
            item_id: Item ID (video, ebook, or report)
            item_type: Item type (video, ebook, or report)
            progress_percent: Progress percentage (0-100)
            time_spent: Time spent in seconds
            last_position: Last position
            is_completed: Is completed flag
            rating: Rating (1-5)
            feedback: User feedback
            meta_data: Additional metadata
            
        Returns:
            EducationProgress object
        """
        # Validate item_type
        if item_type not in ['video', 'ebook', 'report']:
            raise ValueError(f"Invalid item_type: {item_type}")
        
        # Check if progress exists
        progress = self.db.query(EducationProgress).filter(
            and_(
                EducationProgress.user_id == user_id,
                EducationProgress.item_id == item_id,
                EducationProgress.item_type == item_type
            )
        ).first()
        
        if not progress:
            # Create new progress
            progress = EducationProgress(
                user_id=user_id,
                item_id=item_id,
                item_type=item_type,
                progress_percent=0.0,
                time_spent=0,
                is_completed=False
            )
            self.db.add(progress)
        
        # Update progress
        if progress_percent is not None:
            progress.progress_percent = min(100.0, max(0.0, float(progress_percent)))
        
        if time_spent is not None:
            progress.time_spent = (progress.time_spent or 0) + time_spent
        
        if last_position is not None:
            progress.last_position = last_position
        
        if is_completed is not None:
            progress.is_completed = is_completed
            if is_completed and not progress.completed_at:
                progress.completed_at = datetime.utcnow()
        
        if rating is not None:
            progress.rating = min(5, max(1, int(rating)))
        
        if feedback is not None:
            progress.feedback = feedback
        
        if meta_data is not None:
            if progress.meta_data:
                progress.meta_data.update(meta_data)
            else:
                progress.meta_data = meta_data
        
        self.db.commit()
        self.db.refresh(progress)
        
        return progress

