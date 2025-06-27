"""
AI Algo Trade Platform - Main FastAPI Application
Connects to a REAL MetaTrader 5 account and serves its data.
"""
import os
import logging
import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel

# Import the real MT5 service
from modules.mt5_integration.service import RealMT5Service

# --- Environment Setup for MT5 Credentials ---
# In a real production environment, these should be set as actual environment variables.
os.environ['MT5_LOGIN'] = '25201110'
# Using a raw string r'' to ensure special characters in the password are handled correctly.
os.environ['MT5_PASSWORD'] = r'e|([rXU1IsiM'
os.environ['MT5_SERVER'] = 'Tickmill-Demo'

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Algo Trade Platform - REAL DATA",
    description="Serving REAL data from MetaTrader 5. No more mock data.",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MT5 Service Management ---
mt5_service = RealMT5Service()

@app.on_event("startup")
async def startup_event():
    """On startup, connect to the real MT5 account."""
    logger.info("🚀 Platform starting up...")
    login = os.getenv("MT5_LOGIN")
    password = os.getenv("MT5_PASSWORD")
    server = os.getenv("MT5_SERVER")

    if not all([login, password, server]):
        logger.critical("MT5 credentials are not set in the environment!")
        return

    logger.info(f"Attempting to connect to MT5 server {server} for account {login}...")
    connected = await mt5_service.connect(login=int(login), password=password, server=server)
    if not connected:
        logger.critical("🔴 FAILED TO CONNECT TO METATRADER 5. The API will not work correctly.")
    else:
        logger.info("✅ Successfully connected to MetaTrader 5.")

@app.on_event("shutdown")
async def shutdown_event():
    """On shutdown, disconnect from MT5."""
    logger.info("🔌 Platform shutting down...")
    await mt5_service.disconnect()
    logger.info("Disconnected from MT5.")

# --- API Endpoints (Now using REAL MT5 data) ---
# Dependency to check for MT5 connection
async def get_mt5_service():
    if not mt5_service.is_connected():
        raise HTTPException(status_code=503, detail="MT5 service is not available. Check backend logs.")
    return mt5_service

# --- Models for API responses ---
class AccountInfo(BaseModel):
    login: str
    server: str
    balance: float
    equity: float
    profit: float
    currency: str

class Position(BaseModel):
    ticket: int
    symbol: str
    type: str
    volume: float
    open_price: float
    current_price: float
    sl: float
    tp: float
    profit: float
    swap: float
    magic: int
    comment: str
    open_time: str
    
class Symbol(BaseModel):
    name: str
    description: str

# API v1 Router
from fastapi import APIRouter
api_router = APIRouter(prefix="/api/v1")

@api_router.get("/trading/account", response_model=AccountInfo)
async def get_account_info(service: RealMT5Service = Depends(get_mt5_service)):
    try:
        info = await service.get_account_info()
        return info
    except Exception as e:
        logger.error(f"Error in /trading/account endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/trading/positions", response_model=List[Position])
async def get_positions(service: RealMT5Service = Depends(get_mt5_service)):
    try:
        positions = await service.get_positions()
        return positions
    except Exception as e:
        logger.error(f"Error in /trading/positions endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/market/symbols")
async def get_symbols(service: RealMT5Service = Depends(get_mt5_service)):
    try:
        symbols = await service.get_symbols()
        # Filter down the list to avoid overly large responses
        filtered_symbols = [{"name": s["name"], "description": s["description"]} for s in symbols if s['name'].endswith('USD') or s['name'] in ['XAUUSD', 'UK100', 'DE30']]
        return {"symbols": filtered_symbols}
    except Exception as e:
        logger.error(f"Error in /market/symbols endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/market/candles/{symbol}")
async def get_candles(symbol: str, timeframe: str = "H1", count: int = 100, service: RealMT5Service = Depends(get_mt5_service)):
    try:
        candles = await service.get_candles(symbol, timeframe, count)
        return {"candles": candles}
    except Exception as e:
        logger.error(f"Error in /market/candles endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/market/tick/{symbol}")
async def get_symbol_tick(symbol: str, service: RealMT5Service = Depends(get_mt5_service)):
    try:
        tick = await service.get_symbol_tick(symbol)
        return tick
    except Exception as e:
        logger.error(f"Error in /market/tick endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/trading/place_order")
async def place_order(order_data: dict, service: RealMT5Service = Depends(get_mt5_service)):
    try:
        result = await service.place_order(
            symbol=order_data["symbol"],
            order_type=order_data["order_type"].lower(),
            volume=order_data["volume"],
            sl=order_data.get("sl"),
            tp=order_data.get("tp"),
            comment=order_data.get("comment", "AI Algo Trade")
        )
        return {"success": True, "order_id": result["ticket"], "result": result}
    except Exception as e:
        logger.error(f"Error placing order: {e}")
        return {"success": False, "message": str(e)}

@api_router.post("/trading/close_position/{ticket}")
async def close_position(ticket: int, service: RealMT5Service = Depends(get_mt5_service)):
    try:
        result = await service.close_position(ticket)
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Error closing position: {e}")
        return {"success": False, "message": str(e)}

@api_router.get("/signals")
async def get_real_signals(service: RealMT5Service = Depends(get_mt5_service)):
    try:
        signals = await service.get_all_signals()
        return {"success": True, "signals": signals}
    except Exception as e:
        logger.error(f"Error in /signals endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@api_router.get("/performance/summary")
async def get_performance_summary():
     # This endpoint can be developed later with a real performance tracking engine
    return {"message": "Performance analytics are under development. Coming soon."}

from api.v1.god_mode import router as god_mode_router
from api.v1.shadow_mode import router as shadow_mode_router

# Include routers
app.include_router(api_router)
app.include_router(god_mode_router)  # Add God Mode router
app.include_router(shadow_mode_router)  # Add Shadow Mode router

# --- Main execution ---
if __name__ == "__main__":
    logger.info("Starting Uvicorn server for AI Algo Trade Platform...")
    uvicorn.run(
        "simple_main:app",
        host="0.0.0.0",
        port=8000, 
        reload=True,
        log_level="info"
    ) 