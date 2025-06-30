"""
Unified Trading API - Tüm modülleri birleştiren merkezi API
Event-driven architecture ile Adaptive Trade Manager, God Mode, Market Narrator, Shadow Mode entegreli
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from ...core.unified_trading_engine import UnifiedTradingEngine, UnifiedOrder, OrderStatus
from ...core.enhanced_event_bus import EnhancedEvent, EventPriority
from ...modules.mt5_integration.service import MT5Service

router = APIRouter()
logger = logging.getLogger(__name__)

# Global engine instance
engine = UnifiedTradingEngine()

@router.on_event("startup")
async def startup_event():
    """Start the unified trading engine"""
    try:
        await engine.start()
        logger.info("🚀 Unified Trading Engine started via API")
    except Exception as e:
        logger.error(f"Failed to start engine: {e}")

@router.on_event("shutdown")
async def shutdown_event():
    """Stop the unified trading engine"""
    try:
        await engine.stop()
        logger.info("🛑 Unified Trading Engine stopped via API")
    except Exception as e:
        logger.error(f"Failed to stop engine: {e}")

# Engine Status Endpoints

@router.get("/status")
async def get_engine_status():
    """Get unified trading engine status"""
    try:
        return {
            "status": "success",
            "data": {
                "engine_running": engine.is_running,
                "mt5_connected": engine.connected,
                "modules": {
                    "adaptive_manager": await engine.adaptive_manager.get_status(),
                    "god_mode": await engine.god_mode.get_status(),
                    "market_narrator": await engine.market_narrator.get_status(),
                    "shadow_mode": await engine.shadow_mode.get_status()
                },
                "performance": engine.performance_metrics,
                "event_bus_metrics": engine.event_bus.get_metrics()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard")
async def get_unified_dashboard():
    """Get complete dashboard data from all modules"""
    try:
        dashboard_data = await engine.get_unified_dashboard_data()
        return {
            "status": "success",
            "data": dashboard_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Trading Endpoints

@router.post("/signals/generate")
async def generate_unified_signal(signal_data: Dict[str, Any]):
    """Generate and process a trading signal through all modules"""
    try:
        # Emit signal to event bus for processing
        await engine.event_bus.emit(EnhancedEvent(
            type="signal.generated",
            data=signal_data,
            priority=EventPriority.HIGH,
            source="api"
        ))
        
        return {
            "status": "success",
            "message": "Signal generated and sent for processing",
            "signal_id": signal_data.get("id", "unknown")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/orders/place")
async def place_unified_order(order_data: Dict[str, Any]):
    """Place order through unified engine"""
    try:
        # Create unified order
        order = UnifiedOrder(
            id=f"api_order_{datetime.now().timestamp()}",
            symbol=order_data["symbol"],
            order_type=order_data["action"],
            volume=order_data["volume"],
            price=order_data.get("price", 0),
            sl=order_data.get("sl"),
            tp=order_data.get("tp"),
            module="api",
            strategy=order_data.get("strategy", "manual"),
            metadata=order_data.get("metadata", {})
        )
        
        # Execute order
        success = await engine.order_manager.execute_order(order)
        
        if success:
            return {
                "status": "success",
                "message": "Order placed successfully",
                "order_id": order.id,
                "order_status": order.status.value
            }
        else:
            return {
                "status": "error",
                "message": "Order execution failed",
                "order_id": order.id,
                "order_status": order.status.value
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/positions")
async def get_all_positions():
    """Get all active positions with module insights"""
    try:
        positions = await engine.position_manager.get_all_positions()
        
        # Enrich with module data
        enriched_positions = []
        for pos in positions:
            enriched_pos = {
                **pos.__dict__,
                "adaptive_adjustments_count": len(pos.adaptive_adjustments),
                "god_mode_predictions_count": len(pos.god_mode_predictions),
                "narrative_events_count": len(pos.narrative_events),
                "has_shadow_intel": bool(pos.shadow_intel)
            }
            enriched_positions.append(enriched_pos)
        
        return {
            "status": "success",
            "data": {
                "positions": enriched_positions,
                "total_count": len(positions),
                "total_profit": sum(pos.profit for pos in positions)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/positions/{ticket}/close")
async def close_position(ticket: int):
    """Close a specific position"""
    try:
        success = await engine.position_manager.close_position(ticket)
        
        return {
            "status": "success" if success else "error",
            "message": f"Position {ticket} {'closed' if success else 'failed to close'}",
            "ticket": ticket
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/positions/close-all")
async def close_all_positions():
    """Close all open positions"""
    try:
        await engine.position_manager.close_all_positions()
        
        return {
            "status": "success",
            "message": "All positions closed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Module-Specific Endpoints

@router.get("/adaptive-manager/status")
async def get_adaptive_manager_status():
    """Get Adaptive Trade Manager status"""
    try:
        status = await engine.adaptive_manager.get_status()
        return {
            "status": "success",
            "data": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/god-mode/predictions")
async def get_god_mode_predictions():
    """Get God Mode predictions"""
    try:
        predictions = engine.god_mode.predictions[-10:]  # Last 10 predictions
        return {
            "status": "success",
            "data": {
                "predictions": predictions,
                "accuracy": engine.god_mode.prediction_accuracy,
                "total_predictions": len(engine.god_mode.predictions)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market-narrator/stories")
async def get_market_stories():
    """Get Market Narrator stories"""
    try:
        stories = engine.market_narrator.stories[-5:]  # Last 5 stories
        return {
            "status": "success",
            "data": {
                "stories": stories,
                "total_stories": len(engine.market_narrator.stories)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/shadow-mode/detections")
async def get_whale_detections():
    """Get Shadow Mode whale detections"""
    try:
        detections = engine.shadow_mode.whale_detections[-10:]  # Last 10 detections
        return {
            "status": "success",
            "data": {
                "detections": detections,
                "total_detections": len(engine.shadow_mode.whale_detections)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Risk Management Endpoints

@router.get("/risk/status")
async def get_risk_status():
    """Get current risk status"""
    try:
        risk_status = await engine.risk_manager.get_current_risk_status()
        return {
            "status": "success",
            "data": risk_status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/risk/update-params")
async def update_risk_parameters(risk_params: Dict[str, Any]):
    """Update risk management parameters"""
    try:
        if "max_positions" in risk_params:
            engine.risk_manager.max_positions = risk_params["max_positions"]
        if "max_risk_per_trade" in risk_params:
            engine.risk_manager.max_risk_per_trade = risk_params["max_risk_per_trade"]
        if "max_daily_loss" in risk_params:
            engine.risk_manager.max_daily_loss = risk_params["max_daily_loss"]
        
        return {
            "status": "success",
            "message": "Risk parameters updated",
            "updated_params": risk_params
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Event System Endpoints

@router.get("/events/metrics")
async def get_event_metrics():
    """Get event bus metrics"""
    try:
        metrics = engine.event_bus.get_metrics()
        return {
            "status": "success",
            "data": metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events/history")
async def get_event_history(limit: int = 50):
    """Get recent event history"""
    try:
        history = engine.event_bus.event_history[-limit:]
        
        # Serialize events for JSON response
        serialized_history = []
        for event in history:
            serialized_history.append({
                "id": event.id,
                "type": event.type,
                "source": event.source,
                "priority": event.priority.name,
                "timestamp": event.timestamp.isoformat(),
                "data": event.data
            })
        
        return {
            "status": "success",
            "data": {
                "events": serialized_history,
                "total_events": len(engine.event_bus.event_history)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Testing Endpoints

@router.post("/test/signal")
async def test_signal_processing():
    """Test signal processing through all modules"""
    try:
        test_signal = {
            "id": f"test_{datetime.now().timestamp()}",
            "symbol": "EURUSD",
            "action": "BUY",
            "volume": 0.01,
            "sl": 1.0800,
            "tp": 1.0900,
            "module": "test",
            "strategy": "test_strategy",
            "confidence": 0.8
        }
        
        await engine.event_bus.emit(EnhancedEvent(
            type="signal.generated",
            data=test_signal,
            priority=EventPriority.HIGH,
            source="test_api"
        ))
        
        return {
            "status": "success",
            "message": "Test signal sent for processing",
            "signal": test_signal
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test/whale-detection")
async def test_whale_detection():
    """Test whale detection event"""
    try:
        test_whale = {
            "symbol": "BTCUSD",
            "direction": "BUY",
            "volume": 5000000,
            "confidence": 0.9,
            "timestamp": datetime.now()
        }
        
        await engine.event_bus.emit(EnhancedEvent(
            type="shadow.whale_detected",
            data=test_whale,
            priority=EventPriority.CRITICAL,
            source="test_api"
        ))
        
        return {
            "status": "success",
            "message": "Test whale detection sent",
            "whale_data": test_whale
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Performance Endpoints

@router.get("/performance/metrics")
async def get_performance_metrics():
    """Get detailed performance metrics"""
    try:
        return {
            "status": "success",
            "data": {
                "engine_metrics": engine.performance_metrics,
                "module_performance": {
                    "adaptive_adjustments": engine.performance_metrics.get("adaptive_adjustments", 0),
                    "god_mode_accuracy": engine.performance_metrics.get("god_mode_accuracy", 0),
                    "shadow_detections": engine.performance_metrics.get("shadow_detections", 0)
                },
                "event_bus_performance": engine.event_bus.get_metrics()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance/summary")
async def get_performance_summary():
    """Get performance summary with all module insights"""
    try:
        positions = await engine.position_manager.get_all_positions()
        
        # Calculate comprehensive performance
        total_profit = sum(pos.profit for pos in positions)
        total_adaptive_adjustments = sum(len(pos.adaptive_adjustments) for pos in positions)
        total_god_predictions = sum(len(pos.god_mode_predictions) for pos in positions)
        total_narrative_events = sum(len(pos.narrative_events) for pos in positions)
        positions_with_shadow_intel = sum(1 for pos in positions if pos.shadow_intel)
        
        return {
            "status": "success",
            "data": {
                "trading_performance": {
                    "total_positions": len(positions),
                    "total_profit": total_profit,
                    "average_profit_per_position": total_profit / len(positions) if positions else 0
                },
                "module_insights": {
                    "adaptive_trade_manager": {
                        "total_adjustments": total_adaptive_adjustments,
                        "adjustments_per_position": total_adaptive_adjustments / len(positions) if positions else 0
                    },
                    "god_mode": {
                        "total_predictions": total_god_predictions,
                        "accuracy": engine.god_mode.prediction_accuracy,
                        "predictions_per_position": total_god_predictions / len(positions) if positions else 0
                    },
                    "market_narrator": {
                        "total_events": total_narrative_events,
                        "events_per_position": total_narrative_events / len(positions) if positions else 0
                    },
                    "shadow_mode": {
                        "positions_with_intel": positions_with_shadow_intel,
                        "intel_coverage": positions_with_shadow_intel / len(positions) if positions else 0,
                        "total_detections": len(engine.shadow_mode.whale_detections)
                    }
                },
                "system_health": {
                    "engine_running": engine.is_running,
                    "mt5_connected": engine.connected,
                    "event_bus_active": engine.event_bus.is_running,
                    "modules_active": {
                        "atm": engine.adaptive_manager.active,
                        "god_mode": engine.god_mode.active,
                        "narrator": engine.market_narrator.active,
                        "shadow": engine.shadow_mode.active
                    }
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 