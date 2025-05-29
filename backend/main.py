from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import uvicorn
import os
import asyncio
import base64
from datetime import datetime
from typing import Optional, List, Dict, Any
import json

from models.schemas import (
    ImageGenerationRequest, 
    ImageGenerationResponse,
    ChatRequest,
    ChatResponse,
    AIJobResponse,
    ChatHistoryResponse,
    ClassificationResponse,
    DetectionResponse,
    SegmentationResponse
)
from models.database import Base, User, AIRequest, ChatSession, ChatMessage, ServiceType
from services.ai_services import AIServiceManager
from services.rate_limiter import RateLimitService, check_rate_limit
from services.storage import MemoryStorage
from auth.security import get_current_active_user
from database import engine, get_db
from routes.auth import router as auth_router
from routes.users import router as users_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Showcase Platform API",
    description="A comprehensive AI showcase platform with authentication and multiple AI services",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users_router, prefix="/api/v1/users", tags=["Users"])

# Import MLOps router
from routes.mlops import router as mlops_router
app.include_router(mlops_router, prefix="/api/v1", tags=["MLOps & Analytics"])

# Initialize services
ai_service = AIServiceManager()

#init storage
storage = MemoryStorage()

# Import monitoring and MLOps services
from services.mlflow_service import mlflow_service
from services.cache_service import cache_service, CACHE_TTL_CONFIG
from services.monitoring import performance_monitor
from services.rate_limiter import RateLimitService

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("🚀 AI Showcase Platform API Starting...")
    print("📝 API Documentation available at: /docs")
    print("🔬 ReDoc Documentation available at: /redoc")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "AI Showcase Platform API",
        "version": "2.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "services": [
            "Image Generation",
            "Image Classification", 
            "Object Detection",
            "Image Segmentation",
            "AI Chatbot"
        ]
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "openai": ai_service.check_openai_connection(),
            "storage": "operational"
        }
    }

# Image Generation Endpoints
@app.post("/api/v1/generate", response_model=ImageGenerationResponse)
async def generate_image(request: ImageGenerationRequest):
    """Generate images from text prompts using AI models"""
    try:
        # Create job record
        job = await storage.create_ai_job({
            "user_id": 1,  # Demo user
            "service_type": "generate",
            "prompt": request.prompt,
            "parameters": request.parameters.dict() if request.parameters else {},
            "status": "processing"
        })

        # Process the request
        result = await ai_service.generate_image(
            request.prompt, 
            request.parameters.dict() if request.parameters else {}
        )
        
        # Update job with result
        await storage.update_ai_job(job["id"], {
            "status": "completed" if result["success"] else "failed",
            "result": result["data"] if result["success"] else {"error": result["error"]}
        })

        if result["success"]:
            return ImageGenerationResponse(
                job_id=job["id"],
                url=result["data"]["url"],
                prompt=result["data"]["prompt"],
                processing_time=result["processing_time"]
            )
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Image Classification Endpoints
@app.post("/api/v1/classify", response_model=ClassificationResponse)
async def classify_image(
    image: UploadFile = File(...),
    use_hugging_face: bool = Form(False)
):
    """Classify images and identify objects with confidence scores"""
    try:
        # Validate file type
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")

        # Read and encode image
        image_data = await image.read()
        base64_image = base64.b64encode(image_data).decode('utf-8')

        # Create job record
        job = await storage.create_ai_job({
            "user_id": 1,
            "service_type": "classify",
            "parameters": {"use_hugging_face": use_hugging_face},
            "status": "processing"
        })

        # Process the request
        result = await ai_service.classify_image(base64_image, use_hugging_face)
        
        # Update job with result
        await storage.update_ai_job(job["id"], {
            "status": "completed" if result["success"] else "failed",
            "result": result["data"] if result["success"] else {"error": result["error"]}
        })

        if result["success"]:
            data = result["data"]
            return ClassificationResponse(
                job_id=job["id"],
                class_name=data["class"],
                confidence=data["confidence"],
                description=data["description"],
                alternatives=data.get("alternatives", []),
                processing_time=result["processing_time"]
            )
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Object Detection Endpoints
@app.post("/api/v1/detect", response_model=DetectionResponse)
async def detect_objects(
    image: UploadFile = File(...),
    use_hugging_face: bool = Form(False)
):
    """Detect and locate objects in images with bounding boxes"""
    try:
        # Validate file type
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")

        # Read and encode image
        image_data = await image.read()
        base64_image = base64.b64encode(image_data).decode('utf-8')

        # Create job record
        job = await storage.create_ai_job({
            "user_id": 1,
            "service_type": "detect",
            "parameters": {"use_hugging_face": use_hugging_face},
            "status": "processing"
        })

        # Process the request
        result = await ai_service.detect_objects(base64_image, use_hugging_face)
        
        # Update job with result
        await storage.update_ai_job(job["id"], {
            "status": "completed" if result["success"] else "failed",
            "result": result["data"] if result["success"] else {"error": result["error"]}
        })

        if result["success"]:
            return DetectionResponse(
                job_id=job["id"],
                objects=result["data"]["objects"],
                processing_time=result["processing_time"]
            )
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Image Segmentation Endpoints
@app.post("/api/v1/segment", response_model=SegmentationResponse)
async def segment_image(
    image: UploadFile = File(...),
    use_hugging_face: bool = Form(False)
):
    """Perform pixel-level image segmentation and masking"""
    try:
        # Validate file type
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")

        # Read and encode image
        image_data = await image.read()
        base64_image = base64.b64encode(image_data).decode('utf-8')

        # Create job record
        job = await storage.create_ai_job({
            "user_id": 1,
            "service_type": "segment",
            "parameters": {"use_hugging_face": use_hugging_face},
            "status": "processing"
        })

        # Process the request
        result = await ai_service.segment_image(base64_image, use_hugging_face)
        
        # Update job with result
        await storage.update_ai_job(job["id"], {
            "status": "completed" if result["success"] else "failed",
            "result": result["data"] if result["success"] else {"error": result["error"]}
        })

        if result["success"]:
            return SegmentationResponse(
                job_id=job["id"],
                segments=result["data"]["segments"],
                processing_time=result["processing_time"]
            )
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Chat Endpoints
@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat_completion(request: ChatRequest):
    """AI chatbot with context-aware responses"""
    try:
        # Save user message
        await storage.create_chat_message({
            "user_id": 1,
            "role": "user",
            "content": request.message
        })

        # Get chat history
        history = await storage.get_chat_history(1, 10)
        messages = [{"role": msg["role"], "content": msg["content"]} for msg in history]

        # Process chat completion
        result = await ai_service.chat_completion(messages)
        # print("result", result)
        if result["success"]:
            # Save assistant response
            await storage.create_chat_message({
                "user_id": 1,
                "role": "assistant",
                "content": result["data"]["response"]
            })

            return ChatResponse(
                response=result["data"]["response"],
                processing_time=result["processing_time"]
            )
        # else:
        #     raise HTTPException(status_code=500, detail=result["error"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/chat/history", response_model=ChatHistoryResponse)
async def get_chat_history():
    """Get chat conversation history"""
    try:
        history = await storage.get_chat_history(1, 50)
        return ChatHistoryResponse(messages=history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Job Management Endpoints
@app.get("/api/v1/jobs")
async def get_recent_jobs():
    """Get recent AI processing jobs"""
    try:
        jobs = await storage.get_recent_ai_jobs(20)
        return {"jobs": jobs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/jobs/{job_id}", response_model=AIJobResponse)
async def get_job(job_id: int):
    """Get specific AI job details"""
    try:
        job = await storage.get_ai_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return AIJobResponse(**job)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# MLflow Integration Endpoints
@app.get("/api/v1/mlflow/experiments")
async def get_experiments():
    """Get MLflow experiments (placeholder for future implementation)"""
    return {
        "experiments": [
            {
                "id": "1",
                "name": "image_generation_experiments",
                "artifact_location": "mlflow-artifacts:/1",
                "tags": {"framework": "pytorch", "task": "generation"}
            },
            {
                "id": "2", 
                "name": "classification_experiments",
                "artifact_location": "mlflow-artifacts:/2",
                "tags": {"framework": "transformers", "task": "classification"}
            }
        ]
    }

@app.get("/api/v1/mlflow/models")
async def get_models():
    """Get MLflow registered models (placeholder for future implementation)"""
    return {
        "models": [
            {
                "name": "stable-diffusion-v2",
                "version": "1",
                "stage": "Production",
                "tags": {"task": "text-to-image"}
            },
            {
                "name": "resnet-classifier",
                "version": "3",
                "stage": "Staging", 
                "tags": {"task": "classification"}
            }
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        # log_level="info",
        # debug=True
    )