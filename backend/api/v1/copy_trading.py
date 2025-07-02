"""
Copy Trading API Endpoints
Advanced copy trading with real-time execution and risk management
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse

from backend.modules.copy_trading import (
    CopyTradingService,
    CopyTraderProfile,
    CopySettings,
    FollowerStats
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/copy-trading", tags=["Copy Trading"])

# Global service instance
copy_service = CopyTradingService()

@router.on_event("startup")
async def startup_copy_service():
    """Initialize copy trading service"""
    try:
        await copy_service.start_service()
        logger.info("✅ Copy Trading API started successfully")
    except Exception as e:
        logger.error(f"❌ Failed to start Copy Trading API: {e}")

@router.get("/traders", response_model=List[CopyTraderProfile])
async def get_available_traders(
    risk_level: Optional[str] = Query(None, description="Filter by risk level"),
    min_return: Optional[float] = Query(None, description="Minimum monthly return %"),
    max_drawdown: Optional[float] = Query(None, description="Maximum drawdown %"),
    limit: int = Query(20, description="Number of traders to return")
):
    """Get list of available copy traders with filters"""
    try:
        traders = await copy_service.get_available_traders(
            risk_level=risk_level,
            min_return=min_return,
            max_drawdown=max_drawdown
        )
        
        return traders[:limit]
        
    except Exception as e:
        logger.error(f"Error fetching traders: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/traders/{trader_id}", response_model=CopyTraderProfile)
async def get_trader_profile(trader_id: str):
    """Get detailed profile of a specific trader"""
    try:
        if trader_id not in copy_service.trader_profiles:
            raise HTTPException(status_code=404, detail="Trader not found")
            
        return copy_service.trader_profiles[trader_id]
        
    except Exception as e:
        logger.error(f"Error fetching trader profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start-copying")
async def start_copying_trader(
    follower_id: str,
    trader_id: str,
    settings: CopySettings
):
    """Start copying a trader"""
    try:
        # Validate trader exists
        if trader_id not in copy_service.trader_profiles:
            raise HTTPException(status_code=404, detail="Trader not found")
            
        # Update settings with correct IDs
        settings.follower_id = follower_id
        settings.trader_id = trader_id
        
        copy_id = await copy_service.start_copying(follower_id, settings)
        
        return {
            "success": True,
            "copy_id": copy_id,
            "message": f"Started copying trader {trader_id}",
            "settings": settings.dict()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error starting copy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop-copying/{copy_id}")
async def stop_copying_trader(copy_id: str):
    """Stop copying a trader"""
    try:
        success = await copy_service.stop_copying(copy_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Copy settings not found")
            
        return {
            "success": True,
            "message": f"Stopped copying {copy_id}"
        }
        
    except Exception as e:
        logger.error(f"Error stopping copy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/my-copies/{follower_id}")
async def get_my_copies(follower_id: str):
    """Get all active copy settings for a follower"""
    try:
        active_copies = [
            {
                "copy_id": copy_id,
                "settings": settings.dict(),
                "trader": copy_service.trader_profiles.get(settings.trader_id)
            }
            for copy_id, settings in copy_service.active_copy_settings.items()
            if settings.follower_id == follower_id
        ]
        
        return {
            "success": True,
            "active_copies": active_copies,
            "total_active": len(active_copies)
        }
        
    except Exception as e:
        logger.error(f"Error fetching copies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics")
async def get_copy_statistics():
    """Get copy trading platform statistics"""
    try:
        stats = await copy_service.get_copy_statistics()
        
        return {
            "success": True,
            "platform_stats": stats,
            "server_status": "online",
            "last_updated": "2024-01-01T12:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"Error fetching statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/register-trader")
async def register_as_trader(profile: CopyTraderProfile):
    """Register as a copy trader (for traders who want to be copied)"""
    try:
        trader_id = await copy_service.register_trader(profile)
        
        return {
            "success": True,
            "trader_id": trader_id,
            "message": f"Trader {profile.display_name} registered successfully",
            "profile": profile.dict()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error registering trader: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance/{trader_id}")
async def get_trader_performance(
    trader_id: str,
    days: int = Query(30, description="Number of days to analyze")
):
    """Get detailed performance metrics for a trader"""
    try:
        if trader_id not in copy_service.trader_profiles:
            raise HTTPException(status_code=404, detail="Trader not found")
            
        # This would fetch real performance data from database
        # For now, return mock data
        return {
            "success": True,
            "trader_id": trader_id,
            "period_days": days,
            "performance": {
                "total_return": 15.8,
                "monthly_return": 5.2,
                "weekly_return": 1.3,
                "daily_return": 0.2,
                "win_rate": 72.5,
                "profit_factor": 1.85,
                "max_drawdown": 8.2,
                "sharpe_ratio": 1.4,
                "total_trades": 127,
                "winning_trades": 92,
                "losing_trades": 35,
                "average_win": 85.20,
                "average_loss": -42.10,
                "largest_win": 350.00,
                "largest_loss": -120.00
            },
            "equity_curve": [
                {"date": "2024-01-01", "equity": 10000, "drawdown": 0},
                {"date": "2024-01-02", "equity": 10150, "drawdown": 0},
                {"date": "2024-01-03", "equity": 10280, "drawdown": 0},
                {"date": "2024-01-04", "equity": 10100, "drawdown": -1.75},
                {"date": "2024-01-05", "equity": 10350, "drawdown": 0}
            ],
            "monthly_returns": [
                {"month": "2023-12", "return": 4.2},
                {"month": "2024-01", "return": 5.8},
                {"month": "2024-02", "return": 3.1},
                {"month": "2024-03", "return": 7.2}
            ]
        }
        
    except Exception as e:
        logger.error(f"Error fetching performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/live-signals/{trader_id}")
async def get_live_signals(trader_id: str):
    """Get live trading signals from a trader"""
    try:
        if trader_id not in copy_service.trader_profiles:
            raise HTTPException(status_code=404, detail="Trader not found")
            
        # This would fetch real-time signals
        # For now, return mock signals
        return {
            "success": True,
            "trader_id": trader_id,
            "live_signals": [
                {
                    "signal_id": "signal_001",
                    "symbol": "EURUSD",
                    "action": "BUY",
                    "confidence": 0.85,
                    "reasoning": "Bullish breakout above resistance",
                    "entry_price": 1.0950,
                    "stop_loss": 1.0920,
                    "take_profit": 1.1000,
                    "risk_reward": 1.67,
                    "timestamp": "2024-01-01T12:00:00Z"
                }
            ],
            "signal_count": 1
        }
        
    except Exception as e:
        logger.error(f"Error fetching signals: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 