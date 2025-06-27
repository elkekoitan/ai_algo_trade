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
    SMALL = "small"      # 100K - 1M
    MEDIUM = "medium"    # 1M - 10M
    LARGE = "large"      # 10M - 100M
    MASSIVE = "massive"  # 100M+

class InstitutionalType(str, Enum):
    HEDGE_FUND = "hedge_fund"
    PENSION_FUND = "pension_fund"
    INVESTMENT_BANK = "investment_bank"
    MUTUAL_FUND = "mutual_fund"
    SOVEREIGN_FUND = "sovereign_fund"
    FAMILY_OFFICE = "family_office"

class OrderType(str, Enum):
    ICEBERG = "iceberg"
    HIDDEN = "hidden"
    BLOCK = "block"
    SWEEP = "sweep"
    DARK_POOL = "dark_pool"

class WhaleDetection(BaseModel):
    detection_id: str
    symbol: str
    whale_size: WhaleSize
    estimated_position_size: float
    average_price: float
    detection_time: datetime
    confidence: float = Field(..., ge=0, le=100)
    pattern_type: str
    institutional_type: Optional[InstitutionalType] = None
    estimated_remaining: Optional[float] = None
    stealth_score: float = Field(..., ge=0, le=100)

class InstitutionalFlow(BaseModel):
    flow_id: str
    symbol: str
    institution_type: InstitutionalType
    flow_direction: str  # BUY, SELL, NEUTRAL
    volume: float
    estimated_value: float
    time_window: str
    confidence: float = Field(..., ge=0, le=100)
    source: str
    metadata: Dict[str, Any] = {}

class DarkPoolActivity(BaseModel):
    activity_id: str
    symbol: str
    dark_pool_name: str
    volume: float
    estimated_price: float
    public_market_price: float
    price_improvement: float
    timestamp: datetime
    activity_type: OrderType
    estimated_institution: Optional[str] = None

class StealthOrder(BaseModel):
    order_id: str
    symbol: str
    side: str  # BUY, SELL
    total_quantity: float
    executed_quantity: float = 0.0
    remaining_quantity: float
    slice_size: float
    slice_interval: int  # seconds
    stealth_level: int = Field(..., ge=1, le=10)
    anti_detection_enabled: bool = True
    randomization_factor: float = Field(..., ge=0, le=1)
    created_at: datetime
    status: str = "PENDING"

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