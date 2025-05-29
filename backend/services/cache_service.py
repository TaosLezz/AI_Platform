import redis
import json
import hashlib
import os
from typing import Any, Optional
from datetime import timedelta
import time

class CacheService:
    """Redis-based caching service for AI responses"""
    
    def __init__(self):
        try:
            # Redis connection
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            
            # Test connection
            self.redis_client.ping()
            self.is_available = True
        except Exception as e:
            print(f"Redis connection failed: {e}")
            self.redis_client = None
            self.is_available = False
    
    def _generate_cache_key(self, service_type: str, input_data: Any, parameters: dict = None) -> str:
        """Generate a unique cache key based on service and inputs"""
        # Create a hash of the input data and parameters
        input_str = json.dumps(input_data, sort_keys=True, default=str)
        params_str = json.dumps(parameters or {}, sort_keys=True, default=str)
        
        combined = f"{service_type}:{input_str}:{params_str}"
        cache_key = hashlib.md5(combined.encode()).hexdigest()
        
        return f"ai_cache:{service_type}:{cache_key}"
    
    def get(self, service_type: str, input_data: Any, parameters: dict = None) -> Optional[dict]:
        """Get cached result if available"""
        if not self.is_available:
            return None
        
        try:
            cache_key = self._generate_cache_key(service_type, input_data, parameters)
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                result = json.loads(cached_data)
                # Increment hit counter
                self.redis_client.incr("cache_stats:hits")
                return result
            else:
                # Increment miss counter
                self.redis_client.incr("cache_stats:misses")
                return None
                
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    def set(self, service_type: str, input_data: Any, result: dict, parameters: dict = None, ttl_hours: int = 24):
        """Cache the result with TTL"""
        if not self.is_available:
            return False
        
        try:
            cache_key = self._generate_cache_key(service_type, input_data, parameters)
            
            # Add meta_data to cached result
            cached_result = {
                "result": result,
                "cached_at": str(int(time.time())),
                "service_type": service_type,
                "ttl_hours": ttl_hours
            }
            
            # Set with expiration
            ttl_seconds = ttl_hours * 3600
            self.redis_client.setex(
                cache_key, 
                ttl_seconds, 
                json.dumps(cached_result, default=str)
            )
            
            # Increment cache set counter
            self.redis_client.incr("cache_stats:sets")
            return True
            
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def invalidate_pattern(self, pattern: str):
        """Invalidate cache entries matching a pattern"""
        if not self.is_available:
            return False
        
        try:
            keys = self.redis_client.keys(f"ai_cache:{pattern}*")
            if keys:
                self.redis_client.delete(*keys)
                return len(keys)
            return 0
        except Exception as e:
            print(f"Cache invalidate error: {e}")
            return False
    
    def clear_user_cache(self, user_id: int):
        """Clear all cache entries for a specific user"""
        # Note: This would require storing user_id in cache keys
        # For now, we'll implement a simple pattern-based clear
        return self.invalidate_pattern("*")
    
    def get_cache_stats(self) -> dict:
        """Get cache hit/miss statistics"""
        if not self.is_available:
            return {
                "status": "unavailable",
                "hits": 0,
                "misses": 0,
                "sets": 0,
                "hit_rate": 0
            }
        
        try:
            hits = int(self.redis_client.get("cache_stats:hits") or 0)
            misses = int(self.redis_client.get("cache_stats:misses") or 0)
            sets = int(self.redis_client.get("cache_stats:sets") or 0)
            
            total_requests = hits + misses
            hit_rate = (hits / total_requests * 100) if total_requests > 0 else 0
            
            # Get memory usage info
            info = self.redis_client.info("memory")
            memory_used = info.get("used_memory_human", "N/A")
            
            return {
                "status": "available",
                "hits": hits,
                "misses": misses,
                "sets": sets,
                "hit_rate": round(hit_rate, 2),
                "memory_used": memory_used,
                "total_requests": total_requests
            }
        except Exception as e:
            print(f"Cache stats error: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def reset_stats(self):
        """Reset cache statistics"""
        if not self.is_available:
            return False
        
        try:
            self.redis_client.delete("cache_stats:hits", "cache_stats:misses", "cache_stats:sets")
            return True
        except Exception as e:
            print(f"Cache reset stats error: {e}")
            return False

# Global cache service instance
cache_service = CacheService()

# Cache TTL configurations for different services
CACHE_TTL_CONFIG = {
    "generate": 72,  # 72 hours for image generation
    "classify": 168,  # 1 week for classification
    "detect": 168,   # 1 week for object detection
    "segment": 168,  # 1 week for segmentation
    "chat": 24       # 24 hours for chat (shorter due to context sensitivity)
}