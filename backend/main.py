"""
ICT Ultra v2: Algo Forge Edition - Main FastAPI Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from backend.core.config.settings import settings
from backend.core.logger import logger
from backend.core.database import init_db
from backend.modules.mt5_integration import MT5Service, MT5Config
from backend.api.v1 import api_router

# Global MT5 service instance
mt5_service = None

async def get_mt5_service() -> MT5Service:
    """Get the global MT5 service instance."""
    return mt5_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting ICT Ultra v2: Algo Forge Edition...")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Initialize MT5 service
    global mt5_service
    mt5_config = MT5Config(
        login=settings.MT5_LOGIN,
        password=settings.MT5_PASSWORD,
        server=settings.MT5_SERVER
    )
    mt5_service = MT5Service(mt5_config)
    
    # Connect to MT5
    connected = await mt5_service.connect()
    if connected:
        logger.info("MT5 connection established")
    else:
        logger.error("Failed to connect to MT5")
    
    yield
    
    # Shutdown
    logger.info("Shutting down ICT Ultra v2...")
    
    # Disconnect from MT5
    if mt5_service:
        await mt5_service.disconnect()
    
    logger.info("Shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="ICT Ultra v2: Algo Forge Edition",
    description="Advanced algorithmic trading platform with MT5 integration and ICT concepts",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(api_router)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    mt5_connected = mt5_service.is_connected if mt5_service else False
    
    return {
        "status": "healthy",
        "version": "2.0.0",
        "mt5_connected": mt5_connected,
        "environment": settings.ENVIRONMENT
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with system information."""
    mt5_connected = mt5_service.is_connected if mt5_service else False
    account_info = None
    
    if mt5_connected and mt5_service._account_info:
        account_info = {
            "login": mt5_service._account_info.login,
            "balance": mt5_service._account_info.balance,
            "server": mt5_service._account_info.server
        }
    
    return {
        "name": "ICT Ultra v2: Algo Forge Edition",
        "version": "2.0.0",
        "status": "operational",
        "mt5_connected": mt5_connected,
        "account": account_info,
        "api_docs": "/docs",
        "health_check": "/health"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    ) 