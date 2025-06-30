# minimal_starter.py
import uvicorn
import asyncio
import sys
from pathlib import Path

# Proje ana dizinini yola ekle
sys.path.append(str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, Depends
from backend.modules.mt5_integration.service import MT5Service
from backend.core.logger import setup_logger
from backend.core.database import init_db
# ANA API ROUTER'I EKLIYORUZ
from backend.api.v1 import api_router

logger = setup_logger("MinimalStarter")

# --- Dependency Injection için Global Servis ---
mt5 = MT5Service(login=25201110, password="e|([rXU1IsiM", server="Tickmill-Demo")
def get_mt5_service():
    return mt5

# --- FastAPI App ---
app = FastAPI(title="Functional MT5 Backend")

@app.on_event("startup")
async def startup_event():
    logger.info("Functional Backend starting up...")
    await init_db()
    await mt5.connect()
    if mt5.is_connected():
        logger.info("✅✅✅ MT5 CONNECTED SUCCESSFULLY ✅✅✅")
    else:
        logger.error("❌❌❌ FAILED TO CONNECT TO MT5 ❌❌❌")

# --- API Router'ları Dahil Etme ---
# Tum endpointleri (/trading, /signals, vs.) ekliyoruz
app.include_router(api_router, prefix="/api/v1", dependencies=[Depends(get_mt5_service)])

@app.get("/health")
async def health_check():
    is_connected = mt5.is_connected()
    if is_connected:
        acc_info = await mt5.get_account_info()
        return {
            "status": "ok",
            "mt5_status": "connected",
            "login": acc_info.get('login')
        }
    return {"status": "error", "mt5_status": "disconnected"}

if __name__ == "__main__":
    logger.info("Starting Uvicorn for minimal backend...")
    uvicorn.run(app, host="0.0.0.0", port=8000) 