"""
ICT (Inner Circle Trader) REAL signal detection module.

GERÇEK MT5 verilerine dayalı ICT analiz motoru:
- Order Blocks (Gerçek fiyat verilerinden)
- Fair Value Gaps (Canlı market data)
- Breaker Blocks (Live trading data)
- Real-time ICT analysis
"""

from .real_ict_engine import RealICTEngine

__all__ = [
    "RealICTEngine"
] 