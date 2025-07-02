"""
Market Narrator API Endpoints
🎭 AI-powered market storytelling and sentiment analysis
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from typing import Dict, List, Optional
import logging
from datetime import datetime, timedelta
import asyncio

from backend.modules.market_narrator.story_generator import StoryGenerator
from backend.modules.market_narrator.correlation_engine import CorrelationEngine
from backend.modules.market_narrator.data_aggregator import DataAggregator
from backend.modules.market_narrator.models import (
    MarketStory, StoryType, InfluenceLevel, NewsEvent, 
    InfluenceNode, CorrelationData, SentimentData
)
from backend.modules.mt5_integration.service import MT5Service
from backend.modules.mt5_integration.config import MT5_LOGIN, MT5_PASSWORD, MT5_SERVER

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Market Narrator"])

# Global service instances
_story_generator = None
_correlation_engine = None
_data_aggregator = None
_mt5_service = None

def get_services():
    """Get Market Narrator service instances"""
    global _story_generator, _correlation_engine, _data_aggregator, _mt5_service
    
    if _story_generator is None:
        _story_generator = StoryGenerator()
        _correlation_engine = CorrelationEngine()
        _data_aggregator = DataAggregator()
        try:
            _mt5_service = MT5Service(
                login=MT5_LOGIN,
                password=MT5_PASSWORD,
                server=MT5_SERVER
    )
        except Exception as e:
            logger.warning(f"Failed to initialize MT5Service: {e}")
            _mt5_service = None
    
    return _story_generator, _correlation_engine, _data_aggregator, _mt5_service

@router.get("/status")
async def get_narrator_status():
    """Get Market Narrator system status"""
    try:
        story_gen, corr_engine, data_agg, mt5_service = get_services()
        
        mt5_connected = False
        if mt5_service:
            try:
                mt5_connected = mt5_service.is_connected()
            except Exception:
                mt5_connected = False
        
        return {
            "status": "active",
            "components": {
                "story_generator": "operational",
                "correlation_engine": "operational", 
                "data_aggregator": "operational",
                "mt5_connection": "connected" if mt5_connected else "disconnected"
            },
            "ai_model": "gemini-1.5-flash",
            "last_update": datetime.now().isoformat(),
            "version": "2.0.0"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting narrator status: {str(e)}")

@router.get("/stories", response_model=List[MarketStory])
async def get_market_stories(
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    story_type: Optional[StoryType] = Query(None, description="Filter by story type"),
    limit: int = Query(10, ge=1, le=50, description="Number of stories to return")
):
    """Get recent market stories"""
    try:
        story_gen, _, _, _ = get_services()
        
        # For now, generate sample stories
        stories = []
        symbols = [symbol] if symbol else ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "BTCUSD"]
        
        for sym in symbols[:limit]:
            # Generate whale activity story
            whale_data = {
                "volume": 500000,
                "order_type": "BUY",
                "whale_size": "LARGE", 
                "impact_score": 7.5,
                "confidence": 0.85,
                "price_level": 1.0950
            }
            
            story = await story_gen.generate_story(
                StoryType.WHALE_ACTIVITY,
                sym,
                whale_data
            )
            stories.append(story)
            
            if len(stories) >= limit:
                break
        
        return stories
        
    except Exception as e:
        logger.error(f"Error getting market stories: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-story", response_model=MarketStory)
async def generate_story(
    symbol: str,
    story_type: StoryType,
    data: Dict = None,
    language: str = "turkish"
):
    """Generate a new market story"""
    try:
        story_gen, _, _, _ = get_services()
        
        if data is None:
            data = await _get_market_data_for_story(symbol, story_type)
        
        story = await story_gen.generate_story(story_type, symbol, data, language)
        return story
        
    except Exception as e:
        logger.error(f"Error generating story: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sentiment-analysis", response_model=SentimentData)
async def get_sentiment_analysis(
    symbol: str = Query(..., description="Trading symbol"),
    timeframe: str = Query("1h", description="Timeframe for analysis")
):
    """Get sentiment analysis for a symbol"""
    try:
        _, _, data_agg, _ = get_services()
        
        # Mock sentiment data for now
        sentiment_data = SentimentData(
            symbol=symbol,
            overall_sentiment=0.65,  # Positive
            social_sentiment=0.72,
            news_sentiment=0.58,
            institutional_sentiment=0.61,
            retail_sentiment=0.69,
            confidence_score=0.78,
            sources_count=15,
            timestamp=datetime.now(),
            timeframe=timeframe,
            sentiment_history=[
                {"time": datetime.now() - timedelta(hours=i), "value": 0.6 + (i * 0.02)}
                for i in range(24)
            ]
        )
        
        return sentiment_data
        
    except Exception as e:
        logger.error(f"Error getting sentiment analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/influence-map", response_model=List[InfluenceNode])
async def get_influence_map(
    symbol: str = Query(..., description="Central symbol"),
    depth: int = Query(2, ge=1, le=3, description="Relationship depth")
):
    """Get influence map showing symbol relationships"""
    try:
        _, corr_engine, _, _ = get_services()
        
        # Generate influence map
        influence_nodes = await corr_engine.generate_influence_map(symbol, depth)
        return influence_nodes
        
    except Exception as e:
        logger.error(f"Error getting influence map: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/correlations", response_model=List[CorrelationData])
async def get_correlations(
    symbol: str = Query(..., description="Base symbol"),
    timeframe: str = Query("1D", description="Timeframe for correlation"),
    min_correlation: float = Query(0.5, ge=0.0, le=1.0, description="Minimum correlation threshold")
):
    """Get symbol correlations"""
    try:
        _, corr_engine, _, _ = get_services()
        
        correlations = await corr_engine.calculate_correlations(symbol, timeframe, min_correlation)
        return correlations
        
    except Exception as e:
        logger.error(f"Error getting correlations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/news-events", response_model=List[NewsEvent])
async def get_news_events(
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    hours: int = Query(24, ge=1, le=168, description="Hours back to fetch news"),
    impact_level: Optional[InfluenceLevel] = Query(None, description="Filter by impact level")
):
    """Get recent news events affecting markets"""
    try:
        _, _, data_agg, _ = get_services()
        
        news_events = await data_agg.fetch_news_events(symbol, hours, impact_level)
        return news_events
        
    except Exception as e:
        logger.error(f"Error getting news events: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start-live-narration")
async def start_live_narration(
    background_tasks: BackgroundTasks,
    symbols: List[str] = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"],
    interval_minutes: int = 5
):
    """Start live market narration"""
    try:
        background_tasks.add_task(
            _live_narration_task,
            symbols,
            interval_minutes
        )
        
        return {
            "status": "started",
            "symbols": symbols,
            "interval_minutes": interval_minutes,
            "message": "Live market narration started"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting live narration: {str(e)}")

@router.get("/market-pulse")
async def get_market_pulse():
    """Get overall market pulse and sentiment"""
    try:
        story_gen, corr_engine, data_agg, mt5_service = get_services()
        
        # Collect market data
        major_pairs = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"]
        market_data = {}
        
        for pair in major_pairs:
            try:
                rates = await mt5_service.get_rates(pair, "M1", 100)
                if rates:
                    latest = rates[-1]
                    prev = rates[-2] if len(rates) > 1 else rates[-1]
                    change = ((latest.close - prev.close) / prev.close) * 100
                    
                    market_data[pair] = {
                        "price": latest.close,
                        "change": change,
                        "volume": latest.tick_volume
                    }
            except:
                market_data[pair] = {"price": 0, "change": 0, "volume": 0}
        
        # Calculate overall sentiment
        total_change = sum(data.get("change", 0) for data in market_data.values())
        total_volume = sum(data.get("volume", 0) for data in market_data.values())
        
        sentiment = "BULLISH" if total_change > 0.1 else "BEARISH" if total_change < -0.1 else "NEUTRAL"
        
        return {
            "market_sentiment": sentiment,
            "overall_change": total_change,
            "total_volume": total_volume,
            "symbol_data": market_data,
            "active_stories": 5,  # Mock data
            "risk_level": "MEDIUM",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting market pulse: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions
async def _get_market_data_for_story(symbol: str, story_type: StoryType) -> Dict:
    """Get market data for story generation"""
    try:
        _, _, _, mt5_service = get_services()
        
        if story_type == StoryType.WHALE_ACTIVITY:
            return {
                "volume": 750000,
                "order_type": "BUY",
                "whale_size": "LARGE",
                "impact_score": 8.2,
                "confidence": 0.87,
                "price_level": 1.0950
            }
        elif story_type == StoryType.TECHNICAL_ANALYSIS:
            return {
                "rsi": 65.5,
                "macd": "BULLISH_CROSSOVER",
                "trend": "BULLISH",
                "support_level": 1.0900,
                "resistance_level": 1.1000
            }
        else:
            return {
                "sentiment_score": "POSITIVE",
                "social_sentiment": 0.72,
                "news_impact": "MEDIUM",
                "institutional_flow": "BUYING"
            }
            
    except Exception as e:
        logger.error(f"Error getting market data: {str(e)}")
        return {}

async def _live_narration_task(symbols: List[str], interval_minutes: int):
    """Background task for live market narration"""
    try:
        story_gen, _, _, _ = get_services()
        
        while True:
            for symbol in symbols:
                try:
                    # Generate different types of stories
                    story_types = [StoryType.WHALE_ACTIVITY, StoryType.TECHNICAL_ANALYSIS, StoryType.MARKET_SENTIMENT]
                    
                    for story_type in story_types:
                        data = await _get_market_data_for_story(symbol, story_type)
                        story = await story_gen.generate_story(story_type, symbol, data)
                        
                        logger.info(f"Generated live story: {story.title}")
                        
                        # Store story (could save to database here)
                        
                except Exception as e:
                    logger.error(f"Error in live narration for {symbol}: {str(e)}")
            
            # Wait for next iteration
            await asyncio.sleep(interval_minutes * 60)
        
    except Exception as e:
        logger.error(f"Live narration task error: {str(e)}") 