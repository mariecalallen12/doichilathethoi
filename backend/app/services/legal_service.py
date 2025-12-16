"""
Legal Service
Digital Utopia Platform

Business logic cho Legal operations
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from datetime import datetime
import logging

from ..models.legal import TermsOfService, PrivacyPolicy, RiskWarning, Complaint

logger = logging.getLogger(__name__)


class LegalService:
    """
    Service class cho Legal operations
    
    Cung cấp business logic cho:
    - Terms of Service
    - Privacy Policy
    - Risk Warning
    - Complaints
    """
    
    def __init__(self, db: Session):
        """
        Khởi tạo LegalService
        
        Args:
            db: SQLAlchemy session
        """
        self.db = db
    
    # =============== Terms of Service ===============
    
    def get_terms(self) -> Optional[TermsOfService]:
        """
        Lấy current terms of service
        
        Returns:
            TermsOfService object hoặc None
        """
        terms = self.db.query(TermsOfService).filter(
            and_(
                TermsOfService.is_active == True,
                TermsOfService.is_current == True
            )
        ).first()
        
        return terms
    
    def get_terms_by_version(self, version: str) -> Optional[TermsOfService]:
        """
        Lấy terms of service theo version
        
        Args:
            version: Version string
            
        Returns:
            TermsOfService object hoặc None
        """
        terms = self.db.query(TermsOfService).filter(
            and_(
                TermsOfService.version == version,
                TermsOfService.is_active == True
            )
        ).first()
        
        return terms
    
    def get_all_terms(self) -> List[TermsOfService]:
        """
        Lấy tất cả terms versions
        
        Returns:
            List of TermsOfService objects
        """
        terms = self.db.query(TermsOfService).filter(
            TermsOfService.is_active == True
        ).order_by(desc(TermsOfService.effective_date)).all()
        
        return terms
    
    # =============== Privacy Policy ===============
    
    def get_privacy(self) -> Optional[PrivacyPolicy]:
        """
        Lấy current privacy policy
        
        Returns:
            PrivacyPolicy object hoặc None
        """
        privacy = self.db.query(PrivacyPolicy).filter(
            and_(
                PrivacyPolicy.is_active == True,
                PrivacyPolicy.is_current == True
            )
        ).first()
        
        return privacy
    
    def get_privacy_by_version(self, version: str) -> Optional[PrivacyPolicy]:
        """
        Lấy privacy policy theo version
        
        Args:
            version: Version string
            
        Returns:
            PrivacyPolicy object hoặc None
        """
        privacy = self.db.query(PrivacyPolicy).filter(
            and_(
                PrivacyPolicy.version == version,
                PrivacyPolicy.is_active == True
            )
        ).first()
        
        return privacy
    
    def get_all_privacy(self) -> List[PrivacyPolicy]:
        """
        Lấy tất cả privacy versions
        
        Returns:
            List of PrivacyPolicy objects
        """
        privacy = self.db.query(PrivacyPolicy).filter(
            PrivacyPolicy.is_active == True
        ).order_by(desc(PrivacyPolicy.effective_date)).all()
        
        return privacy
    
    # =============== Risk Warning ===============
    
    def get_risk_warning(self, language: str = "en") -> Optional[RiskWarning]:
        """
        Lấy current risk warning
        
        Args:
            language: Language code
            
        Returns:
            RiskWarning object hoặc None
        """
        risk_warning = self.db.query(RiskWarning).filter(
            and_(
                RiskWarning.is_active == True,
                RiskWarning.is_current == True,
                RiskWarning.language == language
            )
        ).first()
        
        return risk_warning
    
    def get_all_risk_warnings(self, language: Optional[str] = None) -> List[RiskWarning]:
        """
        Lấy tất cả risk warnings
        
        Args:
            language: Optional language filter
            
        Returns:
            List of RiskWarning objects
        """
        query = self.db.query(RiskWarning).filter(
            RiskWarning.is_active == True
        )
        
        if language:
            query = query.filter(RiskWarning.language == language)
        
        warnings = query.order_by(desc(RiskWarning.created_at)).all()
        
        return warnings
    
    # =============== Complaints ===============
    
    def get_complaints(
        self,
        user_id: Optional[int] = None,
        status: Optional[str] = None,
        complaint_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Lấy danh sách complaints
        
        Args:
            user_id: Filter by user ID (required for non-admin users)
            status: Filter by status
            complaint_type: Filter by complaint type
            limit: Number of results
            offset: Offset for pagination
            
        Returns:
            Dict với complaints và metadata
        """
        query = self.db.query(Complaint)
        
        if user_id:
            query = query.filter(Complaint.user_id == user_id)
        
        if status:
            query = query.filter(Complaint.status == status)
        
        if complaint_type:
            query = query.filter(Complaint.complaint_type == complaint_type)
        
        total = query.count()
        
        complaints = query.order_by(
            desc(Complaint.submitted_at)
        ).offset(offset).limit(limit).all()
        
        return {
            "complaints": complaints,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    
    def submit_complaint(
        self,
        user_id: int,
        complaint_type: str,
        subject: str,
        description: str,
        related_transaction_id: Optional[int] = None,
        related_order_id: Optional[int] = None,
        related_reference: Optional[str] = None,
        priority: str = "normal",
        attachments: Optional[List[str]] = None
    ) -> Complaint:
        """
        Submit complaint
        
        Args:
            user_id: User ID
            complaint_type: Complaint type
            subject: Subject
            description: Description
            related_transaction_id: Optional related transaction ID
            related_order_id: Optional related order ID
            related_reference: Optional related reference
            priority: Priority level
            attachments: Optional attachments
            
        Returns:
            Complaint object
        """
        complaint = Complaint(
            user_id=user_id,
            complaint_type=complaint_type,
            subject=subject,
            description=description,
            related_transaction_id=related_transaction_id,
            related_order_id=related_order_id,
            related_reference=related_reference,
            priority=priority,
            status="submitted",
            submitted_at=datetime.utcnow(),
            attachments=attachments or []
        )
        
        self.db.add(complaint)
        self.db.commit()
        self.db.refresh(complaint)
        
        return complaint
    
    def get_complaint_by_id(
        self,
        complaint_id: int,
        user_id: Optional[int] = None
    ) -> Optional[Complaint]:
        """
        Lấy complaint theo ID
        
        Args:
            complaint_id: Complaint ID
            user_id: Optional user ID (to ensure user can only access their own)
            
        Returns:
            Complaint object hoặc None
        """
        query = self.db.query(Complaint).filter(
            Complaint.id == complaint_id
        )
        
        if user_id:
            query = query.filter(Complaint.user_id == user_id)
        
        complaint = query.first()
        
        return complaint
    
    def update_complaint(
        self,
        complaint_id: int,
        user_id: Optional[int] = None,
        status: Optional[str] = None,
        resolution: Optional[str] = None,
        user_satisfaction: Optional[str] = None,
        user_feedback: Optional[str] = None
    ) -> Optional[Complaint]:
        """
        Cập nhật complaint
        
        Args:
            complaint_id: Complaint ID
            user_id: Optional user ID (to ensure user can only update their own)
            status: New status
            resolution: Resolution text
            user_satisfaction: User satisfaction
            user_feedback: User feedback
            
        Returns:
            Updated Complaint object hoặc None
        """
        query = self.db.query(Complaint).filter(
            Complaint.id == complaint_id
        )
        
        if user_id:
            query = query.filter(Complaint.user_id == user_id)
        
        complaint = query.first()
        
        if not complaint:
            return None
        
        # Users can only update satisfaction and feedback
        # Status and resolution can only be updated by admins
        if user_id and complaint.user_id == user_id:
            if user_satisfaction is not None:
                complaint.user_satisfaction = user_satisfaction
            if user_feedback is not None:
                complaint.user_feedback = user_feedback
        else:
            # Admin updates
            if status is not None:
                complaint.status = status
                if status in ["resolved", "closed"]:
                    complaint.resolved_at = datetime.utcnow()
            if resolution is not None:
                complaint.resolution = resolution
        
        self.db.commit()
        self.db.refresh(complaint)
        
        return complaint

