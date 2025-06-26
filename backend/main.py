"""
ICT Ultra v2: Algo Forge Edition - Main FastAPI Application
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging

from backend.core.config.settings import settings
from backend.core.logger import logger
from backend.core.database import init_db
from backend.modules.mt5_integration import MT5Service, MT5Config
from backend.api.v1 import api_router

# Import API routers
from api.v1.signals import router as signals_router
from api.v1.market_data import router as market_data_router
from api.v1.trading import router as trading_router
from modules.auto_trader.router import router as auto_trader_router
from modules.performance.router import router as performance_router

# Global MT5 service instance
mt5_service = None

async def get_mt5_service() -> MT5Service:
    """Get the global MT5 service instance."""
    return mt5_service


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
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
        
        logger.info("ICT Ultra v2 platform started successfully")
        
    except Exception as e:
        logger.error(f"Startup error: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    try:
        if mt5_service.is_connected():
            await mt5_service.disconnect()
            logger.info("MT5 connection closed")
        
        logger.info("ICT Ultra v2 platform shutdown complete")
        
    except Exception as e:
        logger.error(f"Shutdown error: {e}")

# Create FastAPI application
app = FastAPI(
    title="ICT Ultra v2: Algo Forge Edition",
    description="Advanced algorithmic trading platform with MT5 integration and ICT concepts",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
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
app.include_router(signals_router, prefix="/api/v1")
app.include_router(market_data_router, prefix="/api/v1")
app.include_router(trading_router, prefix="/api/v1")
app.include_router(auto_trader_router, prefix="/api/v1")
app.include_router(performance_router, prefix="/api/v1")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        mt5_status = mt5_service.is_connected
        account_info = None
        
        if mt5_status:
            account_info = await mt5_service.get_account_info()
        
        return {
            "status": "healthy",
            "mt5_connected": mt5_status,
            "account_info": account_info,
            "timestamp": "2024-01-01T00:00:00Z"  # Would use actual timestamp
        }
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": "2024-01-01T00:00:00Z"
            }
        )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with platform information"""
    return {
        "message": "ICT Ultra v2: Algo Forge Edition",
        "version": "2.0.0",
        "status": "operational",
        "mt5_connected": mt5_service.is_connected,
        "features": [
            "ICT Signal Analysis",
            "Automated Trading",
            "Performance Analytics",
            "MT5 Integration",
            "MQL5 Algo Forge Support"
        ]
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "status_code": 500}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    ) 