from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date
import uuid

class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    comment: Optional[str] = Field(None, max_length=1000, description="Review comment")
    fika_items: Optional[List[str]] = Field(None, description="Fika items tried")
    visit_date: Optional[date] = Field(None, description="Date of visit")
    visit_time: Optional[str] = Field(None, regex="^(morning|afternoon|evening)$", description="Time of visit")
    user_name: Optional[str] = Field(None, max_length=100, description="Reviewer name (optional)")
    
    @validator('fika_items', pre=True)
    def validate_fika_items(cls, v):
        if v is None:
            return []
        return v
    
    @validator('comment')
    def validate_comment(cls, v):
        if v is not None and len(v.strip()) < 10:
            raise ValueError('Comment must be at least 10 characters long')
        return v

class ReviewCreate(ReviewBase):
    """Schema for creating a new review"""
    place_id: uuid.UUID = Field(..., description="ID of the place being reviewed")

class ReviewUpdate(BaseModel):
    """Schema for updating a review"""
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=1000)
    fika_items: Optional[List[str]] = None
    visit_date: Optional[date] = None
    visit_time: Optional[str] = Field(None, regex="^(morning|afternoon|evening)$")
    user_name: Optional[str] = Field(None, max_length=100)

class Review(ReviewBase):
    """Schema for review response"""
    id: uuid.UUID
    place_id: uuid.UUID
    
    created_at: datetime
    updated_at: datetime
    
    # Moderation status
    moderated: int = 0  # 0: pending, 1: approved, -1: rejected
    moderated_at: Optional[datetime] = None
    
    helpful_count: int = 0
    language: str = "sv"
    
    # Computed properties
    is_approved: bool
    is_pending: bool
    rating_stars: str
    
    class Config:
        from_attributes = True

class ReviewList(BaseModel):
    """Schema for paginated review list"""
    reviews: List[Review]
    total: int
    page: int
    per_page: int
    pages: int
    
    class Config:
        from_attributes = True

class ReviewSummary(BaseModel):
    """Schema for review summary statistics"""
    total_reviews: int
    average_rating: float
    rating_distribution: dict  # {1: count, 2: count, ...}
    recent_reviews: List[Review]
    
    class Config:
        from_attributes = True

class ReviewModeration(BaseModel):
    """Schema for review moderation"""
    review_id: uuid.UUID
    action: str = Field(..., regex="^(approve|reject)$")
    reason: Optional[str] = Field(None, max_length=500)