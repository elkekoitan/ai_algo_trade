"""
ICT Signals API endpoints.

This module provides API endpoints for retrieving ICT signals
like Order Blocks, Fair Value Gaps, and Breaker Blocks.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Query, HTTPException, Depends
import MetaTrader5 as mt5
import logging
from datetime import datetime, timedelta

from backend.core.config import get_settings
from backend.modules.signals.ict import (
    find_order_blocks,
    find_fair_value_gaps,
    find_breaker_blocks,
    score_signals
)

logger = logging.getLogger("ict_ultra_v2.api.signals")

router = APIRouter(prefix="/ict", tags=["ICT Signals"])


@router.get("/signals")
async def get_ict_signals(
    symbols: List[str] = Query(["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"]),
    timeframes: List[str] = Query(["M15", "H1", "H4"]),
    signal_types: List[str] = Query(["order_blocks", "fair_value_gaps", "breaker_blocks"]),
    lookback_period: int = Query(100, ge=10, le=500),
    min_score: float = Query(70.0, ge=0.0, le=100.0),
    max_results: int = Query(50, ge=1, le=100)
) -> Dict[str, Any]:
    """
    Get ICT signals for the specified symbols and timeframes.
    
    Args:
        symbols: List of symbols to analyze
        timeframes: List of timeframes to analyze
        signal_types: List of signal types to include
        lookback_period: How far back to look for signals
        min_score: Minimum score for signals
        max_results: Maximum number of results to return
        
    Returns:
        Dictionary with ICT signals
    """
    logger.info(f"Getting ICT signals for {symbols} on {timeframes}")
    
    # Check if MT5 is connected
    if not mt5.initialize():
        logger.error(f"Failed to connect to MT5: {mt5.last_error()}")
        raise HTTPException(status_code=503, detail="Failed to connect to MetaTrader 5")
    
    # Convert timeframe strings to MT5 constants
    mt5_timeframes = {
        "M1": mt5.TIMEFRAME_M1,
        "M5": mt5.TIMEFRAME_M5,
        "M15": mt5.TIMEFRAME_M15,
        "M30": mt5.TIMEFRAME_M30,
        "H1": mt5.TIMEFRAME_H1,
        "H4": mt5.TIMEFRAME_H4,
        "D1": mt5.TIMEFRAME_D1,
        "W1": mt5.TIMEFRAME_W1,
        "MN1": mt5.TIMEFRAME_MN1
    }
    
    all_signals = []
    
    # For each symbol and timeframe, get the requested signals
    for symbol in symbols:
        for tf_str in timeframes:
            tf = mt5_timeframes.get(tf_str)
            if tf is None:
                logger.warning(f"Invalid timeframe: {tf_str}")
                continue
            
            # Get the signals based on the requested types
            signals_for_tf = []
            
            if "order_blocks" in signal_types:
                obs = find_order_blocks(symbol, tf, lookback_period=lookback_period)
                for ob in obs:
                    ob["signal_type"] = "order_block"
                    ob["timeframe"] = tf_str
                    ob["symbol"] = symbol
                signals_for_tf.extend(obs)
            
            if "fair_value_gaps" in signal_types:
                fvgs = find_fair_value_gaps(symbol, tf, lookback_period=lookback_period)
                for fvg in fvgs:
                    fvg["signal_type"] = "fair_value_gap"
                    fvg["timeframe"] = tf_str
                    fvg["symbol"] = symbol
                signals_for_tf.extend(fvgs)
            
            if "breaker_blocks" in signal_types:
                bbs = find_breaker_blocks(symbol, tf, lookback_period=lookback_period)
                for bb in bbs:
                    bb["signal_type"] = "breaker_block"
                    bb["timeframe"] = tf_str
                    bb["symbol"] = symbol
                signals_for_tf.extend(bbs)
            
            # Score the signals
            if signals_for_tf:
                scored_signals = score_signals(signals_for_tf, symbol, tf)
                all_signals.extend(scored_signals)
    
    # Filter by minimum score
    filtered_signals = [s for s in all_signals if s.get("score", 0) >= min_score]
    
    # Sort by score (highest first)
    filtered_signals.sort(key=lambda x: x.get("score", 0), reverse=True)
    
    # Limit the number of results
    limited_signals = filtered_signals[:max_results]
    
    # Add timestamp and metadata
    response = {
        "timestamp": datetime.now().isoformat(),
        "symbols": symbols,
        "timeframes": timeframes,
        "signal_types": signal_types,
        "min_score": min_score,
        "total_signals": len(filtered_signals),
        "returned_signals": len(limited_signals),
        "signals": limited_signals
    }
    
    logger.info(f"Returning {len(limited_signals)} ICT signals")
    return response


@router.get("/signals/{symbol}")
async def get_ict_signals_for_symbol(
    symbol: str,
    timeframes: List[str] = Query(["M15", "H1", "H4"]),
    signal_types: List[str] = Query(["order_blocks", "fair_value_gaps", "breaker_blocks"]),
    lookback_period: int = Query(100, ge=10, le=500),
    min_score: float = Query(70.0, ge=0.0, le=100.0),
    max_results: int = Query(50, ge=1, le=100)
) -> Dict[str, Any]:
    """
    Get ICT signals for a specific symbol.
    
    Args:
        symbol: Symbol to analyze
        timeframes: List of timeframes to analyze
        signal_types: List of signal types to include
        lookback_period: How far back to look for signals
        min_score: Minimum score for signals
        max_results: Maximum number of results to return
        
    Returns:
        Dictionary with ICT signals
    """
    return await get_ict_signals(
        symbols=[symbol],
        timeframes=timeframes,
        signal_types=signal_types,
        lookback_period=lookback_period,
        min_score=min_score,
        max_results=max_results
    ) 