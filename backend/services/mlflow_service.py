import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient
import os
import time
import json
from typing import Dict, Any, Optional
from datetime import datetime
import tempfile
import base64

class MLflowService:
    """Service for MLflow experiment tracking and model management"""
    
    def __init__(self):
        # Set MLflow tracking URI
        tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db")
        mlflow.set_tracking_uri(tracking_uri)
        
        # Initialize MLflow client
        self.client = MlflowClient()
        
        # Create default experiment if it doesn't exist
        try:
            self.client.create_experiment("ai-showcase-platform")
        except:
            pass  # Experiment already exists
    
    def start_run(self, user_id: int, service_type: str, experiment_name: str = "ai-showcase-platform") -> str:
        """Start a new MLflow run for tracking"""
        try:
            # Set experiment
            mlflow.set_experiment(experiment_name)
            
            # Start run with user context
            run = mlflow.start_run(
                tags={
                    "user_id": str(user_id),
                    "service_type": service_type,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            return run.info.run_id
        except Exception as e:
            print(f"MLflow start_run error: {e}")
            return None
    
    def log_params(self, params: Dict[str, Any]):
        """Log parameters to current MLflow run"""
        try:
            for key, value in params.items():
                if isinstance(value, (dict, list)):
                    mlflow.log_param(key, json.dumps(value))
                else:
                    mlflow.log_param(key, str(value))
        except Exception as e:
            print(f"MLflow log_params error: {e}")
    
    def log_metrics(self, metrics: Dict[str, float]):
        """Log metrics to current MLflow run"""
        try:
            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    mlflow.log_metric(key, float(value))
        except Exception as e:
            print(f"MLflow log_metrics error: {e}")
    
    def log_input_artifact(self, input_data: Any, artifact_name: str = "input"):
        """Log input data as artifact"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                if isinstance(input_data, str):
                    f.write(input_data)
                else:
                    json.dump(input_data, f, indent=2, default=str)
                f.flush()
                mlflow.log_artifact(f.name, artifact_path=artifact_name)
        except Exception as e:
            print(f"MLflow log_input_artifact error: {e}")
    
    def log_output_artifact(self, output_data: Any, artifact_name: str = "output"):
        """Log output data as artifact"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(output_data, f, indent=2, default=str)
                f.flush()
                mlflow.log_artifact(f.name, artifact_path=artifact_name)
        except Exception as e:
            print(f"MLflow log_output_artifact error: {e}")
    
    def log_image_artifact(self, base64_image: str, artifact_name: str = "image"):
        """Log base64 image as artifact"""
        try:
            # Decode base64 image
            image_data = base64.b64decode(base64_image)
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
                f.write(image_data)
                f.flush()
                mlflow.log_artifact(f.name, artifact_path=artifact_name)
        except Exception as e:
            print(f"MLflow log_image_artifact error: {e}")
    
    def end_run(self, status: str = "FINISHED"):
        """End current MLflow run"""
        try:
            mlflow.end_run(status=status)
        except Exception as e:
            print(f"MLflow end_run error: {e}")
    
    def get_user_experiments(self, user_id: int) -> list:
        """Get experiments for a specific user"""
        try:
            experiments = self.client.search_experiments()
            user_experiments = []
            
            for exp in experiments:
                # Get runs for this experiment
                runs = self.client.search_runs(
                    experiment_ids=[exp.experiment_id],
                    filter_string=f"tags.user_id = '{user_id}'"
                )
                
                if runs:
                    user_experiments.append({
                        "experiment_id": exp.experiment_id,
                        "name": exp.name,
                        "lifecycle_stage": exp.lifecycle_stage,
                        "run_count": len(runs),
                        "last_updated": max([run.info.end_time or run.info.start_time for run in runs]) if runs else None
                    })
            
            return user_experiments
        except Exception as e:
            print(f"MLflow get_user_experiments error: {e}")
            return []
    
    def get_user_runs(self, user_id: int, limit: int = 50) -> list:
        """Get runs for a specific user"""
        try:
            all_runs = self.client.search_runs(
                experiment_ids=[],
                filter_string=f"tags.user_id = '{user_id}'",
                max_results=limit,
                order_by=["start_time DESC"]
            )
            
            runs_data = []
            for run in all_runs:
                runs_data.append({
                    "run_id": run.info.run_id,
                    "experiment_id": run.info.experiment_id,
                    "status": run.info.status,
                    "start_time": run.info.start_time,
                    "end_time": run.info.end_time,
                    "metrics": dict(run.data.metrics),
                    "params": dict(run.data.params),
                    "tags": dict(run.data.tags)
                })
            
            return runs_data
        except Exception as e:
            print(f"MLflow get_user_runs error: {e}")
            return []
    
    def get_run_details(self, run_id: str, user_id: int) -> Optional[dict]:
        """Get detailed information about a specific run"""
        try:
            run = self.client.get_run(run_id)
            
            # Check if user owns this run or is admin
            if run.data.tags.get("user_id") != str(user_id):
                return None
            
            return {
                "run_id": run.info.run_id,
                "experiment_id": run.info.experiment_id,
                "status": run.info.status,
                "start_time": run.info.start_time,
                "end_time": run.info.end_time,
                "metrics": dict(run.data.metrics),
                "params": dict(run.data.params),
                "tags": dict(run.data.tags),
                "artifacts": self._get_run_artifacts(run_id)
            }
        except Exception as e:
            print(f"MLflow get_run_details error: {e}")
            return None
    
    def _get_run_artifacts(self, run_id: str) -> list:
        """Get artifacts for a specific run"""
        try:
            artifacts = self.client.list_artifacts(run_id)
            return [{"path": artifact.path, "is_dir": artifact.is_dir} for artifact in artifacts]
        except Exception as e:
            print(f"MLflow _get_run_artifacts error: {e}")
            return []
    
    def get_aggregate_metrics(self, user_id: int) -> dict:
        """Get aggregated metrics for a user"""
        try:
            runs = self.get_user_runs(user_id, limit=1000)
            
            if not runs:
                return {}
            
            # Calculate aggregates
            total_runs = len(runs)
            successful_runs = len([r for r in runs if r["status"] == "FINISHED"])
            failed_runs = len([r for r in runs if r["status"] == "FAILED"])
            
            # Service type breakdown
            service_counts = {}
            total_processing_time = 0
            processing_times = []
            
            for run in runs:
                service_type = run["tags"].get("service_type", "unknown")
                service_counts[service_type] = service_counts.get(service_type, 0) + 1
                
                if "processing_time" in run["metrics"]:
                    time_ms = run["metrics"]["processing_time"]
                    total_processing_time += time_ms
                    processing_times.append(time_ms)
            
            avg_processing_time = total_processing_time / len(processing_times) if processing_times else 0
            
            return {
                "total_runs": total_runs,
                "successful_runs": successful_runs,
                "failed_runs": failed_runs,
                "success_rate": (successful_runs / total_runs * 100) if total_runs > 0 else 0,
                "service_breakdown": service_counts,
                "avg_processing_time_ms": avg_processing_time,
                "total_processing_time_ms": total_processing_time
            }
        except Exception as e:
            print(f"MLflow get_aggregate_metrics error: {e}")
            return {}

# Global MLflow service instance
mlflow_service = MLflowService()