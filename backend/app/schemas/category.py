from pydantic import BaseModel, Field
from typing import Optional, List
import uuid

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Category name")
    description: Optional[str] = Field(None, description="Category description")
    icon: Optional[str] = Field(None, max_length=50, description="Icon class or emoji")

class CategoryCreate(CategoryBase):
    """Schema for creating a new category"""
    pass

class CategoryUpdate(BaseModel):
    """Schema for updating a category"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=50)

class Category(CategoryBase):
    """Schema for category response"""
    id: uuid.UUID
    
    class Config:
        from_attributes = True

class CategoryList(BaseModel):
    """Schema for category list"""
    categories: List[Category]
    total: int
    
    class Config:
        from_attributes = True