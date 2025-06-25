"""
Fair Value Gaps (FVG) detection module.

This module implements the ICT concept of Fair Value Gaps.
A Fair Value Gap occurs when price moves so quickly that it creates a gap
between the candles, indicating a strong imbalance between buyers and sellers.
"""

from typing import List, Dict, Any, Tuple, Optional
import numpy as np
import pandas as pd
import MetaTrader5 as mt5
import logging

logger = logging.getLogger("ict_ultra_v2.signals.ict.fair_value_gaps")

# Constants for FVG detection
MIN_GAP_FACTOR = 0.5  # Minimum gap size as a factor of average body size
MAX_AGE_BARS = 50  # Maximum age of FVG in bars to be considered valid


def find_fair_value_gaps(
    symbol: str,
    timeframe: int,
    bars_count: int = 500,
    lookback_period: int = 100,
    min_gap_factor: float = MIN_GAP_FACTOR
) -> List[Dict[str, Any]]:
    """
    Find Fair Value Gaps in the price data.
    
    Args:
        symbol: The trading symbol (e.g., "EURUSD")
        timeframe: The timeframe to analyze (e.g., mt5.TIMEFRAME_H1)
        bars_count: Number of bars to retrieve
        lookback_period: How far back to look for FVGs
        min_gap_factor: Minimum gap size as a factor of average body size
        
    Returns:
        List of dictionaries containing FVG information
    """
    logger.info(f"Finding fair value gaps for {symbol} on timeframe {timeframe}")
    
    # Get price data from MT5
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars_count)
    if rates is None or len(rates) == 0:
        logger.error(f"Failed to get price data for {symbol}: {mt5.last_error()}")
        return []
    
    # Convert to pandas DataFrame
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    
    # Calculate candle properties
    df['body_size'] = abs(df['close'] - df['open'])
    df['is_bullish'] = df['close'] > df['open']
    df['is_bearish'] = df['close'] < df['open']
    
    # Calculate average body size for reference
    avg_body_size = df['body_size'].mean()
    min_gap_size = min_gap_factor * avg_body_size
    
    # Find potential FVGs
    bullish_fvgs = _find_bullish_fvgs(df, min_gap_size, lookback_period)
    bearish_fvgs = _find_bearish_fvgs(df, min_gap_size, lookback_period)
    
    # Combine and sort by time (most recent first)
    all_fvgs = bullish_fvgs + bearish_fvgs
    all_fvgs.sort(key=lambda x: x['time'], reverse=True)
    
    logger.info(f"Found {len(all_fvgs)} fair value gaps for {symbol}")
    return all_fvgs


def _find_bullish_fvgs(
    df: pd.DataFrame, 
    min_gap_size: float, 
    lookback_period: int
) -> List[Dict[str, Any]]:
    """
    Find bullish fair value gaps (gaps to the upside).
    
    Args:
        df: DataFrame with price data
        min_gap_size: Minimum gap size
        lookback_period: How far back to look for FVGs
        
    Returns:
        List of dictionaries containing bullish FVG information
    """
    bullish_fvgs = []
    
    # We need at least 3 candles to find a FVG
    if len(df) < 3:
        return bullish_fvgs
    
    # Iterate through the dataframe, stopping 2 before the end
    for i in range(len(df) - 2):
        # Check if we've gone beyond the lookback period
        if i >= lookback_period:
            break
            
        # For bullish FVG, we need:
        # 1. First candle moving down (bearish)
        # 2. Second candle moving up (bullish)
        # 3. Gap between first candle's low and second candle's high
        
        # Check candle directions
        if not (df.iloc[i]['is_bearish'] and df.iloc[i+1]['is_bullish']):
            continue
            
        # Check for gap: first candle's low > second candle's high
        gap_size = df.iloc[i]['low'] - df.iloc[i+1]['high']
        if gap_size <= min_gap_size:
            continue
            
        # This is a valid bullish FVG
        fvg_top = df.iloc[i]['low']
        fvg_bottom = df.iloc[i+1]['high']
        
        # Calculate strength based on gap size relative to average
        strength = min(1.0, gap_size / (3 * min_gap_size))
        
        bullish_fvgs.append({
            'type': 'bullish',
            'time': df.iloc[i+1]['time'],
            'price_top': fvg_top,
            'price_bottom': fvg_bottom,
            'gap_size': gap_size,
            'strength': strength,
            'filled': False,
            'timeframe': timeframe_to_string(df.iloc[i].name),
            'symbol': df.iloc[i].get('symbol', None),
            'index': i+1  # Index in the dataframe
        })
    
    return bullish_fvgs


def _find_bearish_fvgs(
    df: pd.DataFrame, 
    min_gap_size: float, 
    lookback_period: int
) -> List[Dict[str, Any]]:
    """
    Find bearish fair value gaps (gaps to the downside).
    
    Args:
        df: DataFrame with price data
        min_gap_size: Minimum gap size
        lookback_period: How far back to look for FVGs
        
    Returns:
        List of dictionaries containing bearish FVG information
    """
    bearish_fvgs = []
    
    # We need at least 3 candles to find a FVG
    if len(df) < 3:
        return bearish_fvgs
    
    # Iterate through the dataframe, stopping 2 before the end
    for i in range(len(df) - 2):
        # Check if we've gone beyond the lookback period
        if i >= lookback_period:
            break
            
        # For bearish FVG, we need:
        # 1. First candle moving up (bullish)
        # 2. Second candle moving down (bearish)
        # 3. Gap between first candle's high and second candle's low
        
        # Check candle directions
        if not (df.iloc[i]['is_bullish'] and df.iloc[i+1]['is_bearish']):
            continue
            
        # Check for gap: first candle's high < second candle's low
        gap_size = df.iloc[i+1]['low'] - df.iloc[i]['high']
        if gap_size <= min_gap_size:
            continue
            
        # This is a valid bearish FVG
        fvg_top = df.iloc[i+1]['low']
        fvg_bottom = df.iloc[i]['high']
        
        # Calculate strength based on gap size relative to average
        strength = min(1.0, gap_size / (3 * min_gap_size))
        
        bearish_fvgs.append({
            'type': 'bearish',
            'time': df.iloc[i+1]['time'],
            'price_top': fvg_top,
            'price_bottom': fvg_bottom,
            'gap_size': gap_size,
            'strength': strength,
            'filled': False,
            'timeframe': timeframe_to_string(df.iloc[i].name),
            'symbol': df.iloc[i].get('symbol', None),
            'index': i+1  # Index in the dataframe
        })
    
    return bearish_fvgs


def is_fvg_filled(
    fvg: Dict[str, Any], 
    current_price: float
) -> bool:
    """
    Check if a Fair Value Gap is filled by the current price.
    
    Args:
        fvg: Fair Value Gap information
        current_price: Current price to check against
        
    Returns:
        True if the FVG is filled, False otherwise
    """
    if fvg['type'] == 'bullish':
        # For bullish FVG, it's filled when price moves down into the gap
        return current_price <= fvg['price_top'] and current_price >= fvg['price_bottom']
    else:  # bearish
        # For bearish FVG, it's filled when price moves up into the gap
        return current_price >= fvg['price_bottom'] and current_price <= fvg['price_top']


def timeframe_to_string(timeframe: int) -> str:
    """
    Convert MT5 timeframe constant to string representation.
    
    Args:
        timeframe: MT5 timeframe constant
        
    Returns:
        String representation of the timeframe
    """
    timeframe_map = {
        mt5.TIMEFRAME_M1: "M1",
        mt5.TIMEFRAME_M5: "M5",
        mt5.TIMEFRAME_M15: "M15",
        mt5.TIMEFRAME_M30: "M30",
        mt5.TIMEFRAME_H1: "H1",
        mt5.TIMEFRAME_H4: "H4",
        mt5.TIMEFRAME_D1: "D1",
        mt5.TIMEFRAME_W1: "W1",
        mt5.TIMEFRAME_MN1: "MN1"
    }
    return timeframe_map.get(timeframe, f"TF{timeframe}") 