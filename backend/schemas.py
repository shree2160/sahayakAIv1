"""
Sahayak AI - Pydantic Schemas
=============================
Data validation and serialization models for API requests/responses.
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class InputType(str, Enum):
    """Enum for input types - audio or text"""
    AUDIO = "audio"
    TEXT = "text"


class Category(str, Enum):
    """Categories for local knowledge"""
    GOVERNMENT = "government"
    BANKING = "banking"
    TELECOM = "telecom"
    EDUCATION = "education"
    HEALTH = "health"
    TRANSPORT = "transport"
    UTILITIES = "utilities"
    OTHER = "other"


# =============================================================================
# REQUEST SCHEMAS
# =============================================================================

class AskRequest(BaseModel):
    """
    Request schema for the /ask endpoint.
    Either audio_base64 or text_query must be provided.
    """
    audio_base64: Optional[str] = Field(
        None, 
        description="Base64 encoded audio file (WAV format preferred)"
    )
    text_query: Optional[str] = Field(
        None, 
        description="Text query if not using voice input"
    )
    latitude: Optional[float] = Field(
        None, 
        description="User's latitude for location-based queries",
        ge=-90, 
        le=90
    )
    longitude: Optional[float] = Field(
        None, 
        description="User's longitude for location-based queries",
        ge=-180, 
        le=180
    )
    language: str = Field(
        default="hi", 
        description="Language code (hi=Hindi, en=English)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "text_query": "मोबाइल रिचार्ज कैसे करें?",
                "latitude": 28.6139,
                "longitude": 77.2090,
                "language": "hi"
            }
        }


class LocationQuery(BaseModel):
    """Schema for location-based searches"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    search_type: str = Field(
        ..., 
        description="Type of place to search (hospital, bank, etc.)"
    )
    radius: int = Field(
        default=5000, 
        description="Search radius in meters",
        ge=100, 
        le=50000
    )


class KnowledgeEntry(BaseModel):
    """Schema for adding new knowledge to the database"""
    content: str = Field(..., min_length=10, max_length=10000)
    location: Optional[str] = Field(None, description="Relevant location/city")
    category: Category = Field(default=Category.OTHER)


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================

class AskResponse(BaseModel):
    """
    Response schema for the /ask endpoint.
    Contains both text and audio response.
    """
    success: bool = Field(..., description="Whether the request was successful")
    text_response: str = Field(..., description="Text answer to the query")
    audio_base64: Optional[str] = Field(
        None, 
        description="Base64 encoded audio response (MP3/WAV)"
    )
    transcribed_text: Optional[str] = Field(
        None, 
        description="Transcribed text from audio input"
    )
    detected_intent: Optional[str] = Field(
        None, 
        description="Detected user intent"
    )
    nearby_places: Optional[List[dict]] = Field(
        None, 
        description="List of nearby relevant places if location query"
    )
    error_message: Optional[str] = Field(
        None, 
        description="Error message if request failed"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "text_response": "मोबाइल रिचार्ज करने के लिए आप PhonePe, Paytm या Google Pay का उपयोग कर सकते हैं...",
                "audio_base64": "UklGRiQAAABXQVZFZm10...",
                "transcribed_text": "मोबाइल रिचार्ज कैसे करें",
                "detected_intent": "mobile_recharge_help"
            }
        }


class HealthResponse(BaseModel):
    """Response schema for health check endpoint"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Application version")
    services: dict = Field(..., description="Status of individual services")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "services": {
                    "vosk": "ready",
                    "espeak": "ready",
                    "gemini": "connected",
                    "supabase": "connected"
                }
            }
        }


class NearbyPlace(BaseModel):
    """Schema for nearby place information"""
    name: str
    place_type: str
    distance_meters: float
    latitude: float
    longitude: float
    address: Optional[str] = None
    phone: Optional[str] = None
    opening_hours: Optional[str] = None


class NearbyPlacesResponse(BaseModel):
    """Response schema for nearby places search"""
    success: bool
    places: List[NearbyPlace]
    total_count: int
    search_radius: int
    error_message: Optional[str] = None


class KnowledgeSearchResult(BaseModel):
    """Schema for knowledge search results"""
    id: str
    content: str
    location: Optional[str]
    category: str
    similarity_score: float


class ErrorResponse(BaseModel):
    """Standard error response schema"""
    success: bool = False
    error_code: str
    error_message: str
    details: Optional[dict] = None
