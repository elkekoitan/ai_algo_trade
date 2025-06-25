"""
Application settings management using Pydantic.
"""

import os
from functools import lru_cache
from typing import List, Optional, Dict, Any
from pathlib import Path

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
    VERSION: str = "2.0.0"
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    # MetaTrader 5 settings
    MT5_LOGIN: int = 25201110
    MT5_SERVER: str = "Tickmill-Demo"
    MT5_PASSWORD: str = "e|([rXU1IsiM"
    MT5_TIMEOUT: int = 60000  # milliseconds
    
    # Database settings
    DATABASE_URL: str = "sqlite+aiosqlite:///./ict_ultra_v2.db"
    DATABASE_ECHO: bool = False
    
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
    FORGE_REPOS_PATH: str = "./mql5_forge_repos"
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    
    # Application settings
    APP_NAME: str = "ICT Ultra v2: Algo Forge Edition"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    
    # OpenBLAS settings
    USE_OPENBLAS: bool = True
    OPENBLAS_THREADS: int = 4
    
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