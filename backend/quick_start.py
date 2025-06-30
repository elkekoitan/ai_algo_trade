from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import sys
import os

# MT5 integration
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from modules.mt5_integration.service import RealMT5Service
from modules.mt5_integration.config import MT5_LOGIN, MT5_PASSWORD, MT5_SERVER, DEFAULT_SYMBOLS

app = FastAPI(title="AI Algo Trade Backend - LIVE MT5 DATA", version="2.0.0")

# Global MT5 service
mt5_service = RealMT5Service()

# CORS middleware - Frontend için gerekli
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Startup sırasında MT5'e bağlan"""
    try:
        print("🚀 Connecting to Tickmill Demo...")
        connected = await mt5_service.connect(MT5_LOGIN, MT5_PASSWORD, MT5_SERVER)
        if connected:
            print("✅ MT5 Tickmill Demo connected successfully!")
        else:
            print("⚠️ MT5 connection failed")
    except Exception as e:
        print(f"❌ MT5 startup error: {e}")

@app.get("/")
async def root():
    return {
        "message": "AI Algo Trade Backend v2.0.0 - LIVE MT5 DATA", 
        "mt5_status": "Connected" if mt5_service.is_connected() else "Disconnected",
        "server": MT5_SERVER,
        "account": MT5_LOGIN
    }

@app.get("/health")
async def health():
    return {
        "status": "OK", 
        "message": "Backend is healthy with LIVE MT5 data", 
        "port": 8001,
        "mt5_connected": mt5_service.is_connected()
    }

@app.get("/api/v1/market-data")
async def get_market_data():
    """Gerçek MT5 canlı verileri"""
    try:
        if not mt5_service.is_connected():
            return {
                "data": "MT5 not connected",
                "status": "ERROR",
                "server": "Backend v2.0.0"
            }
        
        # İlk 5 major pair'in canlı fiyatları
        live_data = []
        for symbol in ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "USDCHF"]:
            try:
                tick = await mt5_service.get_symbol_tick(symbol)
                live_data.append({
                    "symbol": symbol,
                    "bid": tick["bid"],
                    "ask": tick["ask"],
                    "spread": round((tick["ask"] - tick["bid"]) * 10000, 2) if symbol != "XAUUSD" else round((tick["ask"] - tick["bid"]) * 100, 2),
                    "time": tick["time"]
                })
            except:
                continue
        
        return {
            "data": live_data,
            "status": "LIVE",
            "server": "Tickmill Demo - Real Data",
            "timestamp": live_data[0]["time"] if live_data else None
        }
    except Exception as e:
        return {
            "data": f"Error: {str(e)}",
            "status": "ERROR", 
            "server": "Backend v2.0.0"
        }

@app.get("/api/v1/account")
async def get_account():
    """Gerçek MT5 hesap bilgileri"""
    try:
        if not mt5_service.is_connected():
            return {"status": "ERROR", "message": "MT5 not connected"}
        
        account_info = await mt5_service.get_account_info()
        return {
            "status": "SUCCESS",
            "data": account_info
        }
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

@app.get("/api/v1/positions")
async def get_positions():
    """Açık pozisyonlar"""
    try:
        if not mt5_service.is_connected():
            return {"status": "ERROR", "message": "MT5 not connected", "data": []}
        
        positions = await mt5_service.get_positions()
        return {
            "status": "SUCCESS",
            "data": positions,
            "count": len(positions)
        }
    except Exception as e:
        return {"status": "ERROR", "message": str(e), "data": []}

@app.get("/api/v1/status")
async def get_status():
    """Sistem durumu"""
    is_connected = mt5_service.is_connected()
    
    status_data = {
        "backend": "Running",
        "frontend": "Available at http://localhost:3000", 
        "api_docs": "Available at http://localhost:8001/docs",
        "quantum_dashboard": "Available at http://localhost:3000/quantum",
        "mt5_connection": "Connected" if is_connected else "Disconnected",
        "data_source": "LIVE Tickmill Demo" if is_connected else "Mock Data",
        "message": "🚀 AI Algo Trading Platform with REAL MT5 DATA!"
    }
    
    if is_connected:
        try:
            account_info = await mt5_service.get_account_info()
            status_data.update({
                "account_balance": f"${account_info.get('balance', 0):,.2f}",
                "account_equity": f"${account_info.get('equity', 0):,.2f}",
                "account_server": account_info.get('server', 'Unknown')
            })
        except:
            pass
    
    return {
        "status": "success",
        "data": status_data
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True) 