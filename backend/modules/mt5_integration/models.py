"""
MT5 data models and configurations.
"""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
from enum import Enum


class OrderType(str, Enum):
    """Order types."""
    BUY = "BUY"
    SELL = "SELL"
    BUY_LIMIT = "BUY_LIMIT"
    SELL_LIMIT = "SELL_LIMIT"
    BUY_STOP = "BUY_STOP"
    SELL_STOP = "SELL_STOP"


class OrderStatus(str, Enum):
    """Order status."""
    PENDING = "PENDING"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


@dataclass
class MT5Config:
    """MT5 connection configuration."""
    login: int
    password: str
    server: str
    timeout: int = 60000
    portable: bool = False


@dataclass
class SymbolInfo:
    """Symbol information from MT5."""
    name: str
    point: float
    digits: int
    spread: int
    bid: float
    ask: float
    volume_min: float
    volume_max: float
    volume_step: float
    trade_mode: int
    
    @property
    def is_tradeable(self) -> bool:
        """Check if symbol is tradeable."""
        return self.trade_mode == 0


@dataclass
class AccountInfo:
    """Account information from MT5."""
    login: int
    balance: float
    equity: float
    margin: float
    margin_free: float
    margin_level: float
    profit: float
    leverage: int
    currency: str
    server: str
    company: str
    
    @property
    def margin_used_percent(self) -> float:
        """Calculate margin usage percentage."""
        if self.equity == 0:
            return 0
        return (self.margin / self.equity) * 100


@dataclass
class OrderRequest:
    """Order request parameters."""
    symbol: str
    order_type: OrderType
    volume: float
    price: Optional[float] = None
    sl: Optional[float] = None
    tp: Optional[float] = None
    deviation: int = 20
    magic: int = 234000
    comment: str = "ICT Ultra v2"
    
    def to_mt5_request(self) -> dict:
        """Convert to MT5 request format."""
        request = {
            "action": 1,  # TRADE_ACTION_DEAL
            "symbol": self.symbol,
            "volume": self.volume,
            "type": self._get_mt5_order_type(),
            "deviation": self.deviation,
            "magic": self.magic,
            "comment": self.comment,
        }
        
        if self.price:
            request["price"] = self.price
            
        if self.sl:
            request["sl"] = self.sl
            
        if self.tp:
            request["tp"] = self.tp
            
        return request
    
    def _get_mt5_order_type(self) -> int:
        """Get MT5 order type constant."""
        mapping = {
            OrderType.BUY: 0,  # ORDER_TYPE_BUY
            OrderType.SELL: 1,  # ORDER_TYPE_SELL
            OrderType.BUY_LIMIT: 2,  # ORDER_TYPE_BUY_LIMIT
            OrderType.SELL_LIMIT: 3,  # ORDER_TYPE_SELL_LIMIT
            OrderType.BUY_STOP: 4,  # ORDER_TYPE_BUY_STOP
            OrderType.SELL_STOP: 5,  # ORDER_TYPE_SELL_STOP
        }
        return mapping[self.order_type]


@dataclass
class OrderResult:
    """Order execution result."""
    success: bool
    order: Optional[int] = None
    deal: Optional[int] = None
    volume: Optional[float] = None
    price: Optional[float] = None
    comment: Optional[str] = None
    request_id: Optional[int] = None
    retcode: Optional[int] = None
    
    @property
    def error_description(self) -> str:
        """Get error description from retcode."""
        errors = {
            10004: "Requote",
            10006: "Request rejected",
            10007: "Request cancelled by trader",
            10008: "Order placed",
            10009: "Request completed",
            10010: "Only part of the request was completed",
            10011: "Request processing error",
            10012: "Request cancelled by timeout",
            10013: "Invalid request",
            10014: "Invalid volume",
            10015: "Invalid price",
            10016: "Invalid stops",
            10017: "Trade is disabled",
            10018: "Market is closed",
            10019: "Insufficient funds",
            10020: "Prices changed",
            10021: "No quotes to process request",
            10022: "Invalid order expiration date",
            10023: "Order state changed",
            10024: "Too frequent requests",
            10025: "No changes in request",
            10026: "Autotrading disabled by server",
            10027: "Autotrading disabled by client terminal",
            10028: "Request locked for processing",
            10029: "Order or position frozen",
            10030: "Invalid order filling type",
            10031: "No connection with the trade server",
        }
        return errors.get(self.retcode, "Unknown error") 