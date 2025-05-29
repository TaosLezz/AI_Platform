import os
import json
import shutil
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime
import zipfile
import tempfile
from pathlib import Path

from sqlalchemy.orm import Session
from models.custom_models import CustomModel, ModelComparison
from models.database import User
from services.mlflow_service import mlflow_service

class CustomModelService:
    """Service for managing custom model uploads and deployments"""
    
    def __init__(self):
        self.models_directory = Path("./custom_models")
        self.models_directory.mkdir(exist_ok=True)
        
        # Supported model types and frameworks
        self.supported_frameworks = ["pytorch", "tensorflow", "huggingface", "onnx"]
        self.supported_types = ["image", "text", "multimodal", "custom"]
        
        # File size limits (in bytes)
        self.max_model_size = 5 * 1024 * 1024 * 1024  # 5GB
        self.allowed_extensions = {".pt", ".pth", ".pkl", ".bin", ".safetensors", ".onnx"}
    
    def validate_model_file(self, file_path: str, file_size: int) -> Dict[str, Any]:
        """Validate uploaded model file"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check file size
        if file_size > self.max_model_size:
            validation_result["valid"] = False
            validation_result["errors"].append(f"File size ({file_size} bytes) exceeds maximum allowed size ({self.max_model_size} bytes)")
        
        # Check file extension
        file_extension = Path(file_path).suffix.lower()
        if file_extension not in self.allowed_extensions:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Unsupported file extension: {file_extension}")
        
        # Check if file exists and is readable
        if not os.path.exists(file_path):
            validation_result["valid"] = False
            validation_result["errors"].append("File does not exist")
        elif not os.access(file_path, os.R_OK):
            validation_result["valid"] = False
            validation_result["errors"].append("File is not readable")
        
        return validation_result
    
    def upload_model(
        self, 
        db: Session,
        user: User,
        file_path: str,
        name: str,
        description: str,
        model_type: str,
        framework: str = "pytorch",
        config: Dict[str, Any] = None
    ) -> CustomModel:
        """Upload and register a custom model"""
        
        # Validate inputs
        if framework not in self.supported_frameworks:
            raise ValueError(f"Unsupported framework: {framework}")
        
        if model_type not in self.supported_types:
            raise ValueError(f"Unsupported model type: {model_type}")
        
        # Get file info
        file_size = os.path.getsize(file_path)
        
        # Validate file
        validation = self.validate_model_file(file_path, file_size)
        if not validation["valid"]:
            raise ValueError(f"Model validation failed: {', '.join(validation['errors'])}")
        
        # Generate unique model ID and storage path
        model_hash = self._generate_model_hash(file_path)
        model_dir = self.models_directory / f"{user.id}_{model_hash}"
        model_dir.mkdir(exist_ok=True)
        
        # Copy model file to secure location
        model_filename = f"model{Path(file_path).suffix}"
        final_model_path = model_dir / model_filename
        shutil.copy2(file_path, final_model_path)
        
        # Save configuration if provided
        if config:
            config_path = model_dir / "config.json"
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
        
        # Create database record
        custom_model = CustomModel(
            name=name,
            description=description,
            model_type=model_type,
            framework=framework,
            file_path=str(final_model_path),
            file_size=file_size,
            config_json=json.dumps(config) if config else None,
            owner_id=user.id
        )
        
        db.add(custom_model)
        db.commit()
        db.refresh(custom_model)
        
        # Log to MLflow
        mlflow_run_id = mlflow_service.start_run(
            user_id=user.id,
            service_type="model_upload",
            experiment_name="custom-models"
        )
        
        if mlflow_run_id:
            mlflow_service.log_params({
                "model_name": name,
                "model_type": model_type,
                "framework": framework,
                "file_size_mb": file_size / (1024 * 1024)
            })
            mlflow_service.log_input_artifact(config or {}, "config")
            mlflow_service.end_run()
        
        return custom_model
    
    def list_user_models(self, db: Session, user: User, include_public: bool = True) -> List[CustomModel]:
        """List models accessible to a user"""
        query = db.query(CustomModel).filter(CustomModel.is_active == True)
        
        if include_public:
            query = query.filter(
                (CustomModel.owner_id == user.id) | 
                (CustomModel.is_public == True)
            )
        else:
            query = query.filter(CustomModel.owner_id == user.id)
        
        return query.order_by(CustomModel.created_at.desc()).all()
    
    def get_model_by_id(self, db: Session, model_id: int, user: User) -> Optional[CustomModel]:
        """Get a specific model if user has access"""
        model = db.query(CustomModel).filter(CustomModel.id == model_id).first()
        
        if not model:
            return None
        
        # Check access permissions
        if model.owner_id == user.id or model.is_public or user.role in ['ADMIN', 'DEVELOPER']:
            return model
        
        return None
    
    def update_model_performance(
        self, 
        db: Session, 
        model_id: int, 
        inference_time: float, 
        success: bool
    ):
        """Update model performance metrics"""
        model = db.query(CustomModel).filter(CustomModel.id == model_id).first()
        if not model:
            return
        
        # Update metrics
        model.total_requests += 1
        
        if model.avg_inference_time is None:
            model.avg_inference_time = inference_time
        else:
            # Running average
            total_time = model.avg_inference_time * (model.total_requests - 1)
            model.avg_inference_time = (total_time + inference_time) / model.total_requests
        
        if success:
            current_successes = (model.success_rate / 100.0) * (model.total_requests - 1)
            model.success_rate = ((current_successes + 1) / model.total_requests) * 100.0
        else:
            current_successes = (model.success_rate / 100.0) * (model.total_requests - 1)
            model.success_rate = (current_successes / model.total_requests) * 100.0
        
        db.commit()
    
    def delete_model(self, db: Session, model_id: int, user: User) -> bool:
        """Delete a custom model"""
        model = db.query(CustomModel).filter(
            CustomModel.id == model_id,
            CustomModel.owner_id == user.id
        ).first()
        
        if not model:
            return False
        
        # Remove files
        try:
            model_dir = Path(model.file_path).parent
            if model_dir.exists():
                shutil.rmtree(model_dir)
        except Exception as e:
            print(f"Error removing model files: {e}")
        
        # Remove from database
        db.delete(model)
        db.commit()
        
        return True
    
    def create_model_comparison(
        self,
        db: Session,
        user: User,
        name: str,
        model_a_id: int,
        model_b_id: int,
        description: str = None,
        test_dataset_path: str = None,
        metrics: List[str] = None
    ) -> ModelComparison:
        """Create a new model comparison/A-B test"""
        
        # Validate models exist and user has access
        model_a = self.get_model_by_id(db, model_a_id, user)
        model_b = self.get_model_by_id(db, model_b_id, user)
        
        if not model_a or not model_b:
            raise ValueError("One or both models not found or access denied")
        
        if model_a.model_type != model_b.model_type:
            raise ValueError("Cannot compare models of different types")
        
        # Create comparison record
        comparison = ModelComparison(
            name=name,
            description=description,
            model_a_id=model_a_id,
            model_b_id=model_b_id,
            test_dataset_path=test_dataset_path,
            metrics_to_compare=json.dumps(metrics or ["accuracy", "inference_time"]),
            user_id=user.id
        )
        
        db.add(comparison)
        db.commit()
        db.refresh(comparison)
        
        return comparison
    
    def _generate_model_hash(self, file_path: str) -> str:
        """Generate a unique hash for the model file"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()[:16]
    
    def load_model_for_inference(self, model_id: int, db: Session) -> Dict[str, Any]:
        """Load a model for inference (placeholder for actual model loading)"""
        model = db.query(CustomModel).filter(CustomModel.id == model_id).first()
        if not model:
            raise ValueError(f"Model {model_id} not found")
        
        # In a real implementation, this would load the actual model
        # For now, return model meta_data
        return {
            "model_id": model.id,
            "name": model.name,
            "type": model.model_type,
            "framework": model.framework,
            "config": json.loads(model.config_json) if model.config_json else {},
            "file_path": model.file_path
        }

# Global custom model service instance
custom_model_service = CustomModelService()