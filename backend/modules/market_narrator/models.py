"""
Data models for the Market Narrator
"""
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class AssetClass(str, Enum):
    FX = "Forex"
    COMMODITY = "Commodity"
    EQUITY = "Equity"
    CRYPTO = "Cryptocurrency"
    INDEX = "Index"

class EventType(str, Enum):
    ECONOMIC = "Economic Data"
    GEOPOLITICAL = "Geopolitical"
    TECHNICAL = "Technical Signal"
    CENTRAL_BANK = "Central Bank"
    MARKET_SENTIMENT = "Market Sentiment"

class Sentiment(str, Enum):
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"

class CausalityLink(BaseModel):
    source_event_id: str
    target_event_id: str
    description: str # e.g., "caused a rise in"
    strength: float = Field(..., ge=0, le=1, description="Strength of the causal link")

class MarketEvent(BaseModel):
    event_id: str = Field(..., default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime
    event_type: EventType
    asset_class: AssetClass
    symbol: str
    headline: str
    summary: str
    sentiment: Sentiment
    data: Dict[str, Any] # e.g., {"actual": "2.5%", "forecast": "2.3%"}

class MarketStory(BaseModel):
    story_id: str = Field(..., default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    title: str = Field(..., description="The main headline of the market story")
    narrative: str = Field(..., description="The full, human-readable story explaining the market events")
    protagonist_asset: str = Field(..., description="The main asset or symbol the story is about (e.g., 'DXY')")
    key_events: List[MarketEvent]
    causal_links: List[CausalityLink]
    sentiment: Sentiment
    key_takeaway: str = Field(..., description="A single, crucial insight from the story")
    confidence_score: float = Field(..., ge=0, le=1, description="AI's confidence in the narrative's accuracy")

class InfluenceNode(BaseModel):
    id: str # e.g., "USD"
    asset_class: AssetClass
    current_impact: float # -1 to 1

class InfluenceMap(BaseModel):
    center_node: InfluenceNode
    linked_nodes: List[InfluenceNode]
    correlations: Dict[str, float]

class MarketScenario(BaseModel):
    scenario_id: str
    based_on_story_id: str
    title: str # e.g., "What if the Fed pivots?"
    description: str
    probability: float = Field(..., ge=0, le=1)
    potential_impact: Dict[str, str] # e.g., {"EURUSD": "Could rise to 1.12", "Gold": "Likely to rally"}

# Need to import uuid for the default factories
import uuid
MarketEvent.model_rebuild()
MarketStory.model_rebuild() 