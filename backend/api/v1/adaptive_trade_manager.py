"""
API Endpoints for the Adaptive Trade Manager
"""
import asyncio
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from typing import List

from backend.core.logger import get_logger
from backend.modules.mt5_integration.service import MT5Service
from backend.modules.adaptive_trade_manager.models import ManagedPosition, RiskMetrics, DashboardData, AdaptiveAlert, ActionType
from backend.modules.adaptive_trade_manager.position_monitor import PositionMonitor
from backend.modules.adaptive_trade_manager.market_analyzer import MarketAnalyzer
from backend.modules.adaptive_trade_manager.risk_calculator import RiskCalculator
from backend.modules.adaptive_trade_manager.optimization_engine import OptimizationEngine
from backend.modules.adaptive_trade_manager.alert_manager import AlertManager

logger = get_logger(__name__)
router = APIRouter(prefix="/atm", tags=["Adaptive Trade Manager"])

# --- Service Initialization ---
# In a real app, these would be managed with a dependency injection system.
mt5_service = MT5Service()
position_monitor = PositionMonitor(mt5_service)
market_analyzer = MarketAnalyzer(mt5_service)
risk_calculator = RiskCalculator(position_monitor, market_analyzer)
optimization_engine = OptimizationEngine()
alert_manager = AlertManager()

# --- Main ATM Background Task ---
atm_task = None

async def run_atm_cycle():
    """The main loop for the Adaptive Trade Manager."""
    logger.info("Starting a new ATM cycle...")
    try:
        positions = await position_monitor.get_all_positions()
        if not positions:
            logger.info("No open positions to manage.")
            return

        for pos in positions:
            risk_metrics = await risk_calculator.calculate_risk_for_position(pos)
            market_condition = await market_analyzer.get_market_condition(pos.symbol)
            
            recommendation = await optimization_engine.generate_recommendation(pos, risk_metrics, market_condition)
            
            if recommendation.action_type != ActionType.DO_NOTHING:
                await alert_manager.create_alert(pos, risk_metrics, recommendation)

    except Exception as e:
        logger.error(f"Error during ATM cycle: {e}", exc_info=True)

async def atm_background_runner():
    while True:
        await run_atm_cycle()
        await asyncio.sleep(15) # Run cycle every 15 seconds

@router.on_event("startup")
async def startup_event():
    global atm_task
    # Connect to MT5 and start monitoring
    if not mt5_service.is_connected():
        # Using hardcoded credentials for demo purposes [[memory:7052824161247122118]]
        login_result = mt5_service.login(25201110, "Tickmill-Demo", "el[{rXU1lsiM")
        if not login_result:
            logger.error("ATM Startup: Failed to connect to MT5. The ATM will not run.")
            return
    
    # Start background tasks
    asyncio.create_task(position_monitor.run())
    asyncio.create_task(market_analyzer.run())
    atm_task = asyncio.create_task(atm_background_runner())
    logger.info("Adaptive Trade Manager background tasks started.")

@router.on_event("shutdown")
async def shutdown_event():
    if atm_task:
        atm_task.cancel()
    mt5_service.shutdown()
    logger.info("Adaptive Trade Manager has been shut down.")


# --- API Endpoints ---

@router.get("/dashboard", response_model=DashboardData)
async def get_dashboard_data():
    """Provides a high-level overview for the ATM dashboard."""
    # This would be more sophisticated in a real app
    positions = await position_monitor.get_all_positions()
    alerts = await alert_manager.get_active_alerts()
    return DashboardData(
        total_positions=len(positions),
        overall_pnl=sum(p.pnl for p in positions),
        portfolio_risk_level="medium", # Placeholder
        portfolio_risk_score=50.0, # Placeholder
        active_alerts=len(alerts),
        market_overview={} # Placeholder
    )

@router.get("/positions", response_model=List[ManagedPosition])
async def get_managed_positions():
    """Gets all currently tracked positions."""
    return await position_monitor.get_all_positions()

@router.get("/risk-metrics", response_model=List[RiskMetrics])
async def get_all_risk_metrics():
    """Gets the latest risk metrics for all positions."""
    return await risk_calculator.calculate_risk_for_all_positions()

@router.post("/actions/{ticket}/{action_type}")
async def execute_action(ticket: int, action_type: str, price: float = 0, percentage: float = 0):
    """Executes a recommended action on a position."""
    position = await position_monitor.get_position(ticket)
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")

    logger.info(f"Executing action '{action_type}' for ticket {ticket}")
    
    success = False
    if action_type == ActionType.ADJUST_SL.value:
        success = mt5_service.modify_position(ticket, sl=price)
    elif action_type == ActionType.ADJUST_TP.value:
        success = mt5_service.modify_position(ticket, tp=price)
    elif action_type == ActionType.FULL_CLOSE.value:
        success = mt5_service.close_position(ticket)
    elif action_type == ActionType.PARTIAL_CLOSE.value:
        volume_to_close = position.volume * (percentage / 100.0)
        success = mt5_service.close_position(ticket, volume=volume_to_close)
    else:
        raise HTTPException(status_code=400, detail="Invalid action type")

    if not success:
        raise HTTPException(status_code=500, detail="Failed to execute action in MT5")

    # Clear any alerts associated with this action
    # (More complex logic needed here to match actions to alerts)
    
    return {"status": "success", "message": f"Action '{action_type}' executed for ticket {ticket}."}


@router.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("ATM WebSocket client connected.")
    try:
        while True:
            alert: AdaptiveAlert = await alert_manager.get_next_alert_for_websocket()
            await websocket.send_json(alert.dict())
            logger.info(f"Sent alert {alert.alert_id} over WebSocket.")
    except WebSocketDisconnect:
        logger.info("ATM WebSocket client disconnected.")
    except Exception as e:
        logger.error(f"Error in ATM WebSocket: {e}", exc_info=True)
        await websocket.close(code=1011) 