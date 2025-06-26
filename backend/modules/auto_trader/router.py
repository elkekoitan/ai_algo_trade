from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Optional
import asyncio
from datetime import datetime

from .models import (
    AutoTradeRequest, AutoTradeResponse, TradingStrategy, 
    AutoTraderStatus, TradeResult, StrategyConfig
)
from .service import AutoTraderService
from ..mt5_integration.service import MT5Service

router = APIRouter(prefix="/auto-trader", tags=["auto-trader"])

# Global auto trader service instance
auto_trader_service = AutoTraderService()

@router.post("/start", response_model=AutoTradeResponse)
async def start_auto_trading(
    request: AutoTradeRequest,
    background_tasks: BackgroundTasks
):
    """Start automated trading with specified strategy"""
    try:
        # Validate strategy exists
        if not auto_trader_service.strategy_exists(request.strategy_name):
            raise HTTPException(
                status_code=404, 
                detail=f"Strategy '{request.strategy_name}' not found"
            )
        
        # Start auto trading in background
        result = await auto_trader_service.start_trading(
            strategy_name=request.strategy_name,
            symbols=request.symbols,
            config=request.config
        )
        
        # Add monitoring task
        background_tasks.add_task(
            auto_trader_service.monitor_trading_session,
            result.session_id
        )
        
        return AutoTradeResponse(
            success=True,
            message=f"Auto trading started with strategy '{request.strategy_name}'",
            session_id=result.session_id,
            data=result.dict()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop/{session_id}", response_model=AutoTradeResponse)
async def stop_auto_trading(session_id: str):
    """Stop automated trading session"""
    try:
        result = await auto_trader_service.stop_trading(session_id)
        
        return AutoTradeResponse(
            success=True,
            message=f"Auto trading session {session_id} stopped",
            session_id=session_id,
            data=result.dict()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status", response_model=AutoTraderStatus)
async def get_auto_trader_status():
    """Get current auto trader status and active sessions"""
    try:
        status = await auto_trader_service.get_status()
        return status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{session_id}", response_model=dict)
async def get_session_status(session_id: str):
    """Get specific trading session status"""
    try:
        status = await auto_trader_service.get_session_status(session_id)
        
        if not status:
            raise HTTPException(
                status_code=404, 
                detail=f"Session {session_id} not found"
            )
        
        return status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/strategies", response_model=List[TradingStrategy])
async def get_available_strategies():
    """Get list of available trading strategies"""
    try:
        strategies = auto_trader_service.get_available_strategies()
        return strategies
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/strategies", response_model=dict)
async def create_strategy(strategy: TradingStrategy):
    """Create new trading strategy"""
    try:
        result = await auto_trader_service.create_strategy(strategy)
        
        return {
            "success": True,
            "message": f"Strategy '{strategy.name}' created successfully",
            "strategy_id": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/strategies/{strategy_name}", response_model=dict)
async def update_strategy(strategy_name: str, strategy: TradingStrategy):
    """Update existing trading strategy"""
    try:
        result = await auto_trader_service.update_strategy(strategy_name, strategy)
        
        return {
            "success": True,
            "message": f"Strategy '{strategy_name}' updated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/strategies/{strategy_name}", response_model=dict)
async def delete_strategy(strategy_name: str):
    """Delete trading strategy"""
    try:
        result = await auto_trader_service.delete_strategy(strategy_name)
        
        return {
            "success": True,
            "message": f"Strategy '{strategy_name}' deleted successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trades/{session_id}", response_model=List[TradeResult])
async def get_session_trades(
    session_id: str,
    limit: Optional[int] = 100,
    offset: Optional[int] = 0
):
    """Get trades for specific session"""
    try:
        trades = await auto_trader_service.get_session_trades(
            session_id, limit, offset
        )
        return trades
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance/{session_id}", response_model=dict)
async def get_session_performance(session_id: str):
    """Get performance metrics for trading session"""
    try:
        performance = await auto_trader_service.get_session_performance(session_id)
        
        if not performance:
            raise HTTPException(
                status_code=404, 
                detail=f"Performance data for session {session_id} not found"
            )
        
        return performance
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/emergency-stop", response_model=dict)
async def emergency_stop_all():
    """Emergency stop all active trading sessions"""
    try:
        result = await auto_trader_service.emergency_stop_all()
        
        return {
            "success": True,
            "message": "All trading sessions stopped",
            "stopped_sessions": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pause/{session_id}", response_model=dict)
async def pause_trading_session(session_id: str):
    """Pause trading session temporarily"""
    try:
        result = await auto_trader_service.pause_session(session_id)
        
        return {
            "success": True,
            "message": f"Session {session_id} paused",
            "paused_at": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/resume/{session_id}", response_model=dict)
async def resume_trading_session(session_id: str):
    """Resume paused trading session"""
    try:
        result = await auto_trader_service.resume_session(session_id)
        
        return {
            "success": True,
            "message": f"Session {session_id} resumed",
            "resumed_at": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/signals/{session_id}", response_model=List[dict])
async def get_session_signals(
    session_id: str,
    limit: Optional[int] = 50
):
    """Get recent signals for trading session"""
    try:
        signals = await auto_trader_service.get_session_signals(session_id, limit)
        return signals
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/config/{session_id}", response_model=dict)
async def update_session_config(
    session_id: str, 
    config: StrategyConfig
):
    """Update configuration for active trading session"""
    try:
        result = await auto_trader_service.update_session_config(session_id, config)
        
        return {
            "success": True,
            "message": f"Configuration updated for session {session_id}",
            "updated_at": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", response_model=dict)
async def health_check():
    """Health check for auto trader service"""
    try:
        health = await auto_trader_service.health_check()
        return health
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        } 