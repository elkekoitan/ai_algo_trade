"""
ICT Signal Scoring Module.

This module implements a comprehensive scoring system for ICT signals,
taking into account multiple factors like trend strength, volume confirmation,
market structure quality, and more.
"""

from typing import Dict, Any, List, Optional, Union
import numpy as np
import pandas as pd
import MetaTrader5 as mt5
import logging
from datetime import datetime

logger = logging.getLogger("ict_ultra_v2.signals.ict.scoring")

# Scoring weights for different factors
SCORING_WEIGHTS = {
    "trend_strength": 0.20,
    "volume_confirmation": 0.15,
    "structure_quality": 0.15,
    "liquidity_presence": 0.10,
    "confluence_factor": 0.20,
    "time_of_day": 0.05,
    "market_sentiment": 0.05,
    "setup_strength": 0.10
}


def score_signals(
    signals: List[Dict[str, Any]],
    symbol: str,
    timeframe: int,
    additional_data: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Score ICT signals based on multiple factors.
    
    Args:
        signals: List of ICT signals (order blocks, FVGs, etc.)
        symbol: The trading symbol (e.g., "EURUSD")
        timeframe: The timeframe of the signals
        additional_data: Additional data for scoring (e.g., market sentiment)
        
    Returns:
        List of signals with added scoring information
    """
    if not signals:
        return []
    
    logger.info(f"Scoring {len(signals)} ICT signals for {symbol} on timeframe {timeframe}")
    
    # Get additional market data for scoring
    market_data = _get_market_data(symbol, timeframe)
    if not market_data:
        logger.warning(f"Could not get market data for scoring {symbol} signals")
        return signals
    
    # Score each signal
    scored_signals = []
    for signal in signals:
        scored_signal = signal.copy()
        
        # Calculate individual factor scores
        factor_scores = _calculate_factor_scores(signal, market_data, additional_data)
        
        # Calculate weighted total score
        total_score = 0
        for factor, score in factor_scores.items():
            weight = SCORING_WEIGHTS.get(factor, 0)
            total_score += score * weight
        
        # Normalize score to 0-100 range
        total_score = min(100, max(0, total_score * 100))
        
        # Add scores to the signal
        scored_signal["factor_scores"] = factor_scores
        scored_signal["score"] = round(total_score, 1)
        
        # Add risk level based on score
        scored_signal["risk_level"] = _get_risk_level(total_score)
        
        scored_signals.append(scored_signal)
    
    # Sort by score (highest first)
    scored_signals.sort(key=lambda x: x["score"], reverse=True)
    
    logger.info(f"Scored {len(scored_signals)} signals. Top score: {scored_signals[0]['score'] if scored_signals else 'N/A'}")
    return scored_signals


def _get_market_data(symbol: str, timeframe: int) -> Dict[str, Any]:
    """
    Get market data needed for signal scoring.
    
    Args:
        symbol: The trading symbol
        timeframe: The timeframe to analyze
        
    Returns:
        Dictionary with market data
    """
    try:
        # Get price data
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 200)
        if rates is None or len(rates) == 0:
            logger.error(f"Failed to get price data for {symbol}: {mt5.last_error()}")
            return {}
        
        # Convert to pandas DataFrame
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        # Calculate basic indicators
        df['body_size'] = abs(df['close'] - df['open'])
        df['is_bullish'] = df['close'] > df['open']
        df['is_bearish'] = df['close'] < df['open']
        
        # Calculate trend indicators
        df['sma20'] = df['close'].rolling(window=20).mean()
        df['sma50'] = df['close'].rolling(window=50).mean()
        df['trend'] = np.where(df['sma20'] > df['sma50'], 1, -1)
        
        # Calculate volatility
        df['atr'] = _calculate_atr(df, 14)
        
        # Calculate volume relative to average
        df['rel_volume'] = df['tick_volume'] / df['tick_volume'].rolling(window=20).mean()
        
        # Get current time
        current_time = datetime.now().time()
        
        return {
            "df": df,
            "current_price": df['close'].iloc[-1],
            "trend": df['trend'].iloc[-1],
            "atr": df['atr'].iloc[-1],
            "avg_body_size": df['body_size'].mean(),
            "current_time": current_time,
            "symbol": symbol,
            "timeframe": timeframe
        }
    except Exception as e:
        logger.error(f"Error getting market data for {symbol}: {e}")
        return {}


def _calculate_factor_scores(
    signal: Dict[str, Any],
    market_data: Dict[str, Any],
    additional_data: Optional[Dict[str, Any]] = None
) -> Dict[str, float]:
    """
    Calculate individual factor scores for a signal.
    
    Args:
        signal: The ICT signal to score
        market_data: Market data for scoring
        additional_data: Additional data for scoring
        
    Returns:
        Dictionary with factor scores (0.0 to 1.0)
    """
    factor_scores = {}
    
    # Get data from the market_data
    df = market_data.get("df")
    current_price = market_data.get("current_price")
    trend = market_data.get("trend")
    
    if df is None or current_price is None:
        return {factor: 0.5 for factor in SCORING_WEIGHTS}
    
    # 1. Trend Strength (0.0 to 1.0)
    # Higher score if signal aligns with the trend
    if "type" in signal:
        trend_alignment = (signal["type"] == "bullish" and trend > 0) or (signal["type"] == "bearish" and trend < 0)
        trend_strength = 0.8 if trend_alignment else 0.3
        factor_scores["trend_strength"] = trend_strength
    else:
        factor_scores["trend_strength"] = 0.5
    
    # 2. Volume Confirmation (0.0 to 1.0)
    # Higher score if volume is above average
    try:
        signal_time = signal.get("time")
        if signal_time and isinstance(df, pd.DataFrame) and not df.empty:
            # Find the closest time in the dataframe
            closest_idx = df['time'].searchsorted(signal_time)
            if closest_idx < len(df):
                rel_volume = df['rel_volume'].iloc[closest_idx]
                volume_score = min(1.0, rel_volume / 2)  # Normalize: 2x avg volume = 1.0 score
                factor_scores["volume_confirmation"] = volume_score
            else:
                factor_scores["volume_confirmation"] = 0.5
        else:
            factor_scores["volume_confirmation"] = 0.5
    except Exception:
        factor_scores["volume_confirmation"] = 0.5
    
    # 3. Structure Quality (0.0 to 1.0)
    # Use the signal's inherent strength if available
    factor_scores["structure_quality"] = signal.get("strength", 0.5)
    
    # 4. Liquidity Presence (0.0 to 1.0)
    # Higher score if the signal is at a key liquidity level
    # This is a simplified implementation
    factor_scores["liquidity_presence"] = 0.7  # Default assumption
    
    # 5. Confluence Factor (0.0 to 1.0)
    # Higher score if multiple signals align
    # This would need to be calculated based on other signals
    factor_scores["confluence_factor"] = additional_data.get("confluence_factor", 0.5) if additional_data else 0.5
    
    # 6. Time of Day (0.0 to 1.0)
    # Higher score during active market hours
    current_time = market_data.get("current_time")
    if current_time:
        # Simplified: higher scores during London/NY sessions
        hour = current_time.hour
        if 8 <= hour <= 16:  # Active trading hours (simplified)
            factor_scores["time_of_day"] = 0.9
        elif 4 <= hour <= 20:  # Extended trading hours
            factor_scores["time_of_day"] = 0.7
        else:  # Overnight
            factor_scores["time_of_day"] = 0.3
    else:
        factor_scores["time_of_day"] = 0.5
    
    # 7. Market Sentiment (0.0 to 1.0)
    # Use provided sentiment or default
    factor_scores["market_sentiment"] = additional_data.get("market_sentiment", 0.5) if additional_data else 0.5
    
    # 8. Setup Strength (0.0 to 1.0)
    # Based on signal type-specific metrics
    if signal.get("type") == "order_block":
        # Order blocks: based on the move after the block
        factor_scores["setup_strength"] = min(1.0, signal.get("strength", 0.5) * 1.2)
    elif signal.get("type") == "fair_value_gap":
        # FVGs: based on the gap size
        factor_scores["setup_strength"] = min(1.0, signal.get("gap_size", 0) / (market_data.get("avg_body_size", 1) * 3))
    else:
        factor_scores["setup_strength"] = signal.get("strength", 0.5)
    
    return factor_scores


def _calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calculate Average True Range (ATR).
    
    Args:
        df: DataFrame with OHLC data
        period: ATR period
        
    Returns:
        Series with ATR values
    """
    high = df['high']
    low = df['low']
    close = df['close'].shift(1)
    
    tr1 = high - low
    tr2 = (high - close).abs()
    tr3 = (low - close).abs()
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    
    return atr


def _get_risk_level(score: float) -> str:
    """
    Get risk level based on signal score.
    
    Args:
        score: Signal score (0-100)
        
    Returns:
        Risk level as string
    """
    if score >= 90:
        return "LOW"
    elif score >= 80:
        return "MEDIUM"
    elif score >= 70:
        return "HIGH"
    else:
        return "EXTREME" 