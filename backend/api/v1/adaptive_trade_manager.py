import asyncio
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends, BackgroundTasks
from typing import List, Dict, Optional
import logging
from datetime import datetime
import uuid

from backend.core.logger import setup_logger
from backend.modules.mt5_integration.service import MT5Service
from backend.modules.adaptive_trade_manager.position_monitor import PositionMonitor
from backend.modules.adaptive_trade_manager.market_analyzer import MarketAnalyzer
from backend.modules.adaptive_trade_manager.risk_calculator import RiskCalculator
from backend.modules.adaptive_trade_manager.optimization_engine import OptimizationEngine
from backend.modules.adaptive_trade_manager.alert_manager import AlertManager
from backend.core.config.settings import get_settings, Settings
from backend.modules.adaptive_trade_manager.models import (
    DashboardData, AdaptiveAlert, ManagedPosition, ActionType,
    DynamicPosition, RiskMetrics, PositionOptimization, PortfolioAnalysis,
    AdaptiveSettings, AdaptiveTradeManagerStatus, PositionAdjustmentResponse,
    RiskAssessmentResponse, TradeAlert, AlertRule, AdjustmentType, RiskLevel,
    PositionStatus
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/atm", tags=["Adaptive Trade Manager"])

# Global instances
optimization_engine = None
risk_calculator = None
position_monitor = None
alert_manager = None
adaptive_settings = AdaptiveSettings()

# --- Dependency Injection Setup ---

def get_settings_dep():
    return get_settings()

def get_mt5_service(settings: Settings = Depends(get_settings_dep)):
    return MT5Service(
        login=settings.MT5_LOGIN,
        password=settings.MT5_PASSWORD,
        server=settings.MT5_SERVER
    )

def get_position_monitor(mt5_service: MT5Service = Depends(get_mt5_service)):
    return PositionMonitor(mt5_service)

def get_market_analyzer(mt5_service: MT5Service = Depends(get_mt5_service)):
    return MarketAnalyzer(mt5_service)

def get_risk_calculator(
    monitor: PositionMonitor = Depends(get_position_monitor),
    analyzer: MarketAnalyzer = Depends(get_market_analyzer)
):
    return RiskCalculator(monitor, analyzer)

def get_optimization_engine():
    return OptimizationEngine()

def get_alert_manager():
    return AlertManager()

async def initialize_services(mt5_service):
    """Initialize all adaptive trade manager services"""
    global optimization_engine, risk_calculator, position_monitor, alert_manager
    
    if optimization_engine is None:
        market_analyzer = MarketAnalyzer()
        position_monitor = PositionMonitor(mt5_service)
        risk_calculator = RiskCalculator(position_monitor, market_analyzer, mt5_service)
        optimization_engine = OptimizationEngine(mt5_service)
        alert_manager = AlertManager(risk_calculator)

# --- API Endpoints ---

@router.on_event("startup")
async def startup_event():
    logger.info("Adaptive Trade Manager API started. MT5 connection will be established on first request.")

@router.get("/dashboard", response_model=DashboardData)
async def get_dashboard_data(
    monitor: PositionMonitor = Depends(get_position_monitor),
    risk_calc: RiskCalculator = Depends(get_risk_calculator),
    alert_manager: AlertManager = Depends(get_alert_manager)
):
    """Provides a high-level overview for the ATM dashboard."""
    try:
        active_positions = await monitor.get_all_positions()
        active_alerts = await alert_manager.get_active_alerts()
        risk_metrics = await risk_calc.calculate_portfolio_risk(active_positions)
        
        return DashboardData(
            total_positions=len(active_positions),
            overall_pnl=sum(p.pnl for p in active_positions),
            portfolio_risk_level=risk_metrics.overall_risk_level.value,
            portfolio_risk_score=risk_metrics.overall_risk_score,
            active_alerts=len(active_alerts),
            market_overview={} # Placeholder, to be filled by market_analyzer
        )
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while fetching dashboard data.")

@router.get("/positions", response_model=List[ManagedPosition])
async def get_managed_positions(monitor: PositionMonitor = Depends(get_position_monitor)):
    """Retrieves all currently managed positions."""
    try:
        return await monitor.get_all_positions()
    except Exception as e:
        logger.error(f"Error getting managed positions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve managed positions.")

@router.get("/alerts", response_model=List[AdaptiveAlert])
async def get_active_alerts(alert_manager: AlertManager = Depends(get_alert_manager)):
    """Retrieves all active adaptive alerts."""
    try:
        return await alert_manager.get_active_alerts()
    except Exception as e:
        logger.error(f"Error getting alerts: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve alerts.")

@router.post("/positions/{ticket}/optimize")
async def optimize_single_position(
    ticket: int,
    optimizer: OptimizationEngine = Depends(get_optimization_engine),
    monitor: PositionMonitor = Depends(get_position_monitor)
):
    """Runs an optimization cycle for a single position."""
    try:
        position = await monitor.get_position(ticket)
        if not position:
            raise HTTPException(status_code=404, detail="Position not found")
        
        mock_market_condition = None # Placeholder
        suggested_action = await optimizer.optimize_position(position, mock_market_condition)
        
        return {
            "position_ticket": ticket,
            "suggested_action": suggested_action.dict()
        }
    except Exception as e:
        logger.error(f"Error optimizing position {ticket}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to optimize position {ticket}.")

@router.post("/actions/{ticket}/{action_type}")
async def execute_action_on_position(
    ticket: int, 
    action_type: ActionType,
    monitor: PositionMonitor = Depends(get_position_monitor),
    mt5_service: MT5Service = Depends(get_mt5_service)
):
    """Executes a recommended action on a position."""
    position = await monitor.get_position(ticket)
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")

    logger.info(f"Executing action '{action_type}' for ticket {ticket}")
    
    success = False
    if action_type == ActionType.ADJUST_SL:
        success = await mt5_service.modify_position(ticket, sl=position.sl)
    elif action_type == ActionType.ADJUST_TP:
        success = await mt5_service.modify_position(ticket, tp=position.tp)
    elif action_type == ActionType.CLOSE_PARTIAL_25:
        success = await mt5_service.partial_close(ticket, 25)
    elif action_type == ActionType.CLOSE_PARTIAL_50:
        success = await mt5_service.partial_close(ticket, 50)
    elif action_type == ActionType.MOVE_SL_TO_BE:
        success = await mt5_service.move_sl_to_break_even(ticket)
    elif action_type == ActionType.CLOSE_FULL:
        success = await mt5_service.close_position(ticket)
    else:
        raise HTTPException(status_code=400, detail="Invalid action type")

    if not success:
        raise HTTPException(status_code=500, detail="Failed to execute action in MT5")
    
    return {"status": "success", "message": f"Action '{action_type}' executed for ticket {ticket}."}

@router.websocket("/ws/alerts")
async def websocket_endpoint(
    websocket: WebSocket, 
    alert_manager: AlertManager = Depends(get_alert_manager)
):
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

@router.get("/status", response_model=AdaptiveTradeManagerStatus)
async def get_manager_status(mt5_service = Depends(get_mt5_service)):
    """Get comprehensive status of the Adaptive Trade Manager"""
    try:
        await initialize_services(mt5_service)
        
        # Get current positions
        positions = await get_current_positions(mt5_service)
        
        # Calculate performance metrics
        performance_score = await calculate_performance_score(positions)
        risk_score = await calculate_risk_score(positions, mt5_service)
        
        # System metrics
        uptime_hours = 24.0  # Mock uptime
        cpu_usage = 15.5
        memory_usage = 32.1
        latency_ms = 45.2
        
        status = AdaptiveTradeManagerStatus(
            total_positions=len(positions),
            active_adjustments=len([p for p in positions if p.status == PositionStatus.ADJUSTING]),
            total_alerts=await get_daily_alert_count(),
            performance_score=performance_score,
            risk_score=risk_score,
            last_optimization=datetime.now(),
            uptime_hours=uptime_hours,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            latency_ms=latency_ms
        )
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting manager status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

@router.get("/positions", response_model=List[DynamicPosition])
async def get_dynamic_positions(symbol: Optional[str] = None, mt5_service = Depends(get_mt5_service)):
    """Get all dynamic positions with AI analytics"""
    try:
        await initialize_services(mt5_service)
        
        positions = await get_current_positions(mt5_service)
        
        if symbol:
            positions = [p for p in positions if p.symbol == symbol]
        
        return positions
        
    except Exception as e:
        logger.error(f"Error getting dynamic positions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get positions: {str(e)}")

@router.get("/risk-analysis", response_model=RiskMetrics)
async def get_risk_analysis(mt5_service = Depends(get_mt5_service)):
    """Get comprehensive real-time risk analysis"""
    try:
        await initialize_services(mt5_service)
        
        # Get positions and account info
        positions = await get_current_positions(mt5_service)
        account_info = await mt5_service.get_account_info()
        
        # Calculate risk metrics
        risk_metrics = await risk_calculator.calculate_real_time_risk(positions, account_info)
        
        return risk_metrics
        
    except Exception as e:
        logger.error(f"Error getting risk analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze risk: {str(e)}")

@router.get("/portfolio-analysis", response_model=PortfolioAnalysis)
async def get_portfolio_analysis(mt5_service = Depends(get_mt5_service)):
    """Get comprehensive portfolio optimization analysis"""
    try:
        await initialize_services(mt5_service)
        
        # Get positions and market data
        positions = await get_current_positions(mt5_service)
        account_info = await mt5_service.get_account_info()
        risk_metrics = await risk_calculator.calculate_real_time_risk(positions, account_info)
        
        # Get market conditions
        market_conditions = await get_market_conditions(mt5_service)
        
        # Run portfolio optimization
        portfolio_analysis = await optimization_engine.optimize_portfolio(
            positions, risk_metrics, market_conditions
        )
        
        return portfolio_analysis
        
    except Exception as e:
        logger.error(f"Error getting portfolio analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze portfolio: {str(e)}")

@router.get("/optimization-suggestions", response_model=List[PositionOptimization])
async def get_optimization_suggestions(mt5_service = Depends(get_mt5_service)):
    """Get AI-driven position optimization suggestions"""
    try:
        await initialize_services(mt5_service)
        
        positions = await get_current_positions(mt5_service)
        account_info = await mt5_service.get_account_info()
        risk_metrics = await risk_calculator.calculate_real_time_risk(positions, account_info)
        
        suggestions = []
        
        for position in positions:
            # Get market data for position
            market_data = await get_market_data_for_symbol(position.symbol, mt5_service)
            
            # Analyze optimization opportunities
            optimization = await optimization_engine.analyze_position_adjustments(
                position, market_data, risk_metrics
            )
            
            if optimization:
                suggestions.append(optimization)
        
        # Sort by priority (highest first)
        suggestions.sort(key=lambda x: x.priority, reverse=True)
        
        return suggestions
        
    except Exception as e:
        logger.error(f"Error getting optimization suggestions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get suggestions: {str(e)}")

@router.post("/adjust-position/{position_id}", response_model=PositionAdjustmentResponse)
async def adjust_position(
    position_id: str,
    adjustment_type: AdjustmentType,
    new_value: float,
    mt5_service = Depends(get_mt5_service)
):
    """Apply AI-recommended position adjustment"""
    try:
        await initialize_services(mt5_service)
        
        # Get current position
        positions = await get_current_positions(mt5_service)
        position = next((p for p in positions if p.position_id == position_id), None)
        
        if not position:
            raise HTTPException(status_code=404, detail="Position not found")
        
        # Store old value for response
        if adjustment_type == AdjustmentType.INCREASE_SIZE or adjustment_type == AdjustmentType.DECREASE_SIZE:
            old_value = position.position_size
            position.position_size = new_value
        elif adjustment_type == AdjustmentType.MOVE_STOP_LOSS:
            old_value = position.stop_loss or 0
            position.stop_loss = new_value
        elif adjustment_type == AdjustmentType.MOVE_TAKE_PROFIT:
            old_value = position.take_profit or 0
            position.take_profit = new_value
        else:
            old_value = 0
        
        # Apply adjustment through MT5
        success = await apply_position_adjustment(position, adjustment_type, new_value, mt5_service)
        
        if success:
            # Update position status
            position.status = PositionStatus.MONITORING
            position.last_update = datetime.now()
            
            # Add to adjustment history
            adjustment_record = {
                'timestamp': datetime.now(),
                'type': adjustment_type.value,
                'old_value': old_value,
                'new_value': new_value,
                'reason': 'AI optimization'
            }
            position.adjustments.append(adjustment_record)
            
            # Generate reasoning
            reasoning = generate_adjustment_reasoning(adjustment_type, old_value, new_value)
            expected_impact = calculate_expected_impact(adjustment_type, old_value, new_value)
            
            return PositionAdjustmentResponse(
                success=True,
                position_id=position_id,
                adjustment_type=adjustment_type,
                old_value=old_value,
                new_value=new_value,
                reasoning=reasoning,
                expected_impact=expected_impact
            )
        else:
            raise HTTPException(status_code=400, detail="Failed to apply adjustment")
        
    except Exception as e:
        logger.error(f"Error adjusting position: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to adjust position: {str(e)}")

@router.post("/calculate-optimal-size")
async def calculate_optimal_position_size(
    symbol: str,
    confidence_score: float = 0.7,
    risk_preference: float = 0.02,
    mt5_service = Depends(get_mt5_service)
):
    """Calculate optimal position size using AI"""
    try:
        await initialize_services(mt5_service)
        
        # Get account info and market data
        account_info = await mt5_service.get_account_info()
        market_data = await get_market_data_for_symbol(symbol, mt5_service)
        
        # Calculate optimal size
        optimal_size = await optimization_engine.calculate_optimal_position_size(
            symbol=symbol,
            account_balance=account_info.get('balance', 0),
            market_data=market_data,
            confidence_score=confidence_score,
            risk_preference=risk_preference
        )
        
        return {
            "success": True,
            "symbol": symbol,
            "optimal_size": optimal_size,
            "confidence_score": confidence_score,
            "risk_preference": risk_preference,
            "reasoning": f"Optimal size calculated based on {confidence_score*100:.1f}% confidence and {risk_preference*100:.1f}% risk"
        }
        
    except Exception as e:
        logger.error(f"Error calculating optimal size: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate size: {str(e)}")

@router.get("/alerts", response_model=List[TradeAlert])
async def get_trade_alerts(
    severity: Optional[str] = None,
    limit: int = 50,
    mt5_service = Depends(get_mt5_service)
):
    """Get recent trade alerts"""
    try:
        await initialize_services(mt5_service)
        
        # Get positions and risk metrics
        positions = await get_current_positions(mt5_service)
        account_info = await mt5_service.get_account_info()
        risk_metrics = await risk_calculator.calculate_real_time_risk(positions, account_info)
        
        # Check for new alerts
        alerts = await risk_calculator.check_risk_alerts(risk_metrics, positions)
        
        # Filter by severity if specified
        if severity:
            alerts = [a for a in alerts if a.severity.value == severity]
        
        # Limit results
        alerts = alerts[:limit]
        
        return alerts
        
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get alerts: {str(e)}")

@router.post("/settings", response_model=AdaptiveSettings)
async def update_settings(settings: AdaptiveSettings):
    """Update adaptive trade manager settings"""
    try:
        global adaptive_settings
        adaptive_settings = settings
        
        logger.info(f"Updated adaptive settings: {settings}")
        return settings
        
    except Exception as e:
        logger.error(f"Error updating settings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update settings: {str(e)}")

@router.get("/settings", response_model=AdaptiveSettings)
async def get_settings():
    """Get current adaptive trade manager settings"""
    return adaptive_settings

@router.post("/risk-assessment", response_model=RiskAssessmentResponse)
async def assess_portfolio_risk(mt5_service = Depends(get_mt5_service)):
    """Get comprehensive risk assessment with recommendations"""
    try:
        await initialize_services(mt5_service)
        
        # Get positions and calculate risk
        positions = await get_current_positions(mt5_service)
        account_info = await mt5_service.get_account_info()
        risk_metrics = await risk_calculator.calculate_real_time_risk(positions, account_info)
        
        # Generate recommendations
        recommendations = []
        immediate_actions = []
        
        if risk_metrics.overall_risk_level == RiskLevel.CRITICAL:
            immediate_actions.append("Close high-risk positions immediately")
            recommendations.append("Reduce position sizes by 50%")
        elif risk_metrics.overall_risk_level == RiskLevel.HIGH:
            immediate_actions.append("Review all open positions")
            recommendations.append("Tighten stop losses on losing positions")
        
        if risk_metrics.correlation_score > 0.8:
            recommendations.append("Diversify portfolio to reduce correlation risk")
        
        if risk_metrics.margin_level < 200:
            immediate_actions.append("Add margin or close positions to avoid margin call")
        
        # Portfolio health assessment
        if risk_metrics.risk_percentage < 5:
            portfolio_health = "Excellent"
        elif risk_metrics.risk_percentage < 10:
            portfolio_health = "Good"
        elif risk_metrics.risk_percentage < 15:
            portfolio_health = "Fair"
        elif risk_metrics.risk_percentage < 25:
            portfolio_health = "Poor"
        else:
            portfolio_health = "Critical"
        
        return RiskAssessmentResponse(
            success=True,
            risk_level=risk_metrics.overall_risk_level,
            risk_score=risk_metrics.risk_percentage,
            recommendations=recommendations,
            immediate_actions=immediate_actions,
            portfolio_health=portfolio_health
        )
        
    except Exception as e:
        logger.error(f"Error assessing risk: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to assess risk: {str(e)}")

# Background task for continuous monitoring
@router.post("/start-monitoring")
async def start_continuous_monitoring(background_tasks: BackgroundTasks, mt5_service = Depends(get_mt5_service)):
    """Start continuous position and risk monitoring"""
    try:
        await initialize_services(mt5_service)
        
        background_tasks.add_task(continuous_monitoring_task, mt5_service)
        
        return {"success": True, "message": "Continuous monitoring started"}
        
    except Exception as e:
        logger.error(f"Error starting monitoring: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start monitoring: {str(e)}")

# Helper functions
async def get_current_positions(mt5_service) -> List[DynamicPosition]:
    """Get current positions with AI analytics"""
    try:
        # Get positions from MT5
        mt5_positions = mt5_service.get_open_positions()
        
        positions = []
        for mt5_pos in mt5_positions:
            # Convert MT5 position to DynamicPosition with AI analytics
            position = DynamicPosition(
                position_id=str(mt5_pos.get('ticket', uuid.uuid4())),
                symbol=mt5_pos.get('symbol', ''),
                entry_price=mt5_pos.get('price_open', 0),
                current_price=mt5_pos.get('price_current', 0),
                position_size=mt5_pos.get('volume', 0),
                original_size=mt5_pos.get('volume', 0),
                status=PositionStatus.OPEN,
                stop_loss=mt5_pos.get('sl'),
                take_profit=mt5_pos.get('tp'),
                unrealized_pnl=mt5_pos.get('profit', 0),
                risk_amount=abs(mt5_pos.get('profit', 0)),
                risk_percentage=2.0,  # Mock
                confidence_score=75.0,  # Mock AI score
                market_sentiment=0.2,   # Mock sentiment
                volatility_forecast=0.025,  # Mock volatility
                trend_strength=0.65,    # Mock trend
                entry_time=datetime.now(),
                last_update=datetime.now(),
                adjustments=[]
            )
            positions.append(position)
        
        return positions
        
    except Exception as e:
        logger.error(f"Error getting current positions: {e}")
        return []

async def get_market_data_for_symbol(symbol: str, mt5_service) -> Dict:
    """Get market data for specific symbol"""
    try:
        # Get latest tick data
        tick_data = mt5_service.get_symbol_info_tick(symbol)
        
        return {
            'current_price': tick_data.get('last', 1.0) if tick_data else 1.0,
            'volatility': 0.02,  # Mock volatility
            'trend_strength': 0.6,  # Mock trend
            'sentiment': 0.1,   # Mock sentiment
            'beta': 1.0,        # Mock beta
            'liquidity_score': 0.8,  # Mock liquidity
            'support_level': None,
            'resistance_level': None
        }
        
    except Exception as e:
        logger.error(f"Error getting market data for {symbol}: {e}")
        return {
            'current_price': 1.0,
            'volatility': 0.02,
            'trend_strength': 0.5,
            'sentiment': 0.0,
            'beta': 1.0,
            'liquidity_score': 0.8
        }

async def get_market_conditions(mt5_service) -> Dict:
    """Get overall market conditions"""
    return {
        'volatility': 0.025,
        'trend_strength': 0.6,
        'sentiment': 0.15,
        'market_movement': 0.01,
        'regime_confidence': 0.75
    }

async def calculate_performance_score(positions: List[DynamicPosition]) -> float:
    """Calculate performance score"""
    if not positions:
        return 50.0
    
    winning_positions = len([p for p in positions if p.unrealized_pnl > 0])
    return (winning_positions / len(positions)) * 100

async def calculate_risk_score(positions: List[DynamicPosition], mt5_service) -> float:
    """Calculate risk score"""
    if not positions:
        return 20.0
    
    total_risk = sum(p.risk_percentage for p in positions)
    return min(100, total_risk)

async def get_daily_alert_count() -> int:
    """Get daily alert count"""
    return 3  # Mock count

async def apply_position_adjustment(position: DynamicPosition, adjustment_type: AdjustmentType, new_value: float, mt5_service) -> bool:
    """Apply position adjustment through MT5"""
    try:
        # Mock implementation - would use actual MT5 API
        logger.info(f"Applying {adjustment_type.value} to position {position.position_id}: {new_value}")
        return True
        
    except Exception as e:
        logger.error(f"Error applying adjustment: {e}")
        return False

def generate_adjustment_reasoning(adjustment_type: AdjustmentType, old_value: float, new_value: float) -> str:
    """Generate reasoning for adjustment"""
    if adjustment_type == AdjustmentType.MOVE_STOP_LOSS:
        return f"AI analysis suggests moving stop loss from {old_value:.5f} to {new_value:.5f} to optimize risk-reward ratio"
    elif adjustment_type == AdjustmentType.INCREASE_SIZE:
        return f"Strong trend detected, increasing position size from {old_value:.4f} to {new_value:.4f}"
    elif adjustment_type == AdjustmentType.DECREASE_SIZE:
        return f"Risk management protocol triggered, reducing size from {old_value:.4f} to {new_value:.4f}"
    else:
        return f"AI optimization recommends adjustment from {old_value} to {new_value}"

def calculate_expected_impact(adjustment_type: AdjustmentType, old_value: float, new_value: float) -> str:
    """Calculate expected impact of adjustment"""
    change_percent = ((new_value - old_value) / old_value * 100) if old_value > 0 else 0
    
    if adjustment_type == AdjustmentType.MOVE_STOP_LOSS:
        return f"Expected risk reduction: {abs(change_percent):.1f}%"
    elif adjustment_type == AdjustmentType.INCREASE_SIZE:
        return f"Expected profit increase: {change_percent:.1f}%"
    elif adjustment_type == AdjustmentType.DECREASE_SIZE:
        return f"Expected risk reduction: {abs(change_percent):.1f}%"
    else:
        return f"Expected performance improvement: {abs(change_percent):.1f}%"

async def continuous_monitoring_task(mt5_service):
    """Continuous monitoring background task"""
    try:
        while True:
            # Monitor positions every 30 seconds
            await asyncio.sleep(30)
            
            positions = await get_current_positions(mt5_service)
            logger.info(f"Monitoring {len(positions)} positions")
            
            # Check for optimization opportunities
            for position in positions:
                if position.status == PositionStatus.OPEN:
                    # Run basic checks
                    market_data = await get_market_data_for_symbol(position.symbol, mt5_service)
                    
                    # Check if position needs attention
                    if abs(position.unrealized_pnl) > position.risk_amount * 0.1:
                        logger.info(f"Position {position.position_id} may need adjustment")
            
    except Exception as e:
        logger.error(f"Error in continuous monitoring: {e}")
        await asyncio.sleep(60)  # Wait before retrying 