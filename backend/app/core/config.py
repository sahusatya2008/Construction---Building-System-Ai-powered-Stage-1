"""
Application Configuration Module
================================
Centralized configuration management using Pydantic Settings.
All environment variables and application settings are defined here.
"""

from functools import lru_cache
from typing import List, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Attributes:
        APP_NAME: Application name
        APP_VERSION: Application version
        DEBUG: Debug mode flag
        API_V1_PREFIX: API version 1 prefix
        SECRET_KEY: Secret key for JWT encoding
        ACCESS_TOKEN_EXPIRE_MINUTES: Token expiration time
        DATABASE_URL: PostgreSQL connection URL
        REDIS_URL: Redis connection URL
        CORS_ORIGINS: Allowed CORS origins
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )
    
    # Application Settings
    APP_NAME: str = "ArchAI Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    
    # Security Settings
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database Settings
    DATABASE_URL: str = "sqlite+aiosqlite:///./archai.db"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis Settings
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_EXPIRE_SECONDS: int = 3600
    
    # Celery Settings
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # CORS Settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD_SECONDS: int = 60
    
    # File Upload Settings
    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: List[str] = [".json", ".dxf", ".csv"]
    
    # AI Model Settings
    MODEL_PATH: str = "models/"
    DEVICE: str = "cpu"  # "cuda" for GPU
    
    # Structural Engineering Defaults
    DEFAULT_SAFETY_FACTOR: float = 1.5
    DEFAULT_LOAD_FACTOR: float = 1.4
    CONCRETE_UNIT_WEIGHT: float = 24.0  # kN/m³
    STEEL_UNIT_WEIGHT: float = 78.5  # kN/m³
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings.
    
    Returns:
        Settings: Application settings instance
    """
    return Settings()


settings = get_settings()