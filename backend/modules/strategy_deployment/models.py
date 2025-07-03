"""
Strategy Deployment Models

MT5 strateji deployment işlemleri için data modelleri.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime

class DeploymentStatus(str, Enum):
    """Deployment durumu enum'u"""
    PENDING = "pending"
    DEPLOYING = "deploying" 
    DEPLOYED = "deployed"
    FAILED = "failed"
    STOPPED = "stopped"

class StrategyType(str, Enum):
    """Strateji türü enum'u"""
    SANAL_SUPURGE_V1 = "sanal_supurge_v1"
    ICT_ORDERBLOCK = "ict_orderblock"
    CUSTOM = "custom"

class MT5AccountInfo(BaseModel):
    """MT5 hesap bilgileri"""
    login: int
    server: str
    password: str
    account_type: str = "demo"
    balance: Optional[float] = None
    leverage: Optional[int] = None

class StrategyParameters(BaseModel):
    """Strateji parametreleri - Sanal Süpürge V1 için özelleştirilmiş"""
    # Temel ayarlar
    buy_islemi_ac: bool = True
    sell_islemi_ac: bool = True
    position_comment: str = "HayaletSüpürge"
    pivot_ust: float = 1.8
    pivot_alt: float = 1.01
    
    # Lot boyutları (1-14 seviye)
    lot_sizes: List[float] = Field(default=[0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1, 0.1, 0.1, 0.1, 0.1])
    
    # TP seviyeleri
    tp_levels: List[int] = Field(default=[1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 2500, 2500, 2500, 2500, 2500])
    
    # SL seviyeleri 
    sl_levels: List[int] = Field(default=[100] * 14)
    
    # Seviye mesafeleri
    level_distances: List[int] = Field(default=[100] * 13)  # 2-14 seviye arası mesafeler
    
    # Aktif seviyeler
    active_orders: List[bool] = Field(default=[True] * 14)
    
    # Alert ayarları
    alert_3: bool = True
    alert_4: bool = True 
    alert_5: bool = True
    
    # Zaman filtreleri
    use_time_limit: bool = False
    do_not_open_after_hour: int = 20
    do_not_open_after_minutes: int = 30
    do_not_open_before_hour: int = 2
    do_not_open_before_minutes: int = 30
    use_time_limit_break: bool = True
    do_not_open_after_hour_break: int = 12
    do_not_open_after_minutes_break: int = 30
    do_not_open_before_hour_break: int = 13
    do_not_open_before_minutes_break: int = 30

class StrategyConfig(BaseModel):
    """Strateji konfigürasyonu"""
    strategy_id: str
    strategy_name: str
    strategy_type: StrategyType
    version: str = "1.0"
    description: Optional[str] = None
    parameters: StrategyParameters
    symbol: str = "EURUSD"
    timeframe: str = "M15"
    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class DeploymentRequest(BaseModel):
    """Deployment isteği"""
    strategy_config: StrategyConfig
    target_accounts: List[MT5AccountInfo]
    master_account: Optional[MT5AccountInfo] = None
    enable_copy_trading: bool = True
    deployment_name: str
    auto_start: bool = True

class DeploymentInfo(BaseModel):
    """Deployment bilgileri"""
    deployment_id: str
    deployment_name: str
    strategy_config: StrategyConfig
    target_accounts: List[MT5AccountInfo]
    master_account: Optional[MT5AccountInfo] = None
    status: DeploymentStatus
    deployed_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None
    error_message: Optional[str] = None
    performance_stats: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class DeploymentResponse(BaseModel):
    """Deployment yanıtı"""
    success: bool
    deployment_id: Optional[str] = None
    message: str
    deployment_info: Optional[DeploymentInfo] = None

class StrategyPerformance(BaseModel):
    """Strateji performans metrikleri"""
    deployment_id: str
    account_login: int
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0
    total_profit: float = 0.0
    total_loss: float = 0.0
    net_profit: float = 0.0
    max_drawdown: float = 0.0
    current_drawdown: float = 0.0
    open_positions: int = 0
    last_updated: datetime = Field(default_factory=datetime.now)

class CopyTradingConfig(BaseModel):
    """Copy trading konfigürasyonu"""
    master_account: MT5AccountInfo
    slave_accounts: List[MT5AccountInfo]
    copy_ratio: float = 1.0  # Kopyalama oranı
    max_lot_size: float = 10.0
    copy_sl_tp: bool = True
    delay_ms: int = 100  # Kopyalama gecikmesi (ms)
    risk_limit_percent: float = 5.0  # Risk limiti (%)

class StrategyListResponse(BaseModel):
    """Strateji liste yanıtı"""
    strategies: List[StrategyConfig]
    total: int
    page: int = 1
    page_size: int = 10

class DeploymentListResponse(BaseModel):
    """Deployment liste yanıtı"""
    deployments: List[DeploymentInfo]
    total: int
    page: int = 1
    page_size: int = 10 