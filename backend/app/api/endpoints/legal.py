"""
Legal module endpoints for FastAPI.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ...dependencies import get_current_user
from ...db.session import get_db
from ...models.user import User
from ...schemas.legal import (
    TermsRequest, TermsResponse, TermsListResponse,
    PrivacyRequest, PrivacyResponse, PrivacyListResponse,
    RiskWarningResponse, RiskWarningListResponse,
    ComplaintSubmitRequest, ComplaintUpdateRequest,
    ComplaintResponse, ComplaintListRequest, ComplaintListResponse,
    ApiResponse, ApiError
)
from ...services.legal_service import LegalService

router = APIRouter()


# ========== Terms of Service Endpoints ==========

@router.get("/terms", response_model=ApiResponse)
async def get_terms(
    version: Optional[str] = Query(None, description="Terms version"),
    db: Session = Depends(get_db)
):
    """Get terms of service"""
    try:
        service = LegalService(db)
        
        if version:
            terms = service.get_terms_by_version(version)
        else:
            terms = service.get_terms()
        
        if not terms:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Terms of service not found"
            )
        
        return ApiResponse(
            success=True,
            data=TermsResponse.from_orm(terms)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching terms: {str(e)}"
        )


@router.get("/terms/version/{version}", response_model=ApiResponse)
async def get_terms_by_version(
    version: str = Path(..., description="Terms version"),
    db: Session = Depends(get_db)
):
    """Get terms of service by version"""
    try:
        service = LegalService(db)
        terms = service.get_terms_by_version(version)
        
        if not terms:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Terms of service not found"
            )
        
        return ApiResponse(
            success=True,
            data=TermsResponse.from_orm(terms)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching terms: {str(e)}"
        )


# ========== Privacy Policy Endpoints ==========

@router.get("/privacy", response_model=ApiResponse)
async def get_privacy(
    version: Optional[str] = Query(None, description="Privacy version"),
    db: Session = Depends(get_db)
):
    """Get privacy policy"""
    try:
        service = LegalService(db)
        
        if version:
            privacy = service.get_privacy_by_version(version)
        else:
            privacy = service.get_privacy()
        
        if not privacy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Privacy policy not found"
            )
        
        return ApiResponse(
            success=True,
            data=PrivacyResponse.from_orm(privacy)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching privacy policy: {str(e)}"
        )


@router.get("/privacy/version/{version}", response_model=ApiResponse)
async def get_privacy_by_version(
    version: str = Path(..., description="Privacy version"),
    db: Session = Depends(get_db)
):
    """Get privacy policy by version"""
    try:
        service = LegalService(db)
        privacy = service.get_privacy_by_version(version)
        
        if not privacy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Privacy policy not found"
            )
        
        return ApiResponse(
            success=True,
            data=PrivacyResponse.from_orm(privacy)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching privacy policy: {str(e)}"
        )


# ========== Risk Warning Endpoints ==========

@router.get("/risk-warning", response_model=ApiResponse)
async def get_risk_warning(
    language: str = Query("en", description="Language code"),
    db: Session = Depends(get_db)
):
    """Get risk warning"""
    try:
        service = LegalService(db)
        risk_warning = service.get_risk_warning(language=language)
        
        if not risk_warning:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Risk warning not found"
            )
        
        return ApiResponse(
            success=True,
            data=RiskWarningResponse.from_orm(risk_warning)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching risk warning: {str(e)}"
        )


# ========== Complaint Endpoints ==========

@router.get("/complaints", response_model=ComplaintListResponse)
async def get_complaints(
    status: Optional[str] = Query(None),
    complaint_type: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of complaints"""
    try:
        service = LegalService(db)
        
        # Non-admin users can only see their own complaints
        user_id = current_user.id
        # TODO: Check if user is admin to allow viewing all complaints
        
        result = service.get_complaints(
            user_id=user_id,
            status=status,
            complaint_type=complaint_type,
            limit=limit,
            offset=offset
        )
        
        complaints = [ComplaintResponse.from_orm(c) for c in result["complaints"]]
        
        return ComplaintListResponse(
            success=True,
            data=complaints,
            total=result["total"],
            limit=result["limit"],
            offset=result["offset"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching complaints: {str(e)}"
        )


@router.post("/complaints", response_model=ApiResponse)
async def submit_complaint(
    request: ComplaintSubmitRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit complaint"""
    try:
        service = LegalService(db)
        complaint = service.submit_complaint(
            user_id=current_user.id,
            complaint_type=request.complaint_type,
            subject=request.subject,
            description=request.description,
            related_transaction_id=request.related_transaction_id,
            related_order_id=request.related_order_id,
            related_reference=request.related_reference,
            priority=request.priority,
            attachments=request.attachments
        )
        
        return ApiResponse(
            success=True,
            data=ComplaintResponse.from_orm(complaint)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error submitting complaint: {str(e)}"
        )


@router.get("/complaints/{complaint_id}", response_model=ApiResponse)
async def get_complaint_by_id(
    complaint_id: int = Path(..., description="Complaint ID"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get complaint by ID"""
    try:
        service = LegalService(db)
        complaint = service.get_complaint_by_id(
            complaint_id=complaint_id,
            user_id=current_user.id  # Users can only access their own complaints
        )
        
        if not complaint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Complaint not found"
            )
        
        return ApiResponse(
            success=True,
            data=ComplaintResponse.from_orm(complaint)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching complaint: {str(e)}"
        )


@router.put("/complaints/{complaint_id}", response_model=ApiResponse)
async def update_complaint(
    complaint_id: int = Path(..., description="Complaint ID"),
    request: ComplaintUpdateRequest = ...,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update complaint"""
    try:
        service = LegalService(db)
        complaint = service.update_complaint(
            complaint_id=complaint_id,
            user_id=current_user.id,  # Users can only update their own complaints
            status=request.status,
            resolution=request.resolution,
            user_satisfaction=request.user_satisfaction,
            user_feedback=request.user_feedback
        )
        
        if not complaint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Complaint not found"
            )
        
        return ApiResponse(
            success=True,
            data=ComplaintResponse.from_orm(complaint)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating complaint: {str(e)}"
        )

