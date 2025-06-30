import asyncio
from fastapi import APIRouter, HTTPException, Depends
from typing import List

from backend.core.logger import setup_logger
from backend.modules.mt5_integration.service import MT5Service
from backend.modules.market_narrator.models import MarketStory
from backend.modules.market_narrator.data_aggregator import DataAggregator
from backend.modules.market_narrator.correlation_engine import CorrelationEngine
from backend.modules.market_narrator.story_generator import StoryGenerator
from backend.core.config.settings import get_settings, Settings

logger = setup_logger(__name__)
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