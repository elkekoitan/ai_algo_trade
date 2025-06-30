"""
Crypto Unified Trading Backend
ETH/USD ve BTC/USD işlemleri için optimize edilmiş
"""

import os
import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import asyncio
import time
from typing import Dict, List
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Algo Trade - Crypto Unified Platform",
    description="ETH/USD ve BTC/USD için event-driven trading sistemi",
    version="3.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
system_state = {
    "status": "initializing",
    "start_time": datetime.now(),
    "processed_trades": 0,
    "active_symbols": ["ETHUSD", "BTCUSD"],
    "performance_metrics": {
        "total_signals": 0,
        "successful_trades": 0,
        "failed_trades": 0,
        "avg_response_time": 0,
        "uptime": 0
    },
    "event_history": [],
    "live_prices": {}
}

# Simulated crypto price data
crypto_prices = {
    "ETHUSD": {"price": 3450.50, "change": 0.025, "volume": 1500000},
    "BTCUSD": {"price": 67800.25, "change": 0.018, "volume": 2800000}
}

class CryptoEventBus:
    """Simplified event bus for crypto trading"""
    
    def __init__(self):
        self.handlers = {}
        self.event_history = []
    
    def subscribe(self, event_type: str, handler):
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
    
    async def emit(self, event_type: str, data: dict, priority: str = "NORMAL"):
        timestamp = datetime.now().isoformat()
        event = {
            "event_type": event_type,
            "data": data,
            "priority": priority,
            "timestamp": timestamp
        }
        
        # Store in history
        self.event_history.append(event)
        if len(self.event_history) > 1000:  # Keep last 1000 events
            self.event_history = self.event_history[-1000:]
        
        # Process handlers
        if event_type in self.handlers:
            for handler in self.handlers[event_type]:
                try:
                    await handler(event_type, data)
                except Exception as e:
                    logger.error(f"Error in event handler: {e}")
        
        logger.info(f"Event emitted: {event_type} - Priority: {priority}")

# Global event bus
event_bus = CryptoEventBus()

# Event handlers
async def trade_signal_handler(event_type: str, data: dict):
    """Handle trade signals"""
    system_state["performance_metrics"]["total_signals"] += 1
    logger.info(f"🔥 Trade Signal: {data}")

async def market_update_handler(event_type: str, data: dict):
    """Handle market updates"""
    symbol = data.get("symbol")
    if symbol in system_state["active_symbols"]:
        system_state["live_prices"][symbol] = data
        logger.info(f"📊 Market Update: {symbol} - ${data.get('price', 0)}")

async def performance_monitor_handler(event_type: str, data: dict):
    """Handle performance monitoring"""
    logger.info(f"📈 Performance: {data}")

# Background tasks
async def crypto_price_simulator():
    """Simulate real-time crypto price updates"""
    import random
    
    while True:
        try:
            for symbol in ["ETHUSD", "BTCUSD"]:
                # Simulate price movement
                current_price = crypto_prices[symbol]["price"]
                change_percent = random.uniform(-0.02, 0.02)  # ±2% change
                new_price = current_price * (1 + change_percent)
                
                crypto_prices[symbol]["price"] = round(new_price, 2)
                crypto_prices[symbol]["change"] = change_percent
                crypto_prices[symbol]["volume"] = random.randint(1000000, 5000000)
                
                # Emit market update event
                await event_bus.emit("market.update", {
                    "symbol": symbol,
                    "price": new_price,
                    "change": change_percent,
                    "volume": crypto_prices[symbol]["volume"],
                    "timestamp": datetime.now().isoformat()
                }, priority="HIGH" if abs(change_percent) > 0.01 else "NORMAL")
            
            await asyncio.sleep(2)  # Update every 2 seconds
            
        except Exception as e:
            logger.error(f"Error in price simulator: {e}")
            await asyncio.sleep(5)

async def signal_generator():
    """Generate trading signals based on price movements"""
    import random
    
    while True:
        try:
            for symbol in ["ETHUSD", "BTCUSD"]:
                # Generate signals based on random conditions (replace with real logic)
                if random.random() < 0.1:  # 10% chance per cycle
                    action = random.choice(["BUY", "SELL"])
                    confidence = random.uniform(0.6, 0.95)
                    
                    signal_data = {
                        "symbol": symbol,
                        "action": action,
                        "confidence": confidence,
                        "price": crypto_prices[symbol]["price"],
                        "volume": random.uniform(0.1, 2.0),
                        "strategy": "momentum" if confidence > 0.8 else "scalping",
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    await event_bus.emit("trade.signal", signal_data, priority="CRITICAL")
                    system_state["processed_trades"] += 1
            
            await asyncio.sleep(5)  # Generate signals every 5 seconds
            
        except Exception as e:
            logger.error(f"Error in signal generator: {e}")
            await asyncio.sleep(10)

@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info("🚀 Starting Crypto Unified Trading Backend...")
    
    # Subscribe event handlers
    event_bus.subscribe("trade.signal", trade_signal_handler)
    event_bus.subscribe("market.update", market_update_handler)
    event_bus.subscribe("performance.metric", performance_monitor_handler)
    
    # Start background tasks
    asyncio.create_task(crypto_price_simulator())
    asyncio.create_task(signal_generator())
    
    system_state["status"] = "operational"
    
    # Emit system ready event
    await event_bus.emit("system.ready", {
        "timestamp": datetime.now().isoformat(),
        "symbols": system_state["active_symbols"],
        "status": "operational"
    }, priority="HIGH")
    
    logger.info("✅ Crypto Unified Trading Backend is ready!")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("🛑 Shutting down Crypto Unified Trading Backend...")
    system_state["status"] = "shutdown"

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint"""
    uptime = (datetime.now() - system_state["start_time"]).total_seconds()
    system_state["performance_metrics"]["uptime"] = uptime
    
    return {
        "name": "AI Algo Trade - Crypto Unified Platform",
        "version": "3.0.0",
        "status": system_state["status"],
        "uptime_seconds": uptime,
        "active_symbols": system_state["active_symbols"],
        "processed_trades": system_state["processed_trades"],
        "api_docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    uptime = (datetime.now() - system_state["start_time"]).total_seconds()
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": uptime,
        "performance": system_state["performance_metrics"],
        "active_symbols": len(system_state["active_symbols"]),
        "event_history_size": len(event_bus.event_history)
    }

@app.get("/api/v1/crypto/prices")
async def get_crypto_prices():
    """Get current crypto prices"""
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "prices": crypto_prices
    }

@app.get("/api/v1/crypto/performance")
async def get_performance_metrics():
    """Get performance metrics"""
    uptime = (datetime.now() - system_state["start_time"]).total_seconds()
    
    metrics = system_state["performance_metrics"].copy()
    metrics["uptime"] = uptime
    metrics["trades_per_minute"] = system_state["processed_trades"] / (uptime / 60) if uptime > 0 else 0
    metrics["success_rate"] = (metrics["successful_trades"] / metrics["total_signals"]) * 100 if metrics["total_signals"] > 0 else 0
    
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "metrics": metrics,
        "system_state": {
            "processed_trades": system_state["processed_trades"],
            "active_symbols": system_state["active_symbols"]
        }
    }

@app.post("/api/v1/events/emit")
async def emit_event(event_type: str, data: dict, priority: str = "NORMAL"):
    """Manually emit an event for testing"""
    await event_bus.emit(event_type, data, priority)
    
    return {
        "status": "event_emitted",
        "event_type": event_type,
        "priority": priority,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/events/history")
async def get_event_history(limit: int = 100, event_type: str = None):
    """Get recent event history"""
    history = event_bus.event_history[-limit:] if limit else event_bus.event_history
    
    if event_type:
        history = [e for e in history if e["event_type"] == event_type]
    
    return {
        "total_events": len(event_bus.event_history),
        "returned": len(history),
        "filter": event_type,
        "events": history
    }

@app.get("/api/v1/crypto/signals")
async def get_recent_signals():
    """Get recent trading signals"""
    signals = [e for e in event_bus.event_history if e["event_type"] == "trade.signal"][-20:]
    
    return {
        "status": "success",
        "total_signals": len(signals),
        "recent_signals": signals
    }

@app.post("/api/v1/crypto/test-trade")
async def test_trade(symbol: str, action: str, volume: float = 0.1):
    """Test trade execution"""
    start_time = time.time()
    
    # Simulate trade processing
    await asyncio.sleep(0.1)  # Simulate processing delay
    
    response_time = (time.time() - start_time) * 1000  # ms
    
    # Update metrics
    system_state["performance_metrics"]["avg_response_time"] = (
        system_state["performance_metrics"]["avg_response_time"] + response_time
    ) / 2
    
    if symbol in crypto_prices:
        system_state["performance_metrics"]["successful_trades"] += 1
        
        # Emit trade execution event
        await event_bus.emit("trade.executed", {
            "symbol": symbol,
            "action": action,
            "volume": volume,
            "price": crypto_prices[symbol]["price"],
            "response_time_ms": response_time,
            "status": "success"
        }, priority="HIGH")
        
        return {
            "status": "success",
            "symbol": symbol,
            "action": action,
            "volume": volume,
            "price": crypto_prices[symbol]["price"],
            "response_time_ms": response_time,
            "timestamp": datetime.now().isoformat()
        }
    else:
        system_state["performance_metrics"]["failed_trades"] += 1
        return {
            "status": "error",
            "message": f"Symbol {symbol} not supported",
            "supported_symbols": list(crypto_prices.keys())
        }

if __name__ == "__main__":
    # Run the server
    logger.info("Starting Crypto Unified Trading Platform...")
    uvicorn.run(
        "crypto_unified_main:app",
        host="0.0.0.0",
        port=8003,  # Different port
        reload=True,
        log_level="info"
    ) 