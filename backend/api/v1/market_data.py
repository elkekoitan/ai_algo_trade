"""
Market data API endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from backend.core.logger import setup_logger

logger = setup_logger("api.market_data")
router = APIRouter()


class SymbolInfoResponse(BaseModel):
    """Symbol information response model."""
    name: str
    point: float
    digits: int
    spread: int
    bid: float
    ask: float
    volume_min: float
    volume_max: float
    volume_step: float
    is_tradeable: bool


class CandleData(BaseModel):
    """Candlestick data model."""
    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    tick_volume: int
    spread: int


@router.get("/symbols")
async def get_symbols() -> List[str]:
    """
    Get list of all available and tradeable trading symbols.
    """
    try:
        from backend.main import get_mt5_service
        mt5_service = await get_mt5_service()
        
        if not mt5_service.is_connected:
            raise HTTPException(status_code=503, detail="MT5 not connected")
        
        import MetaTrader5 as mt5
        symbols = mt5.symbols_get()
        
        if symbols is None:
            return []
            
        # Return all visible (tradeable) symbols
        tradeable_symbols = [s.name for s in symbols if s.visible]
        
        return sorted(tradeable_symbols)
        
    except Exception as e:
        logger.error(f"Error getting symbols: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/symbol/{symbol}", response_model=SymbolInfoResponse)
async def get_symbol_info(symbol: str) -> SymbolInfoResponse:
    """
    Get detailed information for a specific symbol.
    """
    try:
        from backend.main import get_mt5_service
        mt5_service = await get_mt5_service()
        
        if not mt5_service.is_connected:
            raise HTTPException(status_code=503, detail="MT5 not connected")
        
        symbol_info = await mt5_service.get_symbol_info(symbol)
        
        if not symbol_info:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
        
        return SymbolInfoResponse(
            name=symbol_info.name,
            point=symbol_info.point,
            digits=symbol_info.digits,
            spread=symbol_info.spread,
            bid=symbol_info.bid,
            ask=symbol_info.ask,
            volume_min=symbol_info.volume_min,
            volume_max=symbol_info.volume_max,
            volume_step=symbol_info.volume_step,
            is_tradeable=symbol_info.is_tradeable
        )
        
    except Exception as e:
        logger.error(f"Error getting symbol info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/candles/{symbol}", response_model=List[CandleData])
async def get_candles(
    symbol: str,
    timeframe: str = Query("H1", regex="^(M1|M5|M15|M30|H1|H4|D1|W1|MN1)$"),
    count: int = Query(100, ge=1, le=1000)
) -> List[CandleData]:
    """
    Get historical candlestick data for a symbol.
    
    Args:
        symbol: Trading symbol
        timeframe: Timeframe (M1, M5, M15, M30, H1, H4, D1, W1, MN1)
        count: Number of candles to retrieve
    """
    try:
        from backend.main import get_mt5_service
        mt5_service = await get_mt5_service()
        
        if not mt5_service.is_connected:
            raise HTTPException(status_code=503, detail="MT5 not connected")
        
        # Convert timeframe to MT5 constant
        import MetaTrader5 as mt5
        timeframe_map = {
            "M1": mt5.TIMEFRAME_M1,
            "M5": mt5.TIMEFRAME_M5,
            "M15": mt5.TIMEFRAME_M15,
            "M30": mt5.TIMEFRAME_M30,
            "H1": mt5.TIMEFRAME_H1,
            "H4": mt5.TIMEFRAME_H4,
            "D1": mt5.TIMEFRAME_D1,
            "W1": mt5.TIMEFRAME_W1,
            "MN1": mt5.TIMEFRAME_MN1,
        }
        
        mt5_timeframe = timeframe_map[timeframe]
        
        # Get rates
        df = await mt5_service.get_rates(symbol, mt5_timeframe, count)
        
        if df is None or df.empty:
            return []
        
        # Convert to response model
        candles = []
        for _, row in df.iterrows():
            candles.append(CandleData(
                time=row['time'],
                open=row['open'],
                high=row['high'],
                low=row['low'],
                close=row['close'],
                volume=int(row['real_volume']) if 'real_volume' in row else 0,
                tick_volume=int(row['tick_volume']),
                spread=int(row['spread'])
            ))
        
        return candles
        
    except Exception as e:
        logger.error(f"Error getting candles: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tick/{symbol}")
async def get_tick(symbol: str) -> Dict[str, Any]:
    """
    Get current tick data for a symbol.
    """
    try:
        from backend.main import get_mt5_service
        mt5_service = await get_mt5_service()
        
        if not mt5_service.is_connected:
            raise HTTPException(status_code=503, detail="MT5 not connected")
        
        import MetaTrader5 as mt5
        tick = mt5.symbol_info_tick(symbol)
        
        if tick is None:
            raise HTTPException(status_code=404, detail=f"No tick data for {symbol}")
        
        return {
            "time": datetime.fromtimestamp(tick.time),
            "bid": tick.bid,
            "ask": tick.ask,
            "last": tick.last,
            "volume": tick.volume,
            "flags": tick.flags,
            "volume_real": tick.volume_real
        }
        
    except Exception as e:
        logger.error(f"Error getting tick: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 