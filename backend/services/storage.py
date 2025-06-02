from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio

class MemoryStorage:
    """In-memory storage implementation for AI jobs and chat messages"""
    
    def __init__(self):
        self.ai_jobs: Dict[int, Dict[str, Any]] = {}
        self.chat_messages: Dict[int, Dict[str, Any]] = {}
        self.users: Dict[int, Dict[str, Any]] = {}
        self.current_job_id = 1
        self.current_message_id = 1
        self.current_user_id = 1
        
        # Create demo user
        self.users[1] = {
            "id": 1,
            "username": "demo_user",
            "created_at": datetime.utcnow()
        }

    async def create_ai_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new AI job record"""
        job_id = self.current_job_id
        self.current_job_id += 1
        
        job = {
            "id": job_id,
            "user_id": job_data.get("user_id", 1),
            "service_type": job_data["service_type"],
            "prompt": job_data.get("prompt"),
            "image_url": job_data.get("image_url"),
            "status": job_data.get("status", "pending"),
            "result": job_data.get("result"),
            "parameters": job_data.get("parameters", {}),
            "created_at": datetime.utcnow(),
            "completed_at": None
        }
        
        self.ai_jobs[job_id] = job
        return job

    async def get_ai_job(self, job_id: int) -> Optional[Dict[str, Any]]:
        """Get AI job by ID"""
        return self.ai_jobs.get(job_id)

    async def update_ai_job(self, job_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update AI job with new data"""
        if job_id not in self.ai_jobs:
            return None
            
        job = self.ai_jobs[job_id]
        job.update(updates)
        
        if updates.get("status") in ["completed", "failed"]:
            job["completed_at"] = datetime.utcnow()
            
        self.ai_jobs[job_id] = job
        return job

    async def get_ai_jobs_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all AI jobs for a specific user"""
        user_jobs = [
            job for job in self.ai_jobs.values() 
            if job["user_id"] == user_id
        ]
        return sorted(user_jobs, key=lambda x: x["created_at"], reverse=True)

    async def get_recent_ai_jobs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent AI jobs across all users"""
        all_jobs = list(self.ai_jobs.values())
        sorted_jobs = sorted(all_jobs, key=lambda x: x["created_at"], reverse=True)
        return sorted_jobs[:limit]

    async def create_chat_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new chat message"""
        message_id = self.current_message_id
        self.current_message_id += 1
        
        message = {
            "id": message_id,
            "user_id": message_data.get("user_id", 1),
            "role": message_data["role"],
            "content": message_data["content"],
            "timestamp": datetime.utcnow()
        }
        
        self.chat_messages[message_id] = message
        return message

    async def get_chat_history(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get chat history for a specific user"""
        user_messages = [
            msg for msg in self.chat_messages.values() 
            if msg["user_id"] == user_id
        ]
        sorted_messages = sorted(user_messages, key=lambda x: x["timestamp"])
        return sorted_messages[-limit:] if limit else sorted_messages

    async def clear_chat_history(self, user_id: int) -> bool:
        """Clear chat history for a specific user"""
        messages_to_remove = [
            msg_id for msg_id, msg in self.chat_messages.items()
            if msg["user_id"] == user_id
        ]
        
        for msg_id in messages_to_remove:
            del self.chat_messages[msg_id]
            
        return True

    async def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        return {
            "total_jobs": len(self.ai_jobs),
            "total_messages": len(self.chat_messages),
            "total_users": len(self.users),
            "jobs_by_status": self._count_jobs_by_status(),
            "jobs_by_service": self._count_jobs_by_service()
        }

    def _count_jobs_by_status(self) -> Dict[str, int]:
        """Count jobs by status"""
        status_counts = {}
        for job in self.ai_jobs.values():
            status = job["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        return status_counts

    def _count_jobs_by_service(self) -> Dict[str, int]:
        """Count jobs by service type"""
        service_counts = {}
        for job in self.ai_jobs.values():
            service = job["service_type"]
            service_counts[service] = service_counts.get(service, 0) + 1
        return service_counts