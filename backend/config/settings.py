import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    # API Configuration
    app_name: str = "AI Showcase Platform"
    app_version: str = "2.0.0"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = int(os.getenv("PORT", 8000))
    
    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # MLflow Configuration
    mlflow_tracking_uri: str = os.getenv("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db")
    mlflow_artifact_root: str = os.getenv("MLFLOW_ARTIFACT_ROOT", "./mlflow-artifacts")
    
    # Database Configuration (for future use)
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    
    # CORS Configuration
    allowed_origins: list = ["*"]  # In production, specify exact origins
    
    # File Upload Configuration
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: list = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
    
    class Config:
        env_file = ".env"

settings = Settings()