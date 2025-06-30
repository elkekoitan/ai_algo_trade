"""
Gerçek MT5 ile Unified Trading Backend
SADECE gerçek demo hesap verileri kullanılır
"""

import uvicorn
import asyncio
import sys
import os
import subprocess
from pathlib import Path

# Proje kök dizinini Python path'ine ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

# AYARLARI KULLANMADAN ÖNCE, DOĞRUDAN IMPORT EDELİM
from backend.modules.mt5_integration.service import MT5Service
from backend.core.config.settings import get_settings
from backend.core.logger import setup_logger
from backend.api.v1 import api_router

# Global Değişkenler
logger = setup_logger("RealBackend")
mt5_service_global = MT5Service(
    login=25201110,
    password="e|([rXU1IsiM",
    server="Tickmill-Demo"
)

# --- FastAPI Lifespan Events ---
async def startup_event():
    """Uygulama başladığında MT5'e bağlanır."""
    logger.info("🚀🚀🚀 Backend starting up... 🚀🚀🚀")
    logger.info("Attempting to connect to MT5...")
    await mt5_service_global.connect()
    if mt5_service_global.is_connected():
        info = await mt5_service_global.get_account_info()
        logger.info(f"✅✅✅ MT5 Connected Successfully to account {info.get('login')} ✅✅✅")
    else:
        logger.error("❌❌❌ MT5 Connection Failed during startup. ❌❌❌")

async def shutdown_event():
    """Uygulama kapandığında MT5 bağlantısını keser."""
    logger.info("🔌🔌🔌 Backend shutting down... 🔌🔌🔌")
    await mt5_service_global.disconnect()

# --- FastAPI App ---
app = FastAPI(
    title="AI Algo Trade - Real MT5 Backend (Simplified)",
    on_startup=[startup_event],
    on_shutdown=[shutdown_event]
)

# --- Dependency Injection ---
def get_mt5_service() -> MT5Service:
    """MT5 servisini endpoint'lere enjekte eder."""
    return mt5_service_global

# --- Middlewares ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Routers ---
app.include_router(api_router, prefix="/api/v1")

# --- Health Check Endpoint ---
@app.get("/health")
async def health_check(mt5: MT5Service = Depends(get_mt5_service)):
    is_connected = mt5.is_connected()
    return {
        "status": "ok" if is_connected else "error",
        "mt5_connection_status": "connected" if is_connected else "disconnected"
    }

# --- Main Execution ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 