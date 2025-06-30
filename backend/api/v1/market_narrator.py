import asyncio
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Optional
import logging
from datetime import datetime

from backend.core.logger import setup_logger
from backend.modules.mt5_integration.service import MT5Service
from backend.modules.market_narrator.models import (
    MarketStory, MarketNarrative, MarketNarratorStatus, NarrativeRequest, InfluenceMap, DataSource
)
from backend.modules.market_narrator.data_aggregator import DataAggregator
from backend.modules.market_narrator.correlation_engine import CorrelationEngine
from backend.modules.market_narrator.story_generator import StoryGenerator
from backend.core.config.settings import get_settings, Settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/narrator", tags=["Market Narrator"])

# --- Dependency Injection Setup ---
def get_settings_dep():
    return get_settings()

def get_mt5_service(settings: Settings = Depends(get_settings_dep)):
    return MT5Service(
        login=settings.MT5_LOGIN,
        password=settings.MT5_PASSWORD,
        server=settings.MT5_SERVER
    )

def get_data_aggregator(mt5: MT5Service = Depends(get_mt5_service)):
    return DataAggregator(mt5)

def get_correlation_engine(mt5: MT5Service = Depends(get_mt5_service)):
    return CorrelationEngine(mt5)

def get_story_generator():
    return StoryGenerator()

# In-memory cache for narratives and status
narrative_cache: List[MarketNarrative] = []
status = MarketNarratorStatus(
    status="initializing",
    stories_generated_24h=0,
    data_sources_connected=2, # Mock: News & Twitter
    api_calls_today=0,
    error_rate=0.0
)

@router.on_event("startup")
async def startup_event():
    status.status = "active"
    logger.info("Market Narrator API has started.")

@router.get("/status", response_model=MarketNarratorStatus)
async def get_status():
    """Get the current status of the Market Narrator service."""
    status.api_calls_today += 1
    return status

@router.post("/generate-narrative", response_model=MarketNarrative)
async def generate_narrative(
    request: NarrativeRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate a new market narrative for a given symbol.
    This is a long-running process that will be handled in the background.
    """
    status.api_calls_today += 1
    try:
        # Step 1: Aggregate data
        data_points = await get_data_aggregator(get_mt5_service(get_settings_dep())).fetch_data(sources=[DataSource.NEWS_API, DataSource.TWITTER])
        
        # Step 2: Find correlated events
        events = await get_correlation_engine(get_mt5_service(get_settings_dep())).find_events(data_points)
        if not events:
            raise HTTPException(status_code=404, detail="No significant correlated events found to generate a narrative.")
            
        # Step 3: Generate narrative from the most significant event
        narrative = await get_story_generator().create_narrative(events[0])
        
        # Cache the new narrative
        narrative_cache.insert(0, narrative)
        if len(narrative_cache) > 50: # Keep cache size manageable
            narrative_cache.pop()
            
        # Update status
        status.last_story_generated_at = datetime.now()
        status.stories_generated_24h += 1
        
        return narrative
        
    except Exception as e:
        logger.error(f"Error generating narrative for {request.symbol}: {e}")
        status.error_rate = (status.error_rate * (status.api_calls_today - 1) + 1) / status.api_calls_today
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/latest-narratives", response_model=List[MarketNarrative])
async def get_latest_narratives(symbol: Optional[str] = None, limit: int = 10):
    """Get the latest generated market narratives."""
    status.api_calls_today += 1
    
    if not narrative_cache:
        # If cache is empty, generate a default one
        try:
            request = NarrativeRequest(symbol=symbol or "EURUSD")
            narrative = await generate_narrative(request, BackgroundTasks())
            return [narrative]
        except HTTPException as e:
            # If generation fails, return empty with original error
            if e.status_code == 404:
                return []
            raise e
            
    if symbol:
        filtered_narratives = [n for n in narrative_cache if symbol in n.protagonist_symbols]
    else:
        filtered_narratives = narrative_cache
        
    return filtered_narratives[:limit]

@router.get("/narrative/{narrative_id}", response_model=MarketNarrative)
async def get_narrative_by_id(narrative_id: str):
    """Get a specific market narrative by its ID."""
    status.api_calls_today += 1
    
    for narrative in narrative_cache:
        if narrative.narrative_id == narrative_id:
            return narrative
    
    raise HTTPException(status_code=404, detail="Narrative not found.")

@router.get("/influence-map/{symbol}", response_model=InfluenceMap)
async def get_influence_map(symbol: str):
    """Get the influence map for a specific symbol."""
    status.api_calls_today += 1
    
    # This is a mock implementation. A real one would use graph algorithms.
    nodes = [{"id": symbol, "type": "symbol", "size": 30}]
    edges = []
    
    # Find related narratives
    related_narratives = [n for n in narrative_cache if symbol in n.protagonist_symbols]
    
    for i, narrative in enumerate(related_narratives[:3]): # Max 3 narratives on map
        node_id = f"narrative_{i}"
        nodes.append({"id": node_id, "type": "narrative", "label": narrative.key_theme, "size": 20})
        edges.append({"from": node_id, "to": symbol, "strength": narrative.confidence_level})
        
        for j, event in enumerate(narrative.source_events[:2]): # Max 2 events per narrative
            event_node_id = f"event_{i}_{j}"
            nodes.append({"id": event_node_id, "type": "event", "label": event.event_type.name, "size": 10})
            edges.append({"from": event_node_id, "to": node_id, "strength": event.correlation_strength})

    return InfluenceMap(
        map_id=f"map_{symbol}_{datetime.now().timestamp()}",
        symbol=symbol,
        last_updated=datetime.now(),
        nodes=nodes,
        edges=edges,
        key_drivers=[n['label'] for n in nodes if n['type'] == 'narrative'],
        predicted_trajectory="Based on recent narratives, a period of increased volatility is expected.",
        narrative_connections=[n.narrative_id for n in related_narratives]
    )

@router.get("/feed", response_model=List[MarketStory])
async def get_story_feed(
    aggregator: DataAggregator = Depends(get_data_aggregator),
    correlator: CorrelationEngine = Depends(get_correlation_engine),
    generator: StoryGenerator = Depends(get_story_generator)
):
    """
    Generates and returns the latest feed of market stories.
    """
    try:
        # Establish MT5 connection for this request
        if not aggregator.mt5_service.is_connected():
            await aggregator.mt5_service.connect()

        events = await aggregator.gather_data()
        correlations = await correlator.find_significant_correlations()
        
        if not events:
             raise HTTPException(status_code=404, detail="Not enough market events to generate a story.")

        new_story = await generator.generate_story(events, correlations)
        if not new_story:
            raise HTTPException(status_code=500, detail="Failed to generate a new story.")
            
        return [new_story] # Return as a list
        
    except Exception as e:
        logger.error(f"Error generating story feed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while generating stories.")
    finally:
        # Ensure connection is closed after the request
        if aggregator.mt5_service.is_connected():
            await aggregator.mt5_service.disconnect() 