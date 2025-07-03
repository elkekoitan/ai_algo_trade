"""
Tek Noktadan Başlatma Scripti
Backend ve Frontend'i başlatır, MT5'e bağlanır.
"""

import sys
import os
import subprocess
import asyncio
from pathlib import Path
import logging
import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

# 1. Proje Kök Dizinini Ayarla
# Bu, tüm modüllerin doğru şekilde import edilmesini sağlar
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# 2. Loglamayı Yapılandır
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MasterStarter")

# 3. Gerekli Modülleri Import Et
from backend.core.unified_trading_engine import UnifiedTradingEngine
from backend.api.v1.unified_trading import router as unified_router
from backend.api.v1.market_data import router as market_data_router, set_mt5_service as set_market_data_mt5

# --- Global Singleton Engine ---
_trading_engine: Optional[UnifiedTradingEngine] = None

async def get_trading_engine() -> UnifiedTradingEngine:
    global _trading_engine
    if _trading_engine is None:
        raise RuntimeError("Trading engine has not been initialized")
    return _trading_engine

# --- FastAPI App ve Lifespan Events ---
app = FastAPI(title="AI Algo Trade - Unified Platform")

@app.on_event("startup")
async def startup_event():
    """Uygulama başladığında Unified Engine'i başlatır ve MT5'e bağlanır."""
    global _trading_engine
    logger.info("🚀🚀🚀 MASTER STARTUP SEQUENCE INITIATED 🚀🚀🚀")
    
    # Engine'i oluştur ve başlat (bu MT5 bağlantısını da dener)
    _trading_engine = UnifiedTradingEngine()
    await _trading_engine.start()
    
    if _trading_engine.connected:
        logger.info("✅✅✅ MT5 Connection Confirmed via Unified Engine! ✅✅✅")
    else:
        logger.error("❌❌❌ MT5 Connection FAILED! Check terminal and credentials. ❌❌❌")
        
    # Servisleri API router'larına enjekte et
    set_market_data_mt5(_trading_engine.mt5_service)
    logger.info("🔧 MT5 Service injected into API routers.")
    
    logger.info("✅ Backend startup complete.")

@app.on_event("shutdown")
async def shutdown_event():
    """Uygulama kapandığında engine'i durdur."""
    global _trading_engine
    logger.info("🔌🔌🔌 Shutting down all services... 🔌🔌🔌")
    if _trading_engine:
        await _trading_engine.stop()

# --- API Router'larını Ekle ---
app.include_router(unified_router, prefix="/api/v1/unified", tags=["Unified Engine"])
app.include_router(market_data_router, prefix="/api/v1/market_data", tags=["Market Data"])
# Not: Diğer tüm router'lar ana `api_router` içinde olduğundan,
# unified_main.py'deki gibi hepsini tek tek eklemeye gerek yok, unified_router yeterli.

# --- Ana Çalıştırma Bloğu ---
def run_backend():
    """Backend sunucusunu Uvicorn ile çalıştırır."""
    logger.info("🔥 Starting Backend Server on http://localhost:8002...")
    uvicorn.run(app, host="0.0.0.0", port=8002, log_level="info")

def run_frontend():
    """Frontend (Next.js) geliştirme sunucusunu başlatır."""
    frontend_dir = os.path.join(project_root, 'frontend')
    logger.info(f"🔥 Starting Frontend Server from {frontend_dir}...")
    # subprocess.Popen, komutu yeni bir süreçte başlatır
    subprocess.Popen("npm run dev", shell=True, cwd=frontend_dir)

if __name__ == "__main__":
    logger.info("🤖 AI Algo Trade Platform Starting...")
    
    # Frontend'i ayrı bir süreçte başlat
    run_frontend()
    
    # Backend'i ana süreçte başlat (bu script'i bloklar)
    # Bu, logların bu terminalde kalmasını sağlar
    run_backend() 