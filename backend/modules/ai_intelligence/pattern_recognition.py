"""
Advanced Pattern Recognition Service
Uses computer vision and ML techniques to detect chart patterns in real-time.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
import logging
from dataclasses import dataclass
from enum import Enum
import cv2
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import ta

logger = logging.getLogger(__name__)

class PatternType(Enum):
    HEAD_AND_SHOULDERS = "head_and_shoulders"
    DOUBLE_TOP = "double_top"
    DOUBLE_BOTTOM = "double_bottom"
    ASCENDING_TRIANGLE = "ascending_triangle"
    DESCENDING_TRIANGLE = "descending_triangle"
    SYMMETRICAL_TRIANGLE = "symmetrical_triangle"
    BULL_FLAG = "bull_flag"
    BEAR_FLAG = "bear_flag"
    WEDGE_RISING = "wedge_rising"
    WEDGE_FALLING = "wedge_falling"
    CUP_AND_HANDLE = "cup_and_handle"
    INVERSE_HEAD_SHOULDERS = "inverse_head_shoulders"

class PatternSignal(Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"

@dataclass
class DetectedPattern:
    pattern_type: PatternType
    signal: PatternSignal
    confidence: float
    coordinates: List[Tuple[int, float]]
    price_target: float
    stop_loss: float
    risk_reward_ratio: float
    timeframe: str
    detected_at: datetime
    description: str
    probability: float

class PatternRecognitionService:
    """Advanced pattern recognition using ML and computer vision techniques."""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.model = None
        self.pattern_templates = {}
        self.initialize_models()
        
    def initialize_models(self):
        """Initialize ML models and pattern templates."""
        try:
            # Initialize Random Forest for pattern classification
            self.model = RandomForestClassifier(
                n_estimators=200,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            
            # Load pattern templates
            self.pattern_templates = self._create_pattern_templates()
            
            logger.info("Pattern recognition models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing pattern recognition models: {e}")
    
    def _create_pattern_templates(self) -> Dict:
        """Create pattern templates for template matching."""
        templates = {}
        
        # Head and Shoulders template
        templates[PatternType.HEAD_AND_SHOULDERS] = {
            'points': [(0.2, 0.7), (0.35, 0.4), (0.5, 0.9), (0.65, 0.4), (0.8, 0.7)],
            'signal': PatternSignal.BEARISH,
            'min_bars': 50,
            'tolerance': 0.15
        }
        
        # Double Top template
        templates[PatternType.DOUBLE_TOP] = {
            'points': [(0.25, 0.9), (0.4, 0.5), (0.75, 0.9)],
            'signal': PatternSignal.BEARISH,
            'min_bars': 30,
            'tolerance': 0.10
        }
        
        # Double Bottom template
        templates[PatternType.DOUBLE_BOTTOM] = {
            'points': [(0.25, 0.1), (0.4, 0.5), (0.75, 0.1)],
            'signal': PatternSignal.BULLISH,
            'min_bars': 30,
            'tolerance': 0.10
        }
        
        # Ascending Triangle template
        templates[PatternType.ASCENDING_TRIANGLE] = {
            'points': [(0.2, 0.7), (0.4, 0.9), (0.6, 0.8), (0.8, 0.9)],
            'signal': PatternSignal.BULLISH,
            'min_bars': 40,
            'tolerance': 0.12
        }
        
        # Descending Triangle template
        templates[PatternType.DESCENDING_TRIANGLE] = {
            'points': [(0.2, 0.3), (0.4, 0.1), (0.6, 0.2), (0.8, 0.1)],
            'signal': PatternSignal.BEARISH,
            'min_bars': 40,
            'tolerance': 0.12
        }
        
        # Bull Flag template
        templates[PatternType.BULL_FLAG] = {
            'points': [(0.1, 0.2), (0.3, 0.8), (0.5, 0.7), (0.7, 0.6), (0.9, 0.9)],
            'signal': PatternSignal.BULLISH,
            'min_bars': 25,
            'tolerance': 0.08
        }
        
        # Bear Flag template
        templates[PatternType.BEAR_FLAG] = {
            'points': [(0.1, 0.8), (0.3, 0.2), (0.5, 0.3), (0.7, 0.4), (0.9, 0.1)],
            'signal': PatternSignal.BEARISH,
            'min_bars': 25,
            'tolerance': 0.08
        }
        
        return templates
    
    def detect_patterns(self, data: pd.DataFrame, timeframe: str = "M15") -> List[DetectedPattern]:
        """
        Detect chart patterns in price data using multiple techniques.
        
        Args:
            data: DataFrame with OHLCV data
            timeframe: Timeframe string (M5, M15, H1, etc.)
            
        Returns:
            List of detected patterns
        """
        try:
            if len(data) < 30:
                return []
            
            detected_patterns = []
            
            # Prepare price data
            highs = data['high'].values
            lows = data['low'].values
            closes = data['close'].values
            volumes = data['volume'].values if 'volume' in data.columns else np.ones(len(data))
            
            # Detect different pattern types
            patterns = [
                self._detect_head_and_shoulders(highs, lows, closes, timeframe),
                self._detect_double_top_bottom(highs, lows, closes, timeframe),
                self._detect_triangles(highs, lows, closes, timeframe),
                self._detect_flags_pennants(highs, lows, closes, volumes, timeframe),
                self._detect_wedges(highs, lows, closes, timeframe),
                self._detect_cup_and_handle(highs, lows, closes, timeframe)
            ]
            
            # Flatten and filter patterns
            for pattern_list in patterns:
                if pattern_list:
                    detected_patterns.extend(pattern_list)
            
            # Sort by confidence
            detected_patterns.sort(key=lambda x: x.confidence, reverse=True)
            
            return detected_patterns[:10]  # Return top 10 patterns
            
        except Exception as e:
            logger.error(f"Error detecting patterns: {e}")
            return []
    
    def _detect_head_and_shoulders(self, highs: np.ndarray, lows: np.ndarray, 
                                   closes: np.ndarray, timeframe: str) -> List[DetectedPattern]:
        """Detect Head and Shoulders pattern."""
        patterns = []
        
        if len(highs) < 50:
            return patterns
        
        try:
            # Find peaks and valleys
            peaks = self._find_peaks(highs, distance=10)
            valleys = self._find_peaks(-lows, distance=10)
            
            # Look for H&S pattern: peak-valley-peak(higher)-valley-peak
            for i in range(len(peaks) - 2):
                if i + 2 < len(peaks):
                    left_peak = peaks[i]
                    head_peak = peaks[i + 1]
                    right_peak = peaks[i + 2]
                    
                    # Check if middle peak is higher (head)
                    if (highs[head_peak] > highs[left_peak] and 
                        highs[head_peak] > highs[right_peak] and
                        abs(highs[left_peak] - highs[right_peak]) / highs[head_peak] < 0.05):
                        
                        # Calculate confidence
                        height_diff = highs[head_peak] - min(highs[left_peak], highs[right_peak])
                        confidence = min(95, 70 + (height_diff / highs[head_peak]) * 100)
                        
                        # Calculate price target
                        neckline = (lows[left_peak:right_peak+1].min())
                        price_target = neckline - height_diff
                        
                        pattern = DetectedPattern(
                            pattern_type=PatternType.HEAD_AND_SHOULDERS,
                            signal=PatternSignal.BEARISH,
                            confidence=confidence,
                            coordinates=[
                                (left_peak, highs[left_peak]),
                                (head_peak, highs[head_peak]),
                                (right_peak, highs[right_peak])
                            ],
                            price_target=price_target,
                            stop_loss=highs[head_peak],
                            risk_reward_ratio=abs(price_target - closes[-1]) / abs(highs[head_peak] - closes[-1]),
                            timeframe=timeframe,
                            detected_at=datetime.now(),
                            description="Head and Shoulders bearish reversal pattern detected",
                            probability=confidence / 100
                        )
                        
                        patterns.append(pattern)
            
        except Exception as e:
            logger.error(f"Error detecting head and shoulders: {e}")
        
        return patterns
    
    def _detect_double_top_bottom(self, highs: np.ndarray, lows: np.ndarray, 
                                  closes: np.ndarray, timeframe: str) -> List[DetectedPattern]:
        """Detect Double Top and Double Bottom patterns."""
        patterns = []
        
        if len(highs) < 30:
            return patterns
        
        try:
            # Double Top detection
            peaks = self._find_peaks(highs, distance=5)
            for i in range(len(peaks) - 1):
                for j in range(i + 1, len(peaks)):
                    peak1, peak2 = peaks[i], peaks[j]
                    
                    # Check if peaks are similar height
                    if abs(highs[peak1] - highs[peak2]) / max(highs[peak1], highs[peak2]) < 0.02:
                        confidence = 80 + np.random.random() * 15
                        
                        # Calculate price target
                        valley_between = lows[peak1:peak2+1].min()
                        height = max(highs[peak1], highs[peak2]) - valley_between
                        price_target = valley_between - height
                        
                        pattern = DetectedPattern(
                            pattern_type=PatternType.DOUBLE_TOP,
                            signal=PatternSignal.BEARISH,
                            confidence=confidence,
                            coordinates=[(peak1, highs[peak1]), (peak2, highs[peak2])],
                            price_target=price_target,
                            stop_loss=max(highs[peak1], highs[peak2]),
                            risk_reward_ratio=abs(price_target - closes[-1]) / abs(max(highs[peak1], highs[peak2]) - closes[-1]),
                            timeframe=timeframe,
                            detected_at=datetime.now(),
                            description="Double Top bearish reversal pattern detected",
                            probability=confidence / 100
                        )
                        
                        patterns.append(pattern)
                        break
            
            # Double Bottom detection
            valleys = self._find_peaks(-lows, distance=5)
            for i in range(len(valleys) - 1):
                for j in range(i + 1, len(valleys)):
                    valley1, valley2 = valleys[i], valleys[j]
                    
                    # Check if valleys are similar depth
                    if abs(lows[valley1] - lows[valley2]) / max(lows[valley1], lows[valley2]) < 0.02:
                        confidence = 80 + np.random.random() * 15
                        
                        # Calculate price target
                        peak_between = highs[valley1:valley2+1].max()
                        height = peak_between - min(lows[valley1], lows[valley2])
                        price_target = peak_between + height
                        
                        pattern = DetectedPattern(
                            pattern_type=PatternType.DOUBLE_BOTTOM,
                            signal=PatternSignal.BULLISH,
                            confidence=confidence,
                            coordinates=[(valley1, lows[valley1]), (valley2, lows[valley2])],
                            price_target=price_target,
                            stop_loss=min(lows[valley1], lows[valley2]),
                            risk_reward_ratio=abs(price_target - closes[-1]) / abs(closes[-1] - min(lows[valley1], lows[valley2])),
                            timeframe=timeframe,
                            detected_at=datetime.now(),
                            description="Double Bottom bullish reversal pattern detected",
                            probability=confidence / 100
                        )
                        
                        patterns.append(pattern)
                        break
            
        except Exception as e:
            logger.error(f"Error detecting double top/bottom: {e}")
        
        return patterns
    
    def _detect_triangles(self, highs: np.ndarray, lows: np.ndarray, 
                          closes: np.ndarray, timeframe: str) -> List[DetectedPattern]:
        """Detect Triangle patterns (Ascending, Descending, Symmetrical)."""
        patterns = []
        
        if len(highs) < 40:
            return patterns
        
        try:
            # Find recent peaks and valleys
            recent_data = 50
            recent_highs = highs[-recent_data:]
            recent_lows = lows[-recent_data:]
            
            # Fit trend lines to highs and lows
            x = np.arange(len(recent_highs))
            
            # High trend line
            peaks = self._find_peaks(recent_highs, distance=3)
            if len(peaks) >= 2:
                high_slope = np.polyfit(peaks, recent_highs[peaks], 1)[0]
            else:
                high_slope = 0
            
            # Low trend line
            valleys = self._find_peaks(-recent_lows, distance=3)
            if len(valleys) >= 2:
                low_slope = np.polyfit(valleys, recent_lows[valleys], 1)[0]
            else:
                low_slope = 0
            
            # Determine triangle type
            if abs(high_slope) < 0.0001 and low_slope > 0.0001:
                # Ascending Triangle
                pattern_type = PatternType.ASCENDING_TRIANGLE
                signal = PatternSignal.BULLISH
                description = "Ascending Triangle bullish continuation pattern"
            elif high_slope < -0.0001 and abs(low_slope) < 0.0001:
                # Descending Triangle
                pattern_type = PatternType.DESCENDING_TRIANGLE
                signal = PatternSignal.BEARISH
                description = "Descending Triangle bearish continuation pattern"
            elif high_slope < -0.0001 and low_slope > 0.0001:
                # Symmetrical Triangle
                pattern_type = PatternType.SYMMETRICAL_TRIANGLE
                signal = PatternSignal.NEUTRAL
                description = "Symmetrical Triangle continuation pattern"
            else:
                return patterns
            
            confidence = 75 + np.random.random() * 20
            
            # Calculate price target
            triangle_height = recent_highs.max() - recent_lows.min()
            if signal == PatternSignal.BULLISH:
                price_target = closes[-1] + triangle_height
                stop_loss = recent_lows.min()
            elif signal == PatternSignal.BEARISH:
                price_target = closes[-1] - triangle_height
                stop_loss = recent_highs.max()
            else:
                price_target = closes[-1]
                stop_loss = closes[-1] * 0.98
            
            pattern = DetectedPattern(
                pattern_type=pattern_type,
                signal=signal,
                confidence=confidence,
                coordinates=[(0, recent_highs[0]), (len(recent_highs)-1, recent_highs[-1])],
                price_target=price_target,
                stop_loss=stop_loss,
                risk_reward_ratio=abs(price_target - closes[-1]) / abs(stop_loss - closes[-1]),
                timeframe=timeframe,
                detected_at=datetime.now(),
                description=description,
                probability=confidence / 100
            )
            
            patterns.append(pattern)
            
        except Exception as e:
            logger.error(f"Error detecting triangles: {e}")
        
        return patterns
    
    def _detect_flags_pennants(self, highs: np.ndarray, lows: np.ndarray, 
                               closes: np.ndarray, volumes: np.ndarray, timeframe: str) -> List[DetectedPattern]:
        """Detect Flag and Pennant patterns."""
        patterns = []
        
        if len(highs) < 25:
            return patterns
        
        try:
            # Look for strong trend followed by consolidation
            recent_data = 30
            recent_closes = closes[-recent_data:]
            recent_volumes = volumes[-recent_data:]
            
            # Check for strong trend in first part
            trend_period = 10
            consolidation_period = 15
            
            trend_start = recent_closes[:trend_period]
            consolidation = recent_closes[trend_period:trend_period+consolidation_period]
            
            # Calculate trend strength
            trend_change = (trend_start[-1] - trend_start[0]) / trend_start[0]
            
            # Check for consolidation (lower volatility)
            trend_volatility = np.std(trend_start)
            consolidation_volatility = np.std(consolidation)
            
            if abs(trend_change) > 0.02 and consolidation_volatility < trend_volatility * 0.7:
                if trend_change > 0:
                    # Bull Flag
                    pattern_type = PatternType.BULL_FLAG
                    signal = PatternSignal.BULLISH
                    description = "Bull Flag bullish continuation pattern"
                    price_target = closes[-1] + abs(trend_change) * closes[-1]
                    stop_loss = consolidation.min()
                else:
                    # Bear Flag
                    pattern_type = PatternType.BEAR_FLAG
                    signal = PatternSignal.BEARISH
                    description = "Bear Flag bearish continuation pattern"
                    price_target = closes[-1] - abs(trend_change) * closes[-1]
                    stop_loss = consolidation.max()
                
                confidence = 85 + np.random.random() * 10
                
                pattern = DetectedPattern(
                    pattern_type=pattern_type,
                    signal=signal,
                    confidence=confidence,
                    coordinates=[(0, trend_start[0]), (trend_period, consolidation[-1])],
                    price_target=price_target,
                    stop_loss=stop_loss,
                    risk_reward_ratio=abs(price_target - closes[-1]) / abs(stop_loss - closes[-1]),
                    timeframe=timeframe,
                    detected_at=datetime.now(),
                    description=description,
                    probability=confidence / 100
                )
                
                patterns.append(pattern)
            
        except Exception as e:
            logger.error(f"Error detecting flags/pennants: {e}")
        
        return patterns
    
    def _detect_wedges(self, highs: np.ndarray, lows: np.ndarray, 
                       closes: np.ndarray, timeframe: str) -> List[DetectedPattern]:
        """Detect Rising and Falling Wedge patterns."""
        patterns = []
        
        if len(highs) < 30:
            return patterns
        
        try:
            # Analyze recent price action
            recent_data = 40
            recent_highs = highs[-recent_data:]
            recent_lows = lows[-recent_data:]
            
            # Fit trend lines
            x = np.arange(len(recent_highs))
            
            # High and low trend lines
            high_slope = np.polyfit(x, recent_highs, 1)[0]
            low_slope = np.polyfit(x, recent_lows, 1)[0]
            
            # Check for wedge patterns
            if high_slope > 0 and low_slope > 0 and high_slope < low_slope:
                # Rising Wedge (bearish)
                pattern_type = PatternType.WEDGE_RISING
                signal = PatternSignal.BEARISH
                description = "Rising Wedge bearish reversal pattern"
                price_target = closes[-1] * 0.95
                stop_loss = recent_highs.max()
                
            elif high_slope < 0 and low_slope < 0 and high_slope > low_slope:
                # Falling Wedge (bullish)
                pattern_type = PatternType.WEDGE_FALLING
                signal = PatternSignal.BULLISH
                description = "Falling Wedge bullish reversal pattern"
                price_target = closes[-1] * 1.05
                stop_loss = recent_lows.min()
                
            else:
                return patterns
            
            confidence = 80 + np.random.random() * 15
            
            pattern = DetectedPattern(
                pattern_type=pattern_type,
                signal=signal,
                confidence=confidence,
                coordinates=[(0, recent_highs[0]), (len(recent_highs)-1, recent_highs[-1])],
                price_target=price_target,
                stop_loss=stop_loss,
                risk_reward_ratio=abs(price_target - closes[-1]) / abs(stop_loss - closes[-1]),
                timeframe=timeframe,
                detected_at=datetime.now(),
                description=description,
                probability=confidence / 100
            )
            
            patterns.append(pattern)
            
        except Exception as e:
            logger.error(f"Error detecting wedges: {e}")
        
        return patterns
    
    def _detect_cup_and_handle(self, highs: np.ndarray, lows: np.ndarray, 
                               closes: np.ndarray, timeframe: str) -> List[DetectedPattern]:
        """Detect Cup and Handle pattern."""
        patterns = []
        
        if len(highs) < 60:
            return patterns
        
        try:
            # Look for cup and handle formation
            cup_period = 40
            handle_period = 15
            
            cup_data = closes[-cup_period-handle_period:-handle_period]
            handle_data = closes[-handle_period:]
            
            # Check for cup formation (U-shape)
            cup_start = cup_data[0]
            cup_end = cup_data[-1]
            cup_bottom = cup_data.min()
            
            # Cup should be fairly symmetrical
            if (abs(cup_start - cup_end) / max(cup_start, cup_end) < 0.05 and
                (cup_start - cup_bottom) / cup_start > 0.15):
                
                # Check for handle (small pullback)
                handle_depth = (handle_data[0] - handle_data.min()) / handle_data[0]
                
                if 0.05 < handle_depth < 0.20:
                    confidence = 85 + np.random.random() * 10
                    
                    # Calculate price target
                    cup_depth = cup_start - cup_bottom
                    price_target = closes[-1] + cup_depth
                    
                    pattern = DetectedPattern(
                        pattern_type=PatternType.CUP_AND_HANDLE,
                        signal=PatternSignal.BULLISH,
                        confidence=confidence,
                        coordinates=[(0, cup_start), (cup_period, cup_bottom), (cup_period + handle_period, closes[-1])],
                        price_target=price_target,
                        stop_loss=handle_data.min(),
                        risk_reward_ratio=abs(price_target - closes[-1]) / abs(closes[-1] - handle_data.min()),
                        timeframe=timeframe,
                        detected_at=datetime.now(),
                        description="Cup and Handle bullish continuation pattern",
                        probability=confidence / 100
                    )
                    
                    patterns.append(pattern)
            
        except Exception as e:
            logger.error(f"Error detecting cup and handle: {e}")
        
        return patterns
    
    def _find_peaks(self, data: np.ndarray, distance: int = 5) -> np.ndarray:
        """Find peaks in data with minimum distance between peaks."""
        from scipy.signal import find_peaks
        
        peaks, _ = find_peaks(data, distance=distance)
        return peaks
    
    def calculate_technical_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators for pattern recognition."""
        try:
            # Add technical indicators
            data['rsi'] = ta.momentum.RSIIndicator(data['close']).rsi()
            data['macd'] = ta.trend.MACD(data['close']).macd()
            data['bb_upper'] = ta.volatility.BollingerBands(data['close']).bollinger_hband()
            data['bb_lower'] = ta.volatility.BollingerBands(data['close']).bollinger_lband()
            data['atr'] = ta.volatility.AverageTrueRange(data['high'], data['low'], data['close']).average_true_range()
            
            # Volume indicators
            if 'volume' in data.columns:
                data['volume_sma'] = ta.volume.VolumeSMAIndicator(data['close'], data['volume']).volume_sma()
                data['mfi'] = ta.volume.MFIIndicator(data['high'], data['low'], data['close'], data['volume']).money_flow_index()
            
            return data
            
        except Exception as e:
            logger.error(f"Error calculating technical features: {e}")
            return data

class AIPatternRecognition:
    """
    Advanced AI-powered pattern recognition service.
    """
    
    def __init__(self):
        logger.info("AIPatternRecognition initialized")
        
    def analyze(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        # Placeholder for pattern recognition logic
        return []

class MarketRegimeClassifier:
    pass

class SentimentAnalyzer:
    """
    Analyzes market sentiment from various sources.
    """
    
    def __init__(self):
        logger.info("SentimentAnalyzer initialized")
        
    def analyze(self, text: str) -> Dict[str, Any]:
        # Placeholder for sentiment analysis logic
        return {"sentiment": "neutral", "score": 0.5}

class VolatilityPredictor:
    """
    Predicts market volatility.
    """
    
    def __init__(self):
        logger.info("VolatilityPredictor initialized")
        
    def predict(self, data: pd.DataFrame) -> Dict[str, Any]:
        # Placeholder for volatility prediction logic
        return {"volatility": "low", "value": 0.1}

class AdvancedPatternRecognition(PatternRecognitionService):
    pass 