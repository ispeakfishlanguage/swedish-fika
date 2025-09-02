from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import asyncpg
from databases import Database
from .config import settings, get_database_url
import logging

logger = logging.getLogger(__name__)

# Database URL
DATABASE_URL = get_database_url()

# SQLAlchemy setup
if "sqlite" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False},
        echo=settings.debug
    )
else:
    engine = create_engine(
        DATABASE_URL,
        poolclass=NullPool,
        echo=settings.debug
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Async database for FastAPI
database = Database(DATABASE_URL)

# Metadata for Alembic
metadata = MetaData()

# Dependency for getting database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Async database dependency
async def get_database():
    return database

# Database connection management
async def connect_to_database():
    """Connect to the database"""
    try:
        await database.connect()
        logger.info("Connected to database successfully")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

async def disconnect_from_database():
    """Disconnect from the database"""
    try:
        await database.disconnect()
        logger.info("Disconnected from database successfully")
    except Exception as e:
        logger.error(f"Failed to disconnect from database: {e}")
        raise

# Database health check
async def check_database_health() -> bool:
    """Check if database is accessible"""
    try:
        await database.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False

# Create tables (for development)
def create_tables():
    """Create database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise