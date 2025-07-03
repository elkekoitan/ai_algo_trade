"""
Strategy Manager Models

MQL4/5 strateji yönetimi için data modelleri.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from datetime import datetime

class StrategyType(str, Enum):
    """Strateji türleri"""
    GRID_TRADING = "grid_trading"
    SCALPING = "scalping"
    TREND_FOLLOWING = "trend_following"
    BREAKOUT = "breakout"
    ARBITRAGE = "arbitrage"
    HEDGING = "hedging"
    CUSTOM = "custom"

class ExecutionMode(str, Enum):
    """Execution modları"""
    ROBOT = "robot"          # Tam otomatik
    SIGNAL = "signal"        # Sadece sinyal üret
    MANUAL = "manual"        # Manuel trading, strateji analiz sağlar
    HYBRID = "hybrid"        # Sinyal + yarı otomatik

class ParameterType(str, Enum):
    """MQL parametre tipleri"""
    BOOL = "bool"
    INT = "int"
    DOUBLE = "double"
    STRING = "string"
    ENUM = "enum"
    DATETIME = "datetime"
    COLOR = "color"

class SignalType(str, Enum):
    """Sinyal türleri"""
    BUY = "buy"
    SELL = "sell"
    CLOSE_BUY = "close_buy"
    CLOSE_SELL = "close_sell"
    MODIFY = "modify"
    NEUTRAL = "neutral"

class StrategyParameter(BaseModel):
    """Strateji parametresi"""
    name: str
    display_name: str
    type: ParameterType
    default_value: Any
    current_value: Optional[Any] = None
    description: Optional[str] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    step: Optional[Union[int, float]] = None
    options: Optional[List[str]] = None  # Enum için
    group: Optional[str] = None  # UI'da gruplama için
    is_required: bool = True
    is_visible: bool = True
    validation_regex: Optional[str] = None

class ParameterGroup(BaseModel):
    """Parametre grubu - UI organizasyonu için"""
    name: str
    display_name: str
    description: Optional[str] = None
    parameters: List[str]  # Parameter names
    order: int = 0
    is_expanded: bool = True

class StrategyMetadata(BaseModel):
    """Strateji metadata"""
    strategy_id: str
    name: str
    display_name: str
    version: str = "1.0"
    type: StrategyType
    platform: str = "MT5"  # MT4 veya MT5
    description: Optional[str] = None
    author: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Dosya bilgileri
    main_file: str  # Ana .mq4/.mq5 dosyası
    include_files: List[str] = []  # .mqh dosyaları
    resource_files: List[str] = []  # Diğer kaynaklar
    
    # Özellikler
    supported_symbols: List[str] = ["*"]  # * = tüm semboller
    recommended_timeframes: List[str] = []
    minimum_balance: float = 1000.0
    recommended_leverage: int = 100
    
    # Risk parametreleri
    default_risk_percent: float = 1.0
    max_positions: int = 1
    
    # Performans metrikleri
    backtest_results: Optional[Dict[str, Any]] = None
    live_performance: Optional[Dict[str, Any]] = None
    
    # Kullanım istatistikleri
    total_users: int = 0
    active_instances: int = 0
    average_rating: float = 0.0
    
    # Kategoriler ve etiketler
    categories: List[str] = []
    tags: List[str] = []

class StrategyInstance(BaseModel):
    """Çalışan strateji instance'ı"""
    instance_id: str
    strategy_id: str
    user_id: str
    account_login: int
    
    # Execution ayarları
    execution_mode: ExecutionMode
    is_active: bool = True
    
    # Parametre değerleri
    parameters: Dict[str, Any]
    
    # Çalışma durumu
    status: str = "idle"  # idle, running, paused, error
    last_signal: Optional[datetime] = None
    total_signals: int = 0
    
    # Performans
    open_positions: int = 0
    total_trades: int = 0
    profit_loss: float = 0.0
    win_rate: float = 0.0
    
    # Timestamps
    started_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class TradingSignal(BaseModel):
    """Trading sinyali"""
    signal_id: str
    instance_id: str
    strategy_id: str
    
    # Sinyal detayları
    signal_type: SignalType
    symbol: str
    direction: Optional[str] = None  # buy/sell
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    lot_size: Optional[float] = None
    
    # Risk yönetimi
    risk_amount: Optional[float] = None
    risk_percent: Optional[float] = None
    risk_reward_ratio: Optional[float] = None
    
    # Sinyal metadata
    confidence: float = 0.0  # 0-100
    analysis: Optional[Dict[str, Any]] = None  # Teknik analiz dataları
    reasoning: Optional[str] = None  # Sinyal açıklaması
    
    # Execution
    execution_mode: ExecutionMode
    is_executed: bool = False
    executed_at: Optional[datetime] = None
    execution_price: Optional[float] = None
    order_ticket: Optional[int] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    
class StrategyConfig(BaseModel):
    """Strateji konfigürasyonu"""
    strategy_id: str
    name: str
    description: Optional[str] = None
    parameters: Dict[str, Any]
    created_by: Optional[str] = None
    is_public: bool = False
    created_at: datetime = Field(default_factory=datetime.now)

class StrategyUploadRequest(BaseModel):
    """Strateji yükleme isteği"""
    name: str
    display_name: str
    type: StrategyType
    platform: str = "MT5"
    description: Optional[str] = None
    main_file_content: str
    include_files: Optional[Dict[str, str]] = None  # filename: content
    author: Optional[str] = None
    supported_symbols: List[str] = ["*"]
    recommended_timeframes: List[str] = []
    categories: List[str] = []
    tags: List[str] = []

class StrategyListRequest(BaseModel):
    """Strateji listesi isteği"""
    type: Optional[StrategyType] = None
    platform: Optional[str] = None
    categories: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    search: Optional[str] = None
    page: int = 1
    page_size: int = 20
    sort_by: str = "created_at"
    sort_order: str = "desc"

class CreateInstanceRequest(BaseModel):
    """Strateji instance oluşturma isteği"""
    strategy_id: str
    account_login: int
    execution_mode: ExecutionMode = ExecutionMode.SIGNAL
    parameters: Dict[str, Any]
    auto_start: bool = True

class UpdateInstanceRequest(BaseModel):
    """Instance güncelleme isteği"""
    execution_mode: Optional[ExecutionMode] = None
    parameters: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class ManualTradeRequest(BaseModel):
    """Manuel işlem isteği"""
    instance_id: str
    symbol: str
    action: str  # buy, sell, close
    lot_size: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    comment: Optional[str] = None

class BacktestRequest(BaseModel):
    """Backtest isteği"""
    strategy_id: str
    parameters: Dict[str, Any]
    symbol: str
    timeframe: str
    start_date: datetime
    end_date: datetime
    initial_balance: float = 10000.0
    leverage: int = 100
    spread: float = 2.0
    commission: float = 7.0  # per lot

class BacktestResult(BaseModel):
    """Backtest sonucu"""
    strategy_id: str
    parameters: Dict[str, Any]
    
    # Test bilgileri
    symbol: str
    timeframe: str
    start_date: datetime
    end_date: datetime
    initial_balance: float
    final_balance: float
    
    # Performans metrikleri
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    profit_factor: float
    sharpe_ratio: float
    max_drawdown: float
    max_drawdown_percent: float
    
    # Trade istatistikleri
    average_win: float
    average_loss: float
    largest_win: float
    largest_loss: float
    average_trade_duration: float
    
    # Detaylı sonuçlar
    equity_curve: List[Dict[str, Any]]
    trade_history: List[Dict[str, Any]]
    monthly_returns: Dict[str, float]
    
    # Metadata
    execution_time: float
    created_at: datetime = Field(default_factory=datetime.now)

class StrategyStatistics(BaseModel):
    """Strateji istatistikleri"""
    strategy_id: str
    total_instances: int = 0
    active_instances: int = 0
    total_signals: int = 0
    total_trades: int = 0
    average_profit: float = 0.0
    average_win_rate: float = 0.0
    user_ratings: List[int] = []
    average_rating: float = 0.0
    last_updated: datetime = Field(default_factory=datetime.now) 