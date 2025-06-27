"""
God Mode Data Models
Tanrısal veri yapıları
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum

class GodModeStatus(str, Enum):
    INACTIVE = "inactive"
    ACTIVE = "active"
    OMNIPOTENT = "omnipotent"
    TRANSCENDENT = "transcendent"

class PredictionAccuracy(str, Enum):
    MORTAL = "mortal"  # <90%
    DIVINE = "divine"  # 90-95%
    GODLIKE = "godlike"  # 95-99%
    OMNISCIENT = "omniscient"  # >99%

class MarketPrediction(BaseModel):
    symbol: str
    timeframe: str
    prediction_time: datetime
    target_time: datetime
    current_price: float
    predicted_price: float
    predicted_change: float
    predicted_change_percent: float
    confidence: float = Field(..., ge=0, le=100)
    accuracy_level: PredictionAccuracy
    reasoning: str
    quantum_factors: List[str] = []

class RiskAssessment(BaseModel):
    overall_risk_score: float = Field(..., ge=0, le=100)
    volatility_risk: float
    liquidity_risk: float
    correlation_risk: float
    news_risk: float
    manipulation_risk: float
    recommended_position_size: float
    max_drawdown_protection: float
    stop_loss_suggestion: Optional[float] = None
    take_profit_suggestion: Optional[float] = None

class QuantumSignal(BaseModel):
    signal_id: str
    symbol: str
    signal_type: str  # BUY, SELL, HOLD, HEDGE
    strength: float = Field(..., ge=0, le=100)
    quantum_probability: float = Field(..., ge=0, le=100)
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    risk_reward_ratio: Optional[float] = None
    expected_duration: Optional[int] = None  # minutes
    reasoning: str
    created_at: datetime

class GodModeMetrics(BaseModel):
    total_predictions: int = 0
    correct_predictions: int = 0
    accuracy_rate: float = 0.0
    total_trades: int = 0
    winning_trades: int = 0
    win_rate: float = 0.0
    total_profit: float = 0.0
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    divinity_level: int = 1  # 1-10
    omnipotence_score: float = 0.0

class GodModeConfig(BaseModel):
    enabled: bool = True
    status: GodModeStatus = GodModeStatus.INACTIVE
    prediction_accuracy_target: float = 99.7
    max_risk_per_trade: float = 1.0
    quantum_analysis_enabled: bool = True
    prophetic_mode_enabled: bool = True
    divine_intervention_enabled: bool = True
    auto_trading_enabled: bool = False
    symbols_to_monitor: List[str] = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"]
    update_interval_seconds: int = 1

class GodModeAlert(BaseModel):
    alert_id: str
    alert_type: str  # PREDICTION, RISK, MANIPULATION, OPPORTUNITY
    priority: str  # LOW, MEDIUM, HIGH, CRITICAL, DIVINE
    title: str
    message: str
    symbol: Optional[str] = None
    action_required: bool = False
    auto_action_taken: bool = False
    created_at: datetime
    expires_at: Optional[datetime] = None

class MarketManipulationDetection(BaseModel):
    detection_id: str
    symbol: str
    manipulation_type: str  # SPOOFING, LAYERING, PUMP_DUMP, WHALE_DUMP
    confidence: float = Field(..., ge=0, le=100)
    estimated_impact: float
    estimated_duration: int  # minutes
    counter_strategy: Optional[str] = None
    detected_at: datetime
    
class GodModeState(BaseModel):
    status: GodModeStatus
    current_power_level: float = Field(..., ge=0, le=100)
    active_predictions: List[MarketPrediction] = []
    active_signals: List[QuantumSignal] = []
    risk_assessment: Optional[RiskAssessment] = None
    recent_alerts: List[GodModeAlert] = []
    metrics: GodModeMetrics = GodModeMetrics()
    config: GodModeConfig = GodModeConfig()
    last_update: datetime 