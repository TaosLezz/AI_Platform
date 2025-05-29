from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from database import get_db
from models.database import User
from auth.security import get_current_active_user
from services.rate_limiter import RateLimitService

router = APIRouter()

class UsageStatsResponse(BaseModel):
    daily_usage: dict
    monthly_usage: dict
    role: str
    daily_reset_date: str
    monthly_reset_date: str

@router.get("/usage", response_model=UsageStatsResponse)
async def get_user_usage_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's usage statistics and limits"""
    
    usage_stats = RateLimitService.get_usage_stats(current_user, db)
    
    if not usage_stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usage statistics not found"
        )
    
    return UsageStatsResponse(**usage_stats)