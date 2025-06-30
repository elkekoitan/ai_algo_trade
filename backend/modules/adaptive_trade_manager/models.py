"""
Data models for the Adaptive Trade Manager
"""
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class RiskLevel(str, Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class PositionStatus(str, Enum):
    OPEN = "open"
    MONITORING = "monitoring"
    ADJUSTING = "adjusting"
    CLOSING = "closing"
    CLOSED = "closed"

class AdjustmentType(str, Enum):
    INCREASE_SIZE = "increase_size"
    DECREASE_SIZE = "decrease_size"
    MOVE_STOP_LOSS = "move_stop_loss"
    MOVE_TAKE_PROFIT = "move_take_profit"
    PARTIAL_CLOSE = "partial_close"
    HEDGE = "hedge"

class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

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
    account_balance: float = Field(..., description="Current account balance")
    equity: float = Field(..., description="Current equity")
    margin_used: float = Field(..., description="Used margin")
    free_margin: float = Field(..., description="Free margin")
    margin_level: float = Field(..., description="Margin level percentage")
    
    # Portfolio Risk
    total_risk: float = Field(..., description="Total portfolio risk amount")
    risk_percentage: float = Field(..., description="Risk as percentage of equity")
    max_drawdown: float = Field(..., description="Current maximum drawdown")
    var_95: float = Field(..., description="Value at Risk 95%")
    
    # Position Metrics
    open_positions: int = Field(..., description="Number of open positions")
    correlation_score: float = Field(..., description="Portfolio correlation score")
    diversification_ratio: float = Field(..., description="Portfolio diversification")
    
    # Risk Assessment
    overall_risk_level: RiskLevel = Field(..., description="Overall risk assessment")
    recommendation: str = Field(..., description="Risk management recommendation")

class PositionOptimization(BaseModel):
    position_id: str = Field(..., description="Position being optimized")
    optimization_type: str = Field(..., description="Type of optimization")
    
    # Current vs Recommended
    current_size: float = Field(..., description="Current position size")
    recommended_size: float = Field(..., description="AI recommended size")
    current_stop_loss: Optional[float] = Field(None, description="Current stop loss")
    recommended_stop_loss: Optional[float] = Field(None, description="Recommended stop loss")
    current_take_profit: Optional[float] = Field(None, description="Current take profit")
    recommended_take_profit: Optional[float] = Field(None, description="Recommended take profit")
    
    # Optimization Reasoning
    confidence: float = Field(..., description="Confidence in optimization")
    reasoning: str = Field(..., description="AI reasoning for changes")
    expected_improvement: float = Field(..., description="Expected performance improvement")
    risk_reduction: float = Field(..., description="Expected risk reduction")
    
    # Implementation
    priority: int = Field(..., description="Implementation priority 1-10")
    estimated_execution_time: int = Field(..., description="Estimated execution time in seconds")

class AlertRule(BaseModel):
    rule_id: str = Field(..., description="Unique rule identifier")
    name: str = Field(..., description="Alert rule name")
    description: str = Field(..., description="Rule description")
    
    # Trigger Conditions
    metric: str = Field(..., description="Metric to monitor")
    threshold: float = Field(..., description="Alert threshold")
    comparison: str = Field(..., description="Comparison operator")
    
    # Alert Settings
    severity: AlertSeverity = Field(..., description="Alert severity")
    enabled: bool = Field(default=True, description="Rule enabled status")
    cooldown_minutes: int = Field(default=5, description="Cooldown between alerts")
    
    # Actions
    auto_adjust: bool = Field(default=False, description="Auto-adjust positions")
    notify_user: bool = Field(default=True, description="Send notification")
    
    last_triggered: Optional[datetime] = Field(None, description="Last trigger time")

class TradeAlert(BaseModel):
    alert_id: str = Field(..., description="Unique alert identifier")
    rule_id: str = Field(..., description="Triggering rule ID")
    severity: AlertSeverity = Field(..., description="Alert severity")
    
    # Alert Details
    title: str = Field(..., description="Alert title")
    message: str = Field(..., description="Alert message")
    metric_value: float = Field(..., description="Current metric value")
    threshold: float = Field(..., description="Alert threshold")
    
    # Context
    affected_positions: List[str] = Field(default_factory=list, description="Affected position IDs")
    recommended_action: str = Field(..., description="Recommended action")
    auto_executed: bool = Field(default=False, description="Auto-execution status")
    
    # Timestamps
    created_at: datetime = Field(..., description="Alert creation time")
    acknowledged_at: Optional[datetime] = Field(None, description="Acknowledgment time")
    resolved_at: Optional[datetime] = Field(None, description="Resolution time")

class PortfolioAnalysis(BaseModel):
    analysis_time: datetime = Field(..., description="Analysis timestamp")
    
    # Portfolio Metrics
    total_value: float = Field(..., description="Total portfolio value")
    unrealized_pnl: float = Field(..., description="Total unrealized P&L")
    daily_pnl: float = Field(..., description="Daily P&L")
    win_rate: float = Field(..., description="Win rate percentage")
    
    # Risk Analytics
    portfolio_beta: float = Field(..., description="Portfolio beta")
    sharpe_ratio: float = Field(..., description="Sharpe ratio")
    sortino_ratio: float = Field(..., description="Sortino ratio")
    max_drawdown: float = Field(..., description="Maximum drawdown")
    
    # Position Distribution
    positions_by_symbol: Dict[str, int] = Field(default_factory=dict, description="Positions per symbol")
    risk_by_symbol: Dict[str, float] = Field(default_factory=dict, description="Risk per symbol")
    correlation_matrix: Dict[str, Dict[str, float]] = Field(default_factory=dict, description="Correlation matrix")
    
    # AI Insights
    market_regime: str = Field(..., description="Current market regime")
    regime_confidence: float = Field(..., description="Regime detection confidence")
    portfolio_score: float = Field(..., description="Overall portfolio score 0-100")
    optimization_suggestions: List[str] = Field(default_factory=list, description="Optimization suggestions")

class AdaptiveSettings(BaseModel):
    # Risk Management
    max_risk_per_trade: float = Field(default=0.02, description="Maximum risk per trade (2%)")
    max_portfolio_risk: float = Field(default=0.20, description="Maximum portfolio risk (20%)")
    max_correlation: float = Field(default=0.70, description="Maximum position correlation")
    max_positions: int = Field(default=10, description="Maximum concurrent positions")
    
    # Position Sizing
    base_position_size: float = Field(default=0.01, description="Base position size (1%)")
    confidence_multiplier: float = Field(default=2.0, description="Confidence-based multiplier")
    volatility_adjustment: bool = Field(default=True, description="Adjust for volatility")
    trend_adjustment: bool = Field(default=True, description="Adjust for trend strength")
    
    # Auto-Adjustment
    auto_adjust_enabled: bool = Field(default=True, description="Enable auto-adjustments")
    adjustment_threshold: float = Field(default=0.1, description="Threshold for adjustments")
    stop_loss_adjustment: bool = Field(default=True, description="Auto-adjust stop losses")
    take_profit_adjustment: bool = Field(default=True, description="Auto-adjust take profits")
    
    # Monitoring
    update_interval_seconds: int = Field(default=30, description="Update interval")
    alert_enabled: bool = Field(default=True, description="Enable alerts")
    risk_monitoring: bool = Field(default=True, description="Enable risk monitoring")

class AdaptiveTradeManagerStatus(BaseModel):
    status: str = Field(default="active", description="Manager status")
    total_positions: int = Field(..., description="Total managed positions")
    active_adjustments: int = Field(..., description="Active adjustments")
    total_alerts: int = Field(..., description="Total alerts today")
    performance_score: float = Field(..., description="Performance score 0-100")
    risk_score: float = Field(..., description="Risk score 0-100")
    last_optimization: Optional[datetime] = Field(None, description="Last optimization time")
    uptime_hours: float = Field(..., description="System uptime in hours")
    
    # System Health
    cpu_usage: float = Field(..., description="CPU usage percentage")
    memory_usage: float = Field(..., description="Memory usage percentage")
    latency_ms: float = Field(..., description="Average latency in milliseconds")
    error_count: int = Field(default=0, description="Error count in last hour")

# API Response Models
class PositionAdjustmentResponse(BaseModel):
    success: bool
    position_id: str
    adjustment_type: AdjustmentType
    old_value: float
    new_value: float
    reasoning: str
    expected_impact: str

class RiskAssessmentResponse(BaseModel):
    success: bool
    risk_level: RiskLevel
    risk_score: float
    recommendations: List[str]
    immediate_actions: List[str]
    portfolio_health: str

class DynamicPosition(BaseModel):
    position_id: str = Field(..., description="Unique position identifier")
    symbol: str = Field(..., description="Trading symbol")
    entry_price: float = Field(..., description="Entry price")
    current_price: float = Field(..., description="Current market price")
    position_size: float = Field(..., description="Current position size")
    original_size: float = Field(..., description="Original position size")
    status: PositionStatus = Field(..., description="Position status")
    
    # Risk Metrics
    stop_loss: Optional[float] = Field(None, description="Current stop loss level")
    take_profit: Optional[float] = Field(None, description="Current take profit level")
    unrealized_pnl: float = Field(..., description="Current unrealized P&L")
    risk_amount: float = Field(..., description="Amount at risk")
    risk_percentage: float = Field(..., description="Risk as percentage of account")
    
    # AI Analytics
    confidence_score: float = Field(..., description="AI confidence in position 0-100")
    market_sentiment: float = Field(..., description="Market sentiment -100 to +100")
    volatility_forecast: float = Field(..., description="Expected volatility")
    trend_strength: float = Field(..., description="Trend strength 0-100")
    
    # Timestamps
    entry_time: datetime = Field(..., description="Position entry time")
    last_update: datetime = Field(..., description="Last update time")
    
    # Adjustment History
    adjustments: List[Dict[str, Any]] = Field(default_factory=list, description="History of adjustments")

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