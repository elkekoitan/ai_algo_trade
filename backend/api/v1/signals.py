"""
API endpoints for ICT signals.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime

from backend.core.config.settings import settings
from backend.modules.signals.ict import (
    OrderBlockDetector, 
    FairValueGapDetector, 
    BreakerBlockDetector,
    ICTSignalScorer,
    ICTOpenBLASEngine
)
from backend.modules.mt5_integration.service import MT5Service

# Create router
router = APIRouter(prefix="/signals", tags=["signals"])

# Initialize services
mt5_service = MT5Service(
    login=settings.MT5_LOGIN,
    password=settings.MT5_PASSWORD,
    server=settings.MT5_SERVER,
    timeout=settings.MT5_TIMEOUT
)

# Initialize detectors with OpenBLAS
ob_detector = OrderBlockDetector(use_openblas=settings.USE_OPENBLAS)
fvg_detector = FairValueGapDetector(use_openblas=settings.USE_OPENBLAS)
bb_detector = BreakerBlockDetector(use_openblas=settings.USE_OPENBLAS)
signal_scorer = ICTSignalScorer()


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
        
        # Detect order blocks
        order_blocks = ob_detector.detect(
            df,
            min_body_size_factor=min_body_size_factor,
            min_move_after_factor=min_move_after_factor,
            confirmation_candles=confirmation_candles,
            strength_threshold=strength_threshold,
            max_results=max_results
        )
        
        # Score signals
        scored_signals = signal_scorer.score_signals(order_blocks, df)
        
        return scored_signals
        
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
        
        # Detect fair value gaps
        fvgs = fvg_detector.detect(
            df,
            min_gap_factor=min_gap_factor,
            strength_threshold=strength_threshold,
            max_results=max_results
        )
        
        # Score signals
        scored_signals = signal_scorer.score_signals(fvgs, df)
        
        return scored_signals
        
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
        
        # Detect breaker blocks
        breaker_blocks = bb_detector.detect(
            df,
            min_strength=min_strength,
            max_results=max_results
        )
        
        # Score signals
        scored_signals = signal_scorer.score_signals(breaker_blocks, df)
        
        return scored_signals
        
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
        
        # Detect all signal types
        order_blocks = ob_detector.detect(
            df,
            min_body_size_factor=0.6,
            min_move_after_factor=1.5,
            confirmation_candles=3,
            strength_threshold=strength_threshold,
            max_results=max_results
        )
        
        fair_value_gaps = fvg_detector.detect(
            df,
            min_gap_factor=0.5,
            strength_threshold=strength_threshold,
            max_results=max_results
        )
        
        breaker_blocks = bb_detector.detect(
            df,
            min_strength=strength_threshold,
            max_results=max_results
        )
        
        # Score all signals
        scored_obs = signal_scorer.score_signals(order_blocks, df)
        scored_fvgs = signal_scorer.score_signals(fair_value_gaps, df)
        scored_bbs = signal_scorer.score_signals(breaker_blocks, df)
        
        # Return all signals
        return {
            "order_blocks": scored_obs,
            "fair_value_gaps": scored_fvgs,
            "breaker_blocks": scored_bbs
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
