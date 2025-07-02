"""
Strategy Whisperer Data Models - Fixed Version
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from dataclasses import dataclass

class Language(str, Enum):
    TURKISH = "turkish"
    ENGLISH = "english"
    GERMAN = "german"
    FRENCH = "french"
    SPANISH = "spanish"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

class RiskType(str, Enum):
    FIXED_LOT = "FIXED_LOT"
    PERCENT_BALANCE = "PERCENT_BALANCE"
    FIXED_AMOUNT = "FIXED_AMOUNT"

class StrategyType(str, Enum):
    TREND_FOLLOWING = "TREND_FOLLOWING"
    MEAN_REVERSION = "MEAN_REVERSION"
    BREAKOUT = "BREAKOUT"
    SCALPING = "SCALPING"
    SWING_TRADING = "SWING_TRADING"

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

class IndicatorType(str, Enum):
    SMA = "SMA"
    EMA = "EMA"
    RSI = "RSI"
    MACD = "MACD"
    BOLLINGER = "BOLLINGER"
    STOCHASTIC = "STOCHASTIC"
    ADX = "ADX"
    CCI = "CCI"
    WILLIAMS = "WILLIAMS"
    MOMENTUM = "MOMENTUM"
    ROC = "ROC"
    PIVOT = "PIVOT"

class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"

# Trading condition class
class TradingCondition:
    """Trading condition with indicator and comparison"""
    def __init__(self, indicator, parameters, comparison, value, timeframe):
        self.indicator = indicator
        self.parameters = parameters
        self.comparison = comparison
        self.value = value
        self.timeframe = timeframe

# Dataclass models
@dataclass
class StrategyIntent:
    """Represents user's intent for strategy creation"""
    raw_text: str
    language: Language
    detected_type: Optional[str] = None
    confidence: float = 0.0
    entities: Dict[str, Any] = None
    clarifications_needed: List[str] = None
    
    def __post_init__(self):
        if self.entities is None:
            self.entities = {}
        if self.clarifications_needed is None:
            self.clarifications_needed = []

@dataclass  
class StrategyParameters:
    """Complete strategy parameters ready for code generation"""
    name: str
    description: str
    type: str
    symbol: str
    timeframe: str
    entry_conditions: List[Any]
    entry_logic: str = "AND"  # AND/OR logic between conditions
    exit_conditions: List[Any] = None
    exit_logic: str = "OR"
    risk_type: RiskType = RiskType.PERCENT_BALANCE
    risk_value: float = 1.0
    stop_loss_pips: Optional[float] = None
    take_profit_pips: Optional[float] = None
    trailing_stop: Optional[float] = None
    max_positions: int = 1
    is_valid: bool = True
    validation_errors: List[str] = None
    
    def __post_init__(self):
        if self.exit_conditions is None:
            self.exit_conditions = []
        if self.validation_errors is None:
            self.validation_errors = []

# Pydantic models for API
class StrategyRequest(BaseModel):
    description: str
    language: Language = Language.TURKISH
    preferred_timeframe: Optional[str] = "H1"
    risk_tolerance: RiskLevel = RiskLevel.MEDIUM
    max_trades_per_day: Optional[int] = None

class StrategyResponse(BaseModel):
    strategy_id: str
    name: str
    description: str
    mql5_code: str
    parameters: Dict[str, Any]
    risk_level: RiskLevel
    complexity_score: float
    estimated_performance: Dict[str, float]
    warnings: List[str] = []
    suggestions: List[str] = []
    created_at: datetime

class StrategyMetrics(BaseModel):
    strategy_id: str
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    profit_factor: float
    max_drawdown: float
    total_return: float
    sharpe_ratio: float
    sortino_ratio: float
    last_updated: datetime

class BacktestRequest(BaseModel):
    mql5_code: str
    symbol: str = "EURUSD"
    timeframe: str = "H1"
    start_date: datetime
    end_date: datetime
    initial_balance: float = 10000.0

class BacktestResult(BaseModel):
    success: bool
    total_trades: int
    winning_trades: int
    losing_trades: int
    total_profit: float
    max_drawdown: float
    profit_factor: float
    sharpe_ratio: float
    equity_curve: List[Dict[str, Any]]
    detailed_trades: List[Dict[str, Any]]
    generated_at: datetime

class DeploymentRequest(BaseModel):
    strategy_code: str
    symbol: str = "EURUSD"
    lot_size: float = 0.1
    magic_number: Optional[int] = None

class DeploymentResult(BaseModel):
    success: bool
    deployment_id: str
    message: str
    expert_advisor_path: Optional[str] = None
    deployed_at: datetime

class CodeSection(BaseModel):
    section_name: str
    code: str
    description: str

class MQL5Code(BaseModel):
    code: str
    sections: List[CodeSection] = []
    warnings: List[str] = []
    suggestions: List[str] = []
    estimated_complexity: float = 0.5

class DeploymentStatus(BaseModel):
    deployment_id: str
    status: str
    message: str
    deployed_at: Optional[datetime] = None

class ConversationContext(BaseModel):
    conversation_id: str
    state: str = "listening"
    current_intent: Optional[Dict[str, Any]] = None
    current_parameters: Optional[Dict[str, Any]] = None
    messages: List[Dict[str, Any]] = [] 