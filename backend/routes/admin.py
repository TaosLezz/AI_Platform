from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from database import get_db
from models.database import User
from models.custom_models import CustomModel, BatchJob, PlatformAnalytics, SystemConfiguration
from auth.security import get_current_active_user, require_admin, require_premium_or_above
from services.custom_model_service import custom_model_service
from services.batch_processing import batch_service

router = APIRouter()

# Pydantic models for API responses
class UserManagementResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]
    total_requests: int
    
class PlatformStatsResponse(BaseModel):
    total_users: int
    active_users_today: int
    total_requests_today: int
    success_rate: float
    top_services: Dict[str, int]
    system_health: Dict[str, Any]

class ModelManagementResponse(BaseModel):
    id: int
    name: str
    owner_username: str
    model_type: str
    framework: str
    is_public: bool
    is_active: bool
    total_requests: int
    success_rate: float
    created_at: datetime

# Admin endpoints for user management
@router.get("/users", response_model=List[UserManagementResponse])
async def get_all_users(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get all users for admin management"""
    users = db.query(User).offset(offset).limit(limit).all()
    
    user_responses = []
    for user in users:
        # Get user statistics
        total_requests = db.query(BatchJob).filter(BatchJob.user_id == user.id).count()
        
        user_responses.append(UserManagementResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            last_login=user.last_login,
            total_requests=total_requests
        ))
    
    return user_responses

@router.post("/users/{user_id}/role")
async def update_user_role(
    user_id: int,
    new_role: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update user role (admin only)"""
    valid_roles = ["FREE", "PREMIUM", "DEVELOPER", "ADMIN"]
    
    if new_role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {valid_roles}"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent users from demoting themselves
    if user.id == current_user.id and new_role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own admin role"
        )
    
    user.role = new_role
    db.commit()
    
    return {"message": f"User role updated to {new_role}", "user_id": user_id}

@router.post("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Deactivate a user account"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    user.is_active = False
    db.commit()
    
    return {"message": "User deactivated successfully"}

# Platform analytics endpoints
@router.get("/analytics/platform", response_model=PlatformStatsResponse)
async def get_platform_analytics(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get comprehensive platform analytics"""
    from services.monitoring import performance_monitor
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # User statistics
    total_users = db.query(User).count()
    active_users_today = db.query(User).filter(
        User.last_login >= start_date
    ).count()
    
    # Request statistics
    recent_jobs = db.query(BatchJob).filter(
        BatchJob.created_at >= start_date
    ).all()
    
    total_requests_today = len(recent_jobs)
    successful_jobs = [job for job in recent_jobs if job.status == "completed"]
    success_rate = (len(successful_jobs) / total_requests_today * 100) if total_requests_today > 0 else 0
    
    # Service breakdown
    service_counts = {}
    for job in recent_jobs:
        service_type = job.job_type
        service_counts[service_type] = service_counts.get(service_type, 0) + 1
    
    # System health
    system_health = performance_monitor.get_health_status()
    
    return PlatformStatsResponse(
        total_users=total_users,
        active_users_today=active_users_today,
        total_requests_today=total_requests_today,
        success_rate=success_rate,
        top_services=service_counts,
        system_health=system_health
    )

# Model management endpoints
@router.get("/models", response_model=List[ModelManagementResponse])
async def get_all_models(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get all custom models for admin oversight"""
    models = db.query(CustomModel).all()
    
    model_responses = []
    for model in models:
        owner = db.query(User).filter(User.id == model.owner_id).first()
        
        model_responses.append(ModelManagementResponse(
            id=model.id,
            name=model.name,
            owner_username=owner.username if owner else "Unknown",
            model_type=model.model_type,
            framework=model.framework,
            is_public=model.is_public,
            is_active=model.is_active,
            total_requests=model.total_requests or 0,
            success_rate=model.success_rate or 0.0,
            created_at=model.created_at
        ))
    
    return model_responses

@router.post("/models/{model_id}/toggle-public")
async def toggle_model_public_status(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Toggle model public/private status"""
    model = db.query(CustomModel).filter(CustomModel.id == model_id).first()
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    model.is_public = not model.is_public
    db.commit()
    
    status_text = "public" if model.is_public else "private"
    return {"message": f"Model is now {status_text}"}

@router.delete("/models/{model_id}")
async def delete_model_admin(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete any model (admin only)"""
    model = db.query(CustomModel).filter(CustomModel.id == model_id).first()
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    # Get owner for logging
    owner = db.query(User).filter(User.id == model.owner_id).first()
    
    # Delete model files and database record
    success = custom_model_service.delete_model(db, model_id, owner)
    
    if success:
        return {"message": "Model deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete model"
        )

# System configuration endpoints
@router.get("/config")
async def get_system_configuration(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get system configuration settings"""
    configs = db.query(SystemConfiguration).all()
    
    config_dict = {}
    for config in configs:
        config_dict[config.key] = {
            "value": config.value,
            "description": config.description,
            "category": config.category,
            "data_type": config.data_type,
            "requires_restart": config.requires_restart
        }
    
    return config_dict

@router.put("/config/{config_key}")
async def update_system_configuration(
    config_key: str,
    new_value: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update system configuration"""
    config = db.query(SystemConfiguration).filter(
        SystemConfiguration.key == config_key
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration key not found"
        )
    
    config.value = new_value
    config.updated_by = current_user.id
    config.updated_at = datetime.utcnow()
    
    db.commit()
    
    restart_required = config.requires_restart
    
    return {
        "message": "Configuration updated successfully",
        "restart_required": restart_required
    }

# Batch job management
@router.get("/batch-jobs")
async def get_all_batch_jobs(
    status_filter: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get all batch jobs across all users"""
    query = db.query(BatchJob)
    
    if status_filter:
        query = query.filter(BatchJob.status == status_filter)
    
    jobs = query.order_by(BatchJob.created_at.desc()).limit(limit).all()
    
    job_responses = []
    for job in jobs:
        user = db.query(User).filter(User.id == job.user_id).first()
        
        job_responses.append({
            "id": job.id,
            "name": job.name,
            "job_type": job.job_type,
            "status": job.status,
            "progress_percentage": job.progress_percentage,
            "total_items": job.total_items,
            "processed_items": job.processed_items,
            "failed_items": job.failed_items,
            "user_username": user.username if user else "Unknown",
            "created_at": job.created_at,
            "estimated_duration": job.estimated_duration,
            "actual_duration": job.actual_duration
        })
    
    return job_responses

@router.delete("/batch-jobs/{job_id}")
async def delete_batch_job_admin(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete any batch job (admin only)"""
    job = db.query(BatchJob).filter(BatchJob.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch job not found"
        )
    
    user = db.query(User).filter(User.id == job.user_id).first()
    success = batch_service.delete_job(db, job_id, user)
    
    if success:
        return {"message": "Batch job deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete batch job"
        )