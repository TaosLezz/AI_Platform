from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional

from database import get_db
from models.database import User, UsageLimit, ServiceType, UserRole
from auth.security import get_current_active_user

class RateLimitService:
    """Service for managing API rate limits based on user roles"""
    
    @staticmethod
    def check_usage_limit(
        user: User,
        service_type: ServiceType,
        db: Session
    ) -> bool:
        """Check if user has exceeded their usage limits"""
        
        # Admin users have unlimited access
        if user.role == UserRole.ADMIN:
            return True
        
        # Get user's usage limits
        usage_limit = db.query(UsageLimit).filter(
            UsageLimit.user_id == user.id
        ).first()
        
        if not usage_limit:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Usage limits not found for user"
            )
        
        # Reset counters if needed
        RateLimitService._reset_counters_if_needed(usage_limit, db)
        
        # Check daily limits
        daily_used_field = f"daily_{service_type.value}_used"
        daily_limit_field = f"daily_{service_type.value}_limit"
        
        daily_used = getattr(usage_limit, daily_used_field, 0)
        daily_limit = getattr(usage_limit, daily_limit_field, 0)
        
        if daily_limit > 0 and daily_used >= daily_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Daily {service_type.value} limit exceeded ({daily_used}/{daily_limit})"
            )
        
        # Check monthly limits
        monthly_used_field = f"monthly_{service_type.value}_used"
        monthly_limit_field = f"monthly_{service_type.value}_limit"
        
        monthly_used = getattr(usage_limit, monthly_used_field, 0)
        monthly_limit = getattr(usage_limit, monthly_limit_field, 0)
        
        if monthly_limit > 0 and monthly_used >= monthly_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Monthly {service_type.value} limit exceeded ({monthly_used}/{monthly_limit})"
            )
        
        return True
    
    @staticmethod
    def increment_usage(
        user: User,
        service_type: ServiceType,
        db: Session
    ):
        """Increment usage counters for the user"""
        
        # Admin users don't need usage tracking
        if user.role == UserRole.ADMIN:
            return
        
        usage_limit = db.query(UsageLimit).filter(
            UsageLimit.user_id == user.id
        ).first()
        
        if not usage_limit:
            return
        
        # Reset counters if needed
        RateLimitService._reset_counters_if_needed(usage_limit, db)
        
        # Increment daily usage
        daily_used_field = f"daily_{service_type.value}_used"
        current_daily = getattr(usage_limit, daily_used_field, 0)
        setattr(usage_limit, daily_used_field, current_daily + 1)
        
        # Increment monthly usage
        monthly_used_field = f"monthly_{service_type.value}_used"
        current_monthly = getattr(usage_limit, monthly_used_field, 0)
        setattr(usage_limit, monthly_used_field, current_monthly + 1)
        
        db.commit()
    
    @staticmethod
    def _reset_counters_if_needed(usage_limit: UsageLimit, db: Session):
        """Reset daily/monthly counters if time period has passed"""
        now = datetime.utcnow()
        
        # Reset daily counters if it's a new day
        if usage_limit.daily_reset_date.date() < now.date():
            usage_limit.daily_generate_used = 0
            usage_limit.daily_classify_used = 0
            usage_limit.daily_detect_used = 0
            usage_limit.daily_segment_used = 0
            usage_limit.daily_chat_used = 0
            usage_limit.daily_reset_date = now
        
        # Reset monthly counters if it's a new month
        monthly_reset = usage_limit.monthly_reset_date
        if (monthly_reset.year < now.year or 
            (monthly_reset.year == now.year and monthly_reset.month < now.month)):
            usage_limit.monthly_generate_used = 0
            usage_limit.monthly_classify_used = 0
            usage_limit.monthly_detect_used = 0
            usage_limit.monthly_segment_used = 0
            usage_limit.monthly_chat_used = 0
            usage_limit.monthly_reset_date = now
        
        db.commit()
    
    @staticmethod
    def get_usage_stats(user: User, db: Session) -> dict:
        """Get current usage statistics for a user"""
        usage_limit = db.query(UsageLimit).filter(
            UsageLimit.user_id == user.id
        ).first()
        
        if not usage_limit:
            return {}
        
        # Reset counters if needed
        RateLimitService._reset_counters_if_needed(usage_limit, db)
        
        return {
            "daily_usage": {
                "generate": {
                    "used": usage_limit.daily_generate_used,
                    "limit": usage_limit.daily_generate_limit,
                    "remaining": max(0, usage_limit.daily_generate_limit - usage_limit.daily_generate_used)
                        if usage_limit.daily_generate_limit > 0 else -1
                },
                "classify": {
                    "used": usage_limit.daily_classify_used,
                    "limit": usage_limit.daily_classify_limit,
                    "remaining": max(0, usage_limit.daily_classify_limit - usage_limit.daily_classify_used)
                        if usage_limit.daily_classify_limit > 0 else -1
                },
                "detect": {
                    "used": usage_limit.daily_detect_used,
                    "limit": usage_limit.daily_detect_limit,
                    "remaining": max(0, usage_limit.daily_detect_limit - usage_limit.daily_detect_used)
                        if usage_limit.daily_detect_limit > 0 else -1
                },
                "segment": {
                    "used": usage_limit.daily_segment_used,
                    "limit": usage_limit.daily_segment_limit,
                    "remaining": max(0, usage_limit.daily_segment_limit - usage_limit.daily_segment_used)
                        if usage_limit.daily_segment_limit > 0 else -1
                },
                "chat": {
                    "used": usage_limit.daily_chat_used,
                    "limit": usage_limit.daily_chat_limit,
                    "remaining": max(0, usage_limit.daily_chat_limit - usage_limit.daily_chat_used)
                        if usage_limit.daily_chat_limit > 0 else -1
                }
            },
            "monthly_usage": {
                "generate": {
                    "used": usage_limit.monthly_generate_used,
                    "limit": usage_limit.monthly_generate_limit,
                    "remaining": max(0, usage_limit.monthly_generate_limit - usage_limit.monthly_generate_used)
                        if usage_limit.monthly_generate_limit > 0 else -1
                },
                "classify": {
                    "used": usage_limit.monthly_classify_used,
                    "limit": usage_limit.monthly_classify_limit,
                    "remaining": max(0, usage_limit.monthly_classify_limit - usage_limit.monthly_classify_used)
                        if usage_limit.monthly_classify_limit > 0 else -1
                },
                "detect": {
                    "used": usage_limit.monthly_detect_used,
                    "limit": usage_limit.monthly_detect_limit,
                    "remaining": max(0, usage_limit.monthly_detect_limit - usage_limit.monthly_detect_used)
                        if usage_limit.monthly_detect_limit > 0 else -1
                },
                "segment": {
                    "used": usage_limit.monthly_segment_used,
                    "limit": usage_limit.monthly_segment_limit,
                    "remaining": max(0, usage_limit.monthly_segment_limit - usage_limit.monthly_segment_used)
                        if usage_limit.monthly_segment_limit > 0 else -1
                },
                "chat": {
                    "used": usage_limit.monthly_chat_used,
                    "limit": usage_limit.monthly_chat_limit,
                    "remaining": max(0, usage_limit.monthly_chat_limit - usage_limit.monthly_chat_used)
                        if usage_limit.monthly_chat_limit > 0 else -1
                }
            },
            "role": user.role.value,
            "daily_reset_date": usage_limit.daily_reset_date.isoformat(),
            "monthly_reset_date": usage_limit.monthly_reset_date.isoformat()
        }

# Dependency for rate limiting
def check_rate_limit(service_type: ServiceType):
    """Dependency factory for checking rate limits"""
    def rate_limit_checker(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        RateLimitService.check_usage_limit(current_user, service_type, db)
        return current_user
    return rate_limit_checker