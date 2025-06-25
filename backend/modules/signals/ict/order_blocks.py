"""
Order Blocks detection module.

This module implements the ICT concept of Order Blocks.
Order blocks are areas on the chart where significant orders were placed
before a strong move in price, often serving as support/resistance in the future.
"""

from typing import List, Dict, Any, Tuple, Optional
import numpy as np
import pandas as pd
import MetaTrader5 as mt5
import logging

logger = logging.getLogger("ict_ultra_v2.signals.ict.order_blocks")

# Constants for order block detection
MIN_BODY_SIZE_FACTOR = 0.6  # Minimum candle body size as a factor of average body size
MIN_MOVE_AFTER_FACTOR = 1.5  # Minimum move after the order block as a factor of average body size
CONFIRMATION_CANDLES = 3  # Number of candles to confirm the move after the order block


def find_order_blocks(
    symbol: str,
    timeframe: int,
    bars_count: int = 500,
    lookback_period: int = 100,
    strength_threshold: float = 0.7
) -> List[Dict[str, Any]]:
    """
    Find Order Blocks in the price data.
    
    Args:
        symbol: The trading symbol (e.g., "EURUSD")
        timeframe: The timeframe to analyze (e.g., mt5.TIMEFRAME_H1)
        bars_count: Number of bars to retrieve
        lookback_period: How far back to look for order blocks
        strength_threshold: Threshold for order block strength (0.0 to 1.0)
        
    Returns:
        List of dictionaries containing order block information
    """
    logger.info(f"Finding order blocks for {symbol} on timeframe {timeframe}")
    
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
    
    # Find potential order blocks
    bullish_obs = _find_bullish_order_blocks(df, avg_body_size, lookback_period, strength_threshold)
    bearish_obs = _find_bearish_order_blocks(df, avg_body_size, lookback_period, strength_threshold)
    
    # Combine and sort by time (most recent first)
    all_obs = bullish_obs + bearish_obs
    all_obs.sort(key=lambda x: x['time'], reverse=True)
    
    logger.info(f"Found {len(all_obs)} order blocks for {symbol}")
    return all_obs


def _find_bullish_order_blocks(
    df: pd.DataFrame, 
    avg_body_size: float, 
    lookback_period: int,
    strength_threshold: float
) -> List[Dict[str, Any]]:
    """
    Find bullish order blocks (bearish candles before bullish moves).
    
    Args:
        df: DataFrame with price data
        avg_body_size: Average candle body size
        lookback_period: How far back to look for order blocks
        strength_threshold: Threshold for order block strength
        
    Returns:
        List of dictionaries containing bullish order block information
    """
    bullish_obs = []
    
    # We need at least CONFIRMATION_CANDLES + 1 candles
    if len(df) < CONFIRMATION_CANDLES + 1:
        return bullish_obs
    
    # Iterate through the dataframe, stopping CONFIRMATION_CANDLES before the end
    for i in range(len(df) - CONFIRMATION_CANDLES - 1):
        # Check if we've gone beyond the lookback period
        if i >= lookback_period:
            break
            
        # Check if this is a bearish candle (potential bullish order block)
        if not df.iloc[i]['is_bearish']:
            continue
            
        # Check if body size is significant
        if df.iloc[i]['body_size'] < MIN_BODY_SIZE_FACTOR * avg_body_size:
            continue
            
        # Check if the next candles show a bullish move
        next_candles = df.iloc[i+1:i+1+CONFIRMATION_CANDLES]
        if len(next_candles) < CONFIRMATION_CANDLES:
            continue
            
        # Calculate the move after the potential order block
        move_size = next_candles['close'].max() - df.iloc[i]['close']
        
        # Check if the move is significant
        if move_size < MIN_MOVE_AFTER_FACTOR * avg_body_size:
            continue
            
        # Calculate strength based on body size and subsequent move
        strength = min(1.0, (df.iloc[i]['body_size'] / avg_body_size) * 
                      (move_size / (MIN_MOVE_AFTER_FACTOR * avg_body_size)))
        
        if strength < strength_threshold:
            continue
            
        # This is a valid bullish order block
        bullish_obs.append({
            'type': 'bullish',
            'time': df.iloc[i]['time'],
            'price_high': df.iloc[i]['high'],
            'price_low': df.iloc[i]['low'],
            'price_open': df.iloc[i]['open'],
            'price_close': df.iloc[i]['close'],
            'strength': strength,
            'timeframe': df.iloc[i].name,
            'symbol': df.iloc[i].get('symbol', None)
        })
    
    return bullish_obs


def _find_bearish_order_blocks(
    df: pd.DataFrame, 
    avg_body_size: float, 
    lookback_period: int,
    strength_threshold: float
) -> List[Dict[str, Any]]:
    """
    Find bearish order blocks (bullish candles before bearish moves).
    
    Args:
        df: DataFrame with price data
        avg_body_size: Average candle body size
        lookback_period: How far back to look for order blocks
        strength_threshold: Threshold for order block strength
        
    Returns:
        List of dictionaries containing bearish order block information
    """
    bearish_obs = []
    
    # We need at least CONFIRMATION_CANDLES + 1 candles
    if len(df) < CONFIRMATION_CANDLES + 1:
        return bearish_obs
    
    # Iterate through the dataframe, stopping CONFIRMATION_CANDLES before the end
    for i in range(len(df) - CONFIRMATION_CANDLES - 1):
        # Check if we've gone beyond the lookback period
        if i >= lookback_period:
            break
            
        # Check if this is a bullish candle (potential bearish order block)
        if not df.iloc[i]['is_bullish']:
            continue
            
        # Check if body size is significant
        if df.iloc[i]['body_size'] < MIN_BODY_SIZE_FACTOR * avg_body_size:
            continue
            
        # Check if the next candles show a bearish move
        next_candles = df.iloc[i+1:i+1+CONFIRMATION_CANDLES]
        if len(next_candles) < CONFIRMATION_CANDLES:
            continue
            
        # Calculate the move after the potential order block
        move_size = df.iloc[i]['close'] - next_candles['close'].min()
        
        # Check if the move is significant
        if move_size < MIN_MOVE_AFTER_FACTOR * avg_body_size:
            continue
            
        # Calculate strength based on body size and subsequent move
        strength = min(1.0, (df.iloc[i]['body_size'] / avg_body_size) * 
                      (move_size / (MIN_MOVE_AFTER_FACTOR * avg_body_size)))
        
        if strength < strength_threshold:
            continue
            
        # This is a valid bearish order block
        bearish_obs.append({
            'type': 'bearish',
            'time': df.iloc[i]['time'],
            'price_high': df.iloc[i]['high'],
            'price_low': df.iloc[i]['low'],
            'price_open': df.iloc[i]['open'],
            'price_close': df.iloc[i]['close'],
            'strength': strength,
            'timeframe': df.iloc[i].name,
            'symbol': df.iloc[i].get('symbol', None)
        })
    
    return bearish_obs


def is_order_block_valid(
    order_block: Dict[str, Any], 
    current_price: float
) -> Tuple[bool, Optional[float]]:
    """
    Check if an order block is still valid based on the current price.
    
    Args:
        order_block: Order block information
        current_price: Current price to check against
        
    Returns:
        Tuple of (is_valid, distance_percentage)
    """
    if order_block['type'] == 'bullish':
        # For bullish OB, price should be above the OB
        if current_price < order_block['price_low']:
            return False, None
        
        # Calculate distance as percentage from OB zone to current price
        distance = (current_price - order_block['price_high']) / order_block['price_high'] * 100
        return True, distance
    else:  # bearish
        # For bearish OB, price should be below the OB
        if current_price > order_block['price_high']:
            return False, None
        
        # Calculate distance as percentage from OB zone to current price
        distance = (order_block['price_low'] - current_price) / order_block['price_low'] * 100
        return True, distance 