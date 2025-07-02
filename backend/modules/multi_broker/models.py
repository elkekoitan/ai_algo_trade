"""
Multi-Broker Data Models
Universal models for cross-broker trading
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

class BrokerType(str, Enum):
    MT5 = "mt5"
    INTERACTIVE_BROKERS = "interactive_brokers"
    BINANCE = "binance"
    BYBIT = "bybit"
    OANDA = "oanda"
    KRAKEN = "kraken"
    COINBASE = "coinbase"
    FTXUS = "ftxus"
    ALPACA = "alpaca"
    TD_AMERITRADE = "td_ameritrade"

class ConnectionStatus(str, Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    RECONNECTING = "reconnecting"

class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    TRAILING_STOP = "trailing_stop"

class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"

class OrderStatus(str, Enum):
    PENDING = "pending"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"

class AssetType(str, Enum):
    FOREX = "forex"
    CRYPTO = "crypto"
    STOCKS = "stocks"
    COMMODITIES = "commodities"
    INDICES = "indices"
    BONDS = "bonds"
    OPTIONS = "options"
    FUTURES = "futures"

class BrokerConfig(BaseModel):
    """Broker configuration"""
    broker_id: str
    broker_type: BrokerType
    name: str
    display_name: str
    
    # Connection settings
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    server: Optional[str] = None
    login: Optional[str] = None
    password: Optional[str] = None
    
    # Features
    supports_forex: bool = True
    supports_crypto: bool = False
    supports_stocks: bool = False
    supports_options: bool = False
    supports_futures: bool = False
    
    # Limits
    max_positions: int = 100
    max_orders: int = 200
    min_lot_size: float = 0.01
    max_lot_size: float = 100.0
    
    # Settings
    is_demo: bool = True
    is_active: bool = True
    auto_reconnect: bool = True
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_connected: Optional[datetime] = None

class BrokerConnection(BaseModel):
    """Broker connection status"""
    broker_id: str
    broker_type: BrokerType
    status: ConnectionStatus = ConnectionStatus.DISCONNECTED
    
    # Connection info
    connected_at: Optional[datetime] = None
    last_ping: Optional[datetime] = None
    ping_latency: Optional[float] = None
    
    # Account info
    account_id: Optional[str] = None
    account_currency: Optional[str] = None
    balance: Optional[float] = None
    equity: Optional[float] = None
    margin: Optional[float] = None
    free_margin: Optional[float] = None
    
    # Error info
    last_error: Optional[str] = None
    error_count: int = 0
    reconnect_attempts: int = 0
    
    # Statistics
    uptime_percentage: float = 0.0
    total_orders: int = 0
    total_trades: int = 0

class UniversalSymbol(BaseModel):
    """Universal symbol representation"""
    symbol: str
    broker_symbol: str  # Broker-specific symbol
    broker_id: str
    
    # Symbol info
    asset_type: AssetType
    base_currency: Optional[str] = None
    quote_currency: Optional[str] = None
    
    # Trading specs
    min_lot_size: float = 0.01
    max_lot_size: float = 100.0
    lot_step: float = 0.01
    pip_size: float = 0.0001
    pip_value: float = 1.0
    
    # Market hours
    trading_hours: Optional[Dict[str, Any]] = None
    is_tradeable: bool = True
    
    # Current market data
    bid: Optional[float] = None
    ask: Optional[float] = None
    last_price: Optional[float] = None
    volume: Optional[float] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None
    
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class UniversalOrder(BaseModel):
    """Universal order representation"""
    order_id: str
    broker_order_id: str
    broker_id: str
    
    # Order details
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    
    # Order management
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: float = 0.0
    remaining_quantity: float = 0.0
    average_fill_price: Optional[float] = None
    
    # Risk management
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    trailing_stop: Optional[float] = None
    
    # Timing
    time_in_force: str = "GTC"  # Good Till Cancelled
    expires_at: Optional[datetime] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    filled_at: Optional[datetime] = None
    
    # Additional info
    commission: Optional[float] = None
    fees: Optional[float] = None
    notes: Optional[str] = None

class UniversalPosition(BaseModel):
    """Universal position representation"""
    position_id: str
    broker_position_id: str
    broker_id: str
    
    # Position details
    symbol: str
    side: OrderSide
    quantity: float
    entry_price: float
    current_price: Optional[float] = None
    
    # P&L
    unrealized_pnl: Optional[float] = None
    realized_pnl: Optional[float] = None
    total_pnl: Optional[float] = None
    
    # Risk management
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    
    # Timing
    opened_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    closed_at: Optional[datetime] = None
    
    # Additional info
    commission: Optional[float] = None
    swap: Optional[float] = None
    notes: Optional[str] = None

class UniversalTrade(BaseModel):
    """Universal trade representation"""
    trade_id: str
    broker_trade_id: str
    broker_id: str
    order_id: str
    
    # Trade details
    symbol: str
    side: OrderSide
    quantity: float
    price: float
    
    # P&L
    gross_pnl: float
    commission: float = 0.0
    fees: float = 0.0
    swap: float = 0.0
    net_pnl: float
    
    # Timing
    executed_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Additional info
    notes: Optional[str] = None

class BrokerCapabilities(BaseModel):
    """Broker capabilities and features"""
    broker_type: BrokerType
    
    # Asset support
    supported_assets: List[AssetType]
    supported_symbols: List[str]
    
    # Order types
    supported_order_types: List[OrderType]
    supports_stop_loss: bool = True
    supports_take_profit: bool = True
    supports_trailing_stop: bool = False
    
    # Features
    supports_partial_fills: bool = True
    supports_market_data: bool = True
    supports_historical_data: bool = True
    supports_real_time_data: bool = True
    
    # Limitations
    max_orders_per_minute: Optional[int] = None
    max_positions: Optional[int] = None
    min_order_size: Optional[float] = None
    max_order_size: Optional[float] = None
    
    # API features
    has_websocket: bool = False
    has_rest_api: bool = True
    rate_limits: Dict[str, int] = {}

class BrokerAccountInfo(BaseModel):
    """Universal account information"""
    broker_id: str
    account_id: str
    
    # Account details
    account_name: Optional[str] = None
    account_type: str = "demo"  # demo, live
    account_currency: str = "USD"
    
    # Balances
    balance: float = 0.0
    equity: float = 0.0
    margin: float = 0.0
    free_margin: float = 0.0
    margin_level: Optional[float] = None
    
    # Statistics
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    total_profit: float = 0.0
    total_loss: float = 0.0
    
    # Limits
    max_leverage: Optional[float] = None
    margin_call_level: Optional[float] = None
    stop_out_level: Optional[float] = None
    
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class MarketData(BaseModel):
    """Universal market data"""
    symbol: str
    broker_id: str
    
    # Price data
    bid: float
    ask: float
    last: Optional[float] = None
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    
    # Volume and spread
    volume: Optional[float] = None
    spread: Optional[float] = None
    
    # Changes
    change: Optional[float] = None
    change_percent: Optional[float] = None
    
    # Timestamp
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class HistoricalData(BaseModel):
    """Historical market data"""
    symbol: str
    broker_id: str
    timeframe: str  # M1, M5, M15, M30, H1, H4, D1, W1, MN1
    
    # OHLCV data
    data: List[Dict[str, Any]]  # [{"time": datetime, "open": float, "high": float, "low": float, "close": float, "volume": float}]
    
    # Metadata
    start_date: datetime
    end_date: datetime
    total_bars: int
    
    retrieved_at: datetime = Field(default_factory=datetime.utcnow)

class BrokerError(BaseModel):
    """Broker error information"""
    broker_id: str
    error_code: str
    error_message: str
    error_type: str  # connection, api, order, position
    
    # Context
    operation: Optional[str] = None
    symbol: Optional[str] = None
    order_id: Optional[str] = None
    
    # Timing
    occurred_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Additional info
    is_recoverable: bool = True
    retry_count: int = 0
    resolution_status: str = "pending"  # pending, resolved, failed 