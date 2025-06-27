"""
Market Analyzer for Adaptive Trade Manager

Assesses real-time market conditions like volatility and regime.
"""
import asyncio
from typing import Dict, List, Any
import pandas as pd
import numpy as np

from backend.core.logger import get_logger
from backend.modules.mt5_integration.service import MT5Service
from .models import MarketCondition, MarketRegime

logger = get_logger(__name__)

class MarketAnalyzer:
    def __init__(self, mt5_service: MT5Service):
        self.mt5 = mt5_service
        self.market_conditions: Dict[str, MarketCondition] = {}
        self.lock = asyncio.Lock()
        self.tracked_symbols = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "BTCUSD"] # Symbols to analyze

    async def run(self):
        """Starts the continuous market analysis loop."""
        logger.info("Starting Market Analyzer...")
        while True:
            try:
                await self.analyze_all_symbols()
            except Exception as e:
                logger.error(f"Error in Market Analyzer loop: {e}")
            await asyncio.sleep(60) # Update every minute

    async def get_market_condition(self, symbol: str) -> MarketCondition:
        """Returns the current market condition for a symbol."""
        async with self.lock:
            return self.market_conditions.get(symbol, MarketCondition(
                symbol=symbol,
                regime=MarketRegime.RANGING,
                volatility=0.0,
                liquidity_level=0.5,
                sentiment_score=0.0,
                upcoming_events=[]
            ))

    async def analyze_all_symbols(self):
        """Fetches data and analyzes conditions for all tracked symbols."""
        if not self.mt5.connected:
            logger.warning("Market Analyzer: MT5 not connected. Skipping update.")
            return

        for symbol in self.tracked_symbols:
            try:
                # Fetch M15 data for the last 100 bars for analysis
                rates = self.mt5.get_rates(symbol, "M15", 100)
                if rates is None or rates.empty:
                    logger.warning(f"Could not fetch data for {symbol}")
                    continue
                
                volatility = self._calculate_volatility(rates)
                regime = self._determine_market_regime(rates, volatility)
                
                # These would be fetched from other sources in a full implementation
                liquidity = 0.8 
                sentiment = 0.2
                events = self._get_upcoming_events(symbol)

                condition = MarketCondition(
                    symbol=symbol,
                    regime=regime,
                    volatility=volatility,
                    liquidity_level=liquidity,
                    sentiment_score=sentiment,
                    upcoming_events=events
                )

                async with self.lock:
                    self.market_conditions[symbol] = condition
                
                logger.debug(f"Market analysis for {symbol}: Regime={regime.value}, Volatility={volatility:.5f}")

            except Exception as e:
                logger.error(f"Failed to analyze symbol {symbol}: {e}")

    def _calculate_volatility(self, rates: pd.DataFrame) -> float:
        """Calculates a normalized volatility index (e.g., using ATR)."""
        if rates.empty or len(rates) < 15:
            return 0.0
        
        # Calculate ATR
        high_low = rates['high'] - rates['low']
        high_close = np.abs(rates['high'] - rates['close'].shift())
        low_close = np.abs(rates['low'] - rates['close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.ewm(span=14, adjust=False).mean()
        
        # Normalize ATR
        last_price = rates['close'].iloc[-1]
        if last_price == 0: return 0.0
        
        normalized_atr = (atr.iloc[-1] / last_price) * 100
        return round(normalized_atr, 5)

    def _determine_market_regime(self, rates: pd.DataFrame, volatility: float) -> MarketRegime:
        """Determines the market regime (trending, ranging, volatile)."""
        if volatility > 0.15: # High volatility threshold
            return MarketRegime.VOLATILE

        # Use ADX for trend strength
        adx = self._calculate_adx(rates)
        
        if adx is not None and adx.get('adx', 0) > 25:
            if adx.get('plus_di', 0) > adx.get('minus_di', 0):
                return MarketRegime.TRENDING_UP
            else:
                return MarketRegime.TRENDING_DOWN
        
        return MarketRegime.RANGING

    def _calculate_adx(self, rates: pd.DataFrame, period: int = 14) -> Optional[Dict[str, float]]:
        """Calculates the Average Directional Index (ADX)."""
        if len(rates) < period * 2:
            return None

        df = rates.copy()
        df['tr'] = pd.concat([
            df['high'] - df['low'], 
            abs(df['high'] - df['close'].shift()), 
            abs(df['low'] - df['close'].shift())
        ], axis=1).max(axis=1)
        
        df['up_move'] = df['high'] - df['high'].shift()
        df['down_move'] = df['low'].shift() - df['low']
        
        df['plus_dm'] = np.where((df['up_move'] > df['down_move']) & (df['up_move'] > 0), df['up_move'], 0)
        df['minus_dm'] = np.where((df['down_move'] > df['up_move']) & (df['down_move'] > 0), df['down_move'], 0)

        df['plus_di'] = 100 * (df['plus_dm'].ewm(alpha=1/period).mean() / df['tr'].ewm(alpha=1/period).mean())
        df['minus_di'] = 100 * (df['minus_dm'].ewm(alpha=1/period).mean() / df['tr'].ewm(alpha=1/period).mean())
        
        df['dx'] = 100 * (abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di']))
        adx = df['dx'].ewm(alpha=1/period).mean()

        return {
            'adx': adx.iloc[-1],
            'plus_di': df['plus_di'].iloc[-1],
            'minus_di': df['minus_di'].iloc[-1],
        }

    def _get_upcoming_events(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Placeholder for fetching upcoming high-impact news events.
        In a real implementation, this would connect to an economic calendar API.
        """
        # Example for USD
        if "USD" in symbol and datetime.now().weekday() == 4: # Friday
            return [{
                "event": "Non-Farm Payrolls",
                "impact": 3,
                "time_to_event_minutes": 120
            }]
        return [] 