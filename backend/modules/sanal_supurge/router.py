"""
Sanal-Süpürge API Router

FastAPI router for grid trading strategy endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging

from .core_service import SanalSupurgeService
from .grid_calculator import GridCalculator
from .models import (
    GridConfig, TradingSession, GridCalculationResult,
    InstrumentSettings, RiskSettings, GridLevel
)

router = APIRouter(prefix="/api/v1/sanal-supurge", tags=["Sanal-Süpürge"])
logger = logging.getLogger(__name__)


# Request/Response Models
class CreateSessionRequest(BaseModel):
    config: GridConfig

class CalculateGridRequest(BaseModel):
    config: GridConfig
    current_price: float

class SessionResponse(BaseModel):
    session_id: str
    success: bool
    message: str

class GridCalculationResponse(BaseModel):
    result: GridCalculationResult
    success: bool


# Dependency injection
def get_sanal_supurge_service() -> SanalSupurgeService:
    """Get Sanal-Süpürge service instance"""
    # This would be injected from the main app
    from ...core.enhanced_event_bus import EventBus
    event_bus = EventBus()
    return SanalSupurgeService(event_bus)


# Grid Calculator Endpoints
@router.post("/calculate", response_model=GridCalculationResponse)
async def calculate_grid(
    request: CalculateGridRequest,
    service: SanalSupurgeService = Depends(get_sanal_supurge_service)
):
    """
    Calculate grid analysis for given configuration and price
    """
    try:
        calculator = GridCalculator()
        result = calculator.calculate_grid(request.config, request.current_price)
        
        return GridCalculationResponse(
            result=result,
            success=True
        )
    
    except Exception as e:
        logger.error(f"Grid calculation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/calculate/smart-distance")
async def calculate_smart_distance(
    atr_value: float,
    volatility_factor: float = 0.15
):
    """
    Calculate smart grid distance based on ATR
    """
    try:
        calculator = GridCalculator()
        distance = calculator.calculate_smart_distance(atr_value, volatility_factor)
        
        return {
            "smart_distance": distance,
            "atr_value": atr_value,
            "volatility_factor": volatility_factor,
            "success": True
        }
    
    except Exception as e:
        logger.error(f"Smart distance calculation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/calculate/fibonacci")
async def calculate_fibonacci_levels(
    high_price: float,
    low_price: float,
    decimals: int = 5
):
    """
    Calculate Fibonacci retracement levels
    """
    try:
        calculator = GridCalculator()
        levels = calculator.generate_fibonacci_levels(high_price, low_price, decimals)
        
        return {
            "fibonacci_levels": levels,
            "price_range": high_price - low_price,
            "success": True
        }
    
    except Exception as e:
        logger.error(f"Fibonacci calculation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/export/mt5-set")
async def export_mt5_set_file(config: GridConfig):
    """
    Export configuration as MT5 .set file content
    """
    try:
        calculator = GridCalculator()
        set_content = calculator.export_mt5_set_file(config)
        
        return {
            "set_content": set_content,
            "filename": f"{config.strategy_name}.set",
            "success": True
        }
    
    except Exception as e:
        logger.error(f"MT5 set export error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# Session Management Endpoints
@router.post("/sessions", response_model=SessionResponse)
async def create_session(
    request: CreateSessionRequest,
    service: SanalSupurgeService = Depends(get_sanal_supurge_service)
):
    """
    Create a new trading session
    """
    try:
        session_id = await service.create_session(request.config)
        
        return SessionResponse(
            session_id=session_id,
            success=True,
            message="Session created successfully"
        )
    
    except Exception as e:
        logger.error(f"Session creation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/sessions/{session_id}/start")
async def start_session(
    session_id: str,
    background_tasks: BackgroundTasks,
    service: SanalSupurgeService = Depends(get_sanal_supurge_service)
):
    """
    Start a trading session
    """
    try:
        success = await service.start_session(session_id)
        
        if success:
            return {
                "session_id": session_id,
                "success": True,
                "message": "Session started successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Session not found or already active")
    
    except Exception as e:
        logger.error(f"Session start error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/sessions/{session_id}/stop")
async def stop_session(
    session_id: str,
    service: SanalSupurgeService = Depends(get_sanal_supurge_service)
):
    """
    Stop a trading session
    """
    try:
        success = await service.stop_session(session_id)
        
        if success:
            return {
                "session_id": session_id,
                "success": True,
                "message": "Session stopped successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Session not found or already stopped")
    
    except Exception as e:
        logger.error(f"Session stop error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/sessions/{session_id}/status")
async def get_session_status(
    session_id: str,
    service: SanalSupurgeService = Depends(get_sanal_supurge_service)
):
    """
    Get current session status
    """
    try:
        status = await service.get_session_status(session_id)
        
        if status:
            return {
                "status": status,
                "success": True
            }
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    
    except Exception as e:
        logger.error(f"Session status error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/sessions")
async def list_sessions(
    service: SanalSupurgeService = Depends(get_sanal_supurge_service)
):
    """
    List all sessions
    """
    try:
        sessions = []
        for session_id, session in service.active_sessions.items():
            sessions.append({
                "session_id": session_id,
                "is_active": session.is_active,
                "started_at": session.started_at.isoformat() if session.started_at else None,
                "symbol": session.config.instrument.symbol,
                "strategy_name": session.config.strategy_name
            })
        
        return {
            "sessions": sessions,
            "total_count": len(sessions),
            "success": True
        }
    
    except Exception as e:
        logger.error(f"Session list error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# Copy Trading Endpoints
@router.get("/copy-trading/status")
async def get_copy_trading_status(
    service: SanalSupurgeService = Depends(get_sanal_supurge_service)
):
    """
    Get copy trading service status and metrics
    """
    try:
        metrics = service.copy_trading_service.get_performance_metrics()
        
        return {
            "metrics": metrics,
            "success": True
        }
    
    except Exception as e:
        logger.error(f"Copy trading status error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/copy-trading/accounts")
async def list_copy_accounts(
    service: SanalSupurgeService = Depends(get_sanal_supurge_service)
):
    """
    List all copy trading accounts
    """
    try:
        accounts = []
        for account_id, account in service.copy_trading_service.copy_accounts.items():
            accounts.append({
                "account_id": account_id,
                "login": account.login,
                "server": account.server,
                "is_active": account.is_active,
                "risk_multiplier": account.risk_multiplier
            })
        
        return {
            "accounts": accounts,
            "total_count": len(accounts),
            "success": True
        }
    
    except Exception as e:
        logger.error(f"Copy accounts list error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# Configuration Endpoints
@router.get("/instruments")
async def get_supported_instruments():
    """
    Get list of supported trading instruments with default settings
    """
    instruments = {
        "XAUUSD": {
            "symbol": "XAUUSD",
            "point_decimals": 2,
            "tick_size": 0.01,
            "value_per_point": 1.0,
            "contract_size": 100.0,
            "default_volatility": 3000,
            "description": "Gold vs USD"
        },
        "EURUSD": {
            "symbol": "EURUSD", 
            "point_decimals": 5,
            "tick_size": 0.00001,
            "value_per_point": 1.0,
            "contract_size": 100000.0,
            "default_volatility": 800,
            "description": "Euro vs USD"
        },
        "BTCUSD": {
            "symbol": "BTCUSD",
            "point_decimals": 2,
            "tick_size": 0.01,
            "value_per_point": 0.01,
            "contract_size": 1.0,
            "default_volatility": 250000,
            "description": "Bitcoin vs USD"
        }
    }
    
    return {
        "instruments": instruments,
        "success": True
    }


@router.get("/presets")
async def get_strategy_presets():
    """
    Get predefined strategy presets
    """
    presets = {
        "gold_scalping": {
            "name": "Gold Scalping",
            "description": "Optimized for XAUUSD scalping",
            "grid_levels": 5,
            "lot_progression": "martingale",
            "default_distance": 3500,
            "default_tp": 7000,
            "default_sl": 60000
        },
        "forex_conservative": {
            "name": "Forex Conservative",
            "description": "Conservative EURUSD strategy",
            "grid_levels": 7,
            "lot_progression": "linear",
            "default_distance": 800,
            "default_tp": 1000,
            "default_sl": 2000
        },
        "crypto_aggressive": {
            "name": "Crypto Aggressive",
            "description": "Aggressive Bitcoin strategy",
            "grid_levels": 10,
            "lot_progression": "fibonacci_weighted",
            "default_distance": 25000,
            "default_tp": 50000,
            "default_sl": 100000
        }
    }
    
    return {
        "presets": presets,
        "success": True
    } 