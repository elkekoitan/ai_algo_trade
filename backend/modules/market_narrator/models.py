"""
Data models for the Market Narrator
"""
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

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

class StoryType(str, Enum):
    WHALE_ACTIVITY = "whale_activity"
    TECHNICAL_ANALYSIS = "technical_analysis"
    MARKET_SENTIMENT = "market_sentiment"
    NEWS_IMPACT = "news_impact"
    RISK_ALERT = "risk_alert"

class InfluenceLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class CausalityLink(BaseModel):
    source_event_id: str
    target_event_id: str
    description: str # e.g., "caused a rise in"
    strength: float = Field(..., ge=0, le=1, description="Strength of the causal link")

class MarketEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime
    event_type: EventType
    asset_class: AssetClass
    symbol: str
    headline: str
    summary: str
    sentiment: Sentiment
    data: Dict[str, Any] # e.g., {"actual": "2.5%", "forecast": "2.3%"}

class NewsEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime
    title: str
    content: str
    source: str
    symbols: List[str] = []
    impact_level: InfluenceLevel
    sentiment: Sentiment

class MarketStory(BaseModel):
    story_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    title: str = Field(..., description="The main headline of the market story")
    content: str = Field(..., description="The full story content")
    narrative: Optional[str] = Field(None, description="The full, human-readable story explaining the market events")
    protagonist_asset: Optional[str] = Field(None, description="The main asset or symbol the story is about")
    story_type: StoryType
    symbol: str
    influence_level: InfluenceLevel
    confidence_score: float = Field(..., ge=0, le=1, description="AI's confidence in the narrative's accuracy")
    data_sources: List[str] = []
    related_events: List[str] = []
    generated_at: datetime = Field(default_factory=datetime.now)
    key_events: Optional[List[MarketEvent]] = []
    causal_links: Optional[List[CausalityLink]] = []
    sentiment: Optional[Sentiment] = None
    key_takeaway: Optional[str] = Field(None, description="A single, crucial insight from the story")

class InfluenceNode(BaseModel):
    id: str # e.g., "USD"
    symbol: str
    asset_class: AssetClass
    current_impact: float # -1 to 1
    influence_level: InfluenceLevel
    connections: List[str] = []

class CorrelationData(BaseModel):
    symbol_a: str
    symbol_b: str
    correlation: float = Field(..., ge=-1, le=1)
    timeframe: str
    confidence: float = Field(..., ge=0, le=1)
    timestamp: datetime = Field(default_factory=datetime.now)

class SentimentData(BaseModel):
    symbol: str
    overall_sentiment: float = Field(..., ge=-1, le=1)
    social_sentiment: float = Field(..., ge=-1, le=1)
    news_sentiment: float = Field(..., ge=-1, le=1)
    institutional_sentiment: float = Field(..., ge=-1, le=1)
    retail_sentiment: float = Field(..., ge=-1, le=1)
    confidence_score: float = Field(..., ge=0, le=1)
    sources_count: int
    timestamp: datetime = Field(default_factory=datetime.now)
    timeframe: str
    sentiment_history: List[Dict[str, Any]] = []

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
MarketEvent.model_rebuild()
MarketStory.model_rebuild() 