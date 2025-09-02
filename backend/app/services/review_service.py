from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
import uuid
import math
from datetime import datetime

from ..models.review import Review
from ..models.place import Place
from ..schemas.review import ReviewCreate, ReviewUpdate, ReviewList

class ReviewService:
    def __init__(self, db: Session):
        self.db = db

    async def create_review(self, review_data: ReviewCreate) -> Review:
        """Create a new review"""
        # Check if place exists
        place = self.db.query(Place).filter(Place.id == review_data.place_id).first()
        if not place:
            raise ValueError("Place not found")
        
        db_review = Review(**review_data.dict())
        self.db.add(db_review)
        self.db.commit()
        self.db.refresh(db_review)
        
        # Update place rating and review count
        await self._update_place_rating(review_data.place_id)
        
        return db_review

    async def get_review_by_id(self, review_id: uuid.UUID) -> Optional[Review]:
        """Get a review by its ID"""
        return self.db.query(Review).filter(Review.id == review_id).first()

    async def update_review(self, review_id: uuid.UUID, review_data: ReviewUpdate) -> Optional[Review]:
        """Update an existing review"""
        db_review = self.db.query(Review).filter(Review.id == review_id).first()
        if not db_review:
            return None
        
        # Store original place_id and rating for place rating update
        original_place_id = db_review.place_id
        original_rating = db_review.rating
        
        # Update fields
        update_data = review_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_review, field, value)
        
        self.db.commit()
        self.db.refresh(db_review)
        
        # Update place rating if rating changed
        if 'rating' in update_data and update_data['rating'] != original_rating:
            await self._update_place_rating(original_place_id)
        
        return db_review

    async def delete_review(self, review_id: uuid.UUID) -> bool:
        """Delete a review"""
        db_review = self.db.query(Review).filter(Review.id == review_id).first()
        if not db_review:
            return False
        
        place_id = db_review.place_id
        
        self.db.delete(db_review)
        self.db.commit()
        
        # Update place rating after deletion
        await self._update_place_rating(place_id)
        
        return True

    async def get_reviews_by_place(self, place_id: uuid.UUID, page: int = 1, per_page: int = 20, approved_only: bool = True) -> ReviewList:
        """Get reviews for a specific place"""
        query = self.db.query(Review).filter(Review.place_id == place_id)
        
        if approved_only:
            query = query.filter(Review.moderated == 1)
        
        query = query.order_by(Review.created_at.desc())
        
        total = query.count()
        offset = (page - 1) * per_page
        reviews = query.offset(offset).limit(per_page).all()
        
        total_pages = math.ceil(total / per_page)
        
        return ReviewList(
            reviews=reviews,
            total=total,
            page=page,
            per_page=per_page,
            pages=total_pages
        )

    async def get_pending_reviews(self, page: int = 1, per_page: int = 20) -> ReviewList:
        """Get reviews pending moderation"""
        query = self.db.query(Review).filter(Review.moderated == 0).order_by(Review.created_at.asc())
        
        total = query.count()
        offset = (page - 1) * per_page
        reviews = query.offset(offset).limit(per_page).all()
        
        total_pages = math.ceil(total / per_page)
        
        return ReviewList(
            reviews=reviews,
            total=total,
            page=page,
            per_page=per_page,
            pages=total_pages
        )

    async def moderate_review(self, review_id: uuid.UUID, action: str, reason: Optional[str] = None) -> bool:
        """Moderate a review (approve or reject)"""
        db_review = self.db.query(Review).filter(Review.id == review_id).first()
        if not db_review:
            return False
        
        if action == "approve":
            db_review.moderated = 1
        elif action == "reject":
            db_review.moderated = -1
        else:
            raise ValueError("Action must be 'approve' or 'reject'")
        
        db_review.moderated_at = datetime.utcnow()
        
        self.db.commit()
        
        # Update place rating if approved
        if action == "approve":
            await self._update_place_rating(db_review.place_id)
        
        return True

    async def get_user_reviews(self, user_name: str, page: int = 1, per_page: int = 20) -> ReviewList:
        """Get reviews by a specific user"""
        query = self.db.query(Review).filter(
            and_(
                Review.user_name == user_name,
                Review.moderated == 1
            )
        ).order_by(Review.created_at.desc())
        
        total = query.count()
        offset = (page - 1) * per_page
        reviews = query.offset(offset).limit(per_page).all()
        
        total_pages = math.ceil(total / per_page)
        
        return ReviewList(
            reviews=reviews,
            total=total,
            page=page,
            per_page=per_page,
            pages=total_pages
        )

    async def get_recent_reviews(self, limit: int = 10) -> List[Review]:
        """Get recent approved reviews"""
        return self.db.query(Review).filter(
            Review.moderated == 1
        ).order_by(Review.created_at.desc()).limit(limit).all()

    async def mark_helpful(self, review_id: uuid.UUID) -> bool:
        """Mark a review as helpful"""
        db_review = self.db.query(Review).filter(Review.id == review_id).first()
        if not db_review:
            return False
        
        db_review.helpful_count = (db_review.helpful_count or 0) + 1
        self.db.commit()
        
        return True

    async def get_review_statistics(self, place_id: Optional[uuid.UUID] = None) -> dict:
        """Get review statistics"""
        query = self.db.query(Review).filter(Review.moderated == 1)
        
        if place_id:
            query = query.filter(Review.place_id == place_id)
        
        reviews = query.all()
        
        if not reviews:
            return {
                "total_reviews": 0,
                "average_rating": 0.0,
                "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            }
        
        # Calculate statistics
        total_reviews = len(reviews)
        average_rating = sum(r.rating for r in reviews) / total_reviews
        
        # Rating distribution
        rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for review in reviews:
            rating_distribution[review.rating] += 1
        
        return {
            "total_reviews": total_reviews,
            "average_rating": round(average_rating, 2),
            "rating_distribution": rating_distribution
        }

    async def _update_place_rating(self, place_id: uuid.UUID):
        """Update place rating based on approved reviews"""
        place = self.db.query(Place).filter(Place.id == place_id).first()
        if not place:
            return
        
        # Get all approved reviews for this place
        approved_reviews = self.db.query(Review).filter(
            and_(
                Review.place_id == place_id,
                Review.moderated == 1
            )
        ).all()
        
        if approved_reviews:
            # Calculate new rating and review count
            new_rating = sum(r.rating for r in approved_reviews) / len(approved_reviews)
            place.rating = round(new_rating, 2)
            place.review_count = len(approved_reviews)
        else:
            # No approved reviews
            place.rating = None
            place.review_count = 0
        
        self.db.commit()

    async def bulk_moderate_reviews(self, review_ids: List[uuid.UUID], action: str) -> int:
        """Bulk moderate multiple reviews"""
        if action not in ["approve", "reject"]:
            raise ValueError("Action must be 'approve' or 'reject'")
        
        moderated_value = 1 if action == "approve" else -1
        moderated_at = datetime.utcnow()
        
        # Update reviews in bulk
        updated = self.db.query(Review).filter(
            Review.id.in_(review_ids)
        ).update(
            {
                Review.moderated: moderated_value,
                Review.moderated_at: moderated_at
            },
            synchronize_session=False
        )
        
        self.db.commit()
        
        # Update place ratings for affected places if approved
        if action == "approve":
            affected_places = self.db.query(Review.place_id).filter(
                Review.id.in_(review_ids)
            ).distinct().all()
            
            for place_id_tuple in affected_places:
                await self._update_place_rating(place_id_tuple[0])
        
        return updated