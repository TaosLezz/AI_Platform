from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, Enum, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

Base = declarative_base()

class UserRole(str, enum.Enum):
    FREE = "FREE"
    PREMIUM = "PREMIUM"
    DEVELOPER = "DEVELOPER"
    ADMIN = "ADMIN"

class ServiceType(str, enum.Enum):
    GENERATE = "generate"
    CLASSIFY = "classify"
    DETECT = "detect"
    SEGMENT = "segment"
    CHAT = "chat"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255))
    hashed_password = Column(String(255))
    role = Column(Enum(UserRole), default=UserRole.FREE)
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    
    # OAuth fields
    google_id = Column(String(255), unique=True, nullable=True)
    github_id = Column(String(255), unique=True, nullable=True)
    avatar_url = Column(String(500))
    
    # Profile fields
    bio = Column(Text)
    company = Column(String(255))
    location = Column(String(255))
    website = Column(String(500))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Relationships
    ai_requests = relationship("AIRequest", back_populates="user")
    chat_sessions = relationship("ChatSession", back_populates="user")
    usage_limits = relationship("UsageLimit", back_populates="user", uselist=False)

class AIRequest(Base):
    __tablename__ = "ai_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    service_type = Column(Enum(ServiceType), nullable=False)
    prompt = Column(Text)
    parameters = Column(JSON)
    result = Column(JSON)
    status = Column(String(50), default="pending")
    processing_time = Column(Float)
    error_message = Column(Text)
    
    # File handling
    input_file_url = Column(String(500))
    output_file_url = Column(String(500))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="ai_requests")

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255))
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    meta_data = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")

class UsageLimit(Base):
    __tablename__ = "usage_limits"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Daily limits
    daily_generate_limit = Column(Integer, default=5)
    daily_classify_limit = Column(Integer, default=20)
    daily_detect_limit = Column(Integer, default=20)
    daily_segment_limit = Column(Integer, default=10)
    daily_chat_limit = Column(Integer, default=50)
    
    # Monthly limits
    monthly_generate_limit = Column(Integer, default=100)
    monthly_classify_limit = Column(Integer, default=500)
    monthly_detect_limit = Column(Integer, default=500)
    monthly_segment_limit = Column(Integer, default=200)
    monthly_chat_limit = Column(Integer, default=1000)
    
    # Current usage
    daily_generate_used = Column(Integer, default=0)
    daily_classify_used = Column(Integer, default=0)
    daily_detect_used = Column(Integer, default=0)
    daily_segment_used = Column(Integer, default=0)
    daily_chat_used = Column(Integer, default=0)
    
    monthly_generate_used = Column(Integer, default=0)
    monthly_classify_used = Column(Integer, default=0)
    monthly_detect_used = Column(Integer, default=0)
    monthly_segment_used = Column(Integer, default=0)
    monthly_chat_used = Column(Integer, default=0)
    
    # Reset timestamps
    daily_reset_date = Column(DateTime(timezone=True), server_default=func.now())
    monthly_reset_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="usage_limits")

# Role-based limits mapping
ROLE_LIMITS = {
    UserRole.FREE: {
        "daily_generate": 5,
        "daily_classify": 20,
        "daily_detect": 20,
        "daily_segment": 10,
        "daily_chat": 50,
        "monthly_generate": 100,
        "monthly_classify": 500,
        "monthly_detect": 500,
        "monthly_segment": 200,
        "monthly_chat": 1000,
    },
    UserRole.PREMIUM: {
        "daily_generate": 50,
        "daily_classify": 200,
        "daily_detect": 200,
        "daily_segment": 100,
        "daily_chat": 500,
        "monthly_generate": 1000,
        "monthly_classify": 5000,
        "monthly_detect": 5000,
        "monthly_segment": 2000,
        "monthly_chat": 10000,
    },
    UserRole.DEVELOPER: {
        "daily_generate": 200,
        "daily_classify": 1000,
        "daily_detect": 1000,
        "daily_segment": 500,
        "daily_chat": 2000,
        "monthly_generate": 5000,
        "monthly_classify": 25000,
        "monthly_detect": 25000,
        "monthly_segment": 10000,
        "monthly_chat": 50000,
    },
    UserRole.ADMIN: {
        "daily_generate": -1,  # -1 means unlimited
        "daily_classify": -1,
        "daily_detect": -1,
        "daily_segment": -1,
        "daily_chat": -1,
        "monthly_generate": -1,
        "monthly_classify": -1,
        "monthly_detect": -1,
        "monthly_segment": -1,
        "monthly_chat": -1,
    }
}