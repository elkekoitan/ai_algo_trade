"""
Application settings management using Pydantic.
"""

import os
from functools import lru_cache
from typing import List, Optional, Dict, Any

from pydantic_settings import BaseSettings
from pydantic import validator, Field


class Settings(BaseSettings):
    """
    Application settings class using Pydantic BaseSettings.
    
    This loads configuration from environment variables and .env files.
    """
    # API settings
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "ICT Ultra v2"
    VERSION: str = "1.0.0"
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # MetaTrader 5 settings
    MT5_LOGIN: int = 25201110
    MT5_SERVER: str = "Tickmill-Demo"
    MT5_PASSWORD: Optional[str] = None
    MT5_TIMEOUT: int = 60000  # milliseconds
    
    # Database settings
    DATABASE_URL: Optional[str] = None
    
    # Redis settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    
    # Security settings
    SECRET_KEY: str = "supersecretkey"  # Change in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # MQL5 Algo Forge settings
    FORGE_REPOS_PATH: str = "../mql5_forge_repos"
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Any) -> List[str]:
        """
        Parse CORS origins from string or list.
        
        Args:
            v: String or list of origins
            
        Returns:
            List of CORS origins
        """
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        if isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    @property
    def redis_url(self) -> str:
        """
        Construct Redis URL from settings.
        
        Returns:
            Redis URL string
        """
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings with caching.
    
    Returns:
        Settings instance
    """
    return Settings() 