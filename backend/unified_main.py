"""
Unified Trading Backend - Simplified Version
Event-driven architecture ile tüm modülleri başlatır
"""

import sys
import os
from pathlib import Path

# Proje kök dizinini Python path'ine ekle
# Bu, script'in her yerden doğru şekilde çalışmasını sağlar
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root.parent))

import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import asyncio
from typing import Optional

# MT5 credentials
os.environ['MT5_LOGIN'] = '25201110'
os.environ['MT5_PASSWORD'] = 'e|([rXU1IsiM'
os.environ['MT5_SERVER'] = 'Tickmill-Demo'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Algo Trade - Unified Trading Platform",
    description="Event-driven unified trading system with integrated modules",
    version="3.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import after app creation to avoid circular imports
from backend.core.unified_trading_engine import UnifiedTradingEngine
from backend.core.enhanced_event_bus import EnhancedEventBus, EventPriority
from backend.core.shared_data_service import SharedDataService
from backend.api.v1.unified_trading import router as unified_router
from backend.api.v1.market_data import router as market_data_router, set_mt5_service
from backend.api.v1.trading import router as trading_router
from backend.api.v1.signals import router as signals_router
from backend.api.v1.adaptive_trade_manager import router as atm_router
from backend.api.v1.god_mode import router as god_mode_router
from backend.api.v1.market_narrator import router as market_narrator_router
from backend.api.v1.shadow_mode import router as shadow_mode_router
from backend.api.v1.performance import router as performance_router
# from backend.api.v1.events import router as events_router  # Temporarily disabled

# Global instances
event_bus = EnhancedEventBus()

# --- Dependency Injection & Engine Singleton ---
# Bu, uygulama boyunca tek bir engine örneği olmasını sağlar
_trading_engine: Optional[UnifiedTradingEngine] = None

async def get_trading_engine() -> UnifiedTradingEngine:
    global _trading_engine
    if _trading_engine is None:
        raise RuntimeError("Trading engine is not initialized")
    return _trading_engine

@app.on_event("startup")
async def startup_event():
    """Uygulama başlangıcında çalışacak fonksiyonlar."""
    global _trading_engine
    logger.info("Starting up the unified trading engine...")
    
    # Initialize the trading engine
    _trading_engine = UnifiedTradingEngine()
    
    # Store in app state for easy access
    app.state.trading_engine = _trading_engine
    
    # Start the engine
    await _trading_engine.start()
    
    # --- MT5 Connection Test on Startup ---
    try:
        if _trading_engine.connected:
            logger.info("✅✅✅ STARTUP SUCCESS: MT5 connection confirmed!")
            acc_info = await _trading_engine.mt5_service.get_account_info()
            logger.info(f"Account Info on Startup: {acc_info}")
        else:
            logger.error("❌❌❌ STARTUP FAILURE: MT5 connection could not be established!")
    except Exception as e:
        logger.error(f"🔥🔥🔥 STARTUP CRITICAL ERROR during MT5 check: {e}")
    # --- End of Test ---
    
    set_mt5_service(_trading_engine.mt5_service)
    logger.info("API is now using the live MT5 service instance.")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("🛑 Shutting down Unified Trading Backend...")
    if _trading_engine:
        await _trading_engine.stop()
    logger.info("👋 Backend shutdown complete")

# Include routers
app.include_router(unified_router, prefix="/api/v1/unified", tags=["unified"])
app.include_router(market_data_router, prefix="/api/v1/market_data", tags=["market-data"])
app.include_router(trading_router, prefix="/api/v1/trading", tags=["trading"])
app.include_router(signals_router, prefix="/api/v1/signals", tags=["signals"])
app.include_router(atm_router, prefix="/api/v1/adaptive-trade-manager", tags=["adaptive-trade-manager"])
app.include_router(god_mode_router, prefix="/api/v1/god-mode", tags=["god-mode"])
app.include_router(market_narrator_router, prefix="/api/v1/market-narrator", tags=["market-narrator"])
app.include_router(shadow_mode_router, prefix="/api/v1/shadow-mode", tags=["shadow-mode"])
app.include_router(performance_router, prefix="/api/v1/performance", tags=["performance"])
# app.include_router(events_router, prefix="/api/v1/events", tags=["events"])  # Temporarily disabled

@app.get("/", tags=["Root"])
async def read_root():
    """Hoş geldiniz mesajı ve temel platform durumu."""
    engine = await get_trading_engine()
    return {
        "message": "Welcome to the Unified AI Algo Trading Platform",
        "status": "running" if engine.running else "stopped",
        "mt5_connected": engine.connected,
        "docs_url": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        engine = await get_trading_engine()
        
        # MT5 bağlantı durumu
        mt5_status = "connected" if engine.connected else "disconnected"
        
        # Weekend mode kontrolü
        weekend_mode = await engine.mt5_service.is_weekend_mode() if engine.connected else False
        
        # Aktif sembol sayısı
        active_symbols_count = 0
        if engine.connected:
            symbols = await engine.mt5_service.get_active_symbols_for_current_time()
            active_symbols_count = len(symbols)
        
        return {
            "status": "healthy",
            "mt5_connected": engine.connected,
            "mt5_status": mt5_status,
            "weekend_mode": weekend_mode,
            "active_symbols": active_symbols_count,
            "engine_running": engine.running,
            "event_bus_active": engine.event_bus.running if hasattr(engine.event_bus, 'running') else True,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/v1/events/emit")
async def emit_event(event_type: str, data: dict, priority: str = "NORMAL"):
    """Manually emit an event for testing"""
    priority_map = {
        "CRITICAL": EventPriority.CRITICAL,
        "HIGH": EventPriority.HIGH,
        "NORMAL": EventPriority.NORMAL,
        "LOW": EventPriority.LOW
    }
    
    await event_bus.emit(
        event_type, 
        data, 
        priority=priority_map.get(priority, EventPriority.NORMAL)
    )
    
    return {
        "status": "event_emitted",
        "event_type": event_type,
        "priority": priority,
        "data": data
    }

@app.get("/api/v1/events/history")
async def get_event_history(limit: int = 100):
    """Get recent event history"""
    history = event_bus.get_event_history(limit)
    return {
        "total_events": len(event_bus._event_history),
        "returned": len(history),
        "events": history
    }

@app.get("/performance")
async def get_performance_metrics():
    """System performance metrics"""
    try:
        engine = await get_trading_engine()
        
        # System uptime
        import psutil
        import time
        
        # Process info
        process = psutil.Process()
        cpu_percent = process.cpu_percent()
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        
        # Engine metrics
        performance_data = {
            "system": {
                "cpu_usage": cpu_percent,
                "memory_usage_mb": round(memory_mb, 2),
                "uptime_seconds": time.time() - process.create_time(),
                "threads": process.num_threads()
            },
            "trading_engine": {
                "running": engine.running,
                "mt5_connected": engine.connected,
                "weekend_mode": await engine.mt5_service.is_weekend_mode() if engine.connected else False,
                "active_modules": {
                    "adaptive_manager": engine.adaptive_manager.active if hasattr(engine.adaptive_manager, 'active') else True,
                    "god_mode": engine.god_mode.active if hasattr(engine.god_mode, 'active') else True,
                    "market_narrator": engine.market_narrator.active if hasattr(engine.market_narrator, 'active') else True,
                    "shadow_mode": engine.shadow_mode.active if hasattr(engine.shadow_mode, 'active') else True
                }
            },
            "trading_metrics": engine.performance_metrics if hasattr(engine, 'performance_metrics') else {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Add MT5 account info if connected
        if engine.connected:
            try:
                account_info = await engine.mt5_service.get_account_info()
                performance_data["account"] = {
                    "balance": account_info.get("balance", 0),
                    "equity": account_info.get("equity", 0),
                    "profit": account_info.get("profit", 0),
                    "margin_level": account_info.get("margin_level", 0)
                }
                
                # Active symbols count
                symbols = await engine.mt5_service.get_active_symbols_for_current_time()
                performance_data["market"] = {
                    "active_symbols": len(symbols),
                    "weekend_mode": await engine.mt5_service.is_weekend_mode()
                }
            except Exception as e:
                logger.warning(f"Could not get account metrics: {e}")
        
        return performance_data
        
    except Exception as e:
        logger.error(f"Performance metrics error: {e}")
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Bu kısım script doğrudan çalıştırıldığında devreye girer.
if __name__ == "__main__":
    # Bu blok, doğrudan çalıştırma (debug vb.) için.
    # Gerçek production ortamında Gunicorn/Uvicorn ile app objesi kullanılır.
    logger.info("Starting Uvicorn for local development...")
    uvicorn.run(
        "unified_main:app", 
        host="0.0.0.0", 
        port=8002, 
        reload=True, 
        log_level="info"
    ) 