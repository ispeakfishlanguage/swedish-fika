from sqlalchemy import Column, String, Text, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from ..database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text)
    icon = Column(String(50))  # Icon class name or emoji
    
    # Relationships
    places = relationship("PlaceCategory", back_populates="category")
    
    def __repr__(self):
        return f"<Category(name='{self.name}')>"

class PlaceCategory(Base):
    __tablename__ = "place_categories"

    place_id = Column(UUID(as_uuid=True), ForeignKey("places.id", ondelete="CASCADE"), primary_key=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True)
    
    # Relationships
    place = relationship("Place", back_populates="categories")
    category = relationship("Category", back_populates="places")
    
    def __repr__(self):
        return f"<PlaceCategory(place_id='{self.place_id}', category_id='{self.category_id}')>"