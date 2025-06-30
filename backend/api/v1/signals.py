"""
API endpoints for ICT signals.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime
import logging

from backend.core.config.settings import get_settings
from backend.modules.signals.ict import (
    RealICTEngine
)
from backend.modules.mt5_integration.service import MT5Service
from backend.modules.signals.ict.real_ict_engine import RealICTEngine

# Create router
router = APIRouter(prefix="/signals", tags=["signals"])

# Initialize services
settings = get_settings()
mt5_service = MT5Service(
    login=settings.MT5_LOGIN,
    password=settings.MT5_PASSWORD,
    server=settings.MT5_SERVER,
    timeout=settings.MT5_TIMEOUT
)

# Initialize RealICTEngine
engine = RealICTEngine()


@router.get("/order-blocks", response_model=List[Dict[str, Any]])
async def get_order_blocks(
    symbol: str = Query(..., description="Trading symbol (e.g., EURUSD)"),
    timeframe: str = Query("H1", description="Timeframe (M1, M5, M15, M30, H1, H4, D1, W1, MN)"),
    bars_count: int = Query(500, description="Number of bars to analyze"),
    min_body_size_factor: float = Query(0.6, description="Minimum body size factor"),
    min_move_after_factor: float = Query(1.5, description="Minimum move after factor"),
    confirmation_candles: int = Query(3, description="Confirmation candles"),
    strength_threshold: float = Query(0.7, description="Strength threshold (0.0-1.0)"),
    max_results: int = Query(10, description="Maximum number of results to return")
):
    """
    Detect Order Blocks for the given symbol and timeframe.
    
    Order blocks are areas on the chart where significant orders were placed 
    before a strong move in price, often serving as support/resistance in the future.
    """
    # Get market data from MT5
    try:
        # Connect to MT5 if not connected
        if not mt5_service.is_connected():
            if not await mt5_service.connect():
                raise HTTPException(status_code=500, detail="Failed to connect to MetaTrader 5")
        
        # Convert timeframe string to MT5 timeframe
        tf_map = {
            "M1": mt5.TIMEFRAME_M1,
            "M5": mt5.TIMEFRAME_M5,
            "M15": mt5.TIMEFRAME_M15,
            "M30": mt5.TIMEFRAME_M30,
            "H1": mt5.TIMEFRAME_H1,
            "H4": mt5.TIMEFRAME_H4,
            "D1": mt5.TIMEFRAME_D1,
            "W1": mt5.TIMEFRAME_W1,
            "MN": mt5.TIMEFRAME_MN1
        }
        
        mt5_timeframe = tf_map.get(timeframe.upper(), mt5.TIMEFRAME_H1)
        
        # Get market data
        rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, bars_count)
        if rates is None or len(rates) == 0:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol} on {timeframe}")
            
        # Convert to pandas DataFrame
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        # Add symbol and timeframe to DataFrame for reference
        df['symbol'] = symbol
        df['timeframe'] = timeframe
        
        # Use RealICTEngine for analysis
        signals = await engine.analyze_symbol(symbol, timeframe, bars_count)
        order_blocks = signals.get("order_blocks", [])[:max_results]
        
        return order_blocks
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting order blocks: {str(e)}")


@router.get("/fair-value-gaps", response_model=List[Dict[str, Any]])
async def get_fair_value_gaps(
    symbol: str = Query(..., description="Trading symbol (e.g., EURUSD)"),
    timeframe: str = Query("H1", description="Timeframe (M1, M5, M15, M30, H1, H4, D1, W1, MN)"),
    bars_count: int = Query(500, description="Number of bars to analyze"),
    min_gap_factor: float = Query(0.5, description="Minimum gap size factor"),
    strength_threshold: float = Query(0.7, description="Strength threshold (0.0-1.0)"),
    max_results: int = Query(10, description="Maximum number of results to return")
):
    """
    Detect Fair Value Gaps for the given symbol and timeframe.
    
    Fair Value Gaps are areas on the chart where price has 'gapped' and left an
    imbalance between buyers and sellers, often serving as magnets for price to return to.
    """
    # Get market data from MT5
    try:
        # Connect to MT5 if not connected
        if not mt5_service.is_connected():
            if not await mt5_service.connect():
                raise HTTPException(status_code=500, detail="Failed to connect to MetaTrader 5")
        
        # Convert timeframe string to MT5 timeframe
        tf_map = {
            "M1": mt5.TIMEFRAME_M1,
            "M5": mt5.TIMEFRAME_M5,
            "M15": mt5.TIMEFRAME_M15,
            "M30": mt5.TIMEFRAME_M30,
            "H1": mt5.TIMEFRAME_H1,
            "H4": mt5.TIMEFRAME_H4,
            "D1": mt5.TIMEFRAME_D1,
            "W1": mt5.TIMEFRAME_W1,
            "MN": mt5.TIMEFRAME_MN1
        }
        
        mt5_timeframe = tf_map.get(timeframe.upper(), mt5.TIMEFRAME_H1)
        
        # Get market data
        rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, bars_count)
        if rates is None or len(rates) == 0:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol} on {timeframe}")
            
        # Convert to pandas DataFrame
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        # Add symbol and timeframe to DataFrame for reference
        df['symbol'] = symbol
        df['timeframe'] = timeframe
        
        # Use RealICTEngine for analysis
        signals = await engine.analyze_symbol(symbol, timeframe, bars_count)
        fvgs = signals.get("fair_value_gaps", [])[:max_results]
        
        return fvgs
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting fair value gaps: {str(e)}")


@router.get("/breaker-blocks", response_model=List[Dict[str, Any]])
async def get_breaker_blocks(
    symbol: str = Query(..., description="Trading symbol (e.g., EURUSD)"),
    timeframe: str = Query("H1", description="Timeframe (M1, M5, M15, M30, H1, H4, D1, W1, MN)"),
    bars_count: int = Query(500, description="Number of bars to analyze"),
    min_strength: float = Query(0.7, description="Strength threshold (0.0-1.0)"),
    max_results: int = Query(10, description="Maximum number of results to return")
):
    """
    Detect Breaker Blocks for the given symbol and timeframe.
    
    Breaker blocks are order blocks that have been broken and then retested,
    often creating high-probability trading opportunities.
    """
    # Get market data from MT5
    try:
        # Connect to MT5 if not connected
        if not mt5_service.is_connected():
            if not await mt5_service.connect():
                raise HTTPException(status_code=500, detail="Failed to connect to MetaTrader 5")
        
        # Convert timeframe string to MT5 timeframe
        tf_map = {
            "M1": mt5.TIMEFRAME_M1,
            "M5": mt5.TIMEFRAME_M5,
            "M15": mt5.TIMEFRAME_M15,
            "M30": mt5.TIMEFRAME_M30,
            "H1": mt5.TIMEFRAME_H1,
            "H4": mt5.TIMEFRAME_H4,
            "D1": mt5.TIMEFRAME_D1,
            "W1": mt5.TIMEFRAME_W1,
            "MN": mt5.TIMEFRAME_MN1
        }
        
        mt5_timeframe = tf_map.get(timeframe.upper(), mt5.TIMEFRAME_H1)
        
        # Get market data
        rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, bars_count)
        if rates is None or len(rates) == 0:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol} on {timeframe}")
            
        # Convert to pandas DataFrame
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        # Add symbol and timeframe to DataFrame for reference
        df['symbol'] = symbol
        df['timeframe'] = timeframe
        
        # Use RealICTEngine for analysis
        signals = await engine.analyze_symbol(symbol, timeframe, bars_count)
        breaker_blocks = signals.get("breaker_blocks", [])[:max_results]
        
        return breaker_blocks
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting breaker blocks: {str(e)}")


@router.get("/all-signals", response_model=Dict[str, List[Dict[str, Any]]])
async def get_all_signals(
    symbol: str = Query(..., description="Trading symbol (e.g., EURUSD)"),
    timeframe: str = Query("H1", description="Timeframe (M1, M5, M15, M30, H1, H4, D1, W1, MN)"),
    bars_count: int = Query(500, description="Number of bars to analyze"),
    strength_threshold: float = Query(0.7, description="Strength threshold (0.0-1.0)"),
    max_results: int = Query(10, description="Maximum number of results to return per signal type")
):
    """
    Get all ICT signals (Order Blocks, Fair Value Gaps, Breaker Blocks) for the given symbol and timeframe.
    """
    # Get market data from MT5
    try:
        # Connect to MT5 if not connected
        if not mt5_service.is_connected():
            if not await mt5_service.connect():
                raise HTTPException(status_code=500, detail="Failed to connect to MetaTrader 5")
        
        # Convert timeframe string to MT5 timeframe
        tf_map = {
            "M1": mt5.TIMEFRAME_M1,
            "M5": mt5.TIMEFRAME_M5,
            "M15": mt5.TIMEFRAME_M15,
            "M30": mt5.TIMEFRAME_M30,
            "H1": mt5.TIMEFRAME_H1,
            "H4": mt5.TIMEFRAME_H4,
            "D1": mt5.TIMEFRAME_D1,
            "W1": mt5.TIMEFRAME_W1,
            "MN": mt5.TIMEFRAME_MN1
        }
        
        mt5_timeframe = tf_map.get(timeframe.upper(), mt5.TIMEFRAME_H1)
        
        # Get market data
        rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, bars_count)
        if rates is None or len(rates) == 0:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol} on {timeframe}")
            
        # Convert to pandas DataFrame
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        # Add symbol and timeframe to DataFrame for reference
        df['symbol'] = symbol
        df['timeframe'] = timeframe
        
        # Use RealICTEngine for analysis
        signals = await engine.analyze_symbol(symbol, timeframe, bars_count)
        
        # Return all signals with max_results limit
        return {
            "order_blocks": signals.get("order_blocks", [])[:max_results],
            "fair_value_gaps": signals.get("fair_value_gaps", [])[:max_results],
            "breaker_blocks": signals.get("breaker_blocks", [])[:max_results]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting signals: {str(e)}")


@router.get("/top-signals", response_model=List[Dict[str, Any]])
async def get_top_signals(
    symbol: str = Query(..., description="Trading symbol (e.g., EURUSD)"),
    timeframe: str = Query("H1", description="Timeframe (M1, M5, M15, M30, H1, H4, D1, W1, MN)"),
    bars_count: int = Query(500, description="Number of bars to analyze"),
    strength_threshold: float = Query(0.7, description="Strength threshold (0.0-1.0)"),
    max_results: int = Query(10, description="Maximum number of results to return")
):
    """
    Get top ICT signals across all signal types, sorted by strength/score.
    """
    try:
        # Get all signals
        all_signals = await get_all_signals(
            symbol=symbol,
            timeframe=timeframe,
            bars_count=bars_count,
            strength_threshold=strength_threshold,
            max_results=max_results * 2  # Get more signals to choose from
        )
        
        # Combine all signals
        combined_signals = []
        combined_signals.extend(all_signals["order_blocks"])
        combined_signals.extend(all_signals["fair_value_gaps"])
        combined_signals.extend(all_signals["breaker_blocks"])
        
        # Sort by score/strength
        sorted_signals = sorted(
            combined_signals, 
            key=lambda x: x.get("score", x.get("strength", 0)), 
            reverse=True
        )
        
        # Return top N signals
        return sorted_signals[:max_results]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting top signals: {str(e)}")


@router.post("/signals/ict/find_all", summary="Find all ICT signals for given symbols")
async def find_all_signals(symbols: List[str] = ["EURUSD", "GBPUSD", "XAUUSD", "USDJPY"]):
    """
    Asenkron olarak tüm semboller için FVG, OB ve BB sinyallerini bulur.
    """
    try:
        all_signals = await engine.find_all_signals_for_symbols(symbols)
        return {"success": True, "signals": all_signals}
    except Exception as e:
        logging.error(f"Error in find_all_signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))
