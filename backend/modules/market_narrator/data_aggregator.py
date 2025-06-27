"""
Data Aggregator for the Market Narrator

Collects and unifies data from various sources (market data, news, etc.).
"""
import asyncio
from typing import List, Dict, Any
from datetime import datetime, timedelta

from backend.core.logger import get_logger
from backend.modules.mt5_integration.service import MT5Service
from .models import MarketEvent, EventType, AssetClass, Sentiment

logger = get_logger(__name__)

class DataAggregator:
    def __init__(self, mt5_service: MT5Service):
        self.mt5 = mt5_service

    async def gather_data(self) -> List[MarketEvent]:
        """
        Gathers data from all available sources and returns a unified list of market events.
        """
        # In a real application, these would run concurrently
        logger.info("Gathering data for Market Narrator...")
        
        technical_events = self._get_technical_events()
        economic_events = self._get_economic_events()
        news_events = self._get_news_events()
        
        all_events = technical_events + economic_events + news_events
        logger.info(f"Aggregated {len(all_events)} events.")
        
        return sorted(all_events, key=lambda x: x.timestamp, reverse=True)

    def _get_technical_events(self) -> List[MarketEvent]:
        """
        Analyzes MT5 data to find significant technical events.
        (Mock implementation)
        """
        events = []
        if self.mt5.connected:
            symbol = "EURUSD"
            rates = self.mt5.get_rates(symbol, "H1", 10)
            if not rates.empty:
                last_candle = rates.iloc[-1]
                if last_candle['close'] > 1.0800:
                    events.append(MarketEvent(
                        event_id=f"tech_eurusd_{int(datetime.now().timestamp())}",
                        timestamp=datetime.now(),
                        event_type=EventType.TECHNICAL,
                        asset_class=AssetClass.FX,
                        symbol=symbol,
                        headline=f"{symbol} breaks above key 1.0800 resistance",
                        summary="The price of EURUSD has decisively moved above the 1.0800 level, a significant psychological and technical resistance point.",
                        sentiment=Sentiment.POSITIVE,
                        data={"level": 1.0800, "price": last_candle['close']}
                    ))
        return events

    def _get_economic_events(self) -> List[MarketEvent]:
        """
        Fetches major economic events.
        (Mock implementation using a static list)
        """
        # This would come from an economic calendar API
        mock_event = {
            "name": "US Core CPI (MoM)",
            "country": "USD",
            "actual": "0.4%",
            "forecast": "0.3%",
            "previous": "0.2%"
        }
        
        is_higher = float(mock_event['actual'].strip('%')) > float(mock_event['forecast'].strip('%'))
        
        return [MarketEvent(
            event_id=f"econ_cpi_{int(datetime.now().timestamp())}",
            timestamp=datetime.now() - timedelta(hours=1),
            event_type=EventType.ECONOMIC,
            asset_class=AssetClass.INDEX,
            symbol="DXY",
            headline="US Inflation Comes In Hotter Than Expected",
            summary=f"US Core CPI rose by {mock_event['actual']}, surprising markets which had forecast a {mock_event['forecast']} rise. This indicates persistent inflationary pressures.",
            sentiment=Sentiment.POSITIVE if is_higher else Sentiment.NEGATIVE, # Positive for USD
            data=mock_event
        )]

    def _get_news_events(self) -> List[MarketEvent]:
        """
        Fetches market-moving news headlines.
        (Mock implementation)
        """
        # This would come from a news API (e.g., Bloomberg, Reuters)
        return [MarketEvent(
            event_id=f"news_fedspeak_{int(datetime.now().timestamp())}",
            timestamp=datetime.now() - timedelta(hours=2),
            event_type=EventType.CENTRAL_BANK,
            asset_class=AssetClass.FX,
            symbol="USD",
            headline="Fed Chair Hints at 'Higher for Longer' Interest Rate Stance",
            summary="In a recent speech, the Federal Reserve Chair emphasized the need to maintain a restrictive monetary policy to combat inflation, dashing hopes for imminent rate cuts.",
            sentiment=Sentiment.POSITIVE, # Positive for USD
            data={"speaker": "Fed Chair", "stance": "hawkish"}
        )] 