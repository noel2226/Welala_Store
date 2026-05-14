"""
Application configuration management using Pydantic settings.
Supports environment variables and .env file loading.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = "sqlite:///./ecommerce.db"
    
    # API
    api_title: str = "Welala Store API"
    api_version: str = "1.0.0"
    api_description: str = "High-performance ecommerce API for books and general goods"
    
    # Environment
    debug: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
