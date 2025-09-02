from sqlalchemy.orm import Session
from sqlalchemy import func, text, and_, or_
from typing import Optional, List
import uuid
import math

from ..models.place import Place
from ..models.review import Review
from ..schemas.place import PlaceCreate, PlaceUpdate, PlaceList, PlaceSearch
from ..schemas.review import ReviewList

class PlaceService:
    def __init__(self, db: Session):
        self.db = db

    async def get_place_by_id(self, place_id: uuid.UUID) -> Optional[Place]:
        """Get a place by its ID"""
        return self.db.query(Place).filter(Place.id == place_id).first()

    async def search_places(self, search_params: PlaceSearch) -> PlaceList:
        """Search places with various filters and sorting"""
        query = self.db.query(Place)
        
        # Apply filters
        if search_params.query:
            # Full-text search
            search_vector = func.to_tsvector('english', 
                Place.name + ' ' + func.coalesce(Place.description, ''))
            search_query = func.plainto_tsquery('english', search_params.query)
            query = query.filter(search_vector.match(search_query))
        
        if search_params.city:
            query = query.filter(Place.city.ilike(f"%{search_params.city}%"))
        
        if search_params.verified_only:
            query = query.filter(Place.verified == True)
        
        if search_params.min_rating:
            query = query.filter(Place.rating >= search_params.min_rating)
        
        if search_params.price_range:
            query = query.filter(Place.price_range.in_(search_params.price_range))
        
        # Feature filters
        if search_params.has_wifi:
            query = query.filter(Place.features.contains(['wifi']))
        
        if search_params.wheelchair_accessible:
            query = query.filter(Place.features.contains(['wheelchair_accessible']))
        
        if search_params.outdoor_seating:
            query = query.filter(Place.features.contains(['outdoor_seating']))
        
        # Geographic search
        if search_params.latitude and search_params.longitude:
            # Use PostgreSQL's earth distance for nearby search
            point = f"point({search_params.longitude}, {search_params.latitude})"
            radius_meters = (search_params.radius_km or 5.0) * 1000
            
            query = query.filter(
                text(f"earth_distance(ll_to_earth(latitude, longitude), ll_to_earth({search_params.latitude}, {search_params.longitude})) <= {radius_meters}")
            )
            
            if search_params.sort_by == "distance":
                query = query.order_by(
                    text(f"earth_distance(ll_to_earth(latitude, longitude), ll_to_earth({search_params.latitude}, {search_params.longitude}))")
                )
        
        # Sorting
        if search_params.sort_by == "name":
            if search_params.sort_order == "desc":
                query = query.order_by(Place.name.desc())
            else:
                query = query.order_by(Place.name)
        elif search_params.sort_by == "rating":
            if search_params.sort_order == "desc":
                query = query.order_by(Place.rating.desc().nullslast())
            else:
                query = query.order_by(Place.rating.asc().nullsfirst())
        elif search_params.sort_by == "created_at":
            if search_params.sort_order == "desc":
                query = query.order_by(Place.created_at.desc())
            else:
                query = query.order_by(Place.created_at)
        
        # Count total results
        total = query.count()
        
        # Pagination
        offset = (search_params.page - 1) * search_params.per_page
        places = query.offset(offset).limit(search_params.per_page).all()
        
        # Calculate pagination info
        total_pages = math.ceil(total / search_params.per_page)
        
        return PlaceList(
            places=places,
            total=total,
            page=search_params.page,
            per_page=search_params.per_page,
            pages=total_pages
        )

    async def create_place(self, place_data: PlaceCreate) -> Place:
        """Create a new place"""
        # Generate slug from name
        slug = self._generate_slug(place_data.name)
        
        db_place = Place(
            **place_data.dict(),
            slug=slug
        )
        
        self.db.add(db_place)
        self.db.commit()
        self.db.refresh(db_place)
        
        return db_place

    async def update_place(self, place_id: uuid.UUID, place_data: PlaceUpdate) -> Optional[Place]:
        """Update an existing place"""
        db_place = self.db.query(Place).filter(Place.id == place_id).first()
        if not db_place:
            return None
        
        # Update fields
        update_data = place_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_place, field, value)
        
        # Update slug if name changed
        if 'name' in update_data:
            db_place.slug = self._generate_slug(update_data['name'])
        
        self.db.commit()
        self.db.refresh(db_place)
        
        return db_place

    async def delete_place(self, place_id: uuid.UUID) -> bool:
        """Delete a place"""
        db_place = self.db.query(Place).filter(Place.id == place_id).first()
        if not db_place:
            return False
        
        self.db.delete(db_place)
        self.db.commit()
        
        return True

    async def get_cities(self) -> List[str]:
        """Get list of cities with places"""
        cities = self.db.query(Place.city).distinct().order_by(Place.city).all()
        return [city[0] for city in cities]

    async def get_place_reviews(self, place_id: uuid.UUID, page: int, per_page: int) -> ReviewList:
        """Get reviews for a specific place"""
        query = self.db.query(Review).filter(
            and_(
                Review.place_id == place_id,
                Review.moderated == 1  # Only approved reviews
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

    def _generate_slug(self, name: str) -> str:
        """Generate URL-friendly slug from place name"""
        import re
        
        # Convert to lowercase and replace spaces/special chars with hyphens
        slug = re.sub(r'[^\w\s-]', '', name.lower())
        slug = re.sub(r'[-\s]+', '-', slug).strip('-')
        
        # Ensure uniqueness
        base_slug = slug
        counter = 1
        while self.db.query(Place).filter(Place.slug == slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        return slug

    async def get_featured_places(self, city: Optional[str] = None, limit: int = 10) -> List[Place]:
        """Get featured places (high rating, verified, etc.)"""
        query = self.db.query(Place).filter(
            and_(
                Place.verified == True,
                Place.rating >= 4.0
            )
        )
        
        if city:
            query = query.filter(Place.city.ilike(f"%{city}%"))
        
        return query.order_by(Place.rating.desc()).limit(limit).all()

    async def get_place_statistics(self, place_id: uuid.UUID) -> dict:
        """Get statistics for a place"""
        place = await self.get_place_by_id(place_id)
        if not place:
            return {}
        
        # Review statistics
        reviews = self.db.query(Review).filter(
            and_(
                Review.place_id == place_id,
                Review.moderated == 1
            )
        ).all()
        
        if not reviews:
            return {
                "total_reviews": 0,
                "average_rating": 0.0,
                "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            }
        
        rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for review in reviews:
            rating_counts[review.rating] += 1
        
        avg_rating = sum(review.rating for review in reviews) / len(reviews)
        
        return {
            "total_reviews": len(reviews),
            "average_rating": round(avg_rating, 2),
            "rating_distribution": rating_counts
        }