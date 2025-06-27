"""
Data models for the Adaptive Trade Manager
"""
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class MarketRegime(str, Enum):
    TRENDING_UP = "trending_up"
    TRENDING_DOWN = "trending_down"
    RANGING = "ranging"
    VOLATILE = "volatile"
    LOW_LIQUIDITY = "low_liquidity"

class ActionType(str, Enum):
    ADJUST_SL = "adjust_sl"
    ADJUST_TP = "adjust_tp"
    PARTIAL_CLOSE = "partial_close"
    FULL_CLOSE = "full_close"
    SCALE_IN = "scale_in"
    HEDGE = "hedge"
    DO_NOTHING = "do_nothing"

class ManagedPosition(BaseModel):
    ticket: int
    symbol: str
    open_time: datetime
    position_type: str # 'buy' or 'sell'
    volume: float
    open_price: float
    current_price: float
    stop_loss: float
    take_profit: float
    pnl: float = Field(..., description="Profit and Loss of the position")
    pips: float
    is_new: bool = True

class RiskMetrics(BaseModel):
    position_ticket: int
    risk_level: RiskLevel
    risk_score: float = Field(..., ge=0, le=100, description="Overall risk score from 0 to 100")
    volatility_index: float = Field(..., ge=0, description="Market volatility index")
    drawdown_percent: float = Field(..., ge=0, le=100)
    value_at_risk: float
    news_impact_level: int = Field(..., ge=0, le=3, description="Upcoming news impact (0=None, 3=High)")
    correlation_warnings: Dict[str, float] = {}

class MarketCondition(BaseModel):
    symbol: str
    regime: MarketRegime
    volatility: float
    liquidity_level: float # e.g., 0-1
    sentiment_score: float # e.g., -1 to 1
    upcoming_events: List[Dict[str, Any]] = []

class AdaptiveAction(BaseModel):
    action_type: ActionType
    description: str
    confidence: float = Field(..., ge=0, le=1)
    parameters: Dict[str, Any] = {} # e.g., {'price': 1.2345, 'percentage': 50}
    reasoning: str
    predicted_outcome: str

class AdaptiveAlert(BaseModel):
    alert_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    position_ticket: int
    title: str
    description: str
    risk_metrics: RiskMetrics
    recommended_action: AdaptiveAction
    urgency: int = Field(..., ge=1, le=5, description="Urgency level from 1 to 5")

class DashboardData(BaseModel):
    total_positions: int
    overall_pnl: float
    portfolio_risk_level: RiskLevel
    portfolio_risk_score: float
    active_alerts: int
    market_overview: Dict[str, MarketRegime] 