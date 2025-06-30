"""
Data Aggregator for the Market Narrator

Collects and unifies data from various sources (market data, news, etc.).
"""
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random

from backend.core.logger import setup_logger
from backend.modules.mt5_integration.service import MT5Service
from .models import MarketEvent, EventType, AssetClass, Sentiment, NewsEvent, InfluenceLevel

logger = setup_logger(__name__)

class DataAggregator:
    """Aggregates market data from multiple sources for story generation"""
    
    def __init__(self):
        self.news_cache = {}
        self.market_data_cache = {}
        self.cache_expiry = 600  # 10 minutes
        
        # Mock news sources
        self.news_sources = [
            "Reuters", "Bloomberg", "MarketWatch", "CNBC", 
            "Financial Times", "Wall Street Journal", "ForexFactory"
        ]
        
        # Mock news templates
        self.news_templates = {
            "central_bank": [
                "{bank} announces interest rate decision: {rate}%",
                "{bank} Governor signals {stance} monetary policy",
                "{bank} releases economic outlook with {sentiment} projections"
            ],
            "economic_data": [
                "{country} {indicator} comes in at {value}, {comparison} expectations",
                "{country} releases {indicator} data showing {trend}",
                "Latest {indicator} from {country} indicates {outlook}"
            ],
            "geopolitical": [
                "Trade tensions between {country1} and {country2} {escalate/ease}",
                "{country} implements new {policy} affecting {sector}",
                "International summit results in {outcome} for {region}"
            ]
        }
        
        logger.info("📊 Data Aggregator initialized")

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

    async def fetch_news_events(
        self, 
        symbol: Optional[str] = None,
        hours: int = 24,
        impact_level: Optional[InfluenceLevel] = None
    ) -> List[NewsEvent]:
        """Fetch recent news events affecting markets"""
        try:
            cache_key = f"news_{symbol}_{hours}_{impact_level}"
            
            # Check cache
            if self._is_cached(cache_key, self.news_cache):
                return self.news_cache[cache_key]["data"]
            
            # Generate mock news events
            news_events = []
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            # Number of events based on timeframe
            num_events = min(20, max(5, hours // 2))
            
            for i in range(num_events):
                event_time = datetime.now() - timedelta(
                    hours=random.uniform(0, hours)
                )
                
                if event_time < cutoff_time:
                    continue
                
                # Generate mock news event
                news_event = await self._generate_mock_news_event(symbol, event_time)
                
                # Filter by impact level if specified
                if impact_level and news_event.impact_level != impact_level:
                    continue
                
                news_events.append(news_event)
            
            # Sort by timestamp (newest first)
            news_events.sort(key=lambda x: x.timestamp, reverse=True)
            
            # Cache result
            self.news_cache[cache_key] = {
                "data": news_events,
                "timestamp": datetime.now()
            }
            
            return news_events
            
        except Exception as e:
            logger.error(f"Error fetching news events: {e}")
            return []
    
    async def get_market_sentiment(
        self, 
        symbol: str,
        timeframe: str = "1D"
    ) -> Dict[str, float]:
        """Get aggregated market sentiment for a symbol"""
        try:
            cache_key = f"sentiment_{symbol}_{timeframe}"
            
            # Check cache
            if self._is_cached(cache_key, self.market_data_cache):
                return self.market_data_cache[cache_key]["data"]
            
            # Mock sentiment calculation
            base_sentiment = random.uniform(-0.3, 0.3)
            
            # Add some logic based on symbol
            if symbol in ["XAUUSD", "GOLD"]:
                base_sentiment += 0.2  # Gold generally positive sentiment
            elif symbol in ["BTCUSD", "BTC"]:
                base_sentiment += random.uniform(-0.4, 0.4)  # Crypto volatility
            
            sentiment_data = {
                "overall_sentiment": max(-1, min(1, base_sentiment)),
                "social_sentiment": max(-1, min(1, base_sentiment + random.uniform(-0.2, 0.2))),
                "news_sentiment": max(-1, min(1, base_sentiment + random.uniform(-0.15, 0.15))),
                "institutional_sentiment": max(-1, min(1, base_sentiment + random.uniform(-0.1, 0.1))),
                "confidence": random.uniform(0.7, 0.95)
            }
            
            # Cache result
            self.market_data_cache[cache_key] = {
                "data": sentiment_data,
                "timestamp": datetime.now()
            }
            
            return sentiment_data
            
        except Exception as e:
            logger.error(f"Error getting market sentiment: {e}")
            return {
                "overall_sentiment": 0.0,
                "social_sentiment": 0.0,
                "news_sentiment": 0.0,
                "institutional_sentiment": 0.0,
                "confidence": 0.5
            }
    
    async def get_economic_calendar(
        self, 
        days_ahead: int = 7
    ) -> List[MarketEvent]:
        """Get upcoming economic calendar events"""
        try:
            events = []
            
            # Generate mock economic events
            for i in range(days_ahead):
                event_date = datetime.now() + timedelta(days=i)
                
                # 1-3 events per day
                num_events = random.randint(1, 3)
                
                for j in range(num_events):
                    event = await self._generate_economic_event(event_date)
                    events.append(event)
            
            return events
            
        except Exception as e:
            logger.error(f"Error getting economic calendar: {e}")
            return []
    
    async def _generate_mock_news_event(
        self, 
        symbol: Optional[str],
        timestamp: datetime
    ) -> NewsEvent:
        """Generate a mock news event"""
        try:
            # Select random news type and source
            news_types = ["central_bank", "economic_data", "geopolitical"]
            news_type = random.choice(news_types)
            source = random.choice(self.news_sources)
            
            # Generate content based on type
            if news_type == "central_bank":
                title, content = self._generate_central_bank_news()
                impact_level = random.choice([InfluenceLevel.HIGH, InfluenceLevel.CRITICAL])
            elif news_type == "economic_data":
                title, content = self._generate_economic_news()
                impact_level = random.choice([InfluenceLevel.MEDIUM, InfluenceLevel.HIGH])
            else:
                title, content = self._generate_geopolitical_news()
                impact_level = random.choice([InfluenceLevel.LOW, InfluenceLevel.MEDIUM])
            
            # Determine affected symbols
            symbols = []
            if symbol:
                symbols = [symbol]
            else:
                symbols = random.sample(
                    ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "BTCUSD"], 
                    random.randint(1, 3)
                )
            
            # Determine sentiment
            sentiment = random.choice(list(Sentiment))
            
            return NewsEvent(
                timestamp=timestamp,
                title=title,
                content=content,
                source=source,
                symbols=symbols,
                impact_level=impact_level,
                sentiment=sentiment
            )
            
        except Exception as e:
            logger.error(f"Error generating mock news event: {e}")
            raise
    
    async def _generate_economic_event(self, event_date: datetime) -> MarketEvent:
        """Generate a mock economic calendar event"""
        try:
            indicators = [
                "GDP", "CPI", "NFP", "Unemployment Rate", 
                "Interest Rate Decision", "PMI", "Trade Balance"
            ]
            
            countries = ["US", "EU", "UK", "JP", "AU", "CA"]
            
            indicator = random.choice(indicators)
            country = random.choice(countries)
            
            return MarketEvent(
                timestamp=event_date,
                event_type=EventType.ECONOMIC,
                asset_class=AssetClass.FX,
                symbol=f"{country}_{indicator}",
                headline=f"{country} {indicator} Release",
                summary=f"Scheduled release of {country} {indicator} data",
                sentiment=Sentiment.NEUTRAL,
                data={
                    "indicator": indicator,
                    "country": country,
                    "expected": "TBD",
                    "importance": random.choice(["Low", "Medium", "High"])
                }
            )
            
        except Exception as e:
            logger.error(f"Error generating economic event: {e}")
            raise
    
    def _generate_central_bank_news(self) -> tuple:
        """Generate central bank related news"""
        banks = ["Federal Reserve", "ECB", "Bank of England", "Bank of Japan"]
        bank = random.choice(banks)
        rate = round(random.uniform(0.5, 5.0), 2)
        
        title = f"{bank} announces interest rate decision: {rate}%"
        content = f"The {bank} has announced its latest monetary policy decision, " \
                 f"setting rates at {rate}%. Market participants are analyzing " \
                 f"the implications for currency and bond markets."
        
        return title, content
    
    def _generate_economic_news(self) -> tuple:
        """Generate economic data news"""
        indicators = ["GDP", "CPI", "Employment", "PMI"]
        countries = ["US", "Eurozone", "UK", "Japan"]
        
        indicator = random.choice(indicators)
        country = random.choice(countries)
        value = round(random.uniform(-2.0, 5.0), 1)
        
        title = f"{country} {indicator} comes in at {value}%"
        content = f"Latest {indicator} data from {country} shows {value}%, " \
                 f"{'beating' if value > 2 else 'missing'} market expectations. " \
                 f"This could impact monetary policy decisions going forward."
        
        return title, content
    
    def _generate_geopolitical_news(self) -> tuple:
        """Generate geopolitical news"""
        events = [
            "Trade negotiations progress",
            "Diplomatic tensions ease",
            "New sanctions announced", 
            "International summit concluded"
        ]
        
        event = random.choice(events)
        
        title = f"Breaking: {event}"
        content = f"{event} with potential implications for global markets. " \
                 f"Traders are monitoring developments for potential impact " \
                 f"on risk sentiment and currency flows."
        
        return title, content
    
    def _is_cached(self, cache_key: str, cache_dict: Dict) -> bool:
        """Check if data is cached and still valid"""
        if cache_key not in cache_dict:
            return False
        
        cached_time = cache_dict[cache_key]["timestamp"]
        return (datetime.now() - cached_time).seconds < self.cache_expiry
    
    def get_status(self) -> Dict:
        """Get data aggregator status"""
        return {
            "status": "operational",
            "cached_news": len(self.news_cache),
            "cached_market_data": len(self.market_data_cache),
            "news_sources": len(self.news_sources)
        } 