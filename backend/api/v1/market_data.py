"""
Market Data API - GERÇEK MT5 VERİLERİ
SADECE canlı veriler kullanılır
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

from backend.modules.mt5_integration.service import MT5Service
from backend.modules.mt5_integration.config import MT5_LOGIN, MT5_PASSWORD, MT5_SERVER, DEFAULT_SYMBOLS
from backend.core.logger import setup_logger
from fastapi import Request

logger = setup_logger("api.market_data")
router = APIRouter()

def get_mt5_service_from_engine(request: Request) -> MT5Service:
    """Dependency to get the MT5 service from the unified trading engine."""
    if not hasattr(request.app.state, 'trading_engine') or not request.app.state.trading_engine.connected:
        raise HTTPException(status_code=503, detail="MT5 service not available via trading engine")
    return request.app.state.trading_engine.mt5_service

@router.on_event("startup")
async def startup_event():
    """Startup event. MT5 connection is now managed by the Unified Trading Engine."""
    logger.info("Market Data API started. MT5 connection is managed by the central Unified Trading Engine.")

@router.get("/live-prices")
async def get_live_prices(mt5_service: MT5Service = Depends(get_mt5_service_from_engine)):
    """Gerçek canlı fiyatları al"""
    try:
        if not mt5_service.is_connected():
            # Tekrar bağlanmayı dene
            connected = await mt5_service.connect(MT5_LOGIN, MT5_PASSWORD, MT5_SERVER)
            if not connected:
                return {
                    "status": "error",
                    "message": "MT5 bağlantısı yok - Terminal'de manual login yapın",
                    "data": []
                }
        
        prices = []
        for symbol in DEFAULT_SYMBOLS[:10]:  # İlk 10 sembol
            try:
                tick = await mt5_service.get_symbol_tick(symbol)
                prices.append({
                    "symbol": symbol,
                    "bid": tick["bid"],
                    "ask": tick["ask"],
                    "spread": round((tick["ask"] - tick["bid"]) * 10000, 2),
                    "time": tick["time"],
                    "change": 0.0  # Değişim hesaplama gerekiyor
                })
            except Exception as e:
                logger.warning(f"Failed to get {symbol} price: {e}")
                continue
        
        return {
            "status": "success",
            "message": "Gerçek MT5 canlı fiyatları",
            "timestamp": datetime.now().isoformat(),
            "source": "Tickmill Demo",
            "data": prices
        }
        
    except Exception as e:
        logger.error(f"Live prices error: {e}")
        raise HTTPException(status_code=500, detail=f"Canlı fiyat hatası: {str(e)}")

@router.get("/account-info")
async def get_account_info(mt5_service: MT5Service = Depends(get_mt5_service_from_engine)):
    """Gerçek hesap bilgilerini al"""
    try:
        if not mt5_service.is_connected():
            connected = await mt5_service.connect(MT5_LOGIN, MT5_PASSWORD, MT5_SERVER)
            if not connected:
                return {
                    "status": "error",
                    "message": "MT5 bağlantısı yok",
                    "data": None
                }
        
        account_info = await mt5_service.get_account_info()
        
        return {
            "status": "success",
            "message": "Gerçek Tickmill Demo hesap bilgileri",
            "data": account_info
        }
        
    except Exception as e:
        logger.error(f"Account info error: {e}")
        raise HTTPException(status_code=500, detail=f"Hesap bilgisi hatası: {str(e)}")

@router.get("/positions")
async def get_positions(mt5_service: MT5Service = Depends(get_mt5_service_from_engine)):
    """Açık pozisyonları al"""
    try:
        if not mt5_service.is_connected():
            return {
                "status": "error",
                "message": "MT5 bağlantısı yok",
                "data": []
            }
        
        positions = await mt5_service.get_positions()
        
        return {
            "status": "success",
            "message": "Gerçek açık pozisyonlar",
            "data": positions
        }
        
    except Exception as e:
        logger.error(f"Positions error: {e}")
        raise HTTPException(status_code=500, detail=f"Pozisyon hatası: {str(e)}")

@router.get("/candles/{symbol}")
async def get_candles(symbol: str, timeframe: str = "H1", count: int = 100, mt5_service: MT5Service = Depends(get_mt5_service_from_engine)):
    """Gerçek mum verilerini al"""
    try:
        if not mt5_service.is_connected():
            return {
                "status": "error",
                "message": "MT5 bağlantısı yok",
                "data": []
            }
        
        candles = await mt5_service.get_candles(symbol, timeframe, count)
        
        return {
            "status": "success",
            "message": f"Gerçek {symbol} {timeframe} mum verileri",
            "symbol": symbol,
            "timeframe": timeframe,
            "count": len(candles),
            "data": candles
        }
        
    except Exception as e:
        logger.error(f"Candles error: {e}")
        raise HTTPException(status_code=500, detail=f"Mum verisi hatası: {str(e)}")

@router.get("/connection-status")
async def get_connection_status(mt5_service: MT5Service = Depends(get_mt5_service_from_engine)):
    """MT5 bağlantı durumunu kontrol et"""
    try:
        is_connected = mt5_service.is_connected()
        
        status_info = {
            "connected": is_connected,
            "server": MT5_SERVER,
            "login": MT5_LOGIN,
            "account_type": "Classic Demo",
            "message": "Bağlı" if is_connected else "Bağlantı yok - Manual login gerekiyor"
        }
        
        if is_connected:
            account_info = await mt5_service.get_account_info()
            status_info.update({
                "balance": account_info.get("balance", 0),
                "equity": account_info.get("equity", 0),
                "currency": account_info.get("currency", "USD")
            })
        
        return {
            "status": "success",
            "data": status_info
        }
        
    except Exception as e:
        logger.error(f"Connection status error: {e}")
        return {
            "status": "error",
            "message": f"Bağlantı durumu hatası: {str(e)}",
            "data": {"connected": False}
        }

@router.post("/reconnect")
async def reconnect_mt5(mt5_service: MT5Service = Depends(get_mt5_service_from_engine)):
    """MT5'e yeniden bağlan"""
    try:
        await mt5_service.disconnect()
        connected = await mt5_service.connect(MT5_LOGIN, MT5_PASSWORD, MT5_SERVER)
        
        return {
            "status": "success" if connected else "error",
            "message": "Bağlantı başarılı" if connected else "Bağlantı başarısız - Manual login gerekiyor",
            "connected": connected
        }
        
    except Exception as e:
        logger.error(f"Reconnect error: {e}")
        raise HTTPException(status_code=500, detail=f"Yeniden bağlantı hatası: {str(e)}")

@router.get("/symbols")
async def get_symbols(mt5_service: MT5Service = Depends(get_mt5_service_from_engine)):
    """Get all available symbols based on current time (weekend crypto vs regular hours)"""
    try:
        if not mt5_service.is_connected():
            raise HTTPException(status_code=503, detail="MT5 not connected")
        
        # Automatically get active symbols for current time
        symbols = await mt5_service.get_active_symbols_for_current_time()
        weekend_mode = await mt5_service.is_weekend_mode()
        
        return {
            "success": True,
            "weekend_mode": weekend_mode,
            "symbols": symbols,
            "count": len(symbols),
            "message": f"{'Weekend crypto symbols' if weekend_mode else 'Regular trading symbols'} retrieved"
        }
    except Exception as e:
        logger.error(f"Error getting symbols: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/symbols/active")
async def get_active_symbols(mt5_service: MT5Service = Depends(get_mt5_service_from_engine)):
    """Get only currently active symbols with real-time tick data"""
    try:
        if not mt5_service.is_connected():
            raise HTTPException(status_code=503, detail="MT5 not connected")
        
        # Get symbols based on current time
        all_symbols = await mt5_service.get_active_symbols_for_current_time()
        active_symbols = []
        
        # Filter only symbols with active tick data
        for symbol_info in all_symbols:
            try:
                tick_data = await mt5_service.get_symbol_tick(symbol_info["name"])
                if tick_data:
                    # Add tick data to symbol info
                    symbol_info.update({
                        "current_bid": tick_data["bid"],
                        "current_ask": tick_data["ask"],
                        "last_tick_time": tick_data["time"],
                        "is_active": True
                    })
                    active_symbols.append(symbol_info)
            except Exception as e:
                logger.warning(f"Could not get tick for {symbol_info['name']}: {e}")
                continue
        
        weekend_mode = await mt5_service.is_weekend_mode()
        
        return {
            "success": True,
            "weekend_mode": weekend_mode,
            "symbols": active_symbols,
            "count": len(active_symbols),
            "total_available": len(all_symbols),
            "message": f"Found {len(active_symbols)} active symbols"
        }
    except Exception as e:
        logger.error(f"Error getting active symbols: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/symbols/crypto")
async def get_crypto_symbols(mt5_service: MT5Service = Depends(get_mt5_service_from_engine)):
    """Get weekend-active crypto symbols with real-time data"""
    try:
        if not mt5_service.is_connected():
            raise HTTPException(status_code=503, detail="MT5 not connected")
        
        symbols = await mt5_service.get_weekend_crypto_symbols()
        return {
            "success": True,
            "symbols": symbols,
            "count": len(symbols),
            "message": "Weekend crypto symbols with real-time data"
        }
    except Exception as e:
        logger.error(f"Error getting crypto symbols: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tick/{symbol}")
async def get_symbol_tick(symbol: str, mt5_service: MT5Service = Depends(get_mt5_service_from_engine)):
    """Get real-time tick data for a symbol"""
    try:
        if not mt5_service.is_connected():
            raise HTTPException(status_code=503, detail="MT5 not connected")
        
        tick_data = await mt5_service.get_symbol_tick(symbol)
        return {
            "success": True,
            "data": tick_data
        }
    except Exception as e:
        logger.error(f"Error getting tick for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/candles/{symbol}")
async def get_symbol_candles(symbol: str, timeframe: str = "H1", count: int = 100, mt5_service: MT5Service = Depends(get_mt5_service_from_engine)):
    """Get candlestick data for a symbol"""
    try:
        if not mt5_service.is_connected():
            raise HTTPException(status_code=503, detail="MT5 not connected")
        
        candles = await mt5_service.get_candles(symbol, timeframe, count)
        return {
            "success": True,
            "symbol": symbol,
            "timeframe": timeframe,
            "count": len(candles),
            "data": candles
        }
    except Exception as e:
        logger.error(f"Error getting candles for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_market_status(request: Request):
    """Get current market status and connection info from the unified engine."""
    try:
        engine = request.app.state.trading_engine
        is_connected = engine.is_running and engine.connected

        if is_connected:
            account_info = await engine.mt5_service.get_account_info()
            weekend_mode = await engine.mt5_service.is_weekend_mode()
            
            return {
                "success": True,
                "mt5_connected": True,
                "weekend_mode": weekend_mode,
                "account": {
                    "login": account_info.get("login"),
                    "server": account_info.get("server"),
                    "balance": account_info.get("balance"),
                    "equity": account_info.get("equity"),
                    "currency": account_info.get("currency")
                },
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "mt5_connected": False,
                "message": "MT5 not connected via Unified Trading Engine",
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error getting market status: {e}", exc_info=True)
        return {
            "success": False,
            "mt5_connected": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/market/tick/{symbol}")
async def get_market_tick(symbol: str, mt5_service: MT5Service = Depends(get_mt5_service_from_engine)):
    """Get real-time tick data for a symbol - frontend compatible"""
    try:
        if not mt5_service.is_connected():
            raise HTTPException(status_code=503, detail="MT5 not connected")
        
        tick_data = await mt5_service.get_symbol_tick(symbol)
        
        # Format compatible with frontend
        return {
            "symbol": symbol,
            "last": tick_data["ask"],  # Frontend expects "last" price
            "bid": tick_data["bid"],
            "ask": tick_data["ask"],
            "volume": tick_data.get("volume", 0),
            "time": tick_data["time"],
            "spread": round((tick_data["ask"] - tick_data["bid"]) * 10000, 2)
        }
    except Exception as e:
        logger.error(f"Error getting market tick for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 