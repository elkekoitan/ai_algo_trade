"""
Gerçek ICT Analiz Motoru
SADECE gerçek MT5 verilerini kullanır
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class RealICTEngine:
    """
    Gerçek fiyat verilerine dayalı ICT analiz motoru
    SADECE MT5'ten gelen canlı verilerle çalışır
    """
    
    def __init__(self, mt5_service):
        self.mt5_service = mt5_service
        self.timeframes = {
            "M1": mt5.TIMEFRAME_M1,
            "M5": mt5.TIMEFRAME_M5,
            "M15": mt5.TIMEFRAME_M15,
            "M30": mt5.TIMEFRAME_M30,
            "H1": mt5.TIMEFRAME_H1,
            "H4": mt5.TIMEFRAME_H4,
            "D1": mt5.TIMEFRAME_D1
        }
        
    def _get_real_candles(self, symbol: str, timeframe: str, count: int = 500) -> pd.DataFrame:
        """Gerçek mum verilerini MT5'ten al"""
        try:
            if not self.mt5_service.is_connected():
                raise Exception("MT5 not connected")
            
            mt5_timeframe = self.timeframes.get(timeframe, mt5.TIMEFRAME_H1)
            rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, count)
            
            if rates is None:
                raise Exception(f"Failed to get candles for {symbol}")
            
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting real candles: {e}")
            return pd.DataFrame()
    
    def detect_order_blocks(self, symbol: str, timeframe: str = "H1") -> List[Dict[str, Any]]:
        """Gerçek verilerle Order Block tespiti"""
        try:
            df = self._get_real_candles(symbol, timeframe)
            if df.empty:
                return []
            
            order_blocks = []
            
            # Order Block algoritması
            for i in range(20, len(df) - 5):
                current_candle = df.iloc[i]
                
                # Bullish Order Block - Strong rejection candle followed by break upward
                if self._is_bullish_order_block(df, i):
                    order_blocks.append({
                        "id": f"ob_bull_{symbol}_{i}",
                        "type": "order_block",
                        "direction": "bullish",
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "price": float(current_candle['low']),
                        "high": float(current_candle['high']),
                        "low": float(current_candle['low']),
                        "time": current_candle.name.isoformat(),
                        "strength": self._calculate_strength(df, i),
                        "confidence": self._calculate_confidence(df, i),
                        "active": True,
                        "description": f"Bullish Order Block at {current_candle['low']:.5f}"
                    })
                
                # Bearish Order Block
                elif self._is_bearish_order_block(df, i):
                    order_blocks.append({
                        "id": f"ob_bear_{symbol}_{i}",
                        "type": "order_block",
                        "direction": "bearish",
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "price": float(current_candle['high']),
                        "high": float(current_candle['high']),
                        "low": float(current_candle['low']),
                        "time": current_candle.name.isoformat(),
                        "strength": self._calculate_strength(df, i),
                        "confidence": self._calculate_confidence(df, i),
                        "active": True,
                        "description": f"Bearish Order Block at {current_candle['high']:.5f}"
                    })
            
            # Son 10 Order Block'u döndür
            return order_blocks[-10:] if order_blocks else []
            
        except Exception as e:
            logger.error(f"Error detecting order blocks: {e}")
            return []
    
    def detect_fair_value_gaps(self, symbol: str, timeframe: str = "H1") -> List[Dict[str, Any]]:
        """Gerçek verilerle Fair Value Gap tespiti"""
        try:
            df = self._get_real_candles(symbol, timeframe)
            if df.empty:
                return []
            
            fair_value_gaps = []
            
            # FVG algoritması - 3 mum pattern
            for i in range(2, len(df) - 1):
                candle1 = df.iloc[i-2]  # First candle
                candle2 = df.iloc[i-1]  # Middle candle (gap)
                candle3 = df.iloc[i]    # Third candle
                
                # Bullish FVG - Gap between candle1 high and candle3 low
                if (candle1['high'] < candle3['low'] and 
                    abs(candle1['high'] - candle3['low']) > 0.0001):  # Minimum gap size
                    
                    fair_value_gaps.append({
                        "id": f"fvg_bull_{symbol}_{i}",
                        "type": "fair_value_gap",
                        "direction": "bullish",
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "high": float(candle3['low']),
                        "low": float(candle1['high']),
                        "time": candle2.name.isoformat(),
                        "strength": self._calculate_fvg_strength(candle1, candle3),
                        "confidence": 75,
                        "active": True,
                        "description": f"Bullish FVG {candle1['high']:.5f} - {candle3['low']:.5f}"
                    })
                
                # Bearish FVG - Gap between candle1 low and candle3 high
                elif (candle1['low'] > candle3['high'] and 
                      abs(candle1['low'] - candle3['high']) > 0.0001):
                    
                    fair_value_gaps.append({
                        "id": f"fvg_bear_{symbol}_{i}",
                        "type": "fair_value_gap",
                        "direction": "bearish",
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "high": float(candle1['low']),
                        "low": float(candle3['high']),
                        "time": candle2.name.isoformat(),
                        "strength": self._calculate_fvg_strength(candle1, candle3),
                        "confidence": 75,
                        "active": True,
                        "description": f"Bearish FVG {candle3['high']:.5f} - {candle1['low']:.5f}"
                    })
            
            # Son 10 FVG'yi döndür
            return fair_value_gaps[-10:] if fair_value_gaps else []
            
        except Exception as e:
            logger.error(f"Error detecting fair value gaps: {e}")
            return []
    
    def detect_breaker_blocks(self, symbol: str, timeframe: str = "H1") -> List[Dict[str, Any]]:
        """Gerçek verilerle Breaker Block tespiti"""
        try:
            df = self._get_real_candles(symbol, timeframe)
            if df.empty:
                return []
            
            breaker_blocks = []
            
            # Breaker Block algoritması
            for i in range(50, len(df) - 10):
                
                # Structure break pattern detection
                if self._is_structure_break(df, i):
                    current_candle = df.iloc[i]
                    
                    # Determine direction based on break
                    direction = "bullish" if current_candle['close'] > current_candle['open'] else "bearish"
                    
                    breaker_blocks.append({
                        "id": f"bb_{direction}_{symbol}_{i}",
                        "type": "breaker_block",
                        "direction": direction,
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "price": float(current_candle['close']),
                        "high": float(current_candle['high']),
                        "low": float(current_candle['low']),
                        "time": current_candle.name.isoformat(),
                        "strength": self._calculate_breaker_strength(df, i),
                        "confidence": 80,
                        "active": True,
                        "description": f"{direction.title()} Breaker Block at {current_candle['close']:.5f}"
                    })
            
            # Son 5 Breaker Block'u döndür
            return breaker_blocks[-5:] if breaker_blocks else []
            
        except Exception as e:
            logger.error(f"Error detecting breaker blocks: {e}")
            return []
    
    def get_all_signals(self, symbol: str, timeframe: str = "H1") -> List[Dict[str, Any]]:
        """Tüm ICT sinyallerini topla"""
        try:
            all_signals = []
            
            # Order Blocks
            order_blocks = self.detect_order_blocks(symbol, timeframe)
            all_signals.extend(order_blocks)
            
            # Fair Value Gaps
            fvgs = self.detect_fair_value_gaps(symbol, timeframe)
            all_signals.extend(fvgs)
            
            # Breaker Blocks
            breaker_blocks = self.detect_breaker_blocks(symbol, timeframe)
            all_signals.extend(breaker_blocks)
            
            # En son sinyalleri zaman sırasına göre sırala
            all_signals.sort(key=lambda x: x['time'], reverse=True)
            
            return all_signals
            
        except Exception as e:
            logger.error(f"Error getting all signals: {e}")
            return []
    
    def _is_bullish_order_block(self, df: pd.DataFrame, index: int) -> bool:
        """Bullish Order Block kontrolü"""
        try:
            current = df.iloc[index]
            
            # Strong bearish candle followed by bullish momentum
            body_size = abs(current['close'] - current['open'])
            wick_size = current['high'] - max(current['open'], current['close'])
            
            # Rejection criteria
            has_rejection = wick_size > body_size * 0.5
            is_hammer_like = current['low'] < min(current['open'], current['close']) - body_size * 0.3
            
            # Look for subsequent bullish momentum
            future_bullish = False
            for i in range(index + 1, min(index + 5, len(df))):
                if df.iloc[i]['close'] > current['high']:
                    future_bullish = True
                    break
            
            return has_rejection and is_hammer_like and future_bullish
            
        except:
            return False
    
    def _is_bearish_order_block(self, df: pd.DataFrame, index: int) -> bool:
        """Bearish Order Block kontrolü"""
        try:
            current = df.iloc[index]
            
            # Strong bullish candle followed by bearish momentum
            body_size = abs(current['close'] - current['open'])
            wick_size = min(current['open'], current['close']) - current['low']
            
            # Rejection criteria
            has_rejection = wick_size > body_size * 0.5
            is_shooting_star_like = current['high'] > max(current['open'], current['close']) + body_size * 0.3
            
            # Look for subsequent bearish momentum
            future_bearish = False
            for i in range(index + 1, min(index + 5, len(df))):
                if df.iloc[i]['close'] < current['low']:
                    future_bearish = True
                    break
            
            return has_rejection and is_shooting_star_like and future_bearish
            
        except:
            return False
    
    def _is_structure_break(self, df: pd.DataFrame, index: int) -> bool:
        """Structure break kontrolü"""
        try:
            lookback = 20
            start_idx = max(0, index - lookback)
            
            recent_highs = df.iloc[start_idx:index]['high'].max()
            recent_lows = df.iloc[start_idx:index]['low'].min()
            
            current = df.iloc[index]
            
            # High break (bullish structure break)
            bullish_break = current['close'] > recent_highs
            
            # Low break (bearish structure break)
            bearish_break = current['close'] < recent_lows
            
            return bullish_break or bearish_break
            
        except:
            return False
    
    def _calculate_strength(self, df: pd.DataFrame, index: int) -> int:
        """Sinyal gücünü hesapla (0-100)"""
        try:
            current = df.iloc[index]
            
            # Volume analysis
            avg_volume = df.iloc[max(0, index-20):index]['tick_volume'].mean()
            volume_strength = min(100, (current['tick_volume'] / avg_volume) * 50) if avg_volume > 0 else 50
            
            # Price action strength
            body_size = abs(current['close'] - current['open'])
            total_range = current['high'] - current['low']
            body_ratio = (body_size / total_range * 100) if total_range > 0 else 50
            
            # Combine metrics
            strength = int((volume_strength + body_ratio) / 2)
            return min(100, max(0, strength))
            
        except:
            return 50
    
    def _calculate_confidence(self, df: pd.DataFrame, index: int) -> int:
        """Sinyal güvenilirliğini hesapla (0-100)"""
        try:
            # Market structure analysis
            trend_strength = self._analyze_trend_strength(df, index)
            
            # Time of day factor (Higher confidence during major sessions)
            time_factor = 80  # Simplified
            
            # Historical success rate simulation
            historical_factor = 75
            
            confidence = int((trend_strength + time_factor + historical_factor) / 3)
            return min(100, max(0, confidence))
            
        except:
            return 70
    
    def _calculate_fvg_strength(self, candle1, candle3) -> int:
        """FVG gücünü hesapla"""
        try:
            gap_size = abs(candle1['high'] - candle3['low']) if candle1['high'] < candle3['low'] else abs(candle1['low'] - candle3['high'])
            
            # Normalize gap size to strength score
            body1 = abs(candle1['close'] - candle1['open'])
            body3 = abs(candle3['close'] - candle3['open'])
            avg_body = (body1 + body3) / 2
            
            if avg_body > 0:
                strength = min(100, int((gap_size / avg_body) * 30))
            else:
                strength = 50
            
            return max(30, strength)
            
        except:
            return 60
    
    def _calculate_breaker_strength(self, df: pd.DataFrame, index: int) -> int:
        """Breaker Block gücünü hesapla"""
        try:
            current = df.iloc[index]
            
            # Momentum analysis
            momentum_period = 10
            start_idx = max(0, index - momentum_period)
            
            price_change = abs(current['close'] - df.iloc[start_idx]['close'])
            avg_change = abs(df.iloc[start_idx:index]['close'].diff()).mean()
            
            if avg_change > 0:
                momentum_strength = min(100, int((price_change / avg_change) * 20))
            else:
                momentum_strength = 50
            
            return max(40, momentum_strength)
            
        except:
            return 70
    
    def _analyze_trend_strength(self, df: pd.DataFrame, index: int) -> int:
        """Trend gücünü analiz et"""
        try:
            lookback = 20
            start_idx = max(0, index - lookback)
            
            # Simple trend strength using price direction
            recent_closes = df.iloc[start_idx:index]['close']
            if len(recent_closes) < 2:
                return 50
            
            trend_slope = (recent_closes.iloc[-1] - recent_closes.iloc[0]) / len(recent_closes)
            
            # Normalize to 0-100 scale
            strength = min(100, max(0, int(abs(trend_slope) * 10000)))
            
            return strength
            
        except:
            return 50 