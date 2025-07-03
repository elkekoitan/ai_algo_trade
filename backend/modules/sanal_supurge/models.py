"""
Sanal-Süpürge Strategy Models

Pydantic models for grid trading system configuration and operations.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class LotProgressionModel(str, Enum):
    """Lot progression strategies"""
    LINEAR = "linear"
    MARTINGALE = "martingale"
    CUSTOM_MULTIPLIER = "custom_multiplier"
    FIBONACCI_WEIGHTED = "fibonacci_weighted"
    CUSTOM_SEQUENCE = "custom_sequence"


class TradingDirection(str, Enum):
    """Trading directions"""
    BUY = "buy"
    SELL = "sell"
    BOTH = "both"


class GridLevel(BaseModel):
    """Individual grid level configuration"""
    level: int = Field(..., ge=1, le=14, description="Grid level number")
    send_order: bool = Field(True, description="Whether to send order at this level")
    lot_size: float = Field(..., gt=0, description="Lot size for this level")
    distance_points: int = Field(0, ge=0, description="Distance from previous level in points")
    tp_points: int = Field(1000, ge=0, description="Take profit in points")
    sl_points: int = Field(100, ge=0, description="Stop loss in points")
    
    # Runtime fields
    entry_price: Optional[float] = Field(None, description="Actual entry price")
    order_id: Optional[str] = Field(None, description="MT5 order ID")
    opened_at: Optional[datetime] = Field(None, description="Order open time")
    
    @validator('lot_size')
    def validate_lot_size(cls, v):
        if v <= 0 or v > 100:
            raise ValueError('Lot size must be between 0 and 100')
        return round(v, 2)


class RiskSettings(BaseModel):
    """Risk management settings"""
    max_drawdown_percent: float = Field(5.0, ge=0.1, le=50, description="Max drawdown as % of balance")
    max_lot_per_order: float = Field(10.0, gt=0, description="Maximum lot size per order")
    balance: float = Field(10000.0, gt=0, description="Account balance")
    leverage: int = Field(100, ge=1, le=1000, description="Account leverage")
    risk_percent: float = Field(2.0, ge=0.1, le=10, description="Risk per trade as % of balance")


class InstrumentSettings(BaseModel):
    """Trading instrument settings"""
    symbol: str = Field(..., description="Trading symbol")
    point_decimals: int = Field(5, ge=0, le=8, description="Number of decimal places")
    tick_size: float = Field(0.00001, gt=0, description="Minimum price movement")
    value_per_point: float = Field(1.0, gt=0, description="Value per point per lot")
    contract_size: float = Field(100000.0, gt=0, description="Contract size")
    spread: float = Field(0.0, ge=0, description="Current spread")


class GridConfig(BaseModel):
    """Complete grid configuration"""
    # Basic settings
    strategy_name: str = Field("Sanal_Supurge_V1", description="Strategy identifier")
    position_comment: str = Field("HayaletSüpürge", description="MT5 position comment")
    
    # Trading direction
    buy_enabled: bool = Field(True, description="Enable buy orders")
    sell_enabled: bool = Field(True, description="Enable sell orders")
    
    # Pivot settings
    pivot_upper: float = Field(1.8, description="Upper pivot level")
    pivot_lower: float = Field(1.01, description="Lower pivot level")
    
    # Grid configuration
    grid_levels: List[GridLevel] = Field(..., min_items=1, max_items=14, description="Grid levels")
    lot_progression: LotProgressionModel = Field(LotProgressionModel.MARTINGALE, description="Lot progression model")
    custom_multiplier: float = Field(1.5, gt=0, description="Custom multiplier for progression")
    fibonacci_strength: float = Field(0.618, gt=0, le=1, description="Fibonacci strength ratio")
    
    # Auto-calculation settings
    total_lot_target: Optional[float] = Field(None, gt=0, description="Target total lot size")
    default_grid_distance: int = Field(3500, ge=0, description="Default grid distance in points")
    default_tp: int = Field(7000, ge=0, description="Default take profit in points")
    default_sl: int = Field(60000, ge=0, description="Default stop loss in points")
    
    # Time filters
    use_time_filter: bool = Field(False, description="Enable time filtering")
    trading_start_hour: int = Field(2, ge=0, le=23, description="Trading start hour")
    trading_start_minute: int = Field(30, ge=0, le=59, description="Trading start minute")
    trading_end_hour: int = Field(20, ge=0, le=23, description="Trading end hour")
    trading_end_minute: int = Field(30, ge=0, le=59, description="Trading end minute")
    
    use_break_filter: bool = Field(False, description="Enable break time filtering")
    break_start_hour: int = Field(12, ge=0, le=23, description="Break start hour")
    break_start_minute: int = Field(30, ge=0, le=59, description="Break start minute")
    break_end_hour: int = Field(13, ge=0, le=23, description="Break end hour")
    break_end_minute: int = Field(30, ge=0, le=59, description="Break end minute")
    
    # Alert settings
    alert_level_3: bool = Field(True, description="Alert on level 3")
    alert_level_4: bool = Field(True, description="Alert on level 4")
    alert_level_5: bool = Field(True, description="Alert on level 5")
    
    # Instrument and risk
    instrument: InstrumentSettings = Field(..., description="Instrument settings")
    risk_settings: RiskSettings = Field(..., description="Risk management settings")
    
    @validator('grid_levels')
    def validate_grid_levels(cls, v):
        if not v:
            raise ValueError('At least one grid level is required')
        
        # Check level numbers are sequential
        levels = [level.level for level in v]
        if levels != list(range(1, len(levels) + 1)):
            raise ValueError('Grid levels must be sequential starting from 1')
        
        return v


class TradingSession(BaseModel):
    """Active trading session"""
    id: str = Field(..., description="Session ID")
    config: GridConfig = Field(..., description="Grid configuration")
    
    # Session state
    is_active: bool = Field(False, description="Session is active")
    started_at: Optional[datetime] = Field(None, description="Session start time")
    ended_at: Optional[datetime] = Field(None, description="Session end time")
    
    # Current levels
    current_buy_levels: List[GridLevel] = Field(default_factory=list, description="Active buy levels")
    current_sell_levels: List[GridLevel] = Field(default_factory=list, description="Active sell levels")
    
    # Reference levels
    buy_reference_price: Optional[float] = Field(None, description="Buy grid reference price")
    sell_reference_price: Optional[float] = Field(None, description="Sell grid reference price")
    
    # TP/SL levels
    buy_tp_level: float = Field(0.0, description="Current buy TP level")
    sell_tp_level: float = Field(0.0, description="Current sell TP level")
    buy_sl_level: float = Field(0.0, description="Current buy SL level")
    sell_sl_level: float = Field(0.0, description="Current sell SL level")
    
    # Statistics
    total_buy_orders: int = Field(0, description="Total buy orders opened")
    total_sell_orders: int = Field(0, description="Total sell orders opened")
    realized_pnl: float = Field(0.0, description="Realized P&L")
    unrealized_pnl: float = Field(0.0, description="Unrealized P&L")


class PerformanceMetrics(BaseModel):
    """Performance tracking metrics"""
    session_id: str = Field(..., description="Trading session ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="Metrics timestamp")
    
    # P&L metrics
    total_pnl: float = Field(0.0, description="Total P&L")
    realized_pnl: float = Field(0.0, description="Realized P&L")
    unrealized_pnl: float = Field(0.0, description="Unrealized P&L")
    max_drawdown: float = Field(0.0, description="Maximum drawdown")
    max_profit: float = Field(0.0, description="Maximum profit")
    
    # Trade metrics
    total_trades: int = Field(0, description="Total number of trades")
    winning_trades: int = Field(0, description="Number of winning trades")
    losing_trades: int = Field(0, description="Number of losing trades")
    win_rate: float = Field(0.0, description="Win rate percentage")
    
    # Risk metrics
    margin_used: float = Field(0.0, description="Total margin used")
    margin_percentage: float = Field(0.0, description="Margin as % of balance")
    risk_percentage: float = Field(0.0, description="Current risk as % of balance")
    
    # Grid metrics
    active_buy_levels: int = Field(0, description="Number of active buy levels")
    active_sell_levels: int = Field(0, description="Number of active sell levels")
    max_levels_reached: int = Field(0, description="Maximum levels reached simultaneously")
    
    # Speed metrics (for scalping optimization)
    avg_execution_time_ms: float = Field(0.0, description="Average order execution time in milliseconds")
    last_order_latency_ms: float = Field(0.0, description="Last order latency in milliseconds")


class GridCalculationResult(BaseModel):
    """Result of grid calculation"""
    buy_scenarios: List[Dict[str, Any]] = Field(default_factory=list, description="Buy grid scenarios")
    sell_scenarios: List[Dict[str, Any]] = Field(default_factory=list, description="Sell grid scenarios")
    
    # Risk analysis
    max_buy_drawdown: float = Field(0.0, description="Maximum buy drawdown")
    max_sell_drawdown: float = Field(0.0, description="Maximum sell drawdown")
    buy_margin_percent: float = Field(0.0, description="Buy margin percentage")
    sell_margin_percent: float = Field(0.0, description="Sell margin percentage")
    
    # Summary
    total_buy_lots: float = Field(0.0, description="Total buy lots")
    total_sell_lots: float = Field(0.0, description="Total sell lots")
    estimated_max_profit_buy: float = Field(0.0, description="Estimated max profit for buy grid")
    estimated_max_profit_sell: float = Field(0.0, description="Estimated max profit for sell grid")


class CopyTradeSignal(BaseModel):
    """Copy trading signal"""
    signal_id: str = Field(..., description="Unique signal ID")
    source_account: str = Field(..., description="Source account identifier")
    symbol: str = Field(..., description="Trading symbol")
    action: str = Field(..., description="Trade action (open/close/modify)")
    
    # Order details
    order_type: str = Field(..., description="Order type (buy/sell)")
    lot_size: float = Field(..., gt=0, description="Lot size")
    entry_price: float = Field(..., gt=0, description="Entry price")
    take_profit: Optional[float] = Field(None, description="Take profit level")
    stop_loss: Optional[float] = Field(None, description="Stop loss level")
    
    # Metadata
    level: int = Field(..., ge=1, le=14, description="Grid level")
    position_comment: str = Field(..., description="Position comment")
    timestamp: datetime = Field(default_factory=datetime.now, description="Signal timestamp")
    
    # Execution tracking
    executed: bool = Field(False, description="Signal executed")
    execution_time: Optional[datetime] = Field(None, description="Execution timestamp")
    execution_latency_ms: Optional[float] = Field(None, description="Execution latency")
    error_message: Optional[str] = Field(None, description="Error message if execution failed") 