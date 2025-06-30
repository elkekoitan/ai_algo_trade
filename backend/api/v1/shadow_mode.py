"""
Shadow Mode API Endpoints
🥷 Büyük oyuncuların gölgesinde hareket et
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, List, Optional
import logging
import asyncio
from datetime import datetime, timedelta

from backend.modules.shadow_mode.shadow_service import ShadowModeService
from backend.modules.shadow_mode.models import (
    WhaleDetection, DarkPoolActivity, InstitutionalFlow, 
    StealthOrder, ShadowAnalytics, WhaleAlert, ShadowModeStatus
)
from backend.modules.mt5_integration.service import MT5Service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/shadow-mode", tags=["Shadow Mode"])

# Dependency to get Shadow Mode service
async def get_shadow_service():
    from ...modules.mt5_integration.service import MT5Service
    from ...modules.mt5_integration.config import MT5_LOGIN, MT5_PASSWORD, MT5_SERVER
    
    mt5_service = MT5Service(
        login=MT5_LOGIN,
        password=MT5_PASSWORD,
        server=MT5_SERVER
    )
    return ShadowModeService(mt5_service)

@router.post("/activate")
async def activate_shadow_mode(stealth_level: int = 5) -> Dict:
    """
    🥷 Shadow Mode'u aktifleştir
    
    Args:
        stealth_level: Gizlilik seviyesi (1-10)
    """
    try:
        if not 1 <= stealth_level <= 10:
            raise HTTPException(status_code=400, detail="Stealth level must be between 1-10")
        
        result = await shadow_service.activate_shadow_mode(stealth_level)
        
        if result.get('status') == 'error':
            raise HTTPException(status_code=500, detail=result.get('message'))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Shadow Mode activation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/deactivate")
async def deactivate_shadow_mode() -> Dict:
    """
    🛑 Shadow Mode'u deaktifleştir
    """
    try:
        result = await shadow_service.deactivate_shadow_mode()
        
        if result.get('status') == 'error':
            raise HTTPException(status_code=500, detail=result.get('message'))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Shadow Mode deactivation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status", response_model=ShadowModeStatus)
async def get_shadow_mode_status(
    shadow_service: ShadowModeService = Depends(get_shadow_service)
):
    """Get current Shadow Mode system status"""
    try:
        status = await shadow_service.get_shadow_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting shadow status: {str(e)}")

@router.get("/alerts")
async def get_recent_alerts() -> List[Dict]:
    """
    🚨 Son Shadow Mode alertlerini getir
    """
    try:
        return await shadow_service.get_recent_alerts()
        
    except Exception as e:
        logger.error(f"Get alerts error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/whales", response_model=List[WhaleDetection])
async def detect_whales(
    symbol: str = "BTCUSD",
    shadow_service: ShadowModeService = Depends(get_shadow_service)
):
    """Detect whale activity for a specific symbol"""
    try:
        whales = await shadow_service.detect_whales(symbol)
        return whales
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting whales: {str(e)}")

@router.get("/whales/history", response_model=List[WhaleDetection])
async def get_whale_history(
    symbol: str = "BTCUSD",
    hours: int = 24,
    shadow_service: ShadowModeService = Depends(get_shadow_service)
):
    """Get whale detection history for the last N hours"""
    try:
        cutoff_time = datetime.now() - timedelta(hours=hours)
        history = [
            w for w in shadow_service.whale_detections 
            if w.symbol == symbol and w.timestamp > cutoff_time
        ]
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting whale history: {str(e)}")

@router.get("/dark-pools", response_model=List[DarkPoolActivity])
async def monitor_dark_pools(
    symbol: str = "BTCUSD",
    shadow_service: ShadowModeService = Depends(get_shadow_service)
):
    """Monitor dark pool activity for a specific symbol"""
    try:
        activities = await shadow_service.monitor_dark_pools(symbol)
        return activities
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error monitoring dark pools: {str(e)}")

@router.get("/institutional-flows", response_model=List[InstitutionalFlow])
async def track_institutional_flows(
    symbol: str = "BTCUSD",
    shadow_service: ShadowModeService = Depends(get_shadow_service)
):
    """Track institutional vs retail trading flows"""
    try:
        flows = await shadow_service.track_institutional_flows(symbol)
        return flows
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error tracking institutional flows: {str(e)}")

@router.get("/analytics", response_model=ShadowAnalytics)
async def get_shadow_analytics(
    symbol: str = "BTCUSD",
    shadow_service: ShadowModeService = Depends(get_shadow_service)
):
    """Get comprehensive shadow analytics"""
    try:
        analytics = await shadow_service.generate_shadow_analytics(symbol)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating analytics: {str(e)}")

@router.post("/stealth-order", response_model=StealthOrder)
async def create_stealth_order(
    symbol: str,
    order_type: str,  # "buy" or "sell"
    target_volume: float,
    max_chunk_size: float,
    time_interval_seconds: int = 60,
    stealth_level: float = 80.0,
    shadow_service: ShadowModeService = Depends(get_shadow_service)
):
    """Create a new stealth order for gradual execution"""
    try:
        # Create stealth order
        stealth_order = StealthOrder(
            id=str(datetime.now().timestamp()),
            symbol=symbol,
            order_type=order_type,
            target_volume=target_volume,
            max_chunk_size=max_chunk_size,
            time_interval_seconds=time_interval_seconds,
            price_strategy="vwap",  # Volume Weighted Average Price
            stealth_level=stealth_level,
            remaining_volume=target_volume
        )
        
        # Add to service
        shadow_service.stealth_orders.append(stealth_order)
        
        return stealth_order
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating stealth order: {str(e)}")

@router.get("/stealth-orders", response_model=List[StealthOrder])
async def get_stealth_orders(
    symbol: Optional[str] = None,
    status: Optional[str] = None,
    shadow_service: ShadowModeService = Depends(get_shadow_service)
):
    """Get list of stealth orders with optional filtering"""
    try:
        orders = shadow_service.stealth_orders
        
        if symbol:
            orders = [o for o in orders if o.symbol == symbol]
        if status:
            orders = [o for o in orders if o.status == status]
            
        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stealth orders: {str(e)}")

@router.get("/whale-alerts", response_model=List[WhaleAlert])
async def get_whale_alerts(
    symbol: str = "BTCUSD",
    severity: Optional[str] = None,
    shadow_service: ShadowModeService = Depends(get_shadow_service)
):
    """Get whale alerts with optional severity filtering"""
    try:
        # Get recent whales
        recent_whales = [
            w for w in shadow_service.whale_detections 
            if w.symbol == symbol and w.timestamp > datetime.now() - timedelta(hours=1)
        ]
        
        alerts = []
        for whale in recent_whales:
            # Determine severity based on whale size and impact
            if whale.size == "massive" or whale.impact_score > 80:
                alert_severity = "critical"
            elif whale.size == "large" or whale.impact_score > 60:
                alert_severity = "high"
            elif whale.size == "medium" or whale.impact_score > 40:
                alert_severity = "medium"
            else:
                alert_severity = "low"
            
            if severity and alert_severity != severity:
                continue
            
            # Generate alert message
            action = "BUYING" if whale.order_type == "buy" else "SELLING"
            message = f"🐋 {whale.size.upper()} whale {action} ${whale.value:,.0f} worth of {whale.symbol}"
            
            # Recommend action
            if whale.order_type == "buy" and whale.confidence > 0.7:
                recommended_action = "Consider following the whale - potential upward pressure"
            elif whale.order_type == "sell" and whale.confidence > 0.7:
                recommended_action = "Caution advised - potential downward pressure"
            else:
                recommended_action = "Monitor closely for confirmation"
            
            alert = WhaleAlert(
                alert_id=f"whale_{whale.id}",
                severity=alert_severity,
                message=message,
                whale_data=whale,
                recommended_action=recommended_action
            )
            alerts.append(alert)
        
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting whale alerts: {str(e)}")

@router.get("/market-impact", response_model=Dict)
async def get_market_impact_analysis(
    symbol: str = "BTCUSD",
    timeframe: str = "1h",  # 1h, 4h, 1d
    shadow_service: ShadowModeService = Depends(get_shadow_service)
):
    """Get market impact analysis from shadow activities"""
    try:
        # Get analytics
        analytics = await shadow_service.generate_shadow_analytics(symbol)
        
        # Calculate timeframe-specific impact
        timeframe_hours = {"1h": 1, "4h": 4, "1d": 24}.get(timeframe, 1)
        cutoff_time = datetime.now() - timedelta(hours=timeframe_hours)
        
        # Recent activities
        recent_whales = [
            w for w in shadow_service.whale_detections 
            if w.symbol == symbol and w.timestamp > cutoff_time
        ]
        recent_flows = [
            f for f in shadow_service.institutional_flows 
            if f.symbol == symbol and f.timestamp > cutoff_time
        ]
        
        # Calculate impact metrics
        whale_impact = sum(w.impact_score for w in recent_whales) / len(recent_whales) if recent_whales else 0
        flow_impact = sum(f.flow_strength for f in recent_flows) / len(recent_flows) if recent_flows else 0
        
        overall_impact = (whale_impact + flow_impact + analytics.institutional_pressure) / 3
        
        # Market direction prediction
        bullish_signals = sum(1 for w in recent_whales if w.order_type == "buy")
        bearish_signals = sum(1 for w in recent_whales if w.order_type == "sell")
        
        if bullish_signals > bearish_signals * 1.5:
            direction = "bullish"
            confidence = min(95, (bullish_signals / (bullish_signals + bearish_signals)) * 100)
        elif bearish_signals > bullish_signals * 1.5:
            direction = "bearish"
            confidence = min(95, (bearish_signals / (bullish_signals + bearish_signals)) * 100)
        else:
            direction = "neutral"
            confidence = 50
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "overall_impact_score": round(overall_impact, 2),
            "whale_impact": round(whale_impact, 2),
            "institutional_impact": round(flow_impact, 2),
            "market_direction": direction,
            "direction_confidence": round(confidence, 2),
            "whales_detected": len(recent_whales),
            "institutional_flows": len(recent_flows),
            "predicted_volatility": round(analytics.volatility_forecast, 2),
            "smart_money_flow": round(analytics.smart_money_flow, 2),
            "recommendation": self._generate_trading_recommendation(
                overall_impact, direction, confidence
            ),
            "risk_level": self._calculate_risk_level(analytics),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing market impact: {str(e)}")

@router.post("/analyze-realtime")
async def start_realtime_analysis(
    background_tasks: BackgroundTasks,
    symbol: str = "BTCUSD",
    interval_seconds: int = 30,
    shadow_service: ShadowModeService = Depends(get_shadow_service)
):
    """Start real-time shadow analysis for a symbol"""
    try:
        # Add background task for continuous analysis
        background_tasks.add_task(
            _continuous_analysis_task, 
            shadow_service, 
            symbol, 
            interval_seconds
        )
        
        return {
            "status": "started",
            "symbol": symbol,
            "analysis_interval": interval_seconds,
            "message": f"Real-time shadow analysis started for {symbol}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting analysis: {str(e)}")

# Helper functions
def _generate_trading_recommendation(impact: float, direction: str, confidence: float) -> str:
    """Generate trading recommendation based on shadow analysis"""
    if impact > 70 and confidence > 80:
        if direction == "bullish":
            return "STRONG BUY - High institutional buying pressure detected"
        elif direction == "bearish":
            return "STRONG SELL - High institutional selling pressure detected"
    elif impact > 50 and confidence > 60:
        if direction == "bullish":
            return "BUY - Moderate bullish pressure, consider entry"
        elif direction == "bearish":
            return "SELL - Moderate bearish pressure, consider exit"
    elif impact > 30:
        return "HOLD - Mixed signals, wait for clearer direction"
    else:
        return "NO SIGNAL - Insufficient institutional activity"

def _calculate_risk_level(analytics: ShadowAnalytics) -> str:
    """Calculate risk level based on analytics"""
    risk_score = (
        analytics.volatility_forecast + 
        analytics.market_fragmentation + 
        abs(analytics.smart_money_flow)
    ) / 3
    
    if risk_score > 80:
        return "HIGH"
    elif risk_score > 60:
        return "MEDIUM"
    elif risk_score > 40:
        return "LOW"
    else:
        return "VERY_LOW"

# Background task for continuous analysis
async def _continuous_analysis_task(
    shadow_service: ShadowModeService, 
    symbol: str, 
    interval_seconds: int
):
    """Continuous shadow analysis background task"""
    try:
        while True:
            # Run all analysis functions
            await asyncio.gather(
                shadow_service.detect_whales(symbol),
                shadow_service.monitor_dark_pools(symbol),
                shadow_service.track_institutional_flows(symbol)
            )
            
            # Wait for next iteration
            await asyncio.sleep(interval_seconds)
            
    except Exception as e:
        print(f"Continuous analysis error: {e}")
        # Log error but don't stop the background task 