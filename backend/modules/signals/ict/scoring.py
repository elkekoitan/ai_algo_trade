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
from datetime import datetime, time

from backend.core.logger import setup_logger

# Initialize logger
logger = setup_logger("ict_signal_scoring")

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


class ICTSignalScorer:
    """
    Advanced scoring system for ICT trading signals.
    
    This class implements a comprehensive scoring system for ICT signals,
    taking into account multiple factors like trend alignment, volume confirmation,
    market structure quality, and more.
    """
    
    # Scoring factor weights (must sum to 1.0)
    DEFAULT_WEIGHTS = {
        "trend_strength": 0.20,         # 20% - Trend alignment
        "volume_confirmation": 0.15,    # 15% - Volume confirmation
        "structure_quality": 0.15,      # 15% - Market structure quality
        "liquidity_presence": 0.10,     # 10% - Liquidity presence
        "confluence_factor": 0.20,      # 20% - Confluence with other signals
        "time_of_day": 0.05,            # 5%  - Time of day (session)
        "market_sentiment": 0.05,       # 5%  - Market sentiment
        "setup_strength": 0.10          # 10% - Setup strength (pattern quality)
    }
    
    # Risk level thresholds
    RISK_LEVELS = {
        "LOW": 0.90,      # 90% and above - Low risk
        "MEDIUM": 0.80,   # 80-89% - Medium risk
        "HIGH": 0.70,     # 70-79% - High risk
        "EXTREME": 0.0    # Below 70% - Extreme risk
    }
    
    def __init__(self, custom_weights: Optional[Dict[str, float]] = None):
        """
        Initialize the ICT signal scorer.
        
        Args:
            custom_weights: Optional custom weights for scoring factors
        """
        self.weights = custom_weights if custom_weights else self.DEFAULT_WEIGHTS
        
        # Validate weights
        total_weight = sum(self.weights.values())
        if abs(total_weight - 1.0) > 0.001:
            logger.warning(f"Weights do not sum to 1.0 (sum: {total_weight}). Normalizing...")
            self.weights = {k: v / total_weight for k, v in self.weights.items()}
            
        logger.info("ICT signal scorer initialized with weights: " + 
                   ", ".join([f"{k}: {v:.2f}" for k, v in self.weights.items()]))
    
    def score_signal(
        self, 
        signal: Dict[str, Any],
        market_data: Optional[pd.DataFrame] = None,
        additional_factors: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Score an ICT trading signal based on multiple factors.
        
        Args:
            signal: The signal to score
            market_data: Optional market data for additional context
            additional_factors: Optional additional scoring factors
            
        Returns:
            Scored signal with additional metadata
        """
        # Make a copy of the signal to avoid modifying the original
        scored_signal = signal.copy()
        
        # Get existing confluence factors or initialize empty dict
        confluence_factors = scored_signal.get("confluence_factors", {})
        
        # Add additional factors if provided
        if additional_factors:
            confluence_factors.update(additional_factors)
            
        # Calculate missing factors if market data is provided
        if market_data is not None:
            self._calculate_missing_factors(confluence_factors, market_data, signal)
            
        # Calculate overall score
        score = 0.0
        for factor, weight in self.weights.items():
            factor_value = confluence_factors.get(factor, 0.5)  # Default to 0.5 if missing
            score += factor_value * weight
            
        # Ensure score is between 0 and 1
        score = max(0.0, min(1.0, score))
        
        # Update signal with score and risk level
        scored_signal["score"] = score
        scored_signal["risk_level"] = self._get_risk_level(score)
        scored_signal["confluence_factors"] = confluence_factors
        
        # Add score breakdown
        scored_signal["score_breakdown"] = {
            factor: {
                "value": confluence_factors.get(factor, 0.5),
                "weight": weight,
                "contribution": confluence_factors.get(factor, 0.5) * weight
            }
            for factor, weight in self.weights.items()
        }
        
        # Generate analysis text
        scored_signal["analysis"] = self._generate_analysis(scored_signal)
        
        logger.debug(f"Scored signal {signal.get('id', 'unknown')}: {score:.2f} ({scored_signal['risk_level']})")
        return scored_signal
    
    def score_signals(
        self, 
        signals: List[Dict[str, Any]],
        market_data: Optional[pd.DataFrame] = None,
        additional_factors: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """
        Score multiple ICT trading signals.
        
        Args:
            signals: List of signals to score
            market_data: Optional market data for additional context
            additional_factors: Optional additional scoring factors
            
        Returns:
            List of scored signals
        """
        return [self.score_signal(signal, market_data, additional_factors) for signal in signals]
    
    def _calculate_missing_factors(
        self, 
        factors: Dict[str, float], 
        market_data: pd.DataFrame,
        signal: Dict[str, Any]
    ) -> None:
        """Calculate missing scoring factors from market data."""
        # Get signal time
        signal_time = signal.get("time")
        if signal_time is None:
            return
            
        # Convert string time to datetime if needed
        if isinstance(signal_time, str):
            try:
                signal_time = datetime.fromisoformat(signal_time)
            except ValueError:
                return
        
        # Find the row index for this time
        if isinstance(market_data.index, pd.DatetimeIndex):
            # If index is datetime, use it directly
            idx = market_data.index.get_indexer([signal_time], method='nearest')[0]
        else:
            # Otherwise look for a time column
            if 'time' not in market_data.columns:
                return
                
            # Find nearest time
            idx = market_data['time'].sub(signal_time).abs().idxmin()
            
        if idx < 0 or idx >= len(market_data):
            return
            
        # Calculate trend strength if missing
        if "trend_strength" not in factors:
            factors["trend_strength"] = self._calculate_trend_strength(
                market_data, idx, signal.get("type", "bullish")
            )
            
        # Calculate volume confirmation if missing
        if "volume_confirmation" not in factors and any(col in market_data.columns for col in ['volume', 'tick_volume']):
            volume_col = 'volume' if 'volume' in market_data.columns else 'tick_volume'
            factors["volume_confirmation"] = self._calculate_volume_confirmation(
                market_data, idx, volume_col
            )
            
        # Calculate market structure quality if missing
        if "structure_quality" not in factors:
            factors["structure_quality"] = self._calculate_structure_quality(
                market_data, idx
            )
            
        # Calculate time of day factor if missing
        if "time_of_day" not in factors:
            factors["time_of_day"] = self._calculate_time_of_day(signal_time)
    
    def _calculate_trend_strength(
        self, 
        market_data: pd.DataFrame, 
        idx: int,
        signal_type: str
    ) -> float:
        """Calculate trend strength based on price action."""
        # Need at least 20 bars of data before the signal
        if idx < 20:
            return 0.5  # Neutral if not enough data
            
        # Calculate EMAs
        try:
            ema_fast = market_data['close'].iloc[max(0, idx-20):idx+1].ewm(span=8).mean().iloc[-1]
            ema_slow = market_data['close'].iloc[max(0, idx-20):idx+1].ewm(span=21).mean().iloc[-1]
            ema_trend = market_data['close'].iloc[max(0, idx-50):idx+1].ewm(span=50).mean().iloc[-1]
            
            # Calculate trend direction and strength
            if signal_type.lower() in ["bullish", "buy", "long"]:
                # For bullish signals, we want to see an uptrend
                if ema_fast > ema_slow > ema_trend:
                    # Strong uptrend
                    return min(1.0, 0.7 + (ema_fast / ema_slow - 1) * 5)
                elif ema_fast > ema_slow:
                    # Moderate uptrend
                    return min(0.9, 0.6 + (ema_fast / ema_slow - 1) * 5)
                elif ema_fast > ema_trend:
                    # Weak uptrend
                    return 0.6
                else:
                    # Counter-trend
                    return 0.4
            else:
                # For bearish signals, we want to see a downtrend
                if ema_fast < ema_slow < ema_trend:
                    # Strong downtrend
                    return min(1.0, 0.7 + (ema_slow / ema_fast - 1) * 5)
                elif ema_fast < ema_slow:
                    # Moderate downtrend
                    return min(0.9, 0.6 + (ema_slow / ema_fast - 1) * 5)
                elif ema_fast < ema_trend:
                    # Weak downtrend
                    return 0.6
                else:
                    # Counter-trend
                    return 0.4
        except Exception as e:
            logger.warning(f"Error calculating trend strength: {e}")
            return 0.5
    
    def _calculate_volume_confirmation(
        self, 
        market_data: pd.DataFrame, 
        idx: int,
        volume_col: str
    ) -> float:
        """Calculate volume confirmation factor."""
        try:
            # Get recent volumes
            recent_volumes = market_data[volume_col].iloc[max(0, idx-20):idx+1]
            avg_volume = recent_volumes.mean()
            
            # Check for volume spike at signal candle
            signal_volume = market_data[volume_col].iloc[idx]
            
            if signal_volume > avg_volume * 2:
                return min(1.0, 0.7 + signal_volume / avg_volume * 0.1)
            elif signal_volume > avg_volume * 1.5:
                return min(0.9, 0.6 + signal_volume / avg_volume * 0.1)
            elif signal_volume > avg_volume:
                return 0.6
            else:
                return 0.4
        except Exception as e:
            logger.warning(f"Error calculating volume confirmation: {e}")
            return 0.5
    
    def _calculate_structure_quality(
        self, 
        market_data: pd.DataFrame, 
        idx: int
    ) -> float:
        """Calculate market structure quality."""
        try:
            # Need at least 20 bars of data
            if idx < 20:
                return 0.5
                
            # Get recent price data
            recent_data = market_data.iloc[max(0, idx-20):idx+1]
            
            # Find swing highs and lows (simplified)
            highs = recent_data['high'].values
            lows = recent_data['low'].values
            
            swing_highs = []
            swing_lows = []
            
            for i in range(2, len(recent_data) - 2):
                # Check for swing high
                if highs[i] > highs[i-1] and highs[i] > highs[i-2] and highs[i] > highs[i+1] and highs[i] > highs[i+2]:
                    swing_highs.append(highs[i])
                
                # Check for swing low
                if lows[i] < lows[i-1] and lows[i] < lows[i-2] and lows[i] < lows[i+1] and lows[i] < lows[i+2]:
                    swing_lows.append(lows[i])
            
            # Need at least 2 swings to determine structure
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
                return 0.9
            # Mixed structure
            elif (higher_highs and not higher_lows) or (lower_lows and not lower_highs):
                return 0.7
            # Choppy structure
            else:
                return 0.4
        except Exception as e:
            logger.warning(f"Error calculating structure quality: {e}")
            return 0.5
    
    def _calculate_time_of_day(self, signal_time: datetime) -> float:
        """Calculate time of day factor based on forex sessions."""
        try:
            # Convert to time only
            t = signal_time.time()
            
            # Define forex sessions (UTC)
            tokyo_session = (time(0, 0), time(9, 0))  # 00:00-09:00 UTC
            london_session = (time(8, 0), time(17, 0))  # 08:00-17:00 UTC
            new_york_session = (time(13, 0), time(22, 0))  # 13:00-22:00 UTC
            
            # Check for session overlaps (highest liquidity)
            if (tokyo_session[0] <= t <= tokyo_session[1] and london_session[0] <= t <= london_session[1]) or \
               (london_session[0] <= t <= london_session[1] and new_york_session[0] <= t <= new_york_session[1]):
                return 0.9  # Session overlap
            
            # Check for main sessions
            if london_session[0] <= t <= london_session[1]:
                return 0.8  # London session
            if new_york_session[0] <= t <= new_york_session[1]:
                return 0.7  # New York session
            if tokyo_session[0] <= t <= tokyo_session[1]:
                return 0.6  # Tokyo session
                
            # Outside main sessions
            return 0.4
        except Exception as e:
            logger.warning(f"Error calculating time of day factor: {e}")
            return 0.5
    
    def _get_risk_level(self, score: float) -> str:
        """Get risk level based on score."""
        if score >= self.RISK_LEVELS["LOW"]:
            return "LOW"
        elif score >= self.RISK_LEVELS["MEDIUM"]:
            return "MEDIUM"
        elif score >= self.RISK_LEVELS["HIGH"]:
            return "HIGH"
        else:
            return "EXTREME"
    
    def _generate_analysis(self, signal: Dict[str, Any]) -> Dict[str, str]:
        """Generate analysis text for the scored signal."""
        signal_type = signal.get('type', 'unknown')
        score = signal.get('score', 0.0)
        risk_level = signal.get('risk_level', 'EXTREME')
        
        # Get factor values
        factors = signal.get('confluence_factors', {})
        trend_strength = factors.get('trend_strength', 0.5)
        volume_confirmation = factors.get('volume_confirmation', 0.5)
        structure_quality = factors.get('structure_quality', 0.5)
        
        # Generate trend analysis
        if trend_strength > 0.8:
            trend_analysis = f"Strong {'bullish' if signal_type == 'bullish' else 'bearish'} trend alignment"
        elif trend_strength > 0.6:
            trend_analysis = f"Moderate {'bullish' if signal_type == 'bullish' else 'bearish'} trend alignment"
        elif trend_strength > 0.4:
            trend_analysis = "Neutral trend conditions"
        else:
            trend_analysis = f"Counter-trend setup (against {'bullish' if signal_type == 'bearish' else 'bearish'} trend)"
            
        # Generate volume analysis
        if volume_confirmation > 0.8:
            volume_analysis = "Strong volume confirmation"
        elif volume_confirmation > 0.6:
            volume_analysis = "Good volume confirmation"
        elif volume_confirmation > 0.4:
            volume_analysis = "Average volume"
        else:
            volume_analysis = "Low volume confirmation"
            
        # Generate structure analysis
        if structure_quality > 0.8:
            structure_analysis = "High-quality market structure"
        elif structure_quality > 0.6:
            structure_analysis = "Good market structure"
        elif structure_quality > 0.4:
            structure_analysis = "Average market structure"
        else:
            structure_analysis = "Poor market structure"
            
        # Generate entry reasoning
        if score > 0.9:
            entry_reasoning = f"High-probability {signal_type} setup with excellent confluence factors"
        elif score > 0.8:
            entry_reasoning = f"Strong {signal_type} setup with good confluence"
        elif score > 0.7:
            entry_reasoning = f"Moderate {signal_type} setup, exercise caution"
        else:
            entry_reasoning = f"Lower probability {signal_type} setup, high risk"
            
        return {
            "trend_analysis": trend_analysis,
            "volume_analysis": volume_analysis,
            "structure_analysis": structure_analysis,
            "entry_reasoning": entry_reasoning,
            "risk_assessment": f"Risk level: {risk_level} (Score: {score:.2f})"
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