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
import uuid
from datetime import datetime

from backend.core.logger import setup_logger
from .openblas_engine import ICTOpenBLASEngine

# Initialize logger
logger = setup_logger("ict_fair_value_gaps")

# Constants for FVG detection
MIN_GAP_FACTOR = 0.5  # Minimum gap size as a factor of average body size
MAX_AGE_BARS = 50  # Maximum age of FVG in bars to be considered valid


class FairValueGapDetector:
    """
    Detector for ICT Fair Value Gaps (FVGs).
    
    Fair Value Gaps are areas on the chart where price has 'gapped' and left an
    imbalance between buyers and sellers, often serving as magnets for price to return to.
    """
    
    def __init__(self, use_openblas: bool = True):
        """
        Initialize the Fair Value Gap detector.
        
        Args:
            use_openblas: Whether to use OpenBLAS optimization
        """
        self.use_openblas = use_openblas
        self.engine = ICTOpenBLASEngine() if use_openblas else None
        logger.info(f"Fair Value Gap detector initialized (OpenBLAS: {use_openblas})")
        
    def detect(
        self, 
        df: pd.DataFrame,
        min_gap_factor: float = 0.5,
        strength_threshold: float = 0.7,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Detect fair value gaps in the given price data.
        
        Args:
            df: DataFrame with OHLCV data
            min_gap_factor: Minimum gap size as factor of ATR
            strength_threshold: Minimum strength threshold (0-1)
            max_results: Maximum number of results to return
            
        Returns:
            List of FVG signals with metadata
        """
        # Validate input data
        required_columns = ['open', 'high', 'low', 'close', 'time']
        if not all(col in df.columns for col in required_columns):
            logger.error(f"Missing required columns in dataframe: {required_columns}")
            return []
            
        # Use optimized engine if available
        if self.use_openblas and self.engine:
            logger.debug("Using OpenBLAS engine for FVG detection")
            fvgs = self.engine.detect_fair_value_gaps(
                df,
                min_gap_factor=min_gap_factor,
                strength_threshold=strength_threshold
            )
        else:
            logger.debug("Using standard algorithm for FVG detection")
            fvgs = self._detect_standard(
                df,
                min_gap_factor=min_gap_factor,
                strength_threshold=strength_threshold
            )
            
        # Sort by strength and limit results
        fvgs = sorted(fvgs, key=lambda x: x['strength'], reverse=True)[:max_results]
        
        # Enrich with additional metadata
        for fvg in fvgs:
            fvg['pattern_type'] = 'fair_value_gap'
            fvg['signal_type'] = 'BUY' if fvg['type'] == 'bullish' else 'SELL'
            fvg['timestamp'] = fvg['time'].isoformat() if isinstance(fvg['time'], datetime) else fvg['time']
            
            # Calculate risk level
            strength = fvg['strength']
            if strength >= 0.9:
                fvg['risk_level'] = 'LOW'
            elif strength >= 0.8:
                fvg['risk_level'] = 'MEDIUM'
            elif strength >= 0.7:
                fvg['risk_level'] = 'HIGH'
            else:
                fvg['risk_level'] = 'EXTREME'
                
            # Add analysis text
            fvg['analysis'] = self._generate_analysis(fvg)
            
        logger.info(f"Detected {len(fvgs)} fair value gaps with strength >= {strength_threshold}")
        return fvgs
        
    def _detect_standard(
        self, 
        df: pd.DataFrame,
        min_gap_factor: float = 0.5,
        strength_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Standard (non-optimized) algorithm for fair value gap detection.
        """
        # Calculate ATR for volatility normalization
        df['tr'] = np.maximum(
            df['high'] - df['low'],
            np.maximum(
                abs(df['high'] - df['close'].shift(1)),
                abs(df['low'] - df['close'].shift(1))
            )
        )
        df['atr'] = df['tr'].rolling(window=14).mean()
        
        # Fill first ATR value
        if pd.isna(df['atr'].iloc[0]):
            df['atr'].iloc[0] = df['tr'].iloc[0]
            
        # Fill remaining NaN values with forward fill
        df['atr'] = df['atr'].fillna(method='ffill')
        
        fvgs = []
        
        # Find bullish FVGs (gap up)
        for i in range(1, len(df) - 1):
            # Check for gap up (current low > previous high)
            if df.iloc[i]['low'] <= df.iloc[i-1]['high']:
                continue
                
            # Calculate gap size
            gap_size = df.iloc[i]['low'] - df.iloc[i-1]['high']
            
            # Check if gap is significant
            if gap_size < min_gap_factor * df.iloc[i]['atr']:
                continue
                
            # Calculate strength factors
            gap_strength = min(1.0, gap_size / (df.iloc[i]['atr'] * 2))
            
            # Calculate trend strength (simplified)
            prev_data = df.iloc[max(0, i-20):i]
            if len(prev_data) > 5:
                sma_fast = prev_data['close'][-5:].mean()
                sma_slow = prev_data['close'].mean()
                if sma_fast > sma_slow:
                    trend_strength = min(1.0, (sma_fast / sma_slow - 1) * 10)
                else:
                    trend_strength = max(0.3, 0.5 - (sma_slow / sma_fast - 1) * 5)
            else:
                trend_strength = 0.5
                
            # Calculate overall strength
            strength = (
                gap_strength * 0.4 +
                trend_strength * 0.3 +
                0.3  # Base strength for valid gap
            )
            
            # Skip if below threshold
            if strength < strength_threshold:
                continue
                
            # Create FVG signal
            fvg = {
                "id": str(uuid.uuid4()),
                "type": "bullish",
                "entry_price": (df.iloc[i]['low'] + df.iloc[i-1]['high']) / 2,  # Middle of gap
                "stop_loss": df.iloc[i-1]['high'] - df.iloc[i]['atr'] * 0.3,
                "take_profit": df.iloc[i]['low'] + gap_size,
                "risk_reward_ratio": gap_size / (df.iloc[i]['atr'] * 0.3),
                "strength": strength,
                "time": df.iloc[i]['time'],
                "gap_size": gap_size,
                "symbol": df.iloc[0].get('symbol', 'UNKNOWN'),
                "timeframe": df.iloc[0].get('timeframe', 'UNKNOWN'),
                "confluence_factors": {
                    "gap_strength": float(gap_strength),
                    "trend_strength": float(trend_strength),
                    "structure_quality": 0.7,  # Default value
                    "liquidity_presence": 0.5,  # Default value
                    "time_of_day": 0.5,  # Default value
                }
            }
            
            fvgs.append(fvg)
            
        # Find bearish FVGs (gap down)
        for i in range(1, len(df) - 1):
            # Check for gap down (current high < previous low)
            if df.iloc[i]['high'] >= df.iloc[i-1]['low']:
                continue
                
            # Calculate gap size
            gap_size = df.iloc[i-1]['low'] - df.iloc[i]['high']
            
            # Check if gap is significant
            if gap_size < min_gap_factor * df.iloc[i]['atr']:
                continue
                
            # Calculate strength factors
            gap_strength = min(1.0, gap_size / (df.iloc[i]['atr'] * 2))
            
            # Calculate trend strength (simplified)
            prev_data = df.iloc[max(0, i-20):i]
            if len(prev_data) > 5:
                sma_fast = prev_data['close'][-5:].mean()
                sma_slow = prev_data['close'].mean()
                if sma_fast < sma_slow:
                    trend_strength = min(1.0, (sma_slow / sma_fast - 1) * 10)
                else:
                    trend_strength = max(0.3, 0.5 - (sma_fast / sma_slow - 1) * 5)
            else:
                trend_strength = 0.5
                
            # Calculate overall strength
            strength = (
                gap_strength * 0.4 +
                trend_strength * 0.3 +
                0.3  # Base strength for valid gap
            )
            
            # Skip if below threshold
            if strength < strength_threshold:
                continue
                
            # Create FVG signal
            fvg = {
                "id": str(uuid.uuid4()),
                "type": "bearish",
                "entry_price": (df.iloc[i]['high'] + df.iloc[i-1]['low']) / 2,  # Middle of gap
                "stop_loss": df.iloc[i-1]['low'] + df.iloc[i]['atr'] * 0.3,
                "take_profit": df.iloc[i]['high'] - gap_size,
                "risk_reward_ratio": gap_size / (df.iloc[i]['atr'] * 0.3),
                "strength": strength,
                "time": df.iloc[i]['time'],
                "gap_size": gap_size,
                "symbol": df.iloc[0].get('symbol', 'UNKNOWN'),
                "timeframe": df.iloc[0].get('timeframe', 'UNKNOWN'),
                "confluence_factors": {
                    "gap_strength": float(gap_strength),
                    "trend_strength": float(trend_strength),
                    "structure_quality": 0.7,  # Default value
                    "liquidity_presence": 0.5,  # Default value
                    "time_of_day": 0.5,  # Default value
                }
            }
            
            fvgs.append(fvg)
            
        return fvgs
        
    def _generate_analysis(self, fvg: Dict[str, Any]) -> Dict[str, str]:
        """Generate analysis text for the fair value gap."""
        fvg_type = fvg['type']
        strength = fvg['strength']
        risk_level = fvg['risk_level']
        
        # Generate gap analysis
        gap_strength = fvg['confluence_factors'].get('gap_strength', 0.5)
        if gap_strength > 0.8:
            gap_analysis = f"Large {fvg_type} fair value gap with high probability of fill"
        elif gap_strength > 0.6:
            gap_analysis = f"Moderate {fvg_type} fair value gap with good probability of fill"
        else:
            gap_analysis = f"Small {fvg_type} fair value gap"
            
        # Generate trend analysis
        trend_strength = fvg['confluence_factors'].get('trend_strength', 0.5)
        if trend_strength > 0.8:
            trend_analysis = f"Strong {'bullish' if fvg_type == 'bullish' else 'bearish'} trend alignment"
        elif trend_strength > 0.6:
            trend_analysis = f"Moderate {'bullish' if fvg_type == 'bullish' else 'bearish'} trend alignment"
        elif trend_strength > 0.4:
            trend_analysis = "Neutral trend conditions"
        else:
            trend_analysis = f"Counter-trend setup (against {'bullish' if fvg_type == 'bearish' else 'bearish'} trend)"
            
        # Generate entry reasoning
        if strength > 0.9:
            entry_reasoning = f"High-probability {fvg_type} fair value gap with excellent confluence factors"
        elif strength > 0.8:
            entry_reasoning = f"Strong {fvg_type} fair value gap with good confluence"
        elif strength > 0.7:
            entry_reasoning = f"Moderate {fvg_type} fair value gap, exercise caution"
        else:
            entry_reasoning = f"Lower probability {fvg_type} fair value gap, high risk"
            
        return {
            "gap_analysis": gap_analysis,
            "trend_analysis": trend_analysis,
            "entry_reasoning": entry_reasoning
        }


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