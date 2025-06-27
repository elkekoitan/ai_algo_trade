"""
API Endpoints for the Market Narrator
"""
import asyncio
from fastapi import APIRouter, HTTPException
from typing import List

from backend.core.logger import get_logger
from backend.modules.mt5_integration.service import MT5Service
from backend.modules.market_narrator.models import MarketStory
from backend.modules.market_narrator.data_aggregator import DataAggregator
from backend.modules.market_narrator.correlation_engine import CorrelationEngine
from backend.modules.market_narrator.story_generator import StoryGenerator

logger = get_logger(__name__)
router = APIRouter(prefix="/narrator", tags=["Market Narrator"])

# --- Service Initialization ---
mt5_service = MT5Service()
data_aggregator = DataAggregator(mt5_service)
correlation_engine = CorrelationEngine(mt5_service)
story_generator = StoryGenerator()

# In-memory cache for stories
generated_stories: List[MarketStory] = []

# --- Background Task for Story Generation ---
narrator_task = None

async def generate_market_narratives():
    """The main loop that generates market stories."""
    global generated_stories
    logger.info("Narrator Cycle: Generating new market stories...")
    try:
        events = await data_aggregator.gather_data()
        correlations = await correlation_engine.find_significant_correlations()
        
        if not events:
            logger.warning("Narrator Cycle: No events found, skipping story generation.")
            return

        new_story = await story_generator.generate_story(events, correlations)
        
        if new_story:
            # Prepend the new story and keep the list size manageable (e.g., 20 stories)
            generated_stories.insert(0, new_story)
            generated_stories = generated_stories[:20]
            logger.info(f"Successfully generated new story: '{new_story.title}'")
            
    except Exception as e:
        logger.error(f"Error during Market Narrator cycle: {e}", exc_info=True)

async def narrator_background_runner():
    # Initial run
    await generate_market_narratives()
    # Subsequent runs
    while True:
        await asyncio.sleep(60 * 15) # Run every 15 minutes
        await generate_market_narratives()

@router.on_event("startup")
async def startup_event():
    global narrator_task
    if not mt5_service.is_connected():
        login_result = mt5_service.login(25201110, "Tickmill-Demo", "el[{rXU1lsiM") # [[memory:7052824161247122118]]
        if not login_result:
            logger.error("Market Narrator Startup: Failed to connect to MT5.")
            return
    
    narrator_task = asyncio.create_task(narrator_background_runner())
    logger.info("Market Narrator background task started.")

@router.on_event("shutdown")
async def shutdown_event():
    if narrator_task:
        narrator_task.cancel()
    logger.info("Market Narrator has been shut down.")

# --- API Endpoints ---

@router.get("/feed", response_model=List[MarketStory])
async def get_story_feed():
    """
    Returns the latest feed of generated market stories.
    """
    if not generated_stories:
        # If the cache is empty on first load, run a generation cycle
        await generate_market_narratives()

    if not generated_stories:
         raise HTTPException(status_code=404, detail="No market stories available at the moment. Please check back shortly.")

    return generated_stories

@router.get("/story/{story_id}", response_model=MarketStory)
async def get_story_details(story_id: str):
    """
    Returns the details of a specific market story.
    """
    story = next((s for s in generated_stories if s.story_id == story_id), None)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    return story 