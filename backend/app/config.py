from pydantic_settings import BaseSettings
from typing import Optional, List
import os

class Settings(BaseSettings):
    # Application settings
    app_name: str = "Swedish Fika Register"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    
    # Security
    secret_key: str = "your-secret-key-change-this-in-production"
    access_token_expire_minutes: int = 30
    allowed_hosts: List[str] = ["localhost", "127.0.0.1"]
    
    # Database
    database_url: str = "postgresql://postgres:password@localhost:5432/fika_dev"
    
    # Supabase
    supabase_url: Optional[str] = None
    supabase_anon_key: Optional[str] = None
    supabase_service_role_key: Optional[str] = None
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    cache_expire_minutes: int = 60
    
    # Upstash Redis (for production)
    upstash_redis_url: Optional[str] = None
    upstash_redis_token: Optional[str] = None
    
    # AI Configuration
    openrouter_api_key: Optional[str] = None
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    default_ai_model: str = "anthropic/claude-3-haiku"
    
    # LangChain
    langchain_tracing_v2: bool = False
    langchain_api_key: Optional[str] = None
    
    # Frontend URLs
    frontend_url: str = "http://localhost:3000"
    backend_url: str = "http://localhost:8000"
    
    # File upload settings
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: List[str] = ["image/jpeg", "image/png", "image/webp"]
    
    # Rate limiting
    rate_limit_per_minute: int = 60
    
    # Digital Ocean Spaces (for production)
    do_spaces_key: Optional[str] = None
    do_spaces_secret: Optional[str] = None
    do_spaces_region: str = "fra1"
    do_spaces_bucket: str = "fika-assets"
    
    # Geolocation settings
    default_country: str = "Sweden"
    default_timezone: str = "Europe/Stockholm"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Database configuration for different environments
def get_database_url() -> str:
    if settings.environment == "production" and settings.supabase_url:
        return settings.supabase_url
    return settings.database_url

def get_redis_url() -> str:
    if settings.environment == "production" and settings.upstash_redis_url:
        return settings.upstash_redis_url
    return settings.redis_url

def is_production() -> bool:
    return settings.environment == "production"

def is_development() -> bool:
    return settings.environment == "development"