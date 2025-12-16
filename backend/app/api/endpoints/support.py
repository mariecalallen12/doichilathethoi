"""
Support module endpoints for FastAPI.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ...dependencies import get_current_user
from ...db.session import get_db
from ...models.user import User
from ...schemas.support import (
    ArticleListRequest, ArticleListResponse, ArticleResponse,
    CategoryListResponse, CategoryResponse,
    ArticleSearchRequest, ArticleSearchResponse,
    ContactSubmitRequest, ContactResponse,
    OfficeListResponse, OfficeResponse,
    ChannelListResponse, ChannelResponse,
    FAQListRequest, FAQListResponse, FAQResponse,
    FAQSearchRequest, FAQSearchResponse,
    ApiResponse, ApiError
)
from ...services.support_service import SupportService

router = APIRouter()


# ========== Article Endpoints ==========

@router.get("/articles", response_model=ArticleListResponse)
async def get_articles(
    category_id: Optional[int] = Query(None),
    language: Optional[str] = Query(None),
    is_featured: Optional[bool] = Query(None),
    is_pinned: Optional[bool] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get list of support articles"""
    try:
        service = SupportService(db)
        result = service.get_articles(
            category_id=category_id,
            language=language,
            is_featured=is_featured,
            is_pinned=is_pinned,
            limit=limit,
            offset=offset,
            search=search
        )
        
        articles = []
        for article in result["articles"]:
            article_dict = ArticleResponse.from_orm(article).dict()
            if article.category:
                article_dict["category_name"] = article.category.name
            articles.append(ArticleResponse(**article_dict))
        
        return ArticleListResponse(
            success=True,
            data=articles,
            total=result["total"],
            limit=result["limit"],
            offset=result["offset"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching articles: {str(e)}"
        )


@router.get("/articles/{article_id}", response_model=ApiResponse)
async def get_article_by_id(
    article_id: int = Path(..., description="Article ID"),
    db: Session = Depends(get_db)
):
    """Get article by ID"""
    try:
        service = SupportService(db)
        article = service.get_article_by_id(article_id)
        
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Article not found"
            )
        
        article_dict = ArticleResponse.from_orm(article).dict()
        if article.category:
            article_dict["category_name"] = article.category.name
        
        return ApiResponse(
            success=True,
            data=ArticleResponse(**article_dict)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching article: {str(e)}"
        )


# ========== Category Endpoints ==========

@router.get("/categories", response_model=CategoryListResponse)
async def get_categories(
    db: Session = Depends(get_db)
):
    """Get list of support categories"""
    try:
        service = SupportService(db)
        categories = service.get_categories()
        
        category_list = [CategoryResponse.from_orm(c) for c in categories]
        
        return CategoryListResponse(
            success=True,
            data=category_list
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching categories: {str(e)}"
        )


# ========== Search Endpoints ==========

@router.post("/search", response_model=ArticleSearchResponse)
async def search_articles(
    request: ArticleSearchRequest,
    db: Session = Depends(get_db)
):
    """Search support articles"""
    try:
        service = SupportService(db)
        result = service.search_articles(
            query=request.query,
            category_id=request.category_id,
            language=request.language,
            limit=request.limit,
            offset=request.offset
        )
        
        articles = []
        for article in result["articles"]:
            article_dict = ArticleResponse.from_orm(article).dict()
            if article.category:
                article_dict["category_name"] = article.category.name
            articles.append(ArticleResponse(**article_dict))
        
        return ArticleSearchResponse(
            success=True,
            data=articles,
            total=result["total"],
            query=result["query"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching articles: {str(e)}"
        )


# ========== Contact Endpoints ==========

@router.post("/contact", response_model=ApiResponse)
async def submit_contact(
    request: ContactSubmitRequest,
    db: Session = Depends(get_db)
):
    """Submit contact form (anonymous allowed)"""
    try:
        service = SupportService(db)
        contact = service.submit_contact(
            name=request.name,
            email=request.email,
            subject=request.subject,
            message=request.message,
            phone=request.phone,
            contact_type=request.contact_type,
            priority=request.priority,
            user_id=None  # Allow anonymous submissions
        )
        
        return ApiResponse(
            success=True,
            data=ContactResponse.from_orm(contact)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error submitting contact: {str(e)}"
        )


# ========== Office Endpoints ==========

@router.get("/offices", response_model=OfficeListResponse)
async def get_offices(
    db: Session = Depends(get_db)
):
    """Get list of support offices"""
    try:
        service = SupportService(db)
        offices = service.get_offices()
        
        office_list = [OfficeResponse.from_orm(o) for o in offices]
        
        return OfficeListResponse(
            success=True,
            data=office_list
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching offices: {str(e)}"
        )


# ========== Channel Endpoints ==========

@router.get("/channels", response_model=ChannelListResponse)
async def get_channels(
    db: Session = Depends(get_db)
):
    """Get list of support channels"""
    try:
        service = SupportService(db)
        channels = service.get_channels()
        
        channel_list = [ChannelResponse.from_orm(c) for c in channels]
        
        return ChannelListResponse(
            success=True,
            data=channel_list
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching channels: {str(e)}"
        )


# ========== FAQ Endpoints ==========

@router.get("/faq", response_model=FAQListResponse)
async def get_faq(
    category: Optional[str] = Query(None),
    language: Optional[str] = Query(None),
    is_featured: Optional[bool] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get list of FAQ"""
    try:
        service = SupportService(db)
        result = service.get_faq(
            category=category,
            language=language,
            is_featured=is_featured,
            limit=limit,
            offset=offset
        )
        
        faqs = [FAQResponse.from_orm(f) for f in result["faqs"]]
        
        return FAQListResponse(
            success=True,
            data=faqs,
            total=result["total"],
            limit=result["limit"],
            offset=result["offset"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching FAQ: {str(e)}"
        )


@router.get("/faq/{category}", response_model=FAQListResponse)
async def get_faq_by_category(
    category: str = Path(..., description="FAQ category"),
    language: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get FAQ by category"""
    try:
        service = SupportService(db)
        result = service.get_faq(
            category=category,
            language=language,
            limit=limit,
            offset=offset
        )
        
        faqs = [FAQResponse.from_orm(f) for f in result["faqs"]]
        
        return FAQListResponse(
            success=True,
            data=faqs,
            total=result["total"],
            limit=result["limit"],
            offset=result["offset"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching FAQ: {str(e)}"
        )


@router.post("/faq/search", response_model=FAQSearchResponse)
async def search_faq(
    request: FAQSearchRequest,
    db: Session = Depends(get_db)
):
    """Search FAQ"""
    try:
        service = SupportService(db)
        result = service.search_faq(
            query=request.query,
            category=request.category,
            language=request.language,
            limit=request.limit,
            offset=request.offset
        )
        
        faqs = [FAQResponse.from_orm(f) for f in result["faqs"]]
        
        return FAQSearchResponse(
            success=True,
            data=faqs,
            total=result["total"],
            query=result["query"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching FAQ: {str(e)}"
        )

