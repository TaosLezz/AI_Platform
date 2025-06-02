import os
import json
import asyncio
import zipfile
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import uuid

from sqlalchemy.orm import Session
from models.custom_models import BatchJob
from models.database import User
from services.mlflow_service import mlflow_service
from services.ai_services import AIServiceManager

class BatchProcessingService:
    """Service for handling batch AI processing jobs"""
    
    def __init__(self):
        self.batch_directory = Path("./batch_jobs")
        self.batch_directory.mkdir(exist_ok=True)
        
        # Job status tracking
        self.active_jobs = {}
        
        # Supported batch operations
        self.supported_operations = [
            "bulk_classify",
            "bulk_generate", 
            "bulk_detect",
            "bulk_segment",
            "bulk_chat",
            "custom_model_inference"
        ]
        
        # File processing limits
        self.max_files_per_job = 1000
        self.max_total_size = 1 * 1024 * 1024 * 1024  # 1GB
        self.supported_formats = {".jpg", ".jpeg", ".png", ".webp", ".txt", ".csv", ".json"}
    
    def create_batch_job(
        self,
        db: Session,
        user: User,
        name: str,
        job_type: str,
        input_files: List[str],
        parameters: Dict[str, Any],
        output_format: str = "json"
    ) -> BatchJob:
        """Create a new batch processing job"""
        
        if job_type not in self.supported_operations:
            raise ValueError(f"Unsupported job type: {job_type}")
        
        if len(input_files) > self.max_files_per_job:
            raise ValueError(f"Too many files. Maximum allowed: {self.max_files_per_job}")
        
        # Validate input files
        total_size = 0
        valid_files = []
        
        for file_path in input_files:
            if not os.path.exists(file_path):
                continue
            
            file_size = os.path.getsize(file_path)
            total_size += file_size
            
            if total_size > self.max_total_size:
                raise ValueError(f"Total file size exceeds limit: {self.max_total_size} bytes")
            
            file_ext = Path(file_path).suffix.lower()
            if file_ext in self.supported_formats:
                valid_files.append(file_path)
        
        if not valid_files:
            raise ValueError("No valid input files found")
        
        # Create job directory
        job_id = str(uuid.uuid4())
        job_dir = self.batch_directory / job_id
        job_dir.mkdir(exist_ok=True)
        
        # Estimate processing time
        estimated_duration = self._estimate_processing_time(job_type, len(valid_files))
        
        # Create database record
        batch_job = BatchJob(
            name=name,
            job_type=job_type,
            input_files=json.dumps(valid_files),
            parameters=json.dumps(parameters),
            output_format=output_format,
            total_items=len(valid_files),
            estimated_duration=estimated_duration,
            user_id=user.id
        )
        
        db.add(batch_job)
        db.commit()
        db.refresh(batch_job)
        
        return batch_job
    
    async def process_batch_job(self, db: Session, job_id: int):
        """Process a batch job asynchronously"""
        
        job = db.query(BatchJob).filter(BatchJob.id == job_id).first()
        if not job:
            return
        
        try:
            # Update job status
            job.status = "processing"
            job.started_at = datetime.utcnow()
            job.progress_percentage = 0.0
            db.commit()
            
            # Start MLflow tracking
            mlflow_run_id = mlflow_service.start_run(
                user_id=job.user_id,
                service_type=f"batch_{job.job_type}",
                experiment_name="batch-processing"
            )
            
            if mlflow_run_id:
                mlflow_service.log_params({
                    "job_type": job.job_type,
                    "total_items": job.total_items,
                    "parameters": job.parameters
                })
            
            # Process files
            input_files = json.loads(job.input_files)
            parameters = json.loads(job.parameters) if job.parameters else {}
            results = []
            
            ai_service = AIServiceManager()
            
            for i, file_path in enumerate(input_files):
                try:
                    # Process individual file
                    result = await self._process_single_file(
                        ai_service, 
                        job.job_type, 
                        file_path, 
                        parameters
                    )
                    
                    results.append({
                        "file": file_path,
                        "success": True,
                        "result": result
                    })
                    
                    job.processed_items += 1
                    
                except Exception as e:
                    results.append({
                        "file": file_path,
                        "success": False,
                        "error": str(e)
                    })
                    
                    job.failed_items += 1
                
                # Update progress
                job.progress_percentage = (i + 1) / len(input_files) * 100
                db.commit()
                
                # Small delay to prevent overwhelming the system
                await asyncio.sleep(0.1)
            
            # Save results
            job_dir = self.batch_directory / str(job.id)
            results_file = job_dir / f"results.{job.output_format}"
            
            if job.output_format == "json":
                with open(results_file, 'w') as f:
                    json.dump(results, f, indent=2, default=str)
            elif job.output_format == "csv":
                # Convert to CSV format
                self._save_results_as_csv(results, results_file)
            
            # Update job completion
            job.status = "completed"
            job.completed_at = datetime.utcnow()
            job.result_file_path = str(results_file)
            job.actual_duration = int((job.completed_at - job.started_at).total_seconds())
            
            # Log final metrics to MLflow
            if mlflow_run_id:
                mlflow_service.log_metrics({
                    "processed_items": job.processed_items,
                    "failed_items": job.failed_items,
                    "success_rate": (job.processed_items / job.total_items) * 100,
                    "processing_time_seconds": job.actual_duration
                })
                mlflow_service.log_output_artifact(results, "batch_results")
                mlflow_service.end_run()
            
            db.commit()
            
        except Exception as e:
            # Handle job failure
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            
            if mlflow_run_id:
                mlflow_service.end_run(status="FAILED")
            
            db.commit()
    
    async def _process_single_file(
        self, 
        ai_service: AIServiceManager, 
        job_type: str, 
        file_path: str, 
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process a single file based on job type"""
        
        if job_type == "bulk_classify":
            with open(file_path, 'rb') as f:
                file_content = f.read()
            return await ai_service.classify_image(file_content, parameters)
        
        elif job_type == "bulk_detect":
            with open(file_path, 'rb') as f:
                file_content = f.read()
            return await ai_service.detect_objects(file_content, parameters)
        
        elif job_type == "bulk_segment":
            with open(file_path, 'rb') as f:
                file_content = f.read()
            return await ai_service.segment_image(file_content, parameters)
        
        elif job_type == "bulk_generate":
            # For text-based generation
            if file_path.endswith('.txt'):
                with open(file_path, 'r') as f:
                    prompt = f.read().strip()
                return await ai_service.generate_image(prompt, parameters)
        
        elif job_type == "bulk_chat":
            if file_path.endswith('.txt'):
                with open(file_path, 'r') as f:
                    message = f.read().strip()
                return await ai_service.chat_completion(message)
        
        else:
            raise ValueError(f"Unsupported job type: {job_type}")
    
    def get_job_status(self, db: Session, job_id: int, user: User) -> Optional[BatchJob]:
        """Get the status of a batch job"""
        return db.query(BatchJob).filter(
            BatchJob.id == job_id,
            BatchJob.user_id == user.id
        ).first()
    
    def list_user_jobs(
        self, 
        db: Session, 
        user: User, 
        limit: int = 50,
        status_filter: str = None
    ) -> List[BatchJob]:
        """List batch jobs for a user"""
        query = db.query(BatchJob).filter(BatchJob.user_id == user.id)
        
        if status_filter:
            query = query.filter(BatchJob.status == status_filter)
        
        return query.order_by(BatchJob.created_at.desc()).limit(limit).all()
    
    def download_results(self, db: Session, job_id: int, user: User) -> Optional[str]:
        """Get the path to download job results"""
        job = db.query(BatchJob).filter(
            BatchJob.id == job_id,
            BatchJob.user_id == user.id,
            BatchJob.status == "completed"
        ).first()
        
        if not job or not job.result_file_path:
            return None
        
        if os.path.exists(job.result_file_path):
            return job.result_file_path
        
        return None
    
    def delete_job(self, db: Session, job_id: int, user: User) -> bool:
        """Delete a batch job and its files"""
        job = db.query(BatchJob).filter(
            BatchJob.id == job_id,
            BatchJob.user_id == user.id
        ).first()
        
        if not job:
            return False
        
        # Remove job files
        job_dir = self.batch_directory / str(job.id)
        if job_dir.exists():
            import shutil
            shutil.rmtree(job_dir)
        
        # Remove from database
        db.delete(job)
        db.commit()
        
        return True
    
    def _estimate_processing_time(self, job_type: str, file_count: int) -> int:
        """Estimate processing time in seconds"""
        # Base time per file (in seconds)
        base_times = {
            "bulk_classify": 2,
            "bulk_generate": 10,
            "bulk_detect": 5,
            "bulk_segment": 8,
            "bulk_chat": 1,
            "custom_model_inference": 3
        }
        
        base_time = base_times.get(job_type, 3)
        return base_time * file_count
    
    def _save_results_as_csv(self, results: List[Dict], output_path: Path):
        """Save results in CSV format"""
        import csv
        
        with open(output_path, 'w', newline='') as csvfile:
            if not results:
                return
            
            fieldnames = ['file', 'success']
            
            # Get additional fields from first successful result
            for result in results:
                if result.get('success') and 'result' in result:
                    result_data = result['result']
                    if isinstance(result_data, dict):
                        fieldnames.extend(result_data.keys())
                    break
            
            if 'error' not in fieldnames:
                fieldnames.append('error')
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in results:
                row = {
                    'file': result['file'],
                    'success': result['success']
                }
                
                if result['success'] and 'result' in result:
                    result_data = result['result']
                    if isinstance(result_data, dict):
                        row.update(result_data)
                else:
                    row['error'] = result.get('error', '')
                
                writer.writerow(row)

# Global batch processing service instance
batch_service = BatchProcessingService()