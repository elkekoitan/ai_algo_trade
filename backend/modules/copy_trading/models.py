"""
Copy Trading Data Models
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class CopyStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    SUSPENDED = "suspended"

class RiskLevel(str, Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    EXTREME = "extreme"

class TraderTier(str, Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"

class CopyTraderProfile(BaseModel):
    """Profile of a trader available for copying"""
    trader_id: str
    display_name: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    tier: TraderTier = TraderTier.BRONZE
    
    # Performance metrics
    total_return: float = 0.0
    monthly_return: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    total_trades: int = 0
    
    # Social metrics
    followers_count: int = 0
    copied_trades: int = 0
    rating: float = 0.0
    reviews_count: int = 0
    
    # Trading style
    risk_level: RiskLevel = RiskLevel.MODERATE
    average_trade_duration: int = 0  # in hours
    favorite_pairs: List[str] = []
    trading_hours: Dict[str, str] = {}  # timezone info
    
    # Subscription info
    is_premium: bool = False
    subscription_fee: float = 0.0
    min_copy_amount: float = 100.0
    max_copy_amount: float = 100000.0
    
    # Status
    is_active: bool = True
    last_trade_time: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CopySettings(BaseModel):
    """Copy settings for a follower"""
    follower_id: str
    trader_id: str
    
    # Copy parameters
    copy_amount: float = Field(..., ge=10, le=1000000)
    copy_ratio: float = Field(default=1.0, ge=0.1, le=10.0)  # 1:1 ratio default
    
    # Risk management
    max_daily_loss: float = Field(default=100.0, ge=10)
    max_open_positions: int = Field(default=5, ge=1, le=20)
    stop_loss_buffer: float = Field(default=0.0, ge=0, le=50)  # additional SL in pips
    take_profit_buffer: float = Field(default=0.0, ge=0, le=50)  # additional TP in pips
    
    # Copy filters
    copy_only_pairs: List[str] = []  # if empty, copy all
    exclude_pairs: List[str] = []
    min_trade_size: float = 0.01
    max_trade_size: float = 10.0
    
    # Time filters
    copy_schedule: Dict[str, bool] = {}  # day of week -> enabled
    copy_hours_start: Optional[str] = None  # "09:00"
    copy_hours_end: Optional[str] = None    # "17:00"
    
    # Status
    status: CopyStatus = CopyStatus.ACTIVE
    auto_stop_loss: float = Field(default=500.0, ge=50)  # stop copying after this loss
    
    # Notifications
    notify_on_trade: bool = True
    notify_on_profit: bool = True
    notify_on_loss: bool = True
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CopyTradeResult(BaseModel):
    """Result of a copied trade"""
    trade_id: str
    copy_settings_id: str
    original_trade_id: str
    trader_id: str
    follower_id: str
    
    # Trade details
    symbol: str
    trade_type: str  # "BUY" or "SELL"
    volume: float
    open_price: float
    close_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    
    # Copy specific
    copy_ratio_used: float
    original_volume: float
    copy_delay_ms: int = 0  # latency in copying
    
    # Results
    profit_loss: Optional[float] = None
    profit_loss_pips: Optional[float] = None
    commission: float = 0.0
    swap: float = 0.0
    
    # Status
    is_open: bool = True
    copy_status: str = "copied"  # copied, failed, skipped
    error_message: Optional[str] = None
    
    # Timestamps
    original_open_time: datetime
    copy_open_time: datetime
    close_time: Optional[datetime] = None
    
class FollowerStats(BaseModel):
    """Statistics for a follower"""
    follower_id: str
    trader_id: str
    
    # Performance
    total_copied_trades: int = 0
    successful_copies: int = 0
    failed_copies: int = 0
    
    # Financial
    total_profit_loss: float = 0.0
    total_commission: float = 0.0
    total_invested: float = 0.0
    current_equity: float = 0.0
    max_drawdown: float = 0.0
    
    # Copy efficiency
    average_copy_delay: float = 0.0  # in milliseconds
    copy_success_rate: float = 0.0
    correlation_with_trader: float = 0.0
    
    # Time period
    start_date: datetime
    last_trade_date: Optional[datetime] = None
    
    # Settings snapshot
    current_copy_settings: Optional[CopySettings] = None

class CopySignal(BaseModel):
    """Signal to copy a trade"""
    signal_id: str
    trader_id: str
    
    # Trade signal
    symbol: str
    action: str  # "BUY", "SELL", "CLOSE"
    volume: float
    price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    
    # Signal metadata
    signal_strength: float = Field(ge=0, le=1)  # confidence 0-1
    reasoning: Optional[str] = None
    expiry_time: Optional[datetime] = None
    
    # Execution
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_processed: bool = False
    
class TraderApplication(BaseModel):
    """Application to become a copy trader"""
    applicant_id: str
    display_name: str
    
    # Trading experience
    years_of_experience: int = Field(ge=0, le=50)
    trading_style: str
    risk_management_approach: str
    
    # Track record (if available)
    verified_performance: Optional[Dict[str, float]] = None
    account_screenshots: List[str] = []
    
    # Personal info
    bio: str = Field(max_length=500)
    location: Optional[str] = None
    languages: List[str] = []
    
    # Application status
    status: str = "pending"  # pending, approved, rejected
    application_date: datetime = Field(default_factory=datetime.utcnow)
    reviewed_by: Optional[str] = None
    review_notes: Optional[str] = None 