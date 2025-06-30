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

class DataSource(str, Enum):
    NEWS_API = "news_api"
    TWITTER = "twitter"
    REDDIT = "reddit"
    FINANCIAL_REPORTS = "financial_reports"
    FORUM = "forum"
    CUSTOM = "custom"

class SentimentType(str, Enum):
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"

class MarketEventType(str, Enum):
    EARNINGS_CALL = "earnings_call"
    FOMC_MEETING = "fomc_meeting"
    PRODUCT_LAUNCH = "product_launch"
    GEOPOLITICAL_EVENT = "geopolitical_event"
    REGULATORY_CHANGE = "regulatory_change"
    MARKET_SHOCK = "market_shock"

class DataPoint(BaseModel):
    id: str = Field(..., description="Unique ID for the data point")
    source: DataSource = Field(..., description="Source of the data")
    timestamp: datetime = Field(..., description="Timestamp of the data point")
    content: str = Field(..., description="Raw content of the data point")
    author: Optional[str] = Field(None, description="Author or source entity")
    url: Optional[str] = Field(None, description="URL to the original source")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional source-specific metadata")
    
    # AI-enriched fields
    sentiment_score: float = Field(..., description="Sentiment score from -1.0 (very negative) to 1.0 (very positive)")
    sentiment_label: SentimentType = Field(..., description="Categorical sentiment label")
    related_symbols: List[str] = Field(default_factory=list, description="List of related trading symbols")
    keywords: List[str] = Field(default_factory=list, description="Extracted keywords")
    is_verified: bool = Field(default=False, description="Whether the source is verified")
    credibility_score: float = Field(default=0.5, description="Source credibility score 0-1")

class CorrelatedEvent(BaseModel):
    event_id: str = Field(..., description="Unique ID for the correlated event")
    start_time: datetime = Field(..., description="Start time of the event")
    end_time: datetime = Field(..., description="End time of the event")
    event_type: MarketEventType = Field(..., description="Type of market event")
    title: str = Field(..., description="Event title")
    description: str = Field(..., description="Brief description of the event")
    
    # Correlation metrics
    involved_symbols: List[str] = Field(..., description="Symbols involved in the event")
    correlation_strength: float = Field(..., description="Strength of the correlation (0-1)")
    causality_score: float = Field(..., description="Likelihood of this event causing market movement (0-1)")
    leading_indicator: Optional[str] = Field(None, description="Leading data point ID")
    
    # Linked data
    data_points: List[DataPoint] = Field(..., description="List of data points forming this event")
    
    # Impact
    predicted_impact: str = Field(..., description="Predicted market impact (e.g., high volatility, bullish trend)")
    impact_confidence: float = Field(..., description="Confidence in the impact prediction (0-1)")

class MarketNarrative(BaseModel):
    narrative_id: str = Field(..., description="Unique ID for the market narrative")
    timestamp: datetime = Field(..., description="Time the narrative was generated")
    title: str = Field(..., description="Compelling headline for the narrative")
    summary: str = Field(..., description="A short, engaging summary of the narrative")
    full_story: str = Field(..., description="The complete, detailed story generated by the AI")
    
    # Core elements
    protagonist_symbols: List[str] = Field(..., description="Main symbols the story is about")
    key_theme: str = Field(..., description="The central theme of the narrative (e.g., 'Inflation Fears', 'Tech Rally')")
    sentiment_arc: List[float] = Field(..., description="Evolution of sentiment over the story's timeline")
    
    # Analytics and insights
    market_implication: str = Field(..., description="What this narrative means for traders")
    potential_trades: List[Dict[str, Any]] = Field(default_factory=list, description="Actionable trade ideas based on the narrative")
    confidence_level: float = Field(..., description="AI's confidence in the narrative's accuracy and relevance (0-1)")
    projected_lifespan_hours: int = Field(..., description="How long this narrative is expected to be relevant")
    
    # Source attribution
    source_events: List[CorrelatedEvent] = Field(..., description="The correlated events that form the basis of this narrative")

class MarketNarratorStatus(BaseModel):
    status: str = Field(default="active", description="Service status")
    last_story_generated_at: Optional[datetime] = Field(None, description="Timestamp of the last generated story")
    stories_generated_24h: int = Field(..., description="Number of stories generated in the last 24 hours")
    data_sources_connected: int = Field(..., description="Number of active data sources")
    api_calls_today: int = Field(..., description="Number of API calls made today")
    error_rate: float = Field(..., description="Error rate in percentage")

class NarrativeRequest(BaseModel):
    symbol: str = Field(..., description="The primary symbol to generate a narrative for")
    lookback_hours: int = Field(default=24, description="How many hours of data to look back")
    custom_prompt: Optional[str] = Field(None, description="A custom prompt to guide the story generation") 