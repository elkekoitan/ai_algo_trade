"""
Multi-Broker Support Module
Universal trading interface supporting multiple brokers and platforms
"""

from .broker_manager import BrokerManager
from .models import (
    BrokerConfig,
    BrokerConnection,
    UniversalOrder,
    UniversalPosition,
    BrokerType,
    ConnectionStatus
)
from .adapters import (
    MT5Adapter,
    InteractiveBrokersAdapter,
    BinanceAdapter,
    BybitAdapter,
    OandaAdapter
)

__all__ = [
    'BrokerManager',
    'BrokerConfig',
    'BrokerConnection', 
    'UniversalOrder',
    'UniversalPosition',
    'BrokerType',
    'ConnectionStatus',
    'MT5Adapter',
    'InteractiveBrokersAdapter',
    'BinanceAdapter',
    'BybitAdapter',
    'OandaAdapter'
] 