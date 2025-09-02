from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
import uuid

from ..database import get_db
from ..services.ai_service import AIService
from ..services.place_service import PlaceService

router = APIRouter()

def get_ai_service(db: Session = Depends(get_db)) -> AIService:
    return AIService(db)

def get_place_service(db: Session = Depends(get_db)) -> PlaceService:
    return PlaceService(db)

# Pydantic models for AI endpoints
class RecommendationRequest(BaseModel):
    user_preferences: Dict[str, Any]
    city: Optional[str] = None
    max_results: int = 5

class RecommendationResponse(BaseModel):
    recommendations: List[Dict[str, Any]]
    explanation: str
    confidence: float

class ContentModerationRequest(BaseModel):
    text: str
    content_type: str = "review"

class ContentModerationResponse(BaseModel):
    is_appropriate: bool
    toxicity_score: float
    contains_spam: bool
    language: str
    explanation: str

class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    suggestions: List[str]
    confidence: float

@router.get("/dashboard", summary="AI Dashboard")
async def ai_dashboard():
    """AI-powered dashboard for managing fika locations"""
    return {
        "message": "AI Dashboard - Coming Soon!",
        "features": [
            "Content moderation",
            "Personalized recommendations",
            "Analytics and insights",
            "Automated data enrichment"
        ]
    }

@router.post("/recommendations", response_model=RecommendationResponse, summary="Get AI recommendations")
async def get_recommendations(
    request: RecommendationRequest,
    ai_service: AIService = Depends(get_ai_service)
):
    """Get personalized fika place recommendations using AI"""
    try:
        recommendations = await ai_service.get_recommendations(
            user_preferences=request.user_preferences,
            city=request.city,
            max_results=request.max_results
        )
        
        return recommendations
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations: {str(e)}")

@router.post("/moderate", response_model=ContentModerationResponse, summary="Moderate content")
async def moderate_content(
    request: ContentModerationRequest,
    ai_service: AIService = Depends(get_ai_service)
):
    """Use AI to moderate user-generated content"""
    try:
        moderation_result = await ai_service.moderate_content(
            text=request.text,
            content_type=request.content_type
        )
        
        return moderation_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content moderation failed: {str(e)}")

@router.post("/chat", response_model=ChatResponse, summary="Chat with AI assistant")
async def chat_with_ai(
    request: ChatRequest,
    ai_service: AIService = Depends(get_ai_service)
):
    """Chat with AI assistant about fika places and Swedish culture"""
    try:
        chat_response = await ai_service.chat(
            message=request.message,
            context=request.context
        )
        
        return chat_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@router.post("/enrich-place/{place_id}", summary="Enrich place data with AI")
async def enrich_place_data(
    place_id: uuid.UUID,
    ai_service: AIService = Depends(get_ai_service),
    place_service: PlaceService = Depends(get_place_service)
):
    """Use AI to enrich place data with additional information"""
    try:
        # Get existing place data
        place = await place_service.get_place_by_id(place_id)
        if not place:
            raise HTTPException(status_code=404, detail="Place not found")
        
        # Enrich with AI
        enriched_data = await ai_service.enrich_place_data(place)
        
        return {
            "message": "Place data enriched successfully",
            "original_data": place,
            "enriched_data": enriched_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to enrich place data: {str(e)}")

@router.get("/analytics", summary="AI-powered analytics")
async def get_analytics(
    timeframe: str = Query("week", regex="^(day|week|month|year)$"),
    ai_service: AIService = Depends(get_ai_service)
):
    """Get AI-powered analytics and insights"""
    try:
        analytics = await ai_service.get_analytics(timeframe)
        return analytics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate analytics: {str(e)}")

@router.post("/generate-description/{place_id}", summary="Generate place description")
async def generate_place_description(
    place_id: uuid.UUID,
    ai_service: AIService = Depends(get_ai_service),
    place_service: PlaceService = Depends(get_place_service)
):
    """Generate AI-powered description for a place"""
    try:
        place = await place_service.get_place_by_id(place_id)
        if not place:
            raise HTTPException(status_code=404, detail="Place not found")
        
        description = await ai_service.generate_place_description(place)
        
        return {
            "place_id": place_id,
            "generated_description": description,
            "original_description": place.description
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate description: {str(e)}")

@router.post("/detect-duplicates", summary="Detect duplicate places")
async def detect_duplicate_places(
    ai_service: AIService = Depends(get_ai_service)
):
    """Use AI to detect potential duplicate place entries"""
    try:
        duplicates = await ai_service.detect_duplicate_places()
        
        return {
            "message": "Duplicate detection completed",
            "potential_duplicates": duplicates,
            "total_found": len(duplicates)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Duplicate detection failed: {str(e)}")