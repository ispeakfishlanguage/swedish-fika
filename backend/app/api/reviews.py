from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
import uuid

from ..database import get_db
from ..schemas.review import ReviewCreate, ReviewUpdate, Review, ReviewList, ReviewModeration
from ..services.review_service import ReviewService
from ..services.cache_service import CacheService

router = APIRouter()

def get_review_service(db: Session = Depends(get_db)) -> ReviewService:
    return ReviewService(db)

def get_cache_service() -> CacheService:
    return CacheService()

@router.post("/", response_model=Review, summary="Create new review", status_code=201)
async def create_review(
    review_data: ReviewCreate,
    review_service: ReviewService = Depends(get_review_service),
    cache_service: CacheService = Depends(get_cache_service)
):
    """Create a new review for a fika place"""
    try:
        review = await review_service.create_review(review_data)
        
        # Clear place cache since rating might change
        await cache_service.clear_pattern(f"place:{review_data.place_id}")
        await cache_service.clear_pattern(f"reviews:{review_data.place_id}:*")
        
        return review
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create review: {str(e)}")

@router.get("/{review_id}", response_model=Review, summary="Get review by ID")
async def get_review(
    review_id: uuid.UUID,
    review_service: ReviewService = Depends(get_review_service)
):
    """Get a specific review"""
    try:
        review = await review_service.get_review_by_id(review_id)
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        return review
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch review: {str(e)}")

@router.put("/{review_id}", response_model=Review, summary="Update review")
async def update_review(
    review_id: uuid.UUID,
    review_data: ReviewUpdate,
    review_service: ReviewService = Depends(get_review_service),
    cache_service: CacheService = Depends(get_cache_service)
):
    """Update an existing review"""
    try:
        review = await review_service.update_review(review_id, review_data)
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        
        # Clear relevant caches
        await cache_service.clear_pattern(f"place:{review.place_id}")
        await cache_service.clear_pattern(f"reviews:{review.place_id}:*")
        
        return review
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update review: {str(e)}")

@router.delete("/{review_id}", summary="Delete review")
async def delete_review(
    review_id: uuid.UUID,
    review_service: ReviewService = Depends(get_review_service),
    cache_service: CacheService = Depends(get_cache_service)
):
    """Delete a review"""
    try:
        success = await review_service.delete_review(review_id)
        if not success:
            raise HTTPException(status_code=404, detail="Review not found")
        
        # Clear relevant caches
        await cache_service.clear_pattern("place:*")
        await cache_service.clear_pattern("reviews:*")
        
        return {"message": "Review deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete review: {str(e)}")

@router.post("/{review_id}/moderate", summary="Moderate review")
async def moderate_review(
    review_moderation: ReviewModeration,
    review_service: ReviewService = Depends(get_review_service),
    cache_service: CacheService = Depends(get_cache_service)
):
    """Moderate a review (approve or reject)"""
    try:
        success = await review_service.moderate_review(
            review_moderation.review_id,
            review_moderation.action,
            review_moderation.reason
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Review not found")
        
        # Clear relevant caches
        await cache_service.clear_pattern("reviews:*")
        
        return {"message": f"Review {review_moderation.action}d successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to moderate review: {str(e)}")

@router.get("/pending", response_model=ReviewList, summary="Get pending reviews")
async def get_pending_reviews(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    review_service: ReviewService = Depends(get_review_service)
):
    """Get reviews pending moderation"""
    try:
        reviews = await review_service.get_pending_reviews(page, per_page)
        return reviews
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch pending reviews: {str(e)}")