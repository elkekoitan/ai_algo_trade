"""
Application settings management using Pydantic.
"""

import os
from functools import lru_cache
from typing import List, Optional, Dict, Any
from pathlib import Path

from dotenv import load_dotenv
from pydantic import field_validator

# .env dosyasını yükle
load_dotenv()

# Pydantic v2 uyumluluğu için
try:
    # Önce yeni pydantic-settings paketini dene
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:
    # Eğer yoksa, Pydantic v1'in BaseSettings'ini fallback olarak kullan
    from pydantic import BaseSettings
    SettingsConfigDict = dict # Eski versiyon için dummy dict


class Settings(BaseSettings):
    """
    Application settings class using Pydantic BaseSettings.
    
    This loads configuration from environment variables and .env files.
    """
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Algo Trade Platform"
    VERSION: str = "2.0.0"
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8080",
    ]
    
    # MetaTrader 5 settings
    MT5_LOGIN: int = int(os.getenv("MT5_LOGIN", 25201110))
    MT5_SERVER: str = os.getenv("MT5_SERVER", "Tickmill-Demo")
    MT5_PASSWORD: str = os.getenv("MT5_PASSWORD", "e|([rXU1IsiM")
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
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Application settings
    APP_NAME: str = "ICT Ultra v2: Algo Forge Edition"
    ENVIRONMENT: str = "development"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    
    # OpenBLAS settings
    USE_OPENBLAS: bool = True
    OPENBLAS_THREADS: int = 4
    
    # Supabase Configuration
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "https://jregdcopqylriziucooi.supabase.co")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpyZWdkY29wcXlscml6aXVjb29pIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEzMzQwOTMsImV4cCI6MjA2NjkxMDA5M30.placeholder")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "service_role_key_placeholder")
    
    @field_validator("BACKEND_CORS_ORIGINS", mode='before')
    @classmethod
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
        elif isinstance(v, (list, str)):
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
    
    # Pydantic v2 için model yapılandırması
    if 'SettingsConfigDict' in globals() and callable(SettingsConfigDict):
        model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="ignore")
    else: # Pydantic v1 için
        class Config:
            case_sensitive = True
            env_file = ".env"
            extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings with caching.
    
    Returns:
        Settings instance
    """
    return Settings()

settings = get_settings() 