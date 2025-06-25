"""
Breaker Block detection module for ICT Ultra v2.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from backend.core.logger import setup_logger
from .openblas_engine import ICTOpenBLASEngine
from .order_blocks import OrderBlockDetector

# Initialize logger
logger = setup_logger("ict_breaker_blocks")


class BreakerBlockDetector:
    """
    Detector for ICT Breaker Blocks.
    
    Breaker blocks are order blocks that have been broken and then retested,
    often creating high-probability trading opportunities.
    """
    
    def __init__(self, use_openblas: bool = True):
        """
        Initialize the Breaker Block detector.
        
        Args:
            use_openblas: Whether to use OpenBLAS optimization
        """
        self.use_openblas = use_openblas
        self.engine = ICTOpenBLASEngine() if use_openblas else None
        self.ob_detector = OrderBlockDetector(use_openblas=use_openblas)
        logger.info(f"Breaker Block detector initialized (OpenBLAS: {use_openblas})")
        
    def detect(
        self, 
        df: pd.DataFrame,
        min_strength: float = 0.7,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Detect breaker blocks in the given price data.
        
        Args:
            df: DataFrame with OHLCV data
            min_strength: Minimum strength threshold (0-1)
            max_results: Maximum number of results to return
            
        Returns:
            List of breaker block signals with metadata
        """
        # Validate input data
        required_columns = ['open', 'high', 'low', 'close', 'time']
        if not all(col in df.columns for col in required_columns):
            logger.error(f"Missing required columns in dataframe: {required_columns}")
            return []
            
        # Use optimized engine if available
        if self.use_openblas and self.engine:
            logger.debug("Using OpenBLAS engine for breaker block detection")
            breaker_blocks = self.engine.detect_breaker_blocks(
                df,
                min_strength=min_strength
            )
        else:
            logger.debug("Using standard algorithm for breaker block detection")
            breaker_blocks = self._detect_standard(
                df,
                min_strength=min_strength
            )
            
        # Sort by strength and limit results
        breaker_blocks = sorted(breaker_blocks, key=lambda x: x['strength'], reverse=True)[:max_results]
        
        # Enrich with additional metadata
        for bb in breaker_blocks:
            bb['pattern_type'] = 'breaker_block'
            bb['signal_type'] = 'BUY' if bb['type'] == 'bullish' else 'SELL'
            bb['timestamp'] = bb['time'].isoformat() if isinstance(bb['time'], datetime) else bb['time']
            
            # Calculate risk level
            strength = bb['strength']
            if strength >= 0.9:
                bb['risk_level'] = 'LOW'
            elif strength >= 0.8:
                bb['risk_level'] = 'MEDIUM'
            elif strength >= 0.7:
                bb['risk_level'] = 'HIGH'
            else:
                bb['risk_level'] = 'EXTREME'
                
            # Add analysis text
            bb['analysis'] = self._generate_analysis(bb)
            
        logger.info(f"Detected {len(breaker_blocks)} breaker blocks with strength >= {min_strength}")
        return breaker_blocks
        
    def _detect_standard(
        self, 
        df: pd.DataFrame,
        min_strength: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Standard (non-optimized) algorithm for breaker block detection.
        """
        # First detect order blocks with lower strength threshold
        order_blocks = self.ob_detector.detect(
            df,
            min_body_size_factor=0.5,
            min_move_after_factor=1.2,
            confirmation_candles=2,
            strength_threshold=0.6,
            max_results=100  # Get more OBs to find potential breaker blocks
        )
        
        # Filter for breaker blocks (order blocks that have been broken and retested)
        breaker_blocks = []
        
        for ob in order_blocks:
            # Skip low strength order blocks
            if ob["strength"] < 0.6:
                continue
                
            # Find the index of this order block in the dataframe
            ob_time = ob["time"]
            if isinstance(ob_time, str):
                try:
                    ob_time = datetime.fromisoformat(ob_time)
                except ValueError:
                    continue
                    
            # Find the row index for this time
            ob_index = df[df['time'] == ob_time].index
            if len(ob_index) == 0:
                continue
                
            ob_index = ob_index[0]
            
            # Check if there's enough data after this order block
            if ob_index >= len(df) - 5:
                continue
                
            # Check if price has broken through the order block
            if ob["type"] == "bullish":
                # For bullish OB, check if price went below the low
                future_data = df.iloc[ob_index+1:]
                broken_indices = future_data[future_data['low'] < ob["entry_price"]].index
                
                if len(broken_indices) == 0:
                    continue
                    
                # Get the first break
                break_index = broken_indices[0]
                
                # Check if price returned to the level (retest)
                if break_index >= len(df) - 3:
                    continue
                    
                retest_data = df.iloc[break_index+1:]
                retest_indices = retest_data[retest_data['high'] > ob["entry_price"]].index
                
                if len(retest_indices) == 0:
                    continue
                    
                # Get the first retest
                retest_index = retest_indices[0]
                
                # Calculate strength factors
                break_strength = min(1.0, (ob["entry_price"] - df.iloc[break_index]['low']) / ob["entry_price"] * 20)
                retest_quality = min(1.0, 1 - abs(df.iloc[retest_index]['high'] - ob["entry_price"]) / ob["entry_price"] * 100)
                
                # Calculate overall strength
                strength = (
                    ob["strength"] * 0.4 +
                    break_strength * 0.3 +
                    retest_quality * 0.3
                )
                
                if strength >= min_strength:
                    # Calculate ATR for stop loss
                    atr = df.iloc[retest_index].get('atr', None)
                    if atr is None or pd.isna(atr):
                        # Calculate ATR if not available
                        recent_data = df.iloc[max(0, retest_index-14):retest_index+1]
                        tr = np.maximum(
                            recent_data['high'] - recent_data['low'],
                            np.maximum(
                                abs(recent_data['high'] - recent_data['close'].shift(1)),
                                abs(recent_data['low'] - recent_data['close'].shift(1))
                            )
                        )
                        atr = tr.mean()
                    
                    # Create breaker block signal
                    breaker_block = {
                        "id": str(uuid.uuid4()),
                        "type": "bearish",  # Bullish OB becomes bearish breaker
                        "entry_price": ob["entry_price"],
                        "stop_loss": df.iloc[retest_index]['high'] * 1.005 if pd.isna(atr) else df.iloc[retest_index]['high'] + atr * 0.5,
                        "take_profit": ob["entry_price"] - (ob.get("move_after", atr * 2) * 0.8),
                        "risk_reward_ratio": (ob.get("move_after", atr * 2) * 0.8) / (atr * 0.5) if not pd.isna(atr) else 3.0,
                        "strength": strength,
                        "time": df.iloc[retest_index]['time'],
                        "original_ob_time": ob["time"],
                        "symbol": df.iloc[0].get('symbol', 'UNKNOWN'),
                        "timeframe": df.iloc[0].get('timeframe', 'UNKNOWN'),
                        "confluence_factors": {
                            "original_strength": float(ob["strength"]),
                            "break_strength": float(break_strength),
                            "retest_quality": float(retest_quality),
                            "trend_strength": ob["confluence_factors"].get("trend_strength", 0.5),
                            "structure_quality": ob["confluence_factors"].get("structure_quality", 0.7),
                        }
                    }
                    
                    breaker_blocks.append(breaker_block)
                    
            else:  # bearish order block
                # For bearish OB, check if price went above the high
                future_data = df.iloc[ob_index+1:]
                broken_indices = future_data[future_data['high'] > ob["entry_price"]].index
                
                if len(broken_indices) == 0:
                    continue
                    
                # Get the first break
                break_index = broken_indices[0]
                
                # Check if price returned to the level (retest)
                if break_index >= len(df) - 3:
                    continue
                    
                retest_data = df.iloc[break_index+1:]
                retest_indices = retest_data[retest_data['low'] < ob["entry_price"]].index
                
                if len(retest_indices) == 0:
                    continue
                    
                # Get the first retest
                retest_index = retest_indices[0]
                
                # Calculate strength factors
                break_strength = min(1.0, (df.iloc[break_index]['high'] - ob["entry_price"]) / ob["entry_price"] * 20)
                retest_quality = min(1.0, 1 - abs(df.iloc[retest_index]['low'] - ob["entry_price"]) / ob["entry_price"] * 100)
                
                # Calculate overall strength
                strength = (
                    ob["strength"] * 0.4 +
                    break_strength * 0.3 +
                    retest_quality * 0.3
                )
                
                if strength >= min_strength:
                    # Calculate ATR for stop loss
                    atr = df.iloc[retest_index].get('atr', None)
                    if atr is None or pd.isna(atr):
                        # Calculate ATR if not available
                        recent_data = df.iloc[max(0, retest_index-14):retest_index+1]
                        tr = np.maximum(
                            recent_data['high'] - recent_data['low'],
                            np.maximum(
                                abs(recent_data['high'] - recent_data['close'].shift(1)),
                                abs(recent_data['low'] - recent_data['close'].shift(1))
                            )
                        )
                        atr = tr.mean()
                    
                    # Create breaker block signal
                    breaker_block = {
                        "id": str(uuid.uuid4()),
                        "type": "bullish",  # Bearish OB becomes bullish breaker
                        "entry_price": ob["entry_price"],
                        "stop_loss": df.iloc[retest_index]['low'] * 0.995 if pd.isna(atr) else df.iloc[retest_index]['low'] - atr * 0.5,
                        "take_profit": ob["entry_price"] + (ob.get("move_after", atr * 2) * 0.8),
                        "risk_reward_ratio": (ob.get("move_after", atr * 2) * 0.8) / (atr * 0.5) if not pd.isna(atr) else 3.0,
                        "strength": strength,
                        "time": df.iloc[retest_index]['time'],
                        "original_ob_time": ob["time"],
                        "symbol": df.iloc[0].get('symbol', 'UNKNOWN'),
                        "timeframe": df.iloc[0].get('timeframe', 'UNKNOWN'),
                        "confluence_factors": {
                            "original_strength": float(ob["strength"]),
                            "break_strength": float(break_strength),
                            "retest_quality": float(retest_quality),
                            "trend_strength": ob["confluence_factors"].get("trend_strength", 0.5),
                            "structure_quality": ob["confluence_factors"].get("structure_quality", 0.7),
                        }
                    }
                    
                    breaker_blocks.append(breaker_block)
        
        return breaker_blocks
        
    def _generate_analysis(self, bb: Dict[str, Any]) -> Dict[str, str]:
        """Generate analysis text for the breaker block."""
        bb_type = bb['type']
        strength = bb['strength']
        risk_level = bb['risk_level']
        
        # Generate break analysis
        break_strength = bb['confluence_factors'].get('break_strength', 0.5)
        if break_strength > 0.8:
            break_analysis = f"Strong break of original order block with decisive price action"
        elif break_strength > 0.6:
            break_analysis = f"Clear break of original order block"
        else:
            break_analysis = f"Moderate break of original order block"
            
        # Generate retest analysis
        retest_quality = bb['confluence_factors'].get('retest_quality', 0.5)
        if retest_quality > 0.8:
            retest_analysis = f"High-quality retest with precise price reaction"
        elif retest_quality > 0.6:
            retest_analysis = f"Good retest with clear price reaction"
        else:
            retest_analysis = f"Acceptable retest with some price reaction"
            
        # Generate trend analysis
        trend_strength = bb['confluence_factors'].get('trend_strength', 0.5)
        if trend_strength > 0.8:
            trend_analysis = f"Strong {'bullish' if bb_type == 'bullish' else 'bearish'} trend alignment"
        elif trend_strength > 0.6:
            trend_analysis = f"Moderate {'bullish' if bb_type == 'bullish' else 'bearish'} trend alignment"
        elif trend_strength > 0.4:
            trend_analysis = "Neutral trend conditions"
        else:
            trend_analysis = f"Counter-trend setup (against {'bullish' if bb_type == 'bearish' else 'bearish'} trend)"
            
        # Generate entry reasoning
        if strength > 0.9:
            entry_reasoning = f"High-probability {bb_type} breaker block with excellent confluence factors"
        elif strength > 0.8:
            entry_reasoning = f"Strong {bb_type} breaker block with good confluence"
        elif strength > 0.7:
            entry_reasoning = f"Moderate {bb_type} breaker block, exercise caution"
        else:
            entry_reasoning = f"Lower probability {bb_type} breaker block, high risk"
            
        return {
            "break_analysis": break_analysis,
            "retest_analysis": retest_analysis,
            "trend_analysis": trend_analysis,
            "entry_reasoning": entry_reasoning
        } 