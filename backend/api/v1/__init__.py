"""
API v1 module for ICT Ultra v2.
"""

from fastapi import APIRouter
from .signals import router as signals_router
from .trading import router as trading_router
from .market_data import router as market_data_router
from .algo_forge import router as algo_forge_router

api_router = APIRouter(prefix="/api/v1")

# Include all routers
api_router.include_router(signals_router, prefix="/signals", tags=["signals"])
api_router.include_router(trading_router, prefix="/trading", tags=["trading"])
api_router.include_router(market_data_router, prefix="/market", tags=["market"])
api_router.include_router(algo_forge_router, prefix="/forge", tags=["forge"])

__all__ = ["api_router"]
