"""
Order Block detection module for ICT Ultra v2.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from backend.core.logger import setup_logger
from .openblas_engine import ICTOpenBLASEngine

# Initialize logger
logger = setup_logger("ict_order_blocks")


class OrderBlockDetector:
    """
    Detector for ICT Order Blocks.
    
    Order blocks are areas on the chart where significant orders were placed 
    before a strong move in price, often serving as support/resistance in the future.
    """
    
    def __init__(self, use_openblas: bool = True):
        """
        Initialize the Order Block detector.
        
        Args:
            use_openblas: Whether to use OpenBLAS optimization
        """
        self.use_openblas = use_openblas
        self.engine = ICTOpenBLASEngine() if use_openblas else None
        logger.info(f"Order Block detector initialized (OpenBLAS: {use_openblas})")
        
    def detect(
        self, 
        df: pd.DataFrame,
        min_body_size_factor: float = 0.6,
        min_move_after_factor: float = 1.5,
        confirmation_candles: int = 3,
        strength_threshold: float = 0.7,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Detect order blocks in the given price data.
        
        Args:
            df: DataFrame with OHLCV data
            min_body_size_factor: Minimum candle body size as factor of average
            min_move_after_factor: Minimum price move after the order block
            confirmation_candles: Number of candles to confirm the move
            strength_threshold: Minimum strength threshold (0-1)
            max_results: Maximum number of results to return
            
        Returns:
            List of order block signals with metadata
        """
        # Validate input data
        required_columns = ['open', 'high', 'low', 'close', 'time']
        if not all(col in df.columns for col in required_columns):
            logger.error(f"Missing required columns in dataframe: {required_columns}")
            return []
            
        # Use optimized engine if available
        if self.use_openblas and self.engine:
            logger.debug("Using OpenBLAS engine for order block detection")
            order_blocks = self.engine.detect_order_blocks(
                df,
                min_body_size_factor=min_body_size_factor,
                min_move_after_factor=min_move_after_factor,
                confirmation_candles=confirmation_candles,
                strength_threshold=strength_threshold
            )
        else:
            logger.debug("Using standard algorithm for order block detection")
            order_blocks = self._detect_standard(
                df,
                min_body_size_factor=min_body_size_factor,
                min_move_after_factor=min_move_after_factor,
                confirmation_candles=confirmation_candles,
                strength_threshold=strength_threshold
            )
            
        # Sort by strength and limit results
        order_blocks = sorted(order_blocks, key=lambda x: x['strength'], reverse=True)[:max_results]
        
        # Enrich with additional metadata
        for ob in order_blocks:
            ob['pattern_type'] = 'order_block'
            ob['signal_type'] = 'BUY' if ob['type'] == 'bullish' else 'SELL'
            ob['timestamp'] = ob['time'].isoformat() if isinstance(ob['time'], datetime) else ob['time']
            
            # Calculate risk level
            strength = ob['strength']
            if strength >= 0.9:
                ob['risk_level'] = 'LOW'
            elif strength >= 0.8:
                ob['risk_level'] = 'MEDIUM'
            elif strength >= 0.7:
                ob['risk_level'] = 'HIGH'
            else:
                ob['risk_level'] = 'EXTREME'
                
            # Add analysis text
            ob['analysis'] = self._generate_analysis(ob)
            
        logger.info(f"Detected {len(order_blocks)} order blocks with strength >= {strength_threshold}")
        return order_blocks
        
    def _detect_standard(
        self, 
        df: pd.DataFrame,
        min_body_size_factor: float = 0.6,
        min_move_after_factor: float = 1.5,
        confirmation_candles: int = 3,
        strength_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Standard (non-optimized) algorithm for order block detection.
        """
        # Calculate average body size
        df['body_size'] = abs(df['close'] - df['open'])
        avg_body_size = df['body_size'].mean()
        
        # Calculate ATR
        df['tr'] = np.maximum(
            df['high'] - df['low'],
            np.maximum(
                abs(df['high'] - df['close'].shift(1)),
                abs(df['low'] - df['close'].shift(1))
            )
        )
        df['atr'] = df['tr'].rolling(window=14).mean()
        
        order_blocks = []
        
        # Find bullish order blocks (bearish candles before bullish moves)
        for i in range(len(df) - confirmation_candles - 1):
            row = df.iloc[i]
            
            # Check if this is a bearish candle
            if row['close'] >= row['open']:
                continue
                
            # Check if body size is significant
            if row['body_size'] < min_body_size_factor * avg_body_size:
                continue
                
            # Check the move after
            next_candles = df.iloc[i+1:i+1+confirmation_candles]
            max_close = next_candles['close'].max()
            move_size = max_close - row['close']
            
            # Check if move is significant
            if move_size < min_move_after_factor * avg_body_size:
                continue
                
            # Calculate strength factors
            body_strength = min(1.0, row['body_size'] / (avg_body_size * 2))
            move_strength = min(1.0, move_size / (avg_body_size * min_move_after_factor * 2))
            
            # Get volume if available
            volume_strength = 0.5
            if 'volume' in df.columns or 'tick_volume' in df.columns:
                volume_col = 'volume' if 'volume' in df.columns else 'tick_volume'
                avg_volume = df[volume_col].mean()
                current_volume = df.iloc[i][volume_col]
                volume_strength = min(1.0, current_volume / avg_volume * 0.8)
            
            # Calculate trend strength (simplified)
            prev_data = df.iloc[max(0, i-20):i]
            if len(prev_data) > 5:
                sma_fast = prev_data['close'][-5:].mean()
                sma_slow = prev_data['close'].mean()
                trend_strength = min(1.0, abs(sma_fast / sma_slow - 1) * 10)
            else:
                trend_strength = 0.5
                
            # Calculate overall strength
            strength = (
                body_strength * 0.2 +
                move_strength * 0.3 +
                volume_strength * 0.2 +
                trend_strength * 0.2 +
                0.1  # Base strength
            )
            
            # Skip if below threshold
            if strength < strength_threshold:
                continue
                
            # Create order block signal
            order_block = {
                "id": str(uuid.uuid4()),
                "type": "bullish",
                "entry_price": row['low'],
                "stop_loss": row['low'] - row['atr'] * 0.5 if not pd.isna(row['atr']) else row['low'] * 0.995,
                "take_profit": row['low'] + move_size * 1.5,
                "risk_reward_ratio": (move_size * 1.5) / (row['atr'] * 0.5) if not pd.isna(row['atr']) else 3.0,
                "strength": strength,
                "time": row['time'],
                "body_size": row['body_size'],
                "move_after": move_size,
                "symbol": df.iloc[0].get('symbol', 'UNKNOWN'),
                "timeframe": df.iloc[0].get('timeframe', 'UNKNOWN'),
                "confluence_factors": {
                    "trend_strength": trend_strength,
                    "volume_confirmation": volume_strength,
                    "structure_quality": 0.7,  # Default value
                    "liquidity_presence": 0.5,  # Default value
                    "confluence_factor": strength,
                    "time_of_day": 0.5,  # Default value
                    "market_sentiment": 0.5,  # Default value
                    "setup_strength": body_strength
                }
            }
            
            order_blocks.append(order_block)
            
        # Find bearish order blocks (bullish candles before bearish moves)
        for i in range(len(df) - confirmation_candles - 1):
            row = df.iloc[i]
            
            # Check if this is a bullish candle
            if row['close'] <= row['open']:
                continue
                
            # Check if body size is significant
            if row['body_size'] < min_body_size_factor * avg_body_size:
                continue
                
            # Check the move after
            next_candles = df.iloc[i+1:i+1+confirmation_candles]
            min_close = next_candles['close'].min()
            move_size = row['close'] - min_close
            
            # Check if move is significant
            if move_size < min_move_after_factor * avg_body_size:
                continue
                
            # Calculate strength factors
            body_strength = min(1.0, row['body_size'] / (avg_body_size * 2))
            move_strength = min(1.0, move_size / (avg_body_size * min_move_after_factor * 2))
            
            # Get volume if available
            volume_strength = 0.5
            if 'volume' in df.columns or 'tick_volume' in df.columns:
                volume_col = 'volume' if 'volume' in df.columns else 'tick_volume'
                avg_volume = df[volume_col].mean()
                current_volume = df.iloc[i][volume_col]
                volume_strength = min(1.0, current_volume / avg_volume * 0.8)
            
            # Calculate trend strength (simplified)
            prev_data = df.iloc[max(0, i-20):i]
            if len(prev_data) > 5:
                sma_fast = prev_data['close'][-5:].mean()
                sma_slow = prev_data['close'].mean()
                trend_strength = min(1.0, abs(sma_fast / sma_slow - 1) * 10)
            else:
                trend_strength = 0.5
                
            # Calculate overall strength
            strength = (
                body_strength * 0.2 +
                move_strength * 0.3 +
                volume_strength * 0.2 +
                trend_strength * 0.2 +
                0.1  # Base strength
            )
            
            # Skip if below threshold
            if strength < strength_threshold:
                continue
                
            # Create order block signal
            order_block = {
                "id": str(uuid.uuid4()),
                "type": "bearish",
                "entry_price": row['high'],
                "stop_loss": row['high'] + row['atr'] * 0.5 if not pd.isna(row['atr']) else row['high'] * 1.005,
                "take_profit": row['high'] - move_size * 1.5,
                "risk_reward_ratio": (move_size * 1.5) / (row['atr'] * 0.5) if not pd.isna(row['atr']) else 3.0,
                "strength": strength,
                "time": row['time'],
                "body_size": row['body_size'],
                "move_after": move_size,
                "symbol": df.iloc[0].get('symbol', 'UNKNOWN'),
                "timeframe": df.iloc[0].get('timeframe', 'UNKNOWN'),
                "confluence_factors": {
                    "trend_strength": trend_strength,
                    "volume_confirmation": volume_strength,
                    "structure_quality": 0.7,  # Default value
                    "liquidity_presence": 0.5,  # Default value
                    "confluence_factor": strength,
                    "time_of_day": 0.5,  # Default value
                    "market_sentiment": 0.5,  # Default value
                    "setup_strength": body_strength
                }
            }
            
            order_blocks.append(order_block)
            
        return order_blocks
        
    def _generate_analysis(self, order_block: Dict[str, Any]) -> Dict[str, str]:
        """Generate analysis text for the order block."""
        ob_type = order_block['type']
        strength = order_block['strength']
        risk_level = order_block['risk_level']
        
        # Generate trend analysis
        trend_strength = order_block['confluence_factors'].get('trend_strength', 0.5)
        if trend_strength > 0.8:
            trend_analysis = f"Strong {'bullish' if ob_type == 'bullish' else 'bearish'} trend alignment"
        elif trend_strength > 0.6:
            trend_analysis = f"Moderate {'bullish' if ob_type == 'bullish' else 'bearish'} trend alignment"
        elif trend_strength > 0.4:
            trend_analysis = "Neutral trend conditions"
        else:
            trend_analysis = f"Counter-trend setup (against {'bullish' if ob_type == 'bearish' else 'bearish'} trend)"
            
        # Generate volume analysis
        volume_confirmation = order_block['confluence_factors'].get('volume_confirmation', 0.5)
        if volume_confirmation > 0.8:
            volume_analysis = "Strong volume confirmation"
        elif volume_confirmation > 0.6:
            volume_analysis = "Good volume confirmation"
        elif volume_confirmation > 0.4:
            volume_analysis = "Average volume"
        else:
            volume_analysis = "Low volume confirmation"
            
        # Generate structure analysis
        structure_quality = order_block['confluence_factors'].get('structure_quality', 0.5)
        if structure_quality > 0.8:
            structure_analysis = "High-quality market structure"
        elif structure_quality > 0.6:
            structure_analysis = "Good market structure"
        elif structure_quality > 0.4:
            structure_analysis = "Average market structure"
        else:
            structure_analysis = "Poor market structure"
            
        # Generate entry reasoning
        if strength > 0.9:
            entry_reasoning = f"High-probability {ob_type} order block with excellent confluence factors"
        elif strength > 0.8:
            entry_reasoning = f"Strong {ob_type} order block with good confluence"
        elif strength > 0.7:
            entry_reasoning = f"Moderate {ob_type} order block, exercise caution"
        else:
            entry_reasoning = f"Lower probability {ob_type} order block, high risk"
            
        return {
            "trend_analysis": trend_analysis,
            "volume_analysis": volume_analysis,
            "structure_analysis": structure_analysis,
            "entry_reasoning": entry_reasoning
        } 