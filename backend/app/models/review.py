from sqlalchemy import Column, String, Text, Integer, Date, DateTime, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from ..database import Base

class Review(Base):
    __tablename__ = "reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    place_id = Column(UUID(as_uuid=True), ForeignKey("places.id", ondelete="CASCADE"), nullable=False)
    
    # Reviewer information
    user_name = Column(String(100))  # Optional - can be anonymous
    
    # Review content
    rating = Column(Integer, nullable=False)  # 1-5 stars
    comment = Column(Text)
    fika_items = Column(ARRAY(Text))  # Items tried during the visit
    
    # Visit details
    visit_date = Column(Date)
    visit_time = Column(String(20))  # "morning", "afternoon", "evening"
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Moderation
    moderated = Column(Integer, default=0)  # 0: pending, 1: approved, -1: rejected
    moderated_at = Column(DateTime(timezone=True))
    
    # Additional fields
    helpful_count = Column(Integer, default=0)
    language = Column(String(10), default="sv")  # ISO language code
    
    # Relationships
    place = relationship("Place", back_populates="reviews")
    
    def __repr__(self):
        return f"<Review(place_id='{self.place_id}', rating={self.rating})>"
    
    @property
    def is_approved(self):
        """Check if review is approved"""
        return self.moderated == 1
    
    @property
    def is_pending(self):
        """Check if review is pending moderation"""
        return self.moderated == 0
    
    @property
    def rating_stars(self):
        """Return rating as star representation"""
        return "★" * self.rating + "☆" * (5 - self.rating)