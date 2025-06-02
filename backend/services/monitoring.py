import time
import psutil
import functools
from typing import Dict, Any, Callable
from datetime import datetime
import threading
import os

class PerformanceMonitor:
    """Performance monitoring service for tracking system and request metrics"""
    
    def __init__(self):
        self.metrics = {
            "request_count": 0,
            "total_processing_time": 0,
            "error_count": 0,
            "last_updated": datetime.utcnow()
        }
        self.lock = threading.Lock()
    
    def track_request(self, func: Callable) -> Callable:
        """Decorator to track request performance metrics"""
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            start_memory = psutil.Process(os.getpid()).memory_info().rss
            
            try:
                # Execute the function
                result = await func(*args, **kwargs)
                
                # Calculate metrics
                end_time = time.time()
                processing_time = (end_time - start_time) * 1000  # Convert to milliseconds
                end_memory = psutil.Process(os.getpid()).memory_info().rss
                memory_used = end_memory - start_memory
                
                # Update metrics
                with self.lock:
                    self.metrics["request_count"] += 1
                    self.metrics["total_processing_time"] += processing_time
                    self.metrics["last_updated"] = datetime.utcnow()
                
                # Add performance data to result
                if isinstance(result, dict):
                    result["performance"] = {
                        "processing_time_ms": processing_time,
                        "memory_used_bytes": memory_used,
                        "cpu_percent": psutil.cpu_percent()
                    }
                
                return result
                
            except Exception as e:
                # Track error
                with self.lock:
                    self.metrics["error_count"] += 1
                    self.metrics["last_updated"] = datetime.utcnow()
                raise e
                
        return wrapper
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system performance metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available = memory.available
            memory_total = memory.total
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_free = disk.free
            disk_total = disk.total
            
            # Process metrics
            process = psutil.Process(os.getpid())
            process_memory = process.memory_info().rss
            process_cpu = process.cpu_percent()
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "cpu": {
                    "percent": cpu_percent,
                    "count": cpu_count,
                    "process_percent": process_cpu
                },
                "memory": {
                    "percent": memory_percent,
                    "available_bytes": memory_available,
                    "total_bytes": memory_total,
                    "process_bytes": process_memory
                },
                "disk": {
                    "percent": disk_percent,
                    "free_bytes": disk_free,
                    "total_bytes": disk_total
                },
                "requests": {
                    "total_count": self.metrics["request_count"],
                    "error_count": self.metrics["error_count"],
                    "success_count": self.metrics["request_count"] - self.metrics["error_count"],
                    "avg_processing_time_ms": (
                        self.metrics["total_processing_time"] / self.metrics["request_count"]
                        if self.metrics["request_count"] > 0 else 0
                    ),
                    "error_rate": (
                        self.metrics["error_count"] / self.metrics["request_count"] * 100
                        if self.metrics["request_count"] > 0 else 0
                    )
                }
            }
        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall system health status"""
        try:
            metrics = self.get_system_metrics()
            
            # Determine health status
            cpu_healthy = metrics["cpu"]["percent"] < 80
            memory_healthy = metrics["memory"]["percent"] < 80
            disk_healthy = metrics["disk"]["percent"] < 90
            error_rate_healthy = metrics["requests"]["error_rate"] < 5
            
            overall_healthy = all([cpu_healthy, memory_healthy, disk_healthy, error_rate_healthy])
            
            status = "healthy" if overall_healthy else "warning"
            if metrics["cpu"]["percent"] > 90 or metrics["memory"]["percent"] > 90:
                status = "critical"
            
            return {
                "status": status,
                "healthy": overall_healthy,
                "checks": {
                    "cpu": {"healthy": cpu_healthy, "value": metrics["cpu"]["percent"]},
                    "memory": {"healthy": memory_healthy, "value": metrics["memory"]["percent"]},
                    "disk": {"healthy": disk_healthy, "value": metrics["disk"]["percent"]},
                    "error_rate": {"healthy": error_rate_healthy, "value": metrics["requests"]["error_rate"]}
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def reset_metrics(self):
        """Reset all metrics counters"""
        with self.lock:
            self.metrics = {
                "request_count": 0,
                "total_processing_time": 0,
                "error_count": 0,
                "last_updated": datetime.utcnow()
            }

# Global performance monitor instance
performance_monitor = PerformanceMonitor()