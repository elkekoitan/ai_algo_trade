"""
Crypto Trading API Endpoints
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List, Optional
import asyncio
from datetime import datetime

from ...modules.crypto_trading.crypto_service import CryptoTradingService

router = APIRouter(prefix="/crypto-trading", tags=["Crypto Trading"])

# Global crypto trading service instance
crypto_service = None
trading_task = None

@router.on_event("startup")
async def startup_crypto_service():
    global crypto_service
    crypto_service = CryptoTradingService()
    await crypto_service.initialize_crypto_trading()

@router.get("/status")
async def get_crypto_status():
    """Crypto trading sistem durumunu getir"""
    try:
        if not crypto_service:
            return {"status": "not_initialized", "message": "Crypto service başlatılmamış"}
        
        # Aktif pozisyonları al
        positions = await crypto_service.get_active_positions()
        
        # Son analizi al
        last_analysis = crypto_service.last_analysis
        
        return {
            "status": "active",
            "timestamp": datetime.now().isoformat(),
            "active_positions": len(positions),
            "positions": positions,
            "last_analysis": last_analysis,
            "monitored_symbols": crypto_service.crypto_symbols,
            "auto_trading_active": trading_task is not None and not trading_task.done()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status alma hatası: {str(e)}")

@router.get("/market-data")
async def get_crypto_market_data():
    """Crypto piyasa verilerini getir"""
    try:
        if not crypto_service:
            raise HTTPException(status_code=400, detail="Crypto service başlatılmamış")
        
        market_data = await crypto_service.get_crypto_market_data()
        return {
            "success": True,
            "data": market_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Market data hatası: {str(e)}")

@router.post("/analyze")
async def analyze_crypto_market():
    """Crypto piyasa analizi yap"""
    try:
        if not crypto_service:
            raise HTTPException(status_code=400, detail="Crypto service başlatılmamış")
        
        analysis = await crypto_service.analyze_and_trade()
        
        return {
            "success": True,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analiz hatası: {str(e)}")

@router.post("/start-auto-trading")
async def start_auto_trading(background_tasks: BackgroundTasks, interval_minutes: int = 5):
    """Otomatik crypto trading'i başlat"""
    global trading_task
    
    try:
        if not crypto_service:
            raise HTTPException(status_code=400, detail="Crypto service başlatılmamış")
        
        if trading_task and not trading_task.done():
            return {
                "success": False,
                "message": "Auto trading zaten aktif"
            }
        
        # Background task olarak auto trading'i başlat
        async def run_auto_trading():
            await crypto_service.start_auto_trading(interval_minutes)
        
        trading_task = asyncio.create_task(run_auto_trading())
        
        return {
            "success": True,
            "message": f"Auto trading başlatıldı (Her {interval_minutes} dakika)",
            "interval_minutes": interval_minutes
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Auto trading başlatma hatası: {str(e)}")

@router.post("/stop-auto-trading")
async def stop_auto_trading():
    """Otomatik crypto trading'i durdur"""
    global trading_task
    
    try:
        if not trading_task or trading_task.done():
            return {
                "success": False,
                "message": "Auto trading zaten durmuş"
            }
        
        trading_task.cancel()
        
        return {
            "success": True,
            "message": "Auto trading durduruldu"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Auto trading durdurma hatası: {str(e)}")

@router.get("/positions")
async def get_crypto_positions():
    """Aktif crypto pozisyonlarını getir"""
    try:
        if not crypto_service:
            raise HTTPException(status_code=400, detail="Crypto service başlatılmamış")
        
        positions = await crypto_service.get_active_positions()
        
        # Toplam P&L hesapla
        total_profit = sum(pos["profit"] for pos in positions)
        
        return {
            "success": True,
            "positions": positions,
            "total_positions": len(positions),
            "total_profit": total_profit,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pozisyon alma hatası: {str(e)}")

@router.post("/manual-trade")
async def manual_crypto_trade(
    symbol: str,
    action: str,  # BUY or SELL
    lot_size: float = 0.01,
    stop_loss: Optional[float] = None,
    take_profit: Optional[float] = None
):
    """Manuel crypto trade aç"""
    try:
        if not crypto_service:
            raise HTTPException(status_code=400, detail="Crypto service başlatılmamış")
        
        if symbol not in crypto_service.crypto_symbols:
            raise HTTPException(status_code=400, detail=f"Desteklenmeyen symbol: {symbol}")
        
        if action not in ["BUY", "SELL"]:
            raise HTTPException(status_code=400, detail="Action BUY veya SELL olmalı")
        
        # Manuel trade sinyali oluştur
        signal = {
            "symbol": symbol,
            "action": action,
            "lot_size": lot_size,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "confidence": 1.0,  # Manuel trade için %100 güven
            "reasoning": "Manuel trade"
        }
        
        # Trade'i işle
        await crypto_service.process_trading_signal(signal)
        
        return {
            "success": True,
            "message": f"{symbol} {action} trade başlatıldı",
            "signal": signal
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Manuel trade hatası: {str(e)}")

@router.get("/symbols")
async def get_crypto_symbols():
    """Desteklenen crypto sembollerini getir"""
    try:
        if not crypto_service:
            raise HTTPException(status_code=400, detail="Crypto service başlatılmamış")
        
        return {
            "success": True,
            "symbols": crypto_service.crypto_symbols,
            "count": len(crypto_service.crypto_symbols)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Symbol listesi hatası: {str(e)}")

@router.get("/live-analysis")
async def get_live_crypto_analysis():
    """Canlı crypto analizi getir (cache'den)"""
    try:
        if not crypto_service:
            raise HTTPException(status_code=400, detail="Crypto service başlatılmamış")
        
        if not crypto_service.last_analysis:
            # İlk analizi yap
            analysis = await crypto_service.analyze_and_trade()
        else:
            analysis = crypto_service.last_analysis
        
        return {
            "success": True,
            "analysis": analysis,
            "is_cached": crypto_service.last_analysis is not None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Live analiz hatası: {str(e)}") 