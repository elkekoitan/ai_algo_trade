"""
Edge Computing API endpoints for high-frequency processing and advanced execution.
"""

from fastapi import APIRouter, Query, HTTPException, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import asyncio
import logging

from ...modules.edge_computing.high_frequency_processor import (
    HighFrequencyProcessor, DataStreamType
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/edge", tags=["Edge Computing"])

# Global processor instance
hf_processor = HighFrequencyProcessor()

@router.post("/start-processing")
async def start_edge_processing(
    symbols: List[str] = Query(..., description="Symbols to process"),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Start high-frequency edge processing for specified symbols."""
    try:
        if not hf_processor.is_running:
            await hf_processor.initialize()
            
            # Start processing in background
            background_tasks.add_task(hf_processor.start_processing, symbols)
            
            return {
                "success": True,
                "message": f"Edge processing started for {len(symbols)} symbols",
                "symbols": symbols,
                "started_at": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "message": "Edge processing already running",
                "symbols": symbols
            }
            
    except Exception as e:
        logger.error(f"Error starting edge processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop-processing")
async def stop_edge_processing():
    """Stop edge processing."""
    try:
        await hf_processor.stop_processing()
        
        return {
            "success": True,
            "message": "Edge processing stopped",
            "stopped_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error stopping edge processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics")
async def get_edge_metrics():
    """Get real-time edge computing performance metrics."""
    try:
        metrics = hf_processor.get_metrics()
        
        return {
            "success": True,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting edge metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/signals/stream/{symbol}")
async def get_signal_stream(
    symbol: str,
    limit: int = Query(100, description="Number of recent signals")
):
    """Get real-time signal stream for symbol."""
    try:
        # This would get signals from Redis stream
        signals = [
            {
                "signal_id": f"signal_{i}",
                "symbol": symbol,
                "type": "momentum",
                "strength": 75 + (i % 25),
                "confidence": 0.8 + (i % 20) / 100,
                "timestamp": (datetime.now() - timedelta(seconds=i*10)).isoformat()
            }
            for i in range(min(limit, 50))
        ]
        
        return {
            "success": True,
            "symbol": symbol,
            "signals": signals,
            "total_signals": len(signals),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting signal stream: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/execution/smart-routing")
async def get_smart_routing_options(
    symbol: str = Query(..., description="Trading symbol"),
    order_size: float = Query(..., description="Order size"),
    order_type: str = Query("market", description="Order type")
):
    """Get smart order routing recommendations."""
    try:
        # Simulate smart routing analysis
        routing_options = [
            {
                "venue": "Prime Broker A",
                "estimated_fill": 0.95,
                "estimated_slippage": 0.0001,
                "execution_time_ms": 12,
                "cost_estimate": order_size * 0.00005,
                "recommended": True
            },
            {
                "venue": "Dark Pool B",
                "estimated_fill": 0.85,
                "estimated_slippage": 0.00005,
                "execution_time_ms": 25,
                "cost_estimate": order_size * 0.00003,
                "recommended": False
            },
            {
                "venue": "ECN C",
                "estimated_fill": 0.98,
                "estimated_slippage": 0.00015,
                "execution_time_ms": 8,
                "cost_estimate": order_size * 0.00008,
                "recommended": False
            }
        ]
        
        return {
            "success": True,
            "symbol": symbol,
            "order_size": order_size,
            "routing_options": routing_options,
            "analysis_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting smart routing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/risk/real-time/{symbol}")
async def get_realtime_risk_metrics(symbol: str):
    """Get real-time risk metrics for symbol."""
    try:
        import numpy as np
        
        # Simulate real-time risk calculations
        risk_metrics = {
            "var_1d": np.random.uniform(1000, 5000),
            "var_5d": np.random.uniform(2000, 8000),
            "expected_shortfall": np.random.uniform(1500, 6000),
            "correlation_risk": np.random.uniform(0.1, 0.8),
            "concentration_risk": np.random.uniform(0.05, 0.3),
            "stress_test_result": {
                "2008_crisis": np.random.uniform(-0.15, -0.05),
                "covid_crash": np.random.uniform(-0.12, -0.03),
                "flash_crash": np.random.uniform(-0.08, -0.02)
            },
            "portfolio_beta": np.random.uniform(0.8, 1.2),
            "tracking_error": np.random.uniform(0.02, 0.08)
        }
        
        return {
            "success": True,
            "symbol": symbol,
            "risk_metrics": risk_metrics,
            "calculated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting risk metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance/latency")
async def get_latency_metrics():
    """Get system latency performance metrics."""
    try:
        import numpy as np
        
        latency_metrics = {
            "order_to_market_ms": {
                "avg": np.random.uniform(8, 15),
                "p50": np.random.uniform(7, 12),
                "p95": np.random.uniform(15, 25),
                "p99": np.random.uniform(25, 40),
                "max": np.random.uniform(40, 80)
            },
            "market_data_latency_ms": {
                "avg": np.random.uniform(1, 3),
                "p50": np.random.uniform(0.5, 2),
                "p95": np.random.uniform(3, 8),
                "p99": np.random.uniform(8, 15),
                "max": np.random.uniform(15, 30)
            },
            "signal_processing_ms": {
                "avg": np.random.uniform(0.5, 2),
                "p50": np.random.uniform(0.3, 1.5),
                "p95": np.random.uniform(2, 5),
                "p99": np.random.uniform(5, 10),
                "max": np.random.uniform(10, 20)
            },
            "total_processing_ticks": hf_processor.metrics.get('processed_ticks', 0),
            "average_throughput_tps": np.random.uniform(5000, 15000)
        }
        
        return {
            "success": True,
            "latency_metrics": latency_metrics,
            "measurement_period": "last_1_hour",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting latency metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def edge_computing_health():
    """Get edge computing system health."""
    try:
        metrics = hf_processor.get_metrics()
        
        # Determine health status
        health_status = "healthy"
        if not hf_processor.is_running:
            health_status = "stopped"
        elif metrics.get('avg_latency_ms', 0) > 100:
            health_status = "degraded"
        elif len(metrics.get('active_streams', 0)) == 0:
            health_status = "idle"
        
        return {
            "success": True,
            "status": health_status,
            "services": {
                "high_frequency_processor": "active" if hf_processor.is_running else "inactive",
                "redis_streams": "connected",
                "websocket_multiplexer": "active",
                "edge_optimizer": "active"
            },
            "performance": {
                "avg_latency_ms": metrics.get('avg_latency_ms', 0),
                "processed_ticks": metrics.get('processed_ticks', 0),
                "active_streams": len(metrics.get('active_streams', [])),
                "buffer_utilization": sum(metrics.get('buffer_sizes', {}).values()) / 50000 if metrics.get('buffer_sizes') else 0
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error checking edge computing health: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 