"""
Copy Trading Module
Advanced copy trading system with risk management and performance tracking
"""

from .copy_service import CopyTradingService
from .models import (
    CopyTraderProfile,
    CopySettings,
    CopyTradeResult,
    FollowerStats
)

__all__ = [
    'CopyTradingService',
    'CopyTraderProfile',
    'CopySettings', 
    'CopyTradeResult',
    'FollowerStats'
] 