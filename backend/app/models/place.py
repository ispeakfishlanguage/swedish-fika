from sqlalchemy import Column, String, Text, Integer, Numeric, Boolean, DateTime, ARRAY, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from ..database import Base

class Place(Base):
    __tablename__ = "places"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    address = Column(String(500))
    city = Column(String(100), nullable=False, index=True)
    region = Column(String(100))
    
    # Geographic coordinates
    latitude = Column(Numeric(precision=10, scale=8))
    longitude = Column(Numeric(precision=11, scale=8))
    
    # Contact information
    phone = Column(String(50))
    website = Column(String(255))
    
    # Business details
    opening_hours = Column(JSON)  # Store as JSON: {"monday": "8:00-17:00", ...}
    fika_specialties = Column(ARRAY(Text))  # Array of specialty items
    price_range = Column(Integer)  # 1-4 scale ($ to $$$$)
    
    # Ratings and verification
    rating = Column(Numeric(precision=3, scale=2))  # 0.00 to 5.00
    review_count = Column(Integer, default=0)
    verified = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Additional features
    features = Column(ARRAY(Text))  # ["outdoor_seating", "wifi", "wheelchair_accessible"]
    images = Column(ARRAY(Text))  # Array of image URLs
    
    # SEO and metadata
    slug = Column(String(255), unique=True, index=True)
    meta_description = Column(Text)
    
    # Relationships
    reviews = relationship("Review", back_populates="place", cascade="all, delete-orphan")
    categories = relationship("PlaceCategory", back_populates="place")
    
    def __repr__(self):
        return f"<Place(name='{self.name}', city='{self.city}')>"
    
    @property
    def average_rating(self):
        """Calculate average rating from reviews"""
        if hasattr(self, 'reviews') and self.reviews:
            return sum(review.rating for review in self.reviews) / len(self.reviews)
        return self.rating or 0.0
    
    @property
    def price_range_symbol(self):
        """Convert price range to symbol representation"""
        if not self.price_range:
            return ""
        return "$" * self.price_range
    
    @property
    def coordinates(self):
        """Return coordinates as tuple"""
        if self.latitude and self.longitude:
            return (float(self.latitude), float(self.longitude))
        return None