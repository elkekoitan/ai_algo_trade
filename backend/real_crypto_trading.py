"""
Real Crypto Trading with Tickmill Demo Account
ETH/USD ve BTC/USD gerçek MT5 verileri ile trading
"""

import os
import logging
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import asyncio
import time
from typing import Dict, List
import json

# MT5 Integration
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from modules.mt5_integration.service import MT5Service
from modules.mt5_integration.config import MT5_LOGIN, MT5_PASSWORD, MT5_SERVER

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Algo Trade - Real Crypto Trading",
    description="Tickmill Demo hesabı ile gerçek ETH/USD ve BTC/USD trading",
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
    "mt5_connected": False,
    "processed_trades": 0,
    "active_symbols": ["BTCUSD", "ETHUSD"],
    "performance_metrics": {
        "total_signals": 0,
        "successful_trades": 0,
        "failed_trades": 0,
        "avg_response_time": 0,
        "uptime": 0,
        "account_balance": 0,
        "account_equity": 0
    },
    "event_history": [],
    "live_prices": {},
    "positions": []
}

# Global MT5 service
mt5_service = None

class RealCryptoEventBus:
    """Real-time event bus for crypto trading"""
    
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
event_bus = RealCryptoEventBus()

# Event handlers
async def trade_signal_handler(event_type: str, data: dict):
    """Handle trade signals"""
    system_state["performance_metrics"]["total_signals"] += 1
    symbol = data.get("symbol", "")
    action = data.get("action", "")
    price = data.get("price", 0)
    logger.info(f"🔥 Trade Signal: {action} {symbol} @ ${price:.2f}")

async def market_update_handler(event_type: str, data: dict):
    """Handle market updates"""
    symbol = data.get("symbol")
    if symbol in system_state["active_symbols"]:
        system_state["live_prices"][symbol] = data
        price = data.get("bid", 0)
        logger.info(f"📊 Market Update: {symbol} - Bid: ${price:.2f}")

async def account_update_handler(event_type: str, data: dict):
    """Handle account updates"""
    system_state["performance_metrics"]["account_balance"] = data.get("balance", 0)
    system_state["performance_metrics"]["account_equity"] = data.get("equity", 0)
    logger.info(f"💰 Account: Balance=${data.get('balance', 0):.2f}, Equity=${data.get('equity', 0):.2f}")

# Background tasks
async def real_price_monitor():
    """Monitor real-time crypto prices from MT5"""
    global mt5_service
    
    # Sadece aktif sembolleri izle
    symbols_to_monitor = system_state["active_symbols"]

    while True:
        try:
            if not mt5_service or not mt5_service.is_connected():
                logger.warning("MT5 not connected, skipping price update")
                await asyncio.sleep(5)
                continue
            
            for symbol in symbols_to_monitor:
                try:
                    # Get real tick data from MT5
                    tick_data = await mt5_service.get_symbol_tick(symbol)
                    
                    if tick_data:
                        # Calculate change percentage (simplified)
                        current_price = tick_data.get("bid", 0)
                        previous_price = system_state["live_prices"].get(symbol, {}).get("bid", current_price)
                        change_percent = ((current_price - previous_price) / previous_price) if previous_price > 0 else 0
                        
                        price_data = {
                            "symbol": symbol,
                            "bid": tick_data.get("bid", 0),
                            "ask": tick_data.get("ask", 0),
                            "spread": tick_data.get("ask", 0) - tick_data.get("bid", 0),
                            "change_percent": change_percent,
                            "timestamp": datetime.now().isoformat(),
                            "volume": tick_data.get("volume", 0)
                        }
                        
                        # Emit market update event
                        priority = "HIGH" if abs(change_percent) > 0.01 else "NORMAL"
                        await event_bus.emit("market.update", price_data, priority=priority)
                        
                except Exception as e:
                    logger.error(f"Error getting tick data for {symbol}: {e}")
            
            await asyncio.sleep(2)  # Update every 2 seconds
            
        except Exception as e:
            logger.error(f"Error in price monitor: {e}")
            await asyncio.sleep(5)

async def account_monitor():
    """Monitor account information"""
    global mt5_service
    
    while True:
        try:
            if not mt5_service or not mt5_service.is_connected():
                await asyncio.sleep(10)
                continue
            
            # Get account info
            account_info = await mt5_service.get_account_info()
            if account_info:
                await event_bus.emit("account.update", account_info, priority="NORMAL")
            
            # Get positions
            positions = await mt5_service.get_positions()
            system_state["positions"] = positions
            
            await asyncio.sleep(10)  # Update every 10 seconds
            
        except Exception as e:
            logger.error(f"Error in account monitor: {e}")
            await asyncio.sleep(10)

async def signal_analyzer():
    """Analyze market data and generate trading signals"""
    import random
    
    while True:
        try:
            if not mt5_service or not mt5_service.is_connected():
                await asyncio.sleep(10)
                continue
            
            for symbol in system_state["active_symbols"]:
                # Get current price data
                price_data = system_state["live_prices"].get(symbol)
                if not price_data:
                    continue
                
                # Simple signal generation based on price movement
                change_percent = price_data.get("change_percent", 0)
                
                # Generate signal if significant price movement
                if abs(change_percent) > 0.005:  # 0.5% movement
                    action = "BUY" if change_percent > 0 else "SELL"
                    confidence = min(0.95, 0.6 + abs(change_percent) * 20)  # Higher confidence for bigger moves
                    
                    signal_data = {
                        "symbol": symbol,
                        "action": action,
                        "confidence": confidence,
                        "price": price_data.get("bid", 0),
                        "volume": 0.1,  # Standard lot size for crypto
                        "strategy": "momentum" if confidence > 0.8 else "scalping",
                        "timestamp": datetime.now().isoformat(),
                        "reason": f"Price movement: {change_percent:.3f}%"
                    }
                    
                    await event_bus.emit("trade.signal", signal_data, priority="CRITICAL")
                    system_state["processed_trades"] += 1
            
            await asyncio.sleep(5)  # Analyze every 5 seconds
            
        except Exception as e:
            logger.error(f"Error in signal analyzer: {e}")
            await asyncio.sleep(10)

@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    global mt5_service
    
    logger.info("🚀 Starting Real Crypto Trading Backend...")
    
    try:
        # Initialize MT5 connection
        logger.info("🔌 Connecting to Tickmill Demo...")
        mt5_service = MT5Service()
        
        connected = await mt5_service.connect(
            login=MT5_LOGIN,
            password=MT5_PASSWORD,
            server=MT5_SERVER
        )
        
        if connected:
            logger.info("✅ MT5 Tickmill Demo connected successfully!")
            system_state["mt5_connected"] = True
            
            # Get account info
            account_info = await mt5_service.get_account_info()
            if account_info:
                logger.info(f"💰 Account Balance: ${account_info.get('balance', 0):,.2f}")
                logger.info(f"💰 Account Equity: ${account_info.get('equity', 0):,.2f}")
        else:
            logger.error("❌ Failed to connect to MT5!")
            system_state["mt5_connected"] = False
        
        # Subscribe event handlers
        event_bus.subscribe("trade.signal", trade_signal_handler)
        event_bus.subscribe("market.update", market_update_handler)
        event_bus.subscribe("account.update", account_update_handler)
        
        # Start background tasks
        if system_state["mt5_connected"]:
            asyncio.create_task(real_price_monitor())
            asyncio.create_task(account_monitor())
            asyncio.create_task(signal_analyzer())
        
        system_state["status"] = "operational"
        
        # Emit system ready event
        await event_bus.emit("system.ready", {
            "timestamp": datetime.now().isoformat(),
            "symbols": system_state["active_symbols"],
            "status": "operational",
            "mt5_connected": system_state["mt5_connected"]
        }, priority="HIGH")
        
        logger.info("✅ Real Crypto Trading Backend is ready!")
        
    except Exception as e:
        logger.error(f"❌ Failed to start backend: {e}")
        system_state["status"] = "error"

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    global mt5_service
    
    logger.info("🛑 Shutting down Real Crypto Trading Backend...")
    
    if mt5_service:
        await mt5_service.disconnect()
    
    system_state["status"] = "shutdown"

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint"""
    uptime = (datetime.now() - system_state["start_time"]).total_seconds()
    
    return {
        "name": "AI Algo Trade - Real Crypto Trading",
        "version": "3.0.0",
        "status": system_state["status"],
        "mt5_connected": system_state["mt5_connected"],
        "uptime_seconds": uptime,
        "active_symbols": system_state["active_symbols"],
        "processed_trades": system_state["processed_trades"],
        "account_server": MT5_SERVER,
        "account_login": MT5_LOGIN,
        "api_docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    uptime = (datetime.now() - system_state["start_time"]).total_seconds()
    
    return {
        "status": "healthy" if system_state["mt5_connected"] else "degraded",
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": uptime,
        "mt5_connected": system_state["mt5_connected"],
        "performance": system_state["performance_metrics"],
        "active_symbols": len(system_state["active_symbols"]),
        "event_history_size": len(event_bus.event_history),
        "positions_count": len(system_state["positions"])
    }

@app.get("/api/v1/crypto/prices")
async def get_real_crypto_prices():
    """Get real crypto prices from MT5"""
    if not mt5_service or not mt5_service.is_connected():
        raise HTTPException(status_code=503, detail="MT5 not connected")
    
    prices = {}
    for symbol in system_state["active_symbols"]:
        try:
            tick_data = await mt5_service.get_symbol_tick(symbol)
            if tick_data:
                prices[symbol] = {
                    "bid": tick_data.get("bid", 0),
                    "ask": tick_data.get("ask", 0),
                    "spread": tick_data.get("ask", 0) - tick_data.get("bid", 0),
                    "timestamp": tick_data.get("time", ""),
                    "volume": tick_data.get("volume", 0)
                }
        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {e}")
    
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "prices": prices,
        "source": "Tickmill Demo MT5"
    }

@app.get("/api/v1/account")
async def get_account_info():
    """Get real account information"""
    if not mt5_service or not mt5_service.is_connected():
        raise HTTPException(status_code=503, detail="MT5 not connected")
    
    try:
        account_info = await mt5_service.get_account_info()
        return {
            "status": "success",
            "data": account_info,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/positions")
async def get_positions():
    """Get current positions"""
    if not mt5_service or not mt5_service.is_connected():
        raise HTTPException(status_code=503, detail="MT5 not connected")
    
    try:
        positions = await mt5_service.get_positions()
        return {
            "status": "success",
            "data": positions,
            "count": len(positions),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/crypto/trade")
async def execute_real_trade(symbol: str, action: str, volume: float = 0.01):
    """Execute real trade on MT5"""
    if not mt5_service or not mt5_service.is_connected():
        raise HTTPException(status_code=503, detail="MT5 not connected")
    
    if symbol not in system_state["active_symbols"]:
        raise HTTPException(status_code=400, detail=f"Symbol {symbol} not supported")
    
    start_time = time.time()
    
    try:
        # Execute the trade
        result = await mt5_service.place_order(
            symbol=symbol,
            order_type=action.lower(),
            volume=volume,
            comment="AI Crypto Trade"
        )
        
        response_time = (time.time() - start_time) * 1000  # ms
        
        if result.get("success", False):
            system_state["performance_metrics"]["successful_trades"] += 1
            
            # Emit trade execution event
            await event_bus.emit("trade.executed", {
                "symbol": symbol,
                "action": action,
                "volume": volume,
                "ticket": result.get("ticket"),
                "price": result.get("price", 0),
                "response_time_ms": response_time,
                "status": "success"
            }, priority="HIGH")
            
            return {
                "status": "success",
                "symbol": symbol,
                "action": action,
                "volume": volume,
                "ticket": result.get("ticket"),
                "price": result.get("price", 0),
                "response_time_ms": response_time,
                "timestamp": datetime.now().isoformat()
            }
        else:
            system_state["performance_metrics"]["failed_trades"] += 1
            return {
                "status": "error",
                "message": result.get("error", "Trade execution failed"),
                "symbol": symbol,
                "action": action
            }
            
    except Exception as e:
        system_state["performance_metrics"]["failed_trades"] += 1
        logger.error(f"Trade execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
            "active_symbols": system_state["active_symbols"],
            "mt5_connected": system_state["mt5_connected"],
            "positions_count": len(system_state["positions"])
        }
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

if __name__ == "__main__":
    # Run the server
    logger.info("Starting Real Crypto Trading Platform with Tickmill Demo...")
    uvicorn.run(
        "real_crypto_trading:app",
        host="0.0.0.0",
        port=8004,  # Different port
        reload=True,
        log_level="info"
    ) 