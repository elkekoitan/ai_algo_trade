"""
OpenBLAS-powered ICT analysis engine for high-performance signal detection.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import uuid

from backend.core.logger import setup_logger
from backend.core.config.settings import settings

# Initialize logger
logger = setup_logger("ict_openblas_engine")

# Try to import OpenBLAS optimized libraries
try:
    if settings.USE_OPENBLAS:
        # Set number of threads for OpenBLAS
        import os
        os.environ["OPENBLAS_NUM_THREADS"] = str(settings.OPENBLAS_THREADS)
        
        # Import optimized libraries
        from scipy import linalg
        logger.info(f"OpenBLAS engine initialized with {settings.OPENBLAS_THREADS} threads")
    else:
        logger.info("OpenBLAS optimization disabled")
except ImportError:
    logger.warning("OpenBLAS or SciPy not available, falling back to NumPy")


class ICTOpenBLASEngine:
    """
    High-performance ICT analysis engine using OpenBLAS optimization.
    """
    
    def __init__(self):
        """Initialize the ICT OpenBLAS engine."""
        self.use_openblas = settings.USE_OPENBLAS
        
    def detect_order_blocks(
        self, 
        df: pd.DataFrame, 
        min_body_size_factor: float = 0.6,
        min_move_after_factor: float = 1.5,
        confirmation_candles: int = 3,
        strength_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Detect order blocks in price data using optimized calculations.
        
        Args:
            df: DataFrame with OHLCV data
            min_body_size_factor: Minimum candle body size as factor of average
            min_move_after_factor: Minimum price move after the order block
            confirmation_candles: Number of candles to confirm the move
            strength_threshold: Minimum strength threshold (0-1)
            
        Returns:
            List of order block signals with metadata
        """
        # Convert to numpy arrays for faster processing
        opens = df['open'].to_numpy()
        highs = df['high'].to_numpy()
        lows = df['low'].to_numpy()
        closes = df['close'].to_numpy()
        times = df['time'].to_numpy()
        volumes = df['tick_volume'].to_numpy() if 'tick_volume' in df else np.ones_like(opens)
        
        # Calculate body sizes
        body_sizes = np.abs(closes - opens)
        avg_body_size = np.mean(body_sizes)
        
        # Calculate ATR for volatility normalization
        high_low = highs - lows
        high_close = np.abs(highs - np.roll(closes, 1))
        low_close = np.abs(lows - np.roll(closes, 1))
        
        # Stack the three series and find the max for each row
        ranges = np.vstack([high_low, high_close, low_close])
        true_ranges = np.max(ranges, axis=0)
        true_ranges[0] = true_ranges[1]  # Replace the first NaN
        
        atr = np.mean(true_ranges[-20:])  # 20-period ATR
        
        # Initialize results
        order_blocks = []
        
        # Find bullish order blocks (bearish candles before bullish moves)
        for i in range(len(df) - confirmation_candles - 1):
            # Check if this is a bearish candle
            if closes[i] >= opens[i]:
                continue
                
            # Check if body size is significant
            if body_sizes[i] < min_body_size_factor * avg_body_size:
                continue
                
            # Check the move after
            max_close = np.max(closes[i+1:i+1+confirmation_candles])
            move_size = max_close - closes[i]
            
            # Check if move is significant
            if move_size < min_move_after_factor * avg_body_size:
                continue
                
            # Calculate strength factors
            body_strength = min(1.0, body_sizes[i] / (avg_body_size * 2))
            move_strength = min(1.0, move_size / (avg_body_size * min_move_after_factor * 2))
            volume_strength = min(1.0, volumes[i] / np.mean(volumes) * 0.8)
            
            # Calculate confluence factors
            trend_strength = self._calculate_trend_strength(closes, i, 20, "bullish")
            structure_quality = self._calculate_structure_quality(highs, lows, i, 10)
            liquidity_presence = self._calculate_liquidity_presence(volumes, i, 5)
            
            # Calculate overall strength with weighted factors
            strength = (
                body_strength * 0.15 +
                move_strength * 0.20 +
                volume_strength * 0.15 +
                trend_strength * 0.20 +
                structure_quality * 0.15 +
                liquidity_presence * 0.10 +
                0.05  # Time of day factor (simplified)
            )
            
            # Skip if below threshold
            if strength < strength_threshold:
                continue
                
            # Create order block signal
            order_block = {
                "id": str(uuid.uuid4()),
                "type": "bullish",
                "entry_price": lows[i],
                "stop_loss": lows[i] - atr * 0.5,
                "take_profit": lows[i] + move_size * 1.5,
                "risk_reward_ratio": (move_size * 1.5) / (atr * 0.5),
                "strength": strength,
                "time": times[i],
                "body_size": body_sizes[i],
                "move_after": move_size,
                "confluence_factors": {
                    "body_strength": float(body_strength),
                    "move_strength": float(move_strength),
                    "volume_strength": float(volume_strength),
                    "trend_strength": float(trend_strength),
                    "structure_quality": float(structure_quality),
                    "liquidity_presence": float(liquidity_presence),
                }
            }
            
            order_blocks.append(order_block)
        
        # Find bearish order blocks (bullish candles before bearish moves)
        for i in range(len(df) - confirmation_candles - 1):
            # Check if this is a bullish candle
            if closes[i] <= opens[i]:
                continue
                
            # Check if body size is significant
            if body_sizes[i] < min_body_size_factor * avg_body_size:
                continue
                
            # Check the move after
            min_close = np.min(closes[i+1:i+1+confirmation_candles])
            move_size = closes[i] - min_close
            
            # Check if move is significant
            if move_size < min_move_after_factor * avg_body_size:
                continue
                
            # Calculate strength factors
            body_strength = min(1.0, body_sizes[i] / (avg_body_size * 2))
            move_strength = min(1.0, move_size / (avg_body_size * min_move_after_factor * 2))
            volume_strength = min(1.0, volumes[i] / np.mean(volumes) * 0.8)
            
            # Calculate confluence factors
            trend_strength = self._calculate_trend_strength(closes, i, 20, "bearish")
            structure_quality = self._calculate_structure_quality(highs, lows, i, 10)
            liquidity_presence = self._calculate_liquidity_presence(volumes, i, 5)
            
            # Calculate overall strength with weighted factors
            strength = (
                body_strength * 0.15 +
                move_strength * 0.20 +
                volume_strength * 0.15 +
                trend_strength * 0.20 +
                structure_quality * 0.15 +
                liquidity_presence * 0.10 +
                0.05  # Time of day factor (simplified)
            )
            
            # Skip if below threshold
            if strength < strength_threshold:
                continue
                
            # Create order block signal
            order_block = {
                "id": str(uuid.uuid4()),
                "type": "bearish",
                "entry_price": highs[i],
                "stop_loss": highs[i] + atr * 0.5,
                "take_profit": highs[i] - move_size * 1.5,
                "risk_reward_ratio": (move_size * 1.5) / (atr * 0.5),
                "strength": strength,
                "time": times[i],
                "body_size": body_sizes[i],
                "move_after": move_size,
                "confluence_factors": {
                    "body_strength": float(body_strength),
                    "move_strength": float(move_strength),
                    "volume_strength": float(volume_strength),
                    "trend_strength": float(trend_strength),
                    "structure_quality": float(structure_quality),
                    "liquidity_presence": float(liquidity_presence),
                }
            }
            
            order_blocks.append(order_block)
            
        return order_blocks
    
    def detect_fair_value_gaps(
        self, 
        df: pd.DataFrame,
        min_gap_factor: float = 0.5,
        strength_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Detect fair value gaps in price data.
        
        Args:
            df: DataFrame with OHLCV data
            min_gap_factor: Minimum gap size as factor of ATR
            strength_threshold: Minimum strength threshold (0-1)
            
        Returns:
            List of FVG signals with metadata
        """
        # Convert to numpy arrays for faster processing
        opens = df['open'].to_numpy()
        highs = df['high'].to_numpy()
        lows = df['low'].to_numpy()
        closes = df['close'].to_numpy()
        times = df['time'].to_numpy()
        
        # Calculate ATR for volatility normalization
        high_low = highs - lows
        high_close = np.abs(highs - np.roll(closes, 1))
        low_close = np.abs(lows - np.roll(closes, 1))
        
        ranges = np.vstack([high_low, high_close, low_close])
        true_ranges = np.max(ranges, axis=0)
        true_ranges[0] = true_ranges[1]
        
        atr = np.mean(true_ranges[-20:])
        
        # Initialize results
        fvgs = []
        
        # Find bullish FVGs (gap up)
        for i in range(1, len(df) - 1):
            # Check for gap up (current low > previous high)
            if lows[i] <= highs[i-1]:
                continue
                
            # Calculate gap size
            gap_size = lows[i] - highs[i-1]
            
            # Check if gap is significant
            if gap_size < min_gap_factor * atr:
                continue
                
            # Calculate strength factors
            gap_strength = min(1.0, gap_size / (atr * 2))
            trend_strength = self._calculate_trend_strength(closes, i, 20, "bullish")
            
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
                "entry_price": (lows[i] + highs[i-1]) / 2,  # Middle of gap
                "stop_loss": highs[i-1] - atr * 0.3,
                "take_profit": lows[i] + gap_size,
                "risk_reward_ratio": gap_size / (atr * 0.3),
                "strength": strength,
                "time": times[i],
                "gap_size": gap_size,
                "confluence_factors": {
                    "gap_strength": float(gap_strength),
                    "trend_strength": float(trend_strength),
                }
            }
            
            fvgs.append(fvg)
            
        # Find bearish FVGs (gap down)
        for i in range(1, len(df) - 1):
            # Check for gap down (current high < previous low)
            if highs[i] >= lows[i-1]:
                continue
                
            # Calculate gap size
            gap_size = lows[i-1] - highs[i]
            
            # Check if gap is significant
            if gap_size < min_gap_factor * atr:
                continue
                
            # Calculate strength factors
            gap_strength = min(1.0, gap_size / (atr * 2))
            trend_strength = self._calculate_trend_strength(closes, i, 20, "bearish")
            
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
                "entry_price": (highs[i] + lows[i-1]) / 2,  # Middle of gap
                "stop_loss": lows[i-1] + atr * 0.3,
                "take_profit": highs[i] - gap_size,
                "risk_reward_ratio": gap_size / (atr * 0.3),
                "strength": strength,
                "time": times[i],
                "gap_size": gap_size,
                "confluence_factors": {
                    "gap_strength": float(gap_strength),
                    "trend_strength": float(trend_strength),
                }
            }
            
            fvgs.append(fvg)
            
        return fvgs
    
    def detect_breaker_blocks(
        self, 
        df: pd.DataFrame,
        min_strength: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Detect breaker blocks in price data.
        
        Args:
            df: DataFrame with OHLCV data
            min_strength: Minimum strength threshold (0-1)
            
        Returns:
            List of breaker block signals with metadata
        """
        # First detect order blocks
        order_blocks = self.detect_order_blocks(
            df, 
            min_body_size_factor=0.5,
            min_move_after_factor=1.2,
            confirmation_candles=2,
            strength_threshold=0.6
        )
        
        # Filter for breaker blocks (order blocks that have been broken and retested)
        breaker_blocks = []
        
        for ob in order_blocks:
            # Skip low strength order blocks
            if ob["strength"] < 0.6:
                continue
                
            # Find the index of this order block
            ob_time = ob["time"]
            ob_index = np.where(df['time'].to_numpy() == ob_time)[0]
            
            if len(ob_index) == 0:
                continue
                
            ob_index = ob_index[0]
            
            # Check if price has broken through the order block
            if ob["type"] == "bullish":
                # For bullish OB, check if price went below the low
                price_series = df['low'].to_numpy()[ob_index+1:]
                broken = np.any(price_series < ob["entry_price"])
                
                if broken:
                    # Check if price returned to the level (retest)
                    break_index = np.where(price_series < ob["entry_price"])[0][0] + ob_index + 1
                    retest_series = df['high'].to_numpy()[break_index+1:]
                    retested = np.any(retest_series > ob["entry_price"])
                    
                    if retested:
                        # This is a breaker block
                        retest_index = np.where(retest_series > ob["entry_price"])[0][0] + break_index + 1
                        
                        # Calculate strength factors
                        break_strength = min(1.0, (ob["entry_price"] - np.min(price_series[:break_index-ob_index])) / ob["entry_price"] * 20)
                        retest_quality = min(1.0, 1 - abs(df.iloc[retest_index]['high'] - ob["entry_price"]) / ob["entry_price"] * 100)
                        
                        # Calculate overall strength
                        strength = (
                            ob["strength"] * 0.4 +
                            break_strength * 0.3 +
                            retest_quality * 0.3
                        )
                        
                        if strength >= min_strength:
                            breaker_block = {
                                "id": str(uuid.uuid4()),
                                "type": "bearish",  # Bullish OB becomes bearish breaker
                                "entry_price": ob["entry_price"],
                                "stop_loss": df.iloc[retest_index]['high'] * 1.005,
                                "take_profit": ob["entry_price"] - (ob["move_after"] * 0.8),
                                "risk_reward_ratio": (ob["move_after"] * 0.8) / (df.iloc[retest_index]['high'] * 0.005),
                                "strength": strength,
                                "time": df.iloc[retest_index]['time'],
                                "original_ob_time": ob["time"],
                                "confluence_factors": {
                                    "original_strength": float(ob["strength"]),
                                    "break_strength": float(break_strength),
                                    "retest_quality": float(retest_quality),
                                }
                            }
                            
                            breaker_blocks.append(breaker_block)
                            
            else:  # bearish order block
                # For bearish OB, check if price went above the high
                price_series = df['high'].to_numpy()[ob_index+1:]
                broken = np.any(price_series > ob["entry_price"])
                
                if broken:
                    # Check if price returned to the level (retest)
                    break_index = np.where(price_series > ob["entry_price"])[0][0] + ob_index + 1
                    retest_series = df['low'].to_numpy()[break_index+1:]
                    retested = np.any(retest_series < ob["entry_price"])
                    
                    if retested:
                        # This is a breaker block
                        retest_index = np.where(retest_series < ob["entry_price"])[0][0] + break_index + 1
                        
                        # Calculate strength factors
                        break_strength = min(1.0, (np.max(price_series[:break_index-ob_index]) - ob["entry_price"]) / ob["entry_price"] * 20)
                        retest_quality = min(1.0, 1 - abs(df.iloc[retest_index]['low'] - ob["entry_price"]) / ob["entry_price"] * 100)
                        
                        # Calculate overall strength
                        strength = (
                            ob["strength"] * 0.4 +
                            break_strength * 0.3 +
                            retest_quality * 0.3
                        )
                        
                        if strength >= min_strength:
                            breaker_block = {
                                "id": str(uuid.uuid4()),
                                "type": "bullish",  # Bearish OB becomes bullish breaker
                                "entry_price": ob["entry_price"],
                                "stop_loss": df.iloc[retest_index]['low'] * 0.995,
                                "take_profit": ob["entry_price"] + (ob["move_after"] * 0.8),
                                "risk_reward_ratio": (ob["move_after"] * 0.8) / (df.iloc[retest_index]['low'] * 0.005),
                                "strength": strength,
                                "time": df.iloc[retest_index]['time'],
                                "original_ob_time": ob["time"],
                                "confluence_factors": {
                                    "original_strength": float(ob["strength"]),
                                    "break_strength": float(break_strength),
                                    "retest_quality": float(retest_quality),
                                }
                            }
                            
                            breaker_blocks.append(breaker_block)
        
        return breaker_blocks
    
    def _calculate_trend_strength(self, closes: np.ndarray, index: int, period: int, direction: str) -> float:
        """Calculate trend strength based on price action."""
        if index < period:
            return 0.5  # Neutral if not enough data
            
        # Calculate simple moving averages
        sma_fast = np.mean(closes[index-10:index+1])
        sma_slow = np.mean(closes[index-period:index+1])
        
        # Calculate trend direction and strength
        if direction == "bullish":
            if sma_fast > sma_slow:
                # Bullish trend
                return min(1.0, (sma_fast / sma_slow - 1) * 20)
            else:
                # Counter-trend
                return max(0.2, 0.5 - (sma_slow / sma_fast - 1) * 10)
        else:  # bearish
            if sma_fast < sma_slow:
                # Bearish trend
                return min(1.0, (sma_slow / sma_fast - 1) * 20)
            else:
                # Counter-trend
                return max(0.2, 0.5 - (sma_fast / sma_slow - 1) * 10)
    
    def _calculate_structure_quality(self, highs: np.ndarray, lows: np.ndarray, index: int, period: int) -> float:
        """Calculate market structure quality."""
        if index < period:
            return 0.5
            
        # Find swing highs and lows
        swing_highs = []
        swing_lows = []
        
        for i in range(index - period + 2, index + 1):
            # Check for swing high
            if i > 0 and i < len(highs)-1:
                if highs[i-1] < highs[i] and highs[i] > highs[i+1]:
                    swing_highs.append(highs[i])
                    
                # Check for swing low
                if lows[i-1] > lows[i] and lows[i] < lows[i+1]:
                    swing_lows.append(lows[i])
        
        # Calculate structure quality based on number and alignment of swings
        if len(swing_highs) < 2 or len(swing_lows) < 2:
            return 0.5
            
        # Check for higher highs and higher lows (uptrend)
        higher_highs = swing_highs[-1] > swing_highs[0] if len(swing_highs) >= 2 else False
        higher_lows = swing_lows[-1] > swing_lows[0] if len(swing_lows) >= 2 else False
        
        # Check for lower highs and lower lows (downtrend)
        lower_highs = swing_highs[-1] < swing_highs[0] if len(swing_highs) >= 2 else False
        lower_lows = swing_lows[-1] < swing_lows[0] if len(swing_lows) >= 2 else False
        
        # Clear trend structure
        if (higher_highs and higher_lows) or (lower_highs and lower_lows):
            return 0.8
        # Mixed structure
        elif (higher_highs and not higher_lows) or (lower_lows and not lower_highs):
            return 0.6
        # Choppy structure
        else:
            return 0.4
    
    def _calculate_liquidity_presence(self, volumes: np.ndarray, index: int, period: int) -> float:
        """Calculate liquidity presence based on volume patterns."""
        if index < period:
            return 0.5
            
        # Get recent volumes
        recent_volumes = volumes[index-period:index+1]
        avg_volume = np.mean(recent_volumes)
        
        # Check for volume spike at current candle
        current_volume = volumes[index]
        
        if current_volume > avg_volume * 1.5:
            return min(1.0, current_volume / avg_volume * 0.5)
        elif current_volume > avg_volume:
            return 0.7
        else:
            return 0.5 