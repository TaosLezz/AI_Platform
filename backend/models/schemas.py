from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Request Models
class GenerationParameters(BaseModel):
    style: str = "photorealistic"
    resolution: str = "1024x1024"
    guidance_scale: float = 7.5
    steps: int = 50

class ImageGenerationRequest(BaseModel):
    prompt: str = Field(..., description="Text prompt for image generation")
    parameters: Optional[GenerationParameters] = None

class ChatRequest(BaseModel):
    message: str = Field(..., description="User message for the chatbot")

# Response Models
class ImageGenerationResponse(BaseModel):
    job_id: int
    url: str
    prompt: str
    processing_time: float

class ClassificationResponse(BaseModel):
    job_id: int
    class_name: str = Field(..., alias="class")
    confidence: float
    description: str
    alternatives: Optional[List[Dict[str, Any]]] = []
    processing_time: float

class DetectionObject(BaseModel):
    name: str
    confidence: float
    bbox: List[float]

class DetectionResponse(BaseModel):
    job_id: int
    objects: List[DetectionObject]
    processing_time: float

class SegmentationSegment(BaseModel):
    name: str
    mask: str
    confidence: float

class SegmentationResponse(BaseModel):
    job_id: int
    segments: List[SegmentationSegment]
    processing_time: float

class ChatResponse(BaseModel):
    response: str
    processing_time: float

class ChatMessage(BaseModel):
    id: int
    role: str
    content: str
    timestamp: datetime

class ChatHistoryResponse(BaseModel):
    messages: List[ChatMessage]

class AIJobResponse(BaseModel):
    id: int
    user_id: Optional[int]
    service_type: str
    prompt: Optional[str]
    image_url: Optional[str]
    status: str
    result: Optional[Dict[str, Any]]
    parameters: Optional[Dict[str, Any]]
    created_at: datetime
    completed_at: Optional[datetime]

# Error Response Models
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)