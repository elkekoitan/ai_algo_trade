"""
ICT Ultra v2: Algo Forge Edition - Backend Main Module
-----------------------------------------------------
This is the main entry point for the ICT Ultra v2 backend.
It initializes the FastAPI application, sets up middleware,
and connects to the MetaTrader 5 platform.
"""

import os
import sys
import time
from typing import Dict, Any, Optional
import logging

from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Try to import MetaTrader5 package
try:
    import MetaTrader5 as mt5
except ImportError:
    print("ERROR: MetaTrader5 package not found. Please install it with:")
    print("pip install MetaTrader5")
    sys.exit(1)

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/backend.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ict_ultra_v2")

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Initialize FastAPI app
app = FastAPI(
    title="ICT Ultra v2 API",
    description="Next-generation trading platform with MQL5 Algo Forge integration",
    version="1.0.0"
)

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MT5 Connection Management ---

def connect_to_mt5() -> bool:
    """
    Connect to the MetaTrader 5 terminal.
    
    Returns:
        bool: True if connection was successful, False otherwise
    """
    # Initialize MT5 connection
    if not mt5.initialize():
        logger.error(f"MT5 initialize() failed, error code = {mt5.last_error()}")
        return False
    
    # Demo account credentials
    login = 25201110
    server = "Tickmill-Demo"
    # For security, password should be stored in environment variables
    # password = os.getenv("MT5_PASSWORD")
    
    # Try to login (if terminal is already logged in, this will succeed without password)
    authorized = mt5.login(login, server=server)
    
    if authorized:
        logger.info(f"Connected to MT5 account #{login}")
        return True
    else:
        logger.error(f"Failed to connect to account #{login}, error code: {mt5.last_error()}")
        return False

# --- Startup and Shutdown Events ---

@app.on_event("startup")
async def startup_event():
    """Execute when the application starts up."""
    logger.info("Starting ICT Ultra v2 backend...")
    
    # Connect to MT5
    if not connect_to_mt5():
        logger.warning("Could not connect to MT5 on startup. Some features may be limited.")
    
    logger.info("Backend startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Execute when the application shuts down."""
    logger.info("Shutting down ICT Ultra v2 backend...")
    
    # Shutdown MT5 connection
    mt5.shutdown()
    
    logger.info("Backend shutdown complete")

# --- API Endpoints ---

@app.get("/")
async def read_root():
    """Root endpoint."""
    return {"message": "Welcome to ICT Ultra v2 API"}

@app.get("/api/status")
async def get_status():
    """
    Check the status of the API and MT5 connection.
    
    Returns:
        dict: Status information
    """
    terminal_info = mt5.terminal_info()
    if not terminal_info:
        return {
            "api_status": "online",
            "mt5_status": "disconnected",
            "error": mt5.last_error()
        }
        
    return {
        "api_status": "online",
        "mt5_status": "connected",
        "terminal": {
            "name": terminal_info.name,
            "company": terminal_info.company,
            "version": terminal_info.version,
            "build": terminal_info.build,
            "path": terminal_info.path,
        }
    }

@app.get("/api/account_info")
async def get_account_info():
    """
    Get information about the connected MT5 account.
    
    Returns:
        dict: Account information
    """
    account_info = mt5.account_info()
    if account_info:
        return account_info._asdict()
    
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=f"Could not retrieve account info. MT5 error: {mt5.last_error()}"
    )

@app.get("/api/symbols")
async def get_symbols():
    """
    Get list of available symbols.
    
    Returns:
        list: Available symbols
    """
    symbols = mt5.symbols_get()
    if symbols:
        return [symbol.name for symbol in symbols]
    
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=f"Could not retrieve symbols. MT5 error: {mt5.last_error()}"
    )

# --- Error Handling ---

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred."}
    )

# --- Main Entry Point ---

if __name__ == "__main__":
    import uvicorn
    
    # Run the FastAPI application with uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    ) 