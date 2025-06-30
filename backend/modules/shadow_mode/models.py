"""
Shadow Mode Data Models
Gizli mod veri yapıları
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum

class ShadowModeStatus(str, Enum):
    INACTIVE = "inactive"
    ACTIVE = "active"
    STEALTH = "stealth"
    HUNTING = "hunting"

class WhaleSize(str, Enum):
    SMALL = "small"      # 100k-500k
    MEDIUM = "medium"    # 500k-1M
    LARGE = "large"      # 1M-5M
    MASSIVE = "massive"  # 5M+

class InstitutionalType(str, Enum):
    HEDGE_FUND = "hedge_fund"
    PENSION_FUND = "pension_fund"
    INVESTMENT_BANK = "investment_bank"
    CENTRAL_BANK = "central_bank"
    RETAIL_CLUSTER = "retail_cluster"

class OrderType(str, Enum):
    BUY = "buy"
    SELL = "sell"

class WhaleDetection(BaseModel):
    id: str = Field(..., description="Unique whale detection ID")
    timestamp: datetime = Field(..., description="Detection timestamp")
    symbol: str = Field(..., description="Trading symbol")
    size: WhaleSize = Field(..., description="Whale size category")
    volume: float = Field(..., description="Trade volume")
    value: float = Field(..., description="Trade value in USD")
    order_type: OrderType = Field(..., description="Buy or sell order")
    price: float = Field(..., description="Execution price")
    confidence: float = Field(..., description="Detection confidence 0-1")
    impact_score: float = Field(..., description="Market impact score 0-100")
    
    # Additional metadata
    spread_analysis: Dict[str, Any] = Field(default_factory=dict)
    volume_profile: Dict[str, Any] = Field(default_factory=dict)
    time_analysis: Dict[str, Any] = Field(default_factory=dict)

class InstitutionalFlow(BaseModel):
    id: str = Field(..., description="Institutional flow ID")
    timestamp: datetime = Field(..., description="Flow timestamp")
    symbol: str = Field(..., description="Trading symbol")
    institution_type: InstitutionalType = Field(..., description="Institution type")
    flow_direction: OrderType = Field(..., description="Flow direction")
    flow_strength: float = Field(..., description="Flow strength 0-100")
    volume_estimate: float = Field(..., description="Estimated volume")
    duration_minutes: int = Field(..., description="Flow duration in minutes")
    
    # Flow analysis
    retail_vs_institutional: float = Field(..., description="Ratio institutional/retail")
    momentum_score: float = Field(..., description="Flow momentum")
    correlation_with_price: float = Field(..., description="Price correlation")

class DarkPoolActivity(BaseModel):
    id: str = Field(..., description="Dark pool activity ID")
    timestamp: datetime = Field(..., description="Activity timestamp")
    symbol: str = Field(..., description="Trading symbol")
    hidden_volume: float = Field(..., description="Estimated hidden volume")
    visible_volume: float = Field(..., description="Visible market volume")
    dark_pool_ratio: float = Field(..., description="Dark pool percentage 0-100")
    liquidity_depth: float = Field(..., description="Hidden liquidity depth")
    execution_quality: float = Field(..., description="Execution quality score")
    
    # Dark pool analytics
    fragmentation_score: float = Field(..., description="Market fragmentation")
    price_improvement: float = Field(..., description="Price improvement vs public")

class StealthOrder(BaseModel):
    id: str = Field(..., description="Stealth order ID")
    symbol: str = Field(..., description="Trading symbol")
    order_type: OrderType = Field(..., description="Order type")
    target_volume: float = Field(..., description="Total target volume")
    max_chunk_size: float = Field(..., description="Maximum chunk size")
    time_interval_seconds: int = Field(..., description="Time between chunks")
    price_strategy: str = Field(..., description="Price execution strategy")
    stealth_level: float = Field(..., description="Stealth level 0-100")
    
    # Execution tracking
    executed_volume: float = Field(default=0, description="Executed volume")
    remaining_volume: float = Field(..., description="Remaining volume")
    average_price: Optional[float] = Field(default=None, description="Average execution price")
    slippage: Optional[float] = Field(default=None, description="Execution slippage")
    status: str = Field(default="pending", description="Order status")

class ManipulationPattern(BaseModel):
    pattern_id: str
    symbol: str
    pattern_type: str  # SPOOFING, LAYERING, PUMP_DUMP, STOP_HUNT
    detection_time: datetime
    estimated_target: Optional[float] = None
    estimated_duration: Optional[int] = None  # minutes
    confidence: float = Field(..., ge=0, le=100)
    institutional_fingerprint: Optional[str] = None
    counter_strategy: Optional[str] = None

class ShadowPortfolio(BaseModel):
    portfolio_id: str
    target_institution: str
    tracked_positions: List[Dict[str, Any]] = []
    total_value: float = 0.0
    tracking_accuracy: float = Field(..., ge=0, le=100)
    replication_delay: int = 0  # seconds
    risk_adjustment: float = 1.0
    performance_alpha: float = 0.0
    created_at: datetime
    last_rebalance: datetime

class ShadowAlert(BaseModel):
    alert_id: str
    alert_type: str  # WHALE_DETECTED, MANIPULATION, DARK_POOL, INSTITUTIONAL_FLOW
    priority: str  # LOW, MEDIUM, HIGH, CRITICAL, STEALTH
    title: str
    message: str
    symbol: Optional[str] = None
    estimated_impact: Optional[float] = None
    action_suggested: Optional[str] = None
    stealth_required: bool = False
    created_at: datetime
    expires_at: Optional[datetime] = None

class ShadowMetrics(BaseModel):
    total_whales_detected: int = 0
    successful_shadows: int = 0
    stealth_success_rate: float = 0.0
    detection_accuracy: float = 0.0
    average_alpha: float = 0.0
    total_volume_tracked: float = 0.0
    institutions_monitored: int = 0
    manipulation_prevented: int = 0

class ShadowModeConfig(BaseModel):
    enabled: bool = True
    status: ShadowModeStatus = ShadowModeStatus.INACTIVE
    stealth_level: int = Field(5, ge=1, le=10)
    whale_threshold: float = 100000.0  # Minimum position size
    detection_sensitivity: float = 0.8
    auto_shadow_enabled: bool = False
    max_shadow_positions: int = 5
    symbols_to_monitor: List[str] = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "BTCUSD"]
    dark_pools_enabled: bool = True
    manipulation_detection: bool = True
    stealth_execution: bool = True

class ShadowModeState(BaseModel):
    status: ShadowModeStatus
    stealth_level: int
    active_detections: List[WhaleDetection] = []
    active_flows: List[InstitutionalFlow] = []
    dark_pool_activities: List[DarkPoolActivity] = []
    stealth_orders: List[StealthOrder] = []
    manipulation_patterns: List[ManipulationPattern] = []
    shadow_portfolios: List[ShadowPortfolio] = []
    recent_alerts: List[ShadowAlert] = []
    metrics: ShadowMetrics = ShadowMetrics()
    config: ShadowModeConfig = ShadowModeConfig()
    last_update: datetime

class ShadowAnalytics(BaseModel):
    timestamp: datetime = Field(..., description="Analytics timestamp")
    symbol: str = Field(..., description="Trading symbol")
    
    # Whale metrics
    whale_activity_score: float = Field(..., description="Overall whale activity 0-100")
    whale_sentiment: float = Field(..., description="Whale sentiment -100 to +100")
    whale_volume_24h: float = Field(..., description="24h whale volume")
    
    # Dark pool metrics
    dark_pool_intensity: float = Field(..., description="Dark pool intensity 0-100")
    hidden_liquidity: float = Field(..., description="Estimated hidden liquidity")
    market_fragmentation: float = Field(..., description="Market fragmentation score")
    
    # Institutional metrics
    institutional_pressure: float = Field(..., description="Institutional pressure 0-100")
    smart_money_flow: float = Field(..., description="Smart money flow direction")
    retail_sentiment: float = Field(..., description="Retail sentiment score")
    
    # Market impact
    predicted_impact: float = Field(..., description="Predicted market impact")
    volatility_forecast: float = Field(..., description="Volatility forecast")
    trend_strength: float = Field(..., description="Trend strength 0-100")

# API Response Models
class WhaleAlert(BaseModel):
    alert_id: str
    severity: str  # "low", "medium", "high", "critical"
    message: str
    whale_data: WhaleDetection
    recommended_action: str

class ShadowModeStatus(BaseModel):
    status: str = "active"
    whales_detected_24h: int
    dark_pools_monitored: int
    institutional_flows_tracked: int
    stealth_orders_active: int
    system_health: float  # 0-100
    last_update: datetime 