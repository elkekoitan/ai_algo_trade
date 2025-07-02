"""
Test version of main FastAPI application for smoke testing.
This version excludes problematic imports to focus on core functionality.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import sys
import os
import uvicorn
from datetime import datetime

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Algo Trade Platform - Test Mode",
    description="Test version for smoke testing",
    version="2.0.0-test",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    """Root endpoint with platform information."""
    return {
        "name": "AI Algo Trade Platform - Test Mode",
        "version": "2.0.0-test",
        "description": "Test version for smoke testing",
        "status": "Test Mode",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "mode": "test",
        "version": "2.0.0-test"
    }

@app.get("/api/v1/system/status")
async def system_status():
    """System status endpoint."""
    return {
        "success": True,
        "platform": "ai_algo_trade",
        "version": "2.0.0-test",
        "mode": "test",
        "system_health": "test",
        "timestamp": datetime.utcnow().isoformat()
    }

# Trading endpoints for testing
@app.get("/api/v1/trading/account_info")
async def get_account_info():
    """Mock account info for testing."""
    return {
        "balance": 0,
        "equity": 0,
        "status": "test_mode",
        "message": "Test endpoint - no real trading data"
    }

@app.get("/api/v1/trading/account")
async def get_account():
    """Mock account endpoint for testing."""
    return {
        "balance": 0,
        "equity": 0,
        "status": "test_mode"
    }

@app.get("/api/v1/auto-trader/status")
async def get_autotrader_status():
    """Mock auto trader status."""
    return {
        "status": "test_mode",
        "message": "Test endpoint",
        "trades_today": 0,
        "profit_today": 0.0
    }

@app.get("/api/v1/market/tick/{symbol}")
async def get_market_tick(symbol: str):
    """Mock market tick data."""
    return {
        "symbol": symbol,
        "bid": 1.0000,
        "ask": 1.0001,
        "last": 1.0001,
        "volume": 0,
        "time": datetime.utcnow().isoformat(),
        "status": "test_mode"
    }

# Mock router endpoints
@app.get("/api/v1/unified")
async def unified_endpoint():
    """Mock unified trading endpoint."""
    return {"status": "test_mode", "message": "Unified trading endpoint"}

@app.get("/api/v1/market")
async def market_endpoint():
    """Mock market endpoint."""
    return {"status": "test_mode", "message": "Market data endpoint"}

@app.get("/api/v1/performance")
async def performance_endpoint():
    """Mock performance endpoint."""
    return {"status": "test_mode", "message": "Performance monitoring endpoint"}

@app.get("/api/v1/market-narrator")
async def market_narrator_endpoint():
    """Mock market narrator endpoint."""
    return {"status": "test_mode", "message": "Market narrator endpoint"}

@app.get("/api/v1/autotrader")
async def autotrader_endpoint():
    """Mock autotrader endpoint."""
    return {"status": "test_mode", "message": "AutoTrader endpoint"}

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "The requested endpoint was not found",
            "path": str(request.url.path),
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

if __name__ == "__main__":
    logger.info("Starting AI Algo Trade Platform Test Server...")
    uvicorn.run(
        "main_test:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )
