"""
Breaker Blocks detection module.

This module implements the ICT concept of Breaker Blocks.
A Breaker Block is a former support/resistance level that has been broken
and is now being retested from the other side.
"""

from typing import List, Dict, Any, Tuple, Optional
import numpy as np
import pandas as pd
import MetaTrader5 as mt5
import logging

logger = logging.getLogger("ict_ultra_v2.signals.ict.breaker_blocks")

# Constants for breaker block detection
MIN_BODY_SIZE_FACTOR = 0.7  # Minimum candle body size as a factor of average body size
RETEST_THRESHOLD = 0.3  # Maximum distance for retest as a factor of average body size
MAX_LOOKBACK = 50  # Maximum lookback for breaker blocks


def find_breaker_blocks(
    symbol: str,
    timeframe: int,
    bars_count: int = 500,
    lookback_period: int = 100,
    strength_threshold: float = 0.6
) -> List[Dict[str, Any]]:
    """
    Find Breaker Blocks in the price data.
    
    Args:
        symbol: The trading symbol (e.g., "EURUSD")
        timeframe: The timeframe to analyze (e.g., mt5.TIMEFRAME_H1)
        bars_count: Number of bars to retrieve
        lookback_period: How far back to look for breaker blocks
        strength_threshold: Threshold for breaker block strength (0.0 to 1.0)
        
    Returns:
        List of dictionaries containing breaker block information
    """
    logger.info(f"Finding breaker blocks for {symbol} on timeframe {timeframe}")
    
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
    
    # Find swing highs and lows
    swings = _find_swings(df)
    
    # Find potential breaker blocks
    bullish_bbs = _find_bullish_breaker_blocks(df, swings, avg_body_size, lookback_period, strength_threshold)
    bearish_bbs = _find_bearish_breaker_blocks(df, swings, avg_body_size, lookback_period, strength_threshold)
    
    # Combine and sort by time (most recent first)
    all_bbs = bullish_bbs + bearish_bbs
    all_bbs.sort(key=lambda x: x['time'], reverse=True)
    
    logger.info(f"Found {len(all_bbs)} breaker blocks for {symbol}")
    return all_bbs


def _find_swings(df: pd.DataFrame, window: int = 5) -> Dict[str, List[int]]:
    """
    Find swing highs and lows in the price data.
    
    Args:
        df: DataFrame with price data
        window: Window size for swing detection
        
    Returns:
        Dictionary with swing high and low indices
    """
    highs = []
    lows = []
    
    for i in range(window, len(df) - window):
        # Check for swing high
        if all(df['high'].iloc[i] > df['high'].iloc[i-j] for j in range(1, window+1)) and \
           all(df['high'].iloc[i] > df['high'].iloc[i+j] for j in range(1, window+1)):
            highs.append(i)
        
        # Check for swing low
        if all(df['low'].iloc[i] < df['low'].iloc[i-j] for j in range(1, window+1)) and \
           all(df['low'].iloc[i] < df['low'].iloc[i+j] for j in range(1, window+1)):
            lows.append(i)
    
    return {"highs": highs, "lows": lows}


def _find_bullish_breaker_blocks(
    df: pd.DataFrame,
    swings: Dict[str, List[int]],
    avg_body_size: float,
    lookback_period: int,
    strength_threshold: float
) -> List[Dict[str, Any]]:
    """
    Find bullish breaker blocks.
    
    A bullish breaker block is a former resistance level that has been broken
    and is now being retested as support.
    
    Args:
        df: DataFrame with price data
        swings: Dictionary with swing high and low indices
        avg_body_size: Average candle body size
        lookback_period: How far back to look for breaker blocks
        strength_threshold: Threshold for breaker block strength
        
    Returns:
        List of dictionaries containing bullish breaker block information
    """
    bullish_bbs = []
    
    # We need at least a few candles
    if len(df) < 10:
        return bullish_bbs
    
    # Use swing highs as potential resistance levels
    for high_idx in swings["highs"]:
        # Check if we've gone beyond the lookback period
        if high_idx >= lookback_period:
            continue
        
        # This is the resistance level
        resistance_level = df['high'].iloc[high_idx]
        
        # Look for a break of this resistance
        break_idx = None
        for i in range(high_idx + 1, min(high_idx + MAX_LOOKBACK, len(df))):
            if df['close'].iloc[i] > resistance_level and df['is_bullish'].iloc[i]:
                if df['body_size'].iloc[i] >= MIN_BODY_SIZE_FACTOR * avg_body_size:
                    break_idx = i
                    break
        
        if break_idx is None:
            continue
        
        # Look for a retest of this level as support
        retest_idx = None
        for i in range(break_idx + 1, min(break_idx + MAX_LOOKBACK, len(df))):
            if abs(df['low'].iloc[i] - resistance_level) <= RETEST_THRESHOLD * avg_body_size:
                retest_idx = i
                break
        
        if retest_idx is None:
            continue
        
        # Calculate strength based on the break candle and subsequent price action
        break_strength = min(1.0, df['body_size'].iloc[break_idx] / (avg_body_size * 2))
        retest_strength = min(1.0, 1 - abs(df['low'].iloc[retest_idx] - resistance_level) / (avg_body_size * RETEST_THRESHOLD))
        strength = (break_strength + retest_strength) / 2
        
        if strength < strength_threshold:
            continue
        
        # This is a valid bullish breaker block
        bullish_bbs.append({
            'type': 'bullish',
            'time': df['time'].iloc[retest_idx],
            'price_level': resistance_level,
            'resistance_time': df['time'].iloc[high_idx],
            'break_time': df['time'].iloc[break_idx],
            'retest_time': df['time'].iloc[retest_idx],
            'strength': strength,
            'timeframe': df.iloc[high_idx].name,
            'symbol': df.iloc[high_idx].get('symbol', None)
        })
    
    return bullish_bbs


def _find_bearish_breaker_blocks(
    df: pd.DataFrame,
    swings: Dict[str, List[int]],
    avg_body_size: float,
    lookback_period: int,
    strength_threshold: float
) -> List[Dict[str, Any]]:
    """
    Find bearish breaker blocks.
    
    A bearish breaker block is a former support level that has been broken
    and is now being retested as resistance.
    
    Args:
        df: DataFrame with price data
        swings: Dictionary with swing high and low indices
        avg_body_size: Average candle body size
        lookback_period: How far back to look for breaker blocks
        strength_threshold: Threshold for breaker block strength
        
    Returns:
        List of dictionaries containing bearish breaker block information
    """
    bearish_bbs = []
    
    # We need at least a few candles
    if len(df) < 10:
        return bearish_bbs
    
    # Use swing lows as potential support levels
    for low_idx in swings["lows"]:
        # Check if we've gone beyond the lookback period
        if low_idx >= lookback_period:
            continue
        
        # This is the support level
        support_level = df['low'].iloc[low_idx]
        
        # Look for a break of this support
        break_idx = None
        for i in range(low_idx + 1, min(low_idx + MAX_LOOKBACK, len(df))):
            if df['close'].iloc[i] < support_level and df['is_bearish'].iloc[i]:
                if df['body_size'].iloc[i] >= MIN_BODY_SIZE_FACTOR * avg_body_size:
                    break_idx = i
                    break
        
        if break_idx is None:
            continue
        
        # Look for a retest of this level as resistance
        retest_idx = None
        for i in range(break_idx + 1, min(break_idx + MAX_LOOKBACK, len(df))):
            if abs(df['high'].iloc[i] - support_level) <= RETEST_THRESHOLD * avg_body_size:
                retest_idx = i
                break
        
        if retest_idx is None:
            continue
        
        # Calculate strength based on the break candle and subsequent price action
        break_strength = min(1.0, df['body_size'].iloc[break_idx] / (avg_body_size * 2))
        retest_strength = min(1.0, 1 - abs(df['high'].iloc[retest_idx] - support_level) / (avg_body_size * RETEST_THRESHOLD))
        strength = (break_strength + retest_strength) / 2
        
        if strength < strength_threshold:
            continue
        
        # This is a valid bearish breaker block
        bearish_bbs.append({
            'type': 'bearish',
            'time': df['time'].iloc[retest_idx],
            'price_level': support_level,
            'support_time': df['time'].iloc[low_idx],
            'break_time': df['time'].iloc[break_idx],
            'retest_time': df['time'].iloc[retest_idx],
            'strength': strength,
            'timeframe': df.iloc[low_idx].name,
            'symbol': df.iloc[low_idx].get('symbol', None)
        })
    
    return bearish_bbs


def is_breaker_block_valid(
    breaker_block: Dict[str, Any], 
    current_price: float
) -> bool:
    """
    Check if a breaker block is still valid based on the current price.
    
    Args:
        breaker_block: Breaker block information
        current_price: Current price to check against
        
    Returns:
        True if the breaker block is still valid, False otherwise
    """
    if breaker_block['type'] == 'bullish':
        # For bullish BB, price should be above the level
        return current_price > breaker_block['price_level']
    else:  # bearish
        # For bearish BB, price should be below the level
        return current_price < breaker_block['price_level'] 