from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi_cache.decorator import cache
from typing import Optional, List
from sqlalchemy.orm import Session
import uuid

from ..database import get_db
from ..schemas.place import PlaceCreate, PlaceUpdate, Place, PlaceList, PlaceSearch
from ..services.place_service import PlaceService
from ..services.cache_service import CacheService

router = APIRouter()

# Dependency injection
def get_place_service(db: Session = Depends(get_db)) -> PlaceService:
    return PlaceService(db)

def get_cache_service() -> CacheService:
    return CacheService()

@router.get("/", response_model=PlaceList, summary="Get places by city or search")
@cache(expire=3600, key_builder=lambda *args, **kwargs: f"places:{kwargs.get('city', 'all')}:{kwargs.get('page', 1)}")
async def get_places(
    city: Optional[str] = Query(None, description="Filter by city"),
    category: Optional[str] = Query(None, description="Filter by category"),
    verified_only: bool = Query(False, description="Show only verified places"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Minimum rating"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    place_service: PlaceService = Depends(get_place_service)
):
    """Get a paginated list of fika places with optional filters"""
    try:
        search_params = PlaceSearch(
            city=city,
            category=category,
            verified_only=verified_only,
            min_rating=min_rating,
            page=page,
            per_page=per_page
        )
        
        places = await place_service.search_places(search_params)
        return places
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch places: {str(e)}")

@router.get("/search", response_model=PlaceList, summary="Search places by query")
@cache(expire=1800, key_builder=lambda *args, **kwargs: f"search:{hash(kwargs.get('query', ''))}:{kwargs.get('page', 1)}")
async def search_places(
    query: str = Query(..., min_length=2, description="Search query"),
    city: Optional[str] = Query(None, description="Filter by city"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    place_service: PlaceService = Depends(get_place_service)
):
    """Search fika places by name, description, or specialties"""
    try:
        search_params = PlaceSearch(
            query=query,
            city=city,
            page=page,
            per_page=per_page
        )
        
        places = await place_service.search_places(search_params)
        return places
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/cities", summary="Get list of cities with fika places")
@cache(expire=7200)
async def get_cities(
    place_service: PlaceService = Depends(get_place_service)
):
    """Get a list of cities that have fika places"""
    try:
        cities = await place_service.get_cities()
        return {"cities": cities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch cities: {str(e)}")

@router.get("/nearby", response_model=PlaceList, summary="Find places near coordinates")
async def get_nearby_places(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude"),
    radius_km: float = Query(5.0, gt=0, le=100, description="Search radius in kilometers"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    place_service: PlaceService = Depends(get_place_service)
):
    """Find fika places near given coordinates"""
    try:
        search_params = PlaceSearch(
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
            page=page,
            per_page=per_page,
            sort_by="distance"
        )
        
        places = await place_service.search_places(search_params)
        return places
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to find nearby places: {str(e)}")

@router.get("/{place_id}", response_model=Place, summary="Get place by ID")
@cache(expire=14400, key_builder=lambda *args, **kwargs: f"place:{kwargs.get('place_id')}")
async def get_place(
    place_id: uuid.UUID,
    place_service: PlaceService = Depends(get_place_service)
):
    """Get detailed information about a specific fika place"""
    try:
        place = await place_service.get_place_by_id(place_id)
        if not place:
            raise HTTPException(status_code=404, detail="Place not found")
        return place
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch place: {str(e)}")

@router.post("/", response_model=Place, summary="Create new place", status_code=201)
async def create_place(
    place_data: PlaceCreate,
    place_service: PlaceService = Depends(get_place_service),
    cache_service: CacheService = Depends(get_cache_service)
):
    """Create a new fika place (requires authentication in production)"""
    try:
        place = await place_service.create_place(place_data)
        
        # Clear relevant caches
        await cache_service.clear_pattern(f"places:{place.city}:*")
        await cache_service.clear_pattern("search:*")
        
        return place
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create place: {str(e)}")

@router.put("/{place_id}", response_model=Place, summary="Update place")
async def update_place(
    place_id: uuid.UUID,
    place_data: PlaceUpdate,
    place_service: PlaceService = Depends(get_place_service),
    cache_service: CacheService = Depends(get_cache_service)
):
    """Update an existing fika place (requires authentication in production)"""
    try:
        place = await place_service.update_place(place_id, place_data)
        if not place:
            raise HTTPException(status_code=404, detail="Place not found")
        
        # Clear relevant caches
        await cache_service.clear_pattern(f"place:{place_id}")
        await cache_service.clear_pattern(f"places:{place.city}:*")
        await cache_service.clear_pattern("search:*")
        
        return place
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update place: {str(e)}")

@router.delete("/{place_id}", summary="Delete place")
async def delete_place(
    place_id: uuid.UUID,
    place_service: PlaceService = Depends(get_place_service),
    cache_service: CacheService = Depends(get_cache_service)
):
    """Delete a fika place (requires authentication in production)"""
    try:
        success = await place_service.delete_place(place_id)
        if not success:
            raise HTTPException(status_code=404, detail="Place not found")
        
        # Clear relevant caches
        await cache_service.clear_pattern(f"place:{place_id}")
        await cache_service.clear_pattern("places:*")
        await cache_service.clear_pattern("search:*")
        
        return {"message": "Place deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete place: {str(e)}")

@router.get("/{place_id}/reviews", summary="Get reviews for a place")
async def get_place_reviews(
    place_id: uuid.UUID,
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    place_service: PlaceService = Depends(get_place_service)
):
    """Get reviews for a specific place"""
    try:
        reviews = await place_service.get_place_reviews(place_id, page, per_page)
        return reviews
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch reviews: {str(e)}")