from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class CustomModel(Base):
    """Custom model uploads and management"""
    __tablename__ = "custom_models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    model_type = Column(String(100), nullable=False)  # 'image', 'text', 'multimodal'
    framework = Column(String(50), default='pytorch')
    version = Column(String(50), default='1.0.0')
    
    # Model file information
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    config_json = Column(Text)  # Model configuration as JSON
    
    # Ownership and access
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_public = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Performance metrics
    avg_inference_time = Column(Float)
    total_requests = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deployed_at = Column(DateTime)
    
    # Relationships
    owner = relationship("User", back_populates="custom_models")
    batch_jobs = relationship("BatchJob", back_populates="custom_model")
    comparisons = relationship("ModelComparison", back_populates="model")

class BatchJob(Base):
    """Batch processing jobs"""
    __tablename__ = "batch_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    job_type = Column(String(100), nullable=False)  # 'bulk_classify', 'bulk_generate', etc.
    
    # Job configuration
    input_files = Column(Text)  # JSON array of file paths
    parameters = Column(Text)   # JSON parameters
    output_format = Column(String(50), default='json')
    
    # Processing details
    total_items = Column(Integer, default=0)
    processed_items = Column(Integer, default=0)
    failed_items = Column(Integer, default=0)
    
    # Status and results
    status = Column(String(50), default='pending')  # pending, processing, completed, failed
    progress_percentage = Column(Float, default=0.0)
    result_file_path = Column(String(500))
    error_message = Column(Text)
    
    # Resource usage
    estimated_duration = Column(Integer)  # seconds
    actual_duration = Column(Integer)     # seconds
    memory_used = Column(Float)           # MB
    
    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    custom_model_id = Column(Integer, ForeignKey("custom_models.id"))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="batch_jobs")
    custom_model = relationship("CustomModel", back_populates="batch_jobs")

class ModelComparison(Base):
    """A/B testing and model comparisons"""
    __tablename__ = "model_comparisons"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Comparison setup
    model_a_id = Column(Integer, ForeignKey("custom_models.id"), nullable=False)
    model_b_id = Column(Integer, ForeignKey("custom_models.id"), nullable=False)
    test_dataset_path = Column(String(500))
    metrics_to_compare = Column(Text)  # JSON array of metrics
    
    # Results
    model_a_results = Column(Text)  # JSON results
    model_b_results = Column(Text)  # JSON results
    winner_model_id = Column(Integer, ForeignKey("custom_models.id"))
    confidence_score = Column(Float)
    
    # Status
    status = Column(String(50), default='pending')  # pending, running, completed, failed
    progress_percentage = Column(Float, default=0.0)
    
    # Ownership
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User")
    model = relationship("CustomModel", back_populates="comparisons", foreign_keys=[model_a_id])
    model_a = relationship("CustomModel", foreign_keys=[model_a_id])
    model_b = relationship("CustomModel", foreign_keys=[model_b_id])
    winner_model = relationship("CustomModel", foreign_keys=[winner_model_id])

class PlatformAnalytics(Base):
    """Platform-wide analytics and metrics"""
    __tablename__ = "platform_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False)
    
    # User metrics
    total_users = Column(Integer, default=0)
    active_users = Column(Integer, default=0)
    new_users = Column(Integer, default=0)
    
    # Usage metrics
    total_requests = Column(Integer, default=0)
    successful_requests = Column(Integer, default=0)
    failed_requests = Column(Integer, default=0)
    
    # Service breakdown
    generate_requests = Column(Integer, default=0)
    classify_requests = Column(Integer, default=0)
    detect_requests = Column(Integer, default=0)
    segment_requests = Column(Integer, default=0)
    chat_requests = Column(Integer, default=0)
    custom_model_requests = Column(Integer, default=0)
    
    # Performance metrics
    avg_response_time = Column(Float, default=0.0)
    total_processing_time = Column(Float, default=0.0)
    
    # Resource metrics
    peak_cpu_usage = Column(Float, default=0.0)
    peak_memory_usage = Column(Float, default=0.0)
    storage_used = Column(Float, default=0.0)  # GB
    
    # Financial metrics (if applicable)
    total_api_cost = Column(Float, default=0.0)
    revenue_generated = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class SystemConfiguration(Base):
    """System configuration and settings"""
    __tablename__ = "system_configurations"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), unique=True, nullable=False)
    value = Column(Text, nullable=False)
    description = Column(Text)
    category = Column(String(100), default='general')
    
    # Validation and constraints
    data_type = Column(String(50), default='string')  # string, integer, float, boolean, json
    validation_rules = Column(Text)  # JSON validation rules
    
    # Management
    is_public = Column(Boolean, default=False)  # Can non-admin users see this?
    requires_restart = Column(Boolean, default=False)  # Requires app restart to take effect?
    
    # Audit
    updated_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    updated_by_user = relationship("User")