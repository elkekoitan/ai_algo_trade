"""
ICT Ultra Platform v4.0 - Advanced ICT Analysis Engine
World-class ICT trading analysis with ultra-fast performance
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import asyncio
import concurrent.futures
from dataclasses import dataclass
import json

@dataclass
class OrderBlock:
    """Order Block veri yapısı"""
    price: float
    volume: float
    timestamp: datetime
    type: str  # 'demand' or 'supply'
    strength: float  # 0-1 arası güç skoru
    zone_top: float
    zone_bottom: float

class AdvancedICTEngine:
    """Gelişmiş ICT Analiz Engine'i"""
    
    def __init__(self):
        self.forex_pairs = [
            'EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'USDCHF=X', 'AUDUSD=X',
            'USDCAD=X', 'NZDUSD=X', 'EURGBP=X', 'EURJPY=X', 'GBPJPY=X'
        ]
        self.timeframes = ['1h', '4h', '1d']
        
    async def get_market_data(self, symbol: str, period: str = "1mo", interval: str = "1h") -> pd.DataFrame:
        """Gerçek market data çekme - async"""
        try:
            yf_symbol = f"{symbol}=X" if not symbol.endswith('=X') else symbol
            ticker = yf.Ticker(yf_symbol)
            
            # Async olarak data çek
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                hist = await loop.run_in_executor(
                    executor, 
                    lambda: ticker.history(period=period, interval=interval)
                )
            
            if hist.empty:
                raise ValueError(f"No data found for {symbol}")
                
            return hist
            
        except Exception as e:
            raise Exception(f"Market data error for {symbol}: {str(e)}")
    
    def detect_order_blocks(self, df: pd.DataFrame, volume_threshold: float = 1.5) -> List[OrderBlock]:
        """Gelişmiş Order Block detection"""
        order_blocks = []
        
        if len(df) < 20:
            return order_blocks
            
        high = df['High'].values
        low = df['Low'].values
        close = df['Close'].values
        volume = df.get('Volume', pd.Series([1000] * len(df))).values
        timestamps = df.index
        
        # Volume analizi için moving average
        volume_ma = pd.Series(volume).rolling(window=20).mean().values
        
        for i in range(10, len(df) - 10):
            # Yüksek hacimli bölgeleri tespit et
            if volume[i] > volume_ma[i] * volume_threshold:
                
                # Order block zone hesapla
                zone_top = max(high[i-2:i+3])
                zone_bottom = min(low[i-2:i+3])
                zone_size = zone_top - zone_bottom
                
                # Minimum zone size kontrolü
                if zone_size > 0:
                    # Order block type belirleme
                    ob_type = "demand" if close[i] > close[i-1] else "supply"
                    
                    # Strength calculation
                    volume_strength = min(volume[i] / volume_ma[i], 5.0) / 5.0
                    price_action_strength = abs(close[i] - close[i-1]) / zone_size
                    strength = (volume_strength + price_action_strength) / 2
                    
                    order_block = OrderBlock(
                        price=close[i],
                        volume=volume[i],
                        timestamp=timestamps[i],
                        type=ob_type,
                        strength=min(strength, 1.0),
                        zone_top=zone_top,
                        zone_bottom=zone_bottom
                    )
                    
                    order_blocks.append(order_block)
        
        # En güçlü 10 order block'u döndür
        return sorted(order_blocks, key=lambda x: x.strength, reverse=True)[:10]
    
    def calculate_market_structure(self, df: pd.DataFrame) -> Dict:
        """Gelişmiş Market Structure Analysis"""
        if len(df) < 50:
            return {"error": "Insufficient data"}
            
        high = df['High'].values
        low = df['Low'].values
        close = df['Close'].values
        
        # Swing highs ve lows
        swing_highs = []
        swing_lows = []
        
        for i in range(5, len(high) - 5):
            # Swing high: 5 periyot öncesi ve sonrasından yüksek
            if all(high[i] > high[j] for j in range(i-5, i)) and \
               all(high[i] > high[j] for j in range(i+1, i+6)):
                swing_highs.append((i, high[i]))
                
            # Swing low: 5 periyot öncesi ve sonrasından düşük
            if all(low[i] < low[j] for j in range(i-5, i)) and \
               all(low[i] < low[j] for j in range(i+1, i+6)):
                swing_lows.append((i, low[i]))
        
        # Trend analysis
        if len(swing_highs) >= 3 and len(swing_lows) >= 3:
            recent_highs = swing_highs[-3:]
            recent_lows = swing_lows[-3:]
            
            # Higher highs & higher lows = bullish
            hh = all(recent_highs[i][1] > recent_highs[i-1][1] for i in range(1, len(recent_highs)))
            hl = all(recent_lows[i][1] > recent_lows[i-1][1] for i in range(1, len(recent_lows)))
            
            # Lower highs & lower lows = bearish
            lh = all(recent_highs[i][1] < recent_highs[i-1][1] for i in range(1, len(recent_highs)))
            ll = all(recent_lows[i][1] < recent_lows[i-1][1] for i in range(1, len(recent_lows)))
            
            if hh and hl:
                structure = "bullish"
                confidence = 0.9
            elif lh and ll:
                structure = "bearish"
                confidence = 0.9
            else:
                structure = "ranging"
                confidence = 0.5
        else:
            structure = "neutral"
            confidence = 0.3
        
        return {
            "structure": structure,
            "confidence": confidence,
            "swing_highs": len(swing_highs),
            "swing_lows": len(swing_lows),
            "trend_strength": confidence * 100
        }
    
    async def comprehensive_ict_analysis(self, symbol: str) -> Dict:
        """Kapsamlı ICT analizi - tüm bileşenler"""
        try:
            # Multi-timeframe analysis
            results = {}
            
            for timeframe in ['1h', '4h']:
                try:
                    # Data çek
                    if timeframe == '1h':
                        df = await self.get_market_data(symbol, period="1mo", interval="1h")
                    else:  # 4h
                        df = await self.get_market_data(symbol, period="3mo", interval="4h")
                    
                    # ICT bileşenleri analiz et
                    order_blocks = self.detect_order_blocks(df)
                    market_structure = self.calculate_market_structure(df)
                    
                    # Current price
                    current_price = float(df['Close'].iloc[-1])
                    
                    # ICT Score hesaplama
                    structure_score = market_structure.get('confidence', 0.5) * 50
                    ob_score = min(len(order_blocks) * 10, 50)
                    
                    ict_score = structure_score + ob_score
                    
                    results[timeframe] = {
                        "current_price": round(current_price, 5),
                        "order_blocks_count": len(order_blocks),
                        "market_structure": market_structure,
                        "ict_score": round(ict_score, 1)
                    }
                    
                except Exception as e:
                    results[timeframe] = {"error": str(e)}
            
            # Overall analysis
            overall_score = np.mean([
                results[tf].get('ict_score', 0) 
                for tf in results if 'ict_score' in results[tf]
            ])
            
            return {
                "symbol": symbol,
                "analysis_timestamp": datetime.now().isoformat(),
                "timeframes": results,
                "overall_ict_score": round(overall_score, 1),
                "data_source": "REAL - Yahoo Finance",
                "analysis_type": "Advanced ICT Multi-Timeframe"
            }
            
        except Exception as e:
            return {"error": f"Comprehensive ICT analysis failed: {str(e)}"}

# Global instance
ict_engine = AdvancedICTEngine()

# Test fonksiyonu
async def test_advanced_ict():
    """Gelişmiş ICT engine test"""
    print("Testing Advanced ICT Engine...")
    
    result = await ict_engine.comprehensive_ict_analysis("EURUSD")
    
    if "error" not in result:
        print("✅ Advanced ICT Analysis Success!")
        print(f"��� Overall ICT Score: {result['overall_ict_score']}%")
        print(f"��� Symbol: {result['symbol']}")
        
        for tf in result['timeframes']:
            if 'ict_score' in result['timeframes'][tf]:
                print(f"   {tf}: {result['timeframes'][tf]['ict_score']}%")
    else:
        print(f"❌ Error: {result['error']}")

if __name__ == "__main__":
    asyncio.run(test_advanced_ict())
