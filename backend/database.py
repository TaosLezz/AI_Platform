from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os

# Database URL from environment variables
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://hieu:123456@localhost/ai_platform_db"
)

# Create SQLAlchemy engine
if DATABASE_URL.startswith("sqlite"):
    # SQLite configuration for development
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    # MySQL/PostgreSQL configuration for production
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
    )

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()