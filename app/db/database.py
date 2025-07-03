from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import text
import os
from dotenv import load_dotenv

load_dotenv()

# Get database URL from environment variable or use a default for development
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/model_providers")


# ------------------------------------------------------------------
# Engine & sessionmaker
# ------------------------------------------------------------------
engine = create_engine(
    DATABASE_URL,
    pool_size=20,        # steady connections kept open
    max_overflow=20,     # temporary bursts
    pool_timeout=30,     # seconds to wait for a free conn
    pool_pre_ping=True,  # validate before checkout
    pool_recycle=1800,   # recycle every 30 min (set 0 to disable)
    echo=False,          # flip to True to debug pool activity
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for SQLAlchemy models
Base = declarative_base()

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
