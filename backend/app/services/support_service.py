"""
Support Service
Digital Utopia Platform

Business logic cho Support operations
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from datetime import datetime
import logging

from ..models.support import (
    SupportArticle, SupportCategory, SupportContact,
    SupportOffice, SupportChannel, FAQ
)

logger = logging.getLogger(__name__)


class SupportService:
    """
    Service class cho Support operations
    
    Cung cấp business logic cho:
    - Support articles
    - Categories
    - Contact submissions
    - Offices
    - Channels
    - FAQ
    """
    
    def __init__(self, db: Session):
        """
        Khởi tạo SupportService
        
        Args:
            db: SQLAlchemy session
        """
        self.db = db
    
    # =============== Articles ===============
    
    def get_articles(
        self,
        category_id: Optional[int] = None,
        language: Optional[str] = None,
        is_featured: Optional[bool] = None,
        is_pinned: Optional[bool] = None,
        limit: int = 20,
        offset: int = 0,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Lấy danh sách articles
        
        Args:
            category_id: Filter by category ID
            language: Filter by language
            is_featured: Filter by featured status
            is_pinned: Filter by pinned status
            limit: Number of results
            offset: Offset for pagination
            search: Search query
            
        Returns:
            Dict với articles và metadata
        """
        query = self.db.query(SupportArticle).filter(
            SupportArticle.is_published == True
        )
        
        if category_id:
            query = query.filter(SupportArticle.category_id == category_id)
        
        if language:
            query = query.filter(SupportArticle.language == language)
        
        if is_featured is not None:
            query = query.filter(SupportArticle.is_featured == is_featured)
        
        if is_pinned is not None:
            query = query.filter(SupportArticle.is_pinned == is_pinned)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    SupportArticle.title.ilike(search_pattern),
                    SupportArticle.content.ilike(search_pattern),
                    SupportArticle.excerpt.ilike(search_pattern)
                )
            )
        
        total = query.count()
        
        articles = query.order_by(
            desc(SupportArticle.is_pinned),
            desc(SupportArticle.is_featured),
            desc(SupportArticle.sort_order),
            desc(SupportArticle.created_at)
        ).offset(offset).limit(limit).all()
        
        return {
            "articles": articles,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    
    def get_article_by_id(self, article_id: int) -> Optional[SupportArticle]:
        """
        Lấy article theo ID
        
        Args:
            article_id: Article ID
            
        Returns:
            SupportArticle object hoặc None
        """
        article = self.db.query(SupportArticle).filter(
            and_(
                SupportArticle.id == article_id,
                SupportArticle.is_published == True
            )
        ).first()
        
        if article:
            # Increment view count
            article.view_count = (article.view_count or 0) + 1
            self.db.commit()
        
        return article
    
    # =============== Categories ===============
    
    def get_categories(self) -> List[SupportCategory]:
        """
        Lấy danh sách categories
        
        Returns:
            List of SupportCategory objects
        """
        categories = self.db.query(SupportCategory).filter(
            SupportCategory.is_active == True
        ).order_by(
            SupportCategory.sort_order.asc(),
            SupportCategory.name.asc()
        ).all()
        
        # Add article count to each category
        for category in categories:
            article_count = self.db.query(func.count(SupportArticle.id)).filter(
                and_(
                    SupportArticle.category_id == category.id,
                    SupportArticle.is_published == True
                )
            ).scalar()
            category.article_count = article_count or 0
        
        return categories
    
    # =============== Search ===============
    
    def search_articles(
        self,
        query: str,
        category_id: Optional[int] = None,
        language: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Tìm kiếm articles
        
        Args:
            query: Search query
            category_id: Filter by category ID
            language: Filter by language
            limit: Number of results
            offset: Offset for pagination
            
        Returns:
            Dict với articles và metadata
        """
        search_pattern = f"%{query}%"
        
        db_query = self.db.query(SupportArticle).filter(
            and_(
                SupportArticle.is_published == True,
                or_(
                    SupportArticle.title.ilike(search_pattern),
                    SupportArticle.content.ilike(search_pattern),
                    SupportArticle.excerpt.ilike(search_pattern)
                )
            )
        )
        
        if category_id:
            db_query = db_query.filter(SupportArticle.category_id == category_id)
        
        if language:
            db_query = db_query.filter(SupportArticle.language == language)
        
        total = db_query.count()
        
        articles = db_query.order_by(
            desc(SupportArticle.is_pinned),
            desc(SupportArticle.is_featured),
            desc(SupportArticle.view_count)
        ).offset(offset).limit(limit).all()
        
        return {
            "articles": articles,
            "total": total,
            "query": query,
            "limit": limit,
            "offset": offset
        }
    
    # =============== Contact ===============
    
    def submit_contact(
        self,
        name: str,
        email: str,
        subject: str,
        message: str,
        phone: Optional[str] = None,
        contact_type: Optional[str] = None,
        priority: str = "normal",
        user_id: Optional[int] = None
    ) -> SupportContact:
        """
        Submit contact form
        
        Args:
            name: Contact name
            email: Contact email
            subject: Subject
            message: Message
            phone: Optional phone
            contact_type: Contact type
            priority: Priority level
            user_id: Optional user ID
            
        Returns:
            SupportContact object
        """
        contact = SupportContact(
            user_id=user_id,
            name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message,
            contact_type=contact_type,
            priority=priority,
            status="pending",
            submitted_at=datetime.utcnow()
        )
        
        self.db.add(contact)
        self.db.commit()
        self.db.refresh(contact)
        
        return contact
    
    # =============== Offices ===============
    
    def get_offices(self) -> List[SupportOffice]:
        """
        Lấy danh sách offices
        
        Returns:
            List of SupportOffice objects
        """
        offices = self.db.query(SupportOffice).filter(
            SupportOffice.is_active == True
        ).order_by(
            desc(SupportOffice.is_headquarters),
            SupportOffice.sort_order.asc(),
            SupportOffice.name.asc()
        ).all()
        
        return offices
    
    # =============== Channels ===============
    
    def get_channels(self) -> List[SupportChannel]:
        """
        Lấy danh sách channels
        
        Returns:
            List of SupportChannel objects
        """
        channels = self.db.query(SupportChannel).filter(
            SupportChannel.is_active == True
        ).order_by(
            desc(SupportChannel.is_primary),
            SupportChannel.sort_order.asc(),
            SupportChannel.name.asc()
        ).all()
        
        return channels
    
    # =============== FAQ ===============
    
    def get_faq(
        self,
        category: Optional[str] = None,
        language: Optional[str] = None,
        is_featured: Optional[bool] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Lấy danh sách FAQ
        
        Args:
            category: Filter by category
            language: Filter by language
            is_featured: Filter by featured status
            limit: Number of results
            offset: Offset for pagination
            
        Returns:
            Dict với FAQs và metadata
        """
        query = self.db.query(FAQ).filter(
            FAQ.is_published == True
        )
        
        if category:
            query = query.filter(FAQ.category == category)
        
        if language:
            query = query.filter(FAQ.language == language)
        
        if is_featured is not None:
            query = query.filter(FAQ.is_featured == is_featured)
        
        total = query.count()
        
        faqs = query.order_by(
            desc(FAQ.is_featured),
            FAQ.sort_order.asc(),
            FAQ.question.asc()
        ).offset(offset).limit(limit).all()
        
        return {
            "faqs": faqs,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    
    def search_faq(
        self,
        query: str,
        category: Optional[str] = None,
        language: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Tìm kiếm FAQ
        
        Args:
            query: Search query
            category: Filter by category
            language: Filter by language
            limit: Number of results
            offset: Offset for pagination
            
        Returns:
            Dict với FAQs và metadata
        """
        search_pattern = f"%{query}%"
        
        db_query = self.db.query(FAQ).filter(
            and_(
                FAQ.is_published == True,
                or_(
                    FAQ.question.ilike(search_pattern),
                    FAQ.answer.ilike(search_pattern)
                )
            )
        )
        
        if category:
            db_query = db_query.filter(FAQ.category == category)
        
        if language:
            db_query = db_query.filter(FAQ.language == language)
        
        total = db_query.count()
        
        faqs = db_query.order_by(
            desc(FAQ.is_featured),
            desc(FAQ.view_count)
        ).offset(offset).limit(limit).all()
        
        return {
            "faqs": faqs,
            "total": total,
            "query": query,
            "limit": limit,
            "offset": offset
        }

