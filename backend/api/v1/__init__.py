"""
API v1 module for ICT Ultra v2.
"""

from fastapi import APIRouter

from . import trading, signals, performance, market_data, strategy_whisperer, adaptive_trade_manager, shadow_mode
# god_mode, market_narrator temporarily disabled

api_router = APIRouter()

# Include all routers from the v1 modules
api_router.include_router(trading.router, prefix="/trading", tags=["Trading"])
api_router.include_router(signals.router, prefix="/signals", tags=["Signals"])
api_router.include_router(performance.router, prefix="/performance", tags=["Performance"])
api_router.include_router(market_data.router, prefix="/market", tags=["Market Data"])
api_router.include_router(strategy_whisperer.router, prefix="/strategy-whisperer", tags=["Strategy Whisperer"])
api_router.include_router(adaptive_trade_manager.router, prefix="/adaptive-trade-manager", tags=["Adaptive Trade Manager"])
# api_router.include_router(god_mode.router, prefix="/god-mode", tags=["God Mode"])
api_router.include_router(shadow_mode.router, prefix="/shadow-mode", tags=["Shadow Mode"])
# api_router.include_router(market_narrator.router, prefix="/market-narrator", tags=["Market Narrator"])

__all__ = ["api_router"]
