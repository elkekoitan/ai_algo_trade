from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class AutoTraderStatus(str, Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    PAUSED = "paused"
    ERROR = "error"

class TradingPairConfig(BaseModel):
    symbol: str
    volume: float = Field(0.01, gt=0, description="Default trade volume")
    risk_weight: float = Field(1.0, gt=0, description="Risk weight for the symbol")
    min_score: int = Field(75, ge=0, le=100, description="Minimum ICT score to trade")
    max_positions: int = Field(2, ge=1, description="Maximum open positions for this symbol")

class AutoTraderSettings(BaseModel):
    min_score: int = Field(85, ge=0, le=100, description="Global minimum score for any trade")
    max_daily_trades: int = Field(50, ge=1, description="Maximum total trades per day")
    trade_cooldown_seconds: int = Field(60, ge=5, description="Cooldown period between trades")
    dynamic_volume_enabled: bool = Field(True, description="Enable dynamic lot sizing based on score")
    no_sl_for_ultra_high: bool = Field(True, description="Disable Stop Loss for scores >= 95")
    trading_pairs: List[TradingPairConfig] = Field(..., description="Configuration for each trading pair")

class AutoTraderState(BaseModel):
    status: AutoTraderStatus = AutoTraderStatus.STOPPED
    trades_today: int = 0
    total_profit: float = 0.0
    active_positions: Dict[str, int] = {}
    last_trade_timestamp: Optional[float] = None
    last_error: Optional[str] = None 