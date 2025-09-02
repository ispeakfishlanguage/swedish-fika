from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime
import uuid

class PlaceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Name of the fika place")
    description: Optional[str] = Field(None, description="Description of the place")
    address: Optional[str] = Field(None, max_length=500, description="Street address")
    city: str = Field(..., max_length=100, description="City name")
    region: Optional[str] = Field(None, max_length=100, description="Region or state")
    
    latitude: Optional[Decimal] = Field(None, ge=-90, le=90, description="Latitude coordinate")
    longitude: Optional[Decimal] = Field(None, ge=-180, le=180, description="Longitude coordinate")
    
    phone: Optional[str] = Field(None, max_length=50, description="Phone number")
    website: Optional[str] = Field(None, max_length=255, description="Website URL")
    
    opening_hours: Optional[Dict[str, str]] = Field(None, description="Opening hours by day")
    fika_specialties: Optional[List[str]] = Field(None, description="Special fika items")
    price_range: Optional[int] = Field(None, ge=1, le=4, description="Price range (1-4)")
    
    features: Optional[List[str]] = Field(None, description="Place features")
    images: Optional[List[str]] = Field(None, description="Image URLs")
    
    @validator('fika_specialties', 'features', 'images', pre=True)
    def validate_arrays(cls, v):
        if v is None:
            return []
        return v

class PlaceCreate(PlaceBase):
    """Schema for creating a new place"""
    pass

class PlaceUpdate(BaseModel):
    """Schema for updating a place"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    region: Optional[str] = Field(None, max_length=100)
    
    latitude: Optional[Decimal] = Field(None, ge=-90, le=90)
    longitude: Optional[Decimal] = Field(None, ge=-180, le=180)
    
    phone: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = Field(None, max_length=255)
    
    opening_hours: Optional[Dict[str, str]] = None
    fika_specialties: Optional[List[str]] = None
    price_range: Optional[int] = Field(None, ge=1, le=4)
    
    features: Optional[List[str]] = None
    images: Optional[List[str]] = None
    
    verified: Optional[bool] = None

class Place(PlaceBase):
    """Schema for place response"""
    id: uuid.UUID
    slug: Optional[str] = None
    rating: Optional[Decimal] = Field(None, ge=0, le=5)
    review_count: int = 0
    verified: bool = False
    
    created_at: datetime
    updated_at: datetime
    
    # Computed properties
    price_range_symbol: Optional[str] = None
    coordinates: Optional[tuple] = None
    
    class Config:
        from_attributes = True

class PlaceList(BaseModel):
    """Schema for paginated place list"""
    places: List[Place]
    total: int
    page: int
    per_page: int
    pages: int
    
    class Config:
        from_attributes = True

class PlaceSearch(BaseModel):
    """Schema for place search parameters"""
    query: Optional[str] = None
    city: Optional[str] = None
    category: Optional[str] = None
    price_range: Optional[List[int]] = None
    min_rating: Optional[float] = Field(None, ge=0, le=5)
    verified_only: bool = False
    has_wifi: bool = False
    wheelchair_accessible: bool = False
    outdoor_seating: bool = False
    
    # Geographic search
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_km: Optional[float] = Field(None, gt=0, le=100)
    
    # Pagination
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1, le=100)
    
    # Sorting
    sort_by: str = Field("name", regex="^(name|rating|distance|created_at)$")
    sort_order: str = Field("asc", regex="^(asc|desc)$")