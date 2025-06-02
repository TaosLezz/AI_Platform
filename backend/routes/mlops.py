from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from database import get_db
from models.database import User
from auth.security import get_current_active_user
from services.mlflow_service import mlflow_service
from services.cache_service import cache_service
from services.monitoring import performance_monitor

router = APIRouter()

class ExperimentResponse(BaseModel):
    experiment_id: str
    name: str
    lifecycle_stage: str
    run_count: int
    last_updated: Optional[int] = None

class RunResponse(BaseModel):
    run_id: str
    experiment_id: str
    status: str
    start_time: int
    end_time: Optional[int]
    metrics: Dict[str, float]
    params: Dict[str, str]
    tags: Dict[str, str]

class RunDetailResponse(BaseModel):
    run_id: str
    experiment_id: str
    status: str
    start_time: int
    end_time: Optional[int]
    metrics: Dict[str, float]
    params: Dict[str, str]
    tags: Dict[str, str]
    artifacts: List[Dict[str, Any]]

class MetricsDashboardResponse(BaseModel):
    total_runs: int
    successful_runs: int
    failed_runs: int
    success_rate: float
    service_breakdown: Dict[str, int]
    avg_processing_time_ms: float
    total_processing_time_ms: float

class PerformanceStatsResponse(BaseModel):
    timestamp: str
    cpu: Dict[str, Any]
    memory: Dict[str, Any]
    disk: Dict[str, Any]
    requests: Dict[str, Any]

class CacheStatsResponse(BaseModel):
    status: str
    hits: int
    misses: int
    sets: int
    hit_rate: float
    memory_used: str
    total_requests: int

@router.get("/experiments", response_model=List[ExperimentResponse])
async def get_user_experiments(
    current_user: User = Depends(get_current_active_user)
):
    """Get user's MLflow experiments"""
    try:
        experiments = mlflow_service.get_user_experiments(current_user.id)
        return [ExperimentResponse(**exp) for exp in experiments]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch experiments: {str(e)}"
        )

@router.get("/runs", response_model=List[RunResponse])
async def get_user_runs(
    limit: int = 50,
    current_user: User = Depends(get_current_active_user)
):
    """Get user's MLflow runs"""
    try:
        runs = mlflow_service.get_user_runs(current_user.id, limit)
        return [RunResponse(**run) for run in runs]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch runs: {str(e)}"
        )

@router.get("/runs/{run_id}", response_model=RunDetailResponse)
async def get_run_details(
    run_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get specific run details"""
    try:
        run_details = mlflow_service.get_run_details(run_id, current_user.id)
        
        if not run_details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Run not found or access denied"
            )
        
        return RunDetailResponse(**run_details)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch run details: {str(e)}"
        )

@router.get("/metrics/dashboard", response_model=MetricsDashboardResponse)
async def get_metrics_dashboard(
    current_user: User = Depends(get_current_active_user)
):
    """Get aggregated metrics for user's dashboard"""
    try:
        metrics = mlflow_service.get_aggregate_metrics(current_user.id)
        
        if not metrics:
            # Return empty metrics for new users
            metrics = {
                "total_runs": 0,
                "successful_runs": 0,
                "failed_runs": 0,
                "success_rate": 0,
                "service_breakdown": {},
                "avg_processing_time_ms": 0,
                "total_processing_time_ms": 0
            }
        
        return MetricsDashboardResponse(**metrics)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch dashboard metrics: {str(e)}"
        )

@router.get("/performance/stats", response_model=PerformanceStatsResponse)
async def get_performance_stats(
    current_user: User = Depends(get_current_active_user)
):
    """Get system performance statistics"""
    try:
        stats = performance_monitor.get_system_metrics()
        return PerformanceStatsResponse(**stats)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch performance stats: {str(e)}"
        )

@router.get("/performance/health")
async def get_health_status(
    current_user: User = Depends(get_current_active_user)
):
    """Get system health status"""
    try:
        health = performance_monitor.get_health_status()
        return health
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch health status: {str(e)}"
        )

@router.get("/cache/stats", response_model=CacheStatsResponse)
async def get_cache_stats(
    current_user: User = Depends(get_current_active_user)
):
    """Get cache statistics"""
    try:
        stats = cache_service.get_cache_stats()
        return CacheStatsResponse(**stats)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch cache stats: {str(e)}"
        )

@router.post("/cache/clear")
async def clear_user_cache(
    current_user: User = Depends(get_current_active_user)
):
    """Clear user's cache entries"""
    try:
        cleared_count = cache_service.clear_user_cache(current_user.id)
        return {
            "message": "Cache cleared successfully",
            "cleared_entries": cleared_count
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear cache: {str(e)}"
        )