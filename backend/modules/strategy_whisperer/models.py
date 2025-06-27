"""
Strategy Whisperer Data Models
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field


class Language(str, Enum):
    TURKISH = "tr"
    ENGLISH = "en"


class StrategyType(str, Enum):
    TREND_FOLLOWING = "trend_following"
    MEAN_REVERSION = "mean_reversion"
    BREAKOUT = "breakout"
    SCALPING = "scalping"
    SWING = "swing"
    ARBITRAGE = "arbitrage"


class TimeFrame(str, Enum):
    M1 = "M1"
    M5 = "M5"
    M15 = "M15"
    M30 = "M30"
    H1 = "H1"
    H4 = "H4"
    D1 = "D1"
    W1 = "W1"
    MN1 = "MN1"


class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class RiskType(str, Enum):
    FIXED_LOT = "fixed_lot"
    PERCENT_BALANCE = "percent_balance"
    PERCENT_EQUITY = "percent_equity"
    FIXED_AMOUNT = "fixed_amount"


class IndicatorType(str, Enum):
    RSI = "RSI"
    MACD = "MACD"
    MA = "MA"
    EMA = "EMA"
    SMA = "SMA"
    BOLLINGER = "BOLLINGER"
    STOCHASTIC = "STOCHASTIC"
    ATR = "ATR"
    ADX = "ADX"
    ICHIMOKU = "ICHIMOKU"
    FIBONACCI = "FIBONACCI"
    PIVOT = "PIVOT"


class StrategyIntent(BaseModel):
    """User's strategy intent from natural language"""
    raw_text: str
    language: Language
    detected_type: Optional[StrategyType] = None
    confidence: float = Field(ge=0, le=1)
    entities: Dict[str, Any] = {}
    clarifications_needed: List[str] = []
    timestamp: datetime = Field(default_factory=datetime.now)


class TradingCondition(BaseModel):
    """A single trading condition"""
    indicator: IndicatorType
    parameters: Dict[str, Any]
    comparison: str  # >, <, ==, crosses_above, crosses_below
    value: float
    timeframe: TimeFrame


class StrategyParameters(BaseModel):
    """Complete strategy parameters"""
    name: str
    description: str
    type: StrategyType
    symbol: str = "EURUSD"
    timeframe: TimeFrame
    
    # Entry conditions
    entry_conditions: List[TradingCondition]
    entry_logic: str = "AND"  # AND/OR
    
    # Exit conditions
    exit_conditions: List[TradingCondition]
    exit_logic: str = "AND"  # AND/OR
    
    # Risk management
    risk_type: RiskType
    risk_value: float
    stop_loss_pips: Optional[float] = None
    stop_loss_atr: Optional[float] = None
    take_profit_pips: Optional[float] = None
    take_profit_ratio: Optional[float] = None
    trailing_stop: Optional[float] = None
    
    # Additional parameters
    max_positions: int = 1
    magic_number: int = Field(default_factory=lambda: int(datetime.now().timestamp()))
    
    # Validation status
    is_valid: bool = True
    validation_errors: List[str] = []


class BacktestRequest(BaseModel):
    """Backtest request parameters"""
    strategy_id: str
    symbol: str
    timeframe: TimeFrame
    start_date: datetime
    end_date: datetime
    initial_balance: float = 10000
    leverage: int = 100
    spread: float = 1.0
    commission: float = 0.0
    
    # Advanced options
    monte_carlo_runs: int = 0
    walk_forward: bool = False
    optimization: bool = False


class BacktestResult(BaseModel):
    """Backtest execution results"""
    strategy_id: str
    
    # Performance metrics
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    
    # Financial metrics
    initial_balance: float
    final_balance: float
    net_profit: float
    gross_profit: float
    gross_loss: float
    profit_factor: float
    
    # Risk metrics
    max_drawdown: float
    max_drawdown_percent: float
    sharpe_ratio: float
    sortino_ratio: float
    
    # Trade statistics
    average_win: float
    average_loss: float
    largest_win: float
    largest_loss: float
    average_trade_duration: float
    
    # Additional data
    equity_curve: List[float]
    trade_list: List[Dict[str, Any]]
    monthly_returns: Dict[str, float]
    
    # Execution info
    execution_time: float
    backtest_date: datetime = Field(default_factory=datetime.now)


class MQL5Code(BaseModel):
    """Generated MQL5 code"""
    strategy_id: str
    code: str
    version: str = "1.0.0"
    
    # Metadata
    estimated_lines: int
    includes: List[str]
    external_dependencies: List[str]
    
    # Validation
    syntax_valid: bool = True
    syntax_errors: List[str] = []
    warnings: List[str] = []
    
    # Optimization hints
    optimization_suggestions: List[str] = []
    performance_score: float = Field(ge=0, le=100)


class DeploymentRequest(BaseModel):
    """Strategy deployment request"""
    strategy_id: str
    code: str
    target_account: str
    symbol: str
    
    # Deployment options
    auto_start: bool = False
    test_mode: bool = True
    notification_email: Optional[str] = None


class DeploymentStatus(BaseModel):
    """Deployment status tracking"""
    deployment_id: str
    strategy_id: str
    status: str  # pending, deploying, success, failed
    
    # MT5 info
    expert_name: str
    magic_number: int
    chart_id: Optional[int] = None
    
    # Version control
    version: str
    previous_version: Optional[str] = None
    
    # Status details
    progress: float = Field(ge=0, le=100)
    messages: List[str] = []
    error: Optional[str] = None
    
    # Timestamps
    started_at: datetime
    completed_at: Optional[datetime] = None


class StrategyTemplate(BaseModel):
    """Pre-built strategy templates"""
    template_id: str
    name: str
    description: str
    category: StrategyType
    
    # Template content
    base_code: str
    placeholders: Dict[str, str]
    default_parameters: Dict[str, Any]
    
    # Usage stats
    usage_count: int = 0
    success_rate: float = Field(ge=0, le=1)
    average_performance: float = 0.0
    
    # Metadata
    author: str = "AI"
    created_at: datetime
    updated_at: datetime


class ConversationContext(BaseModel):
    """Chat conversation context"""
    session_id: str
    user_id: str
    messages: List[Dict[str, str]] = []
    
    # Current strategy being discussed
    current_intent: Optional[StrategyIntent] = None
    current_parameters: Optional[StrategyParameters] = None
    
    # Context state
    state: str = "initial"  # initial, clarifying, generating, testing, deploying
    clarifications_pending: List[str] = []
    
    # History
    generated_strategies: List[str] = []
    deployed_strategies: List[str] = []
    
    # Timestamps
    started_at: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now) 