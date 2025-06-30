from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
from datetime import datetime, timedelta
import pandas as pd
import random
from fastapi import HTTPException
import MetaTrader5 as mt5
import numpy as np
import json
from typing import Dict, List, Optional

# Shared data service import
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.shared_data_service import shared_data_service

app = FastAPI(title="AI Algo Trade Live API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gerçek MT5 bağlantısı için import
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
    
    # Tickmill hesap bilgileri
    MT5_LOGIN = 25201110
    MT5_PASSWORD = "e|([rXU1IsiM"
    MT5_SERVER = "Tickmill-Demo"
    
except ImportError:
    MT5_AVAILABLE = False

# Global variables
active_connections: List[WebSocket] = []

@app.on_event("startup")
async def startup_event():
    """Initialize MT5 connection on startup"""
    try:
        if not mt5.initialize():
            print("MT5 initialization failed")
        else:
            print("MT5 initialized successfully")
            account_info = mt5.account_info()
            if account_info:
                print(f"Connected to account: {account_info.login}")
    except Exception as e:
        print(f"Startup error: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean shutdown"""
    mt5.shutdown()

# WebSocket connection manager
async def broadcast_to_all(message: dict):
    """Broadcast message to all connected clients"""
    if active_connections:
        disconnected = []
        for connection in active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                disconnected.append(connection)
        
        # Remove disconnected clients
        for conn in disconnected:
            if conn in active_connections:
                active_connections.remove(conn)

@app.websocket("/ws/system-events")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            # Keep connection alive and send periodic updates
            await asyncio.sleep(5)
            await websocket.send_text(json.dumps({
                "type": "heartbeat",
                "timestamp": datetime.now().isoformat()
            }))
    except WebSocketDisconnect:
        active_connections.remove(websocket)

@app.get("/")
async def root():
    return {"message": "AI Algo Trade Live API", "status": "running", "version": "2.0.0"}

@app.get("/api/health")
async def health_check():
    """System health check"""
    try:
        mt5_status = mt5.initialize()
        if mt5_status:
            account_info = mt5.account_info()
            mt5.shutdown()
            
            return {
                "status": "healthy",
                "mt5_connected": True,
                "account": account_info.login if account_info else None,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "mt5_error",
                "mt5_connected": False,
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/live-signals")
async def get_live_signals():
    """ICT signals with real MT5 data"""
    try:
        if not mt5.initialize():
            raise HTTPException(status_code=500, detail="MT5 connection failed")
        
        symbols = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"]
        signals = []
        
        for symbol in symbols:
            # Get real market data
            tick = mt5.symbol_info_tick(symbol)
            if not tick:
                continue
            
            # Simulate ICT signal detection
            signal_types = ['ORDER_BLOCK', 'FAIR_VALUE_GAP', 'BREAKER_BLOCK', 'LIQUIDITY_SWEEP', 'MARKET_STRUCTURE']
            signal_type = random.choice(signal_types)
            
            signal = {
                "id": f"signal_{symbol}_{int(datetime.now().timestamp())}",
                "symbol": symbol,
                "signal_type": signal_type,
                "direction": random.choice(['BULLISH', 'BEARISH']),
                "confidence": 70 + random.uniform(0, 25),
                "current_price": tick.bid,
                "entry_price": tick.bid * (1 + random.uniform(-0.001, 0.001)),
                "stop_loss": tick.bid * (1 + random.uniform(-0.01, -0.005)),
                "take_profit": tick.bid * (1 + random.uniform(0.005, 0.015)),
                "volume_analysis": {
                    "institutional_interest": random.choice(['HIGH', 'MEDIUM', 'LOW']),
                    "volume_spike": random.choice([True, False]),
                    "smart_money_flow": random.choice(['BUYING', 'SELLING', 'NEUTRAL'])
                },
                "timeframe": random.choice(['M15', 'H1', 'H4']),
                "timestamp": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(hours=2)).isoformat()
            }
            
            signals.append(signal)
        
        # Broadcast signals to WebSocket clients
        await broadcast_to_all({
            "type": "live_signals",
            "data": signals,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "success": True,
            "signals": signals,
            "total_signals": len(signals),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Signals error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        mt5.shutdown()

@app.get("/api/shadow-mode/whale-activity")
async def get_whale_activity():
    """Shadow Mode whale tracking"""
    try:
        if not mt5.initialize():
            raise HTTPException(status_code=500, detail="MT5 connection failed")
        
        symbols = ["EURUSD", "GBPUSD", "XAUUSD", "BTCUSD"]
        whale_activities = []
        
        for symbol in symbols:
            tick = mt5.symbol_info_tick(symbol)
            if not tick:
                continue
            
            # Simulate whale detection
            activity = {
                "symbol": symbol,
                "whale_id": f"WHALE_{random.randint(1000, 9999)}",
                "activity_type": random.choice(['ACCUMULATION', 'DISTRIBUTION', 'LARGE_ORDER', 'ICEBERG']),
                "size_estimate": random.uniform(10, 500),  # Million USD
                "impact_score": 70 + random.uniform(0, 30),
                "detection_confidence": 80 + random.uniform(0, 20),
                "price_at_detection": tick.bid,
                "estimated_entry": tick.bid * (1 + random.uniform(-0.002, 0.002)),
                "institutional_type": random.choice(['BANK', 'HEDGE_FUND', 'SOVEREIGN_FUND', 'PENSION_FUND']),
                "stealth_level": random.choice(['LOW', 'MEDIUM', 'HIGH']),
                "timestamp": datetime.now().isoformat(),
                "duration": random.choice(['5-15 min', '15-30 min', '30-60 min'])
            }
            
            whale_activities.append(activity)
        
        return {
            "success": True,
            "whale_activities": whale_activities,
            "active_whales": len(whale_activities),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Whale tracking error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        mt5.shutdown()

@app.get("/api/shadow-mode/institutional-positions")
async def get_institutional_positions():
    """Institutional position analysis"""
    try:
        institutions = [
            {
                "name": "Goldman Sachs",
                "position_size": random.uniform(50, 200),
                "direction": random.choice(['LONG', 'SHORT']),
                "confidence": 85 + random.uniform(0, 15),
                "symbols": ["EURUSD", "XAUUSD"]
            },
            {
                "name": "JPMorgan",
                "position_size": random.uniform(75, 300),
                "direction": random.choice(['LONG', 'SHORT']),
                "confidence": 80 + random.uniform(0, 20),
                "symbols": ["GBPUSD", "USDJPY"]
            },
            {
                "name": "Bridgewater",
                "position_size": random.uniform(100, 400),
                "direction": random.choice(['LONG', 'SHORT']),
                "confidence": 75 + random.uniform(0, 25),
                "symbols": ["XAUUSD", "BTCUSD"]
            }
        ]
        
        return {
            "success": True,
            "institutional_positions": institutions,
            "total_institutions": len(institutions),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Institutional positions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/adaptive-trade-manager/positions")
async def get_adaptive_positions():
    """Adaptive Trade Manager positions"""
    try:
        if not mt5.initialize():
            raise HTTPException(status_code=500, detail="MT5 connection failed")
        
        # Get real positions from MT5
        positions = mt5.positions_get()
        adaptive_positions = []
        
        if positions:
            for pos in positions:
                adaptive_pos = {
                    "ticket": pos.ticket,
                    "symbol": pos.symbol,
                    "type": "BUY" if pos.type == 0 else "SELL",
                    "volume": pos.volume,
                    "price_open": pos.price_open,
                    "price_current": pos.price_current,
                    "profit": pos.profit,
                    "pnl_percentage": (pos.profit / (pos.price_open * pos.volume * 100000)) * 100,
                    "ai_risk_score": 30 + random.uniform(0, 40),
                    "adaptive_sl": pos.sl,
                    "adaptive_tp": pos.tp,
                    "ai_recommendation": random.choice(['HOLD', 'SCALE_OUT', 'ADD_POSITION', 'CLOSE']),
                    "time_open": pos.time.isoformat() if hasattr(pos.time, 'isoformat') else str(pos.time),
                    "duration_hours": (datetime.now() - datetime.fromtimestamp(pos.time)).total_seconds() / 3600
                }
                adaptive_positions.append(adaptive_pos)
        
        # If no real positions, create mock data
        if not adaptive_positions:
            mock_symbols = ["EURUSD", "XAUUSD"]
            for i, symbol in enumerate(mock_symbols):
                tick = mt5.symbol_info_tick(symbol)
                if tick:
                    adaptive_pos = {
                        "ticket": 1000 + i,
                        "symbol": symbol,
                        "type": random.choice(["BUY", "SELL"]),
                        "volume": 0.1,
                        "price_open": tick.bid * (1 + random.uniform(-0.01, 0.01)),
                        "price_current": tick.bid,
                        "profit": random.uniform(-50, 150),
                        "pnl_percentage": random.uniform(-2, 5),
                        "ai_risk_score": 30 + random.uniform(0, 40),
                        "adaptive_sl": tick.bid * 0.99,
                        "adaptive_tp": tick.bid * 1.02,
                        "ai_recommendation": random.choice(['HOLD', 'SCALE_OUT', 'ADD_POSITION']),
                        "time_open": (datetime.now() - timedelta(hours=2)).isoformat(),
                        "duration_hours": 2.5
                    }
                    adaptive_positions.append(adaptive_pos)
        
        return {
            "success": True,
            "positions": adaptive_positions,
            "total_positions": len(adaptive_positions),
            "total_pnl": sum(pos["profit"] for pos in adaptive_positions),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Adaptive positions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        mt5.shutdown()

@app.get("/api/system/unified-view")
async def get_unified_system_view():
    """Unified view of all modules"""
    try:
        # Collect data from all modules
        signals_data = await get_live_signals()
        whale_data = await get_whale_activity()
        positions_data = await get_adaptive_positions()
        
        unified_view = {
            "system_status": "ACTIVE",
            "modules": {
                "signals": {
                    "active": True,
                    "total_signals": len(signals_data["signals"]),
                    "high_confidence_signals": len([s for s in signals_data["signals"] if s["confidence"] > 80])
                },
                "shadow_mode": {
                    "active": True,
                    "whale_activities": len(whale_data["whale_activities"]),
                    "institutional_flow": "BULLISH"
                },
                "adaptive_trader": {
                    "active": True,
                    "open_positions": len(positions_data["positions"]),
                    "total_pnl": positions_data["total_pnl"]
                },
                "god_mode": {
                    "active": True,
                    "quantum_coherence": 85 + random.uniform(0, 15),
                    "prediction_accuracy": 78 + random.uniform(0, 15)
                },
                "market_narrator": {
                    "active": True,
                    "stories_generated": 12,
                    "sentiment_score": random.uniform(-20, 30)
                },
                "strategy_whisperer": {
                    "active": True,
                    "strategies_created": 8,
                    "deployed_strategies": 3
                }
            },
            "cross_module_correlations": {
                "signal_whale_correlation": 0.75,
                "sentiment_price_correlation": 0.68,
                "institutional_flow_signals": 0.82
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return unified_view
        
    except Exception as e:
        print(f"Unified view error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/god-mode/predictions")
async def get_god_mode_predictions():
    """God Mode quantum predictions"""
    try:
        if not mt5.initialize():
            raise HTTPException(status_code=500, detail="MT5 connection failed")
        
        symbols = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "BTCUSD"]
        predictions = []
        
        for symbol in symbols:
            # Get current price
            tick = mt5.symbol_info_tick(symbol)
            if not tick:
                continue
                
            # Quantum analysis simulation (gerçek sistemde AI model)
            direction = random.choice(['BULLISH', 'BEARISH', 'NEUTRAL'])
            confidence = 70 + random.uniform(0, 25)
            quantum_prob = 60 + random.uniform(0, 35)
            
            # Calculate target price based on direction
            current_price = tick.bid
            if direction == 'BULLISH':
                target_price = current_price * (1 + random.uniform(0.005, 0.02))
            elif direction == 'BEARISH':
                target_price = current_price * (1 - random.uniform(0.005, 0.02))
            else:
                target_price = current_price * (1 + random.uniform(-0.005, 0.005))
            
            prediction = {
                "symbol": symbol,
                "direction": direction,
                "confidence": confidence,
                "quantum_probability": quantum_prob,
                "current_price": current_price,
                "target_price": target_price,
                "timeframe": random.choice(['1H', '4H', '1D']),
                "risk_level": random.choice(['LOW', 'MEDIUM', 'HIGH']),
                "ai_reasoning": f"Quantum neural network analysis indicates {direction.lower()} momentum with {confidence:.0f}% probability",
                "market_factors": random.sample(['Institutional Flow', 'Technical Breakout', 'Momentum Divergence', 'Volume Spike', 'Correlation Shift'], 3),
                "time_horizon": random.choice(['2-4 hours', '6-12 hours', '1-2 days']),
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(hours=4)).isoformat()
            }
            
            predictions.append(prediction)
        
        return {
            "success": True,
            "predictions": predictions,
            "quantum_coherence": 85 + random.uniform(0, 15),
            "market_sentiment": random.choice(['EXTREME_BULLISH', 'BULLISH', 'NEUTRAL', 'BEARISH', 'EXTREME_BEARISH']),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"God mode error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        mt5.shutdown()

@app.get("/api/market-narrator/stories")
async def get_market_stories():
    """Market Narrator stories"""
    try:
        if not mt5.initialize():
            raise HTTPException(status_code=500, detail="MT5 connection failed")
        
        # Get market data for story generation
        symbols = ["EURUSD", "GBPUSD", "XAUUSD", "BTCUSD"]
        stories = []
        
        # Generate stories based on market movements
        for i, symbol in enumerate(symbols[:3]):
            tick = mt5.symbol_info_tick(symbol)
            if not tick:
                continue
            
            # Story generation logic
            story_types = ['BREAKING', 'ANALYSIS', 'PREDICTION', 'ALERT']
            sentiments = ['BULLISH', 'BEARISH', 'NEUTRAL']
            
            story = {
                "title": f"{symbol} Shows {random.choice(['Strong', 'Weak', 'Mixed'])} {random.choice(['Momentum', 'Reversal', 'Consolidation'])} Signals",
                "content": f"Advanced AI analysis of {symbol} reveals significant market dynamics. Technical indicators suggest {random.choice(['bullish', 'bearish', 'neutral'])} momentum with institutional backing. Volume analysis confirms {random.choice(['accumulation', 'distribution', 'consolidation'])} phase.",
                "summary": f"{random.choice(['Strong', 'Moderate', 'Weak'])} {random.choice(['bullish', 'bearish'])} sentiment driven by {random.choice(['institutional flows', 'technical breakouts', 'economic data'])}",
                "sentiment": random.choice(sentiments),
                "confidence": 70 + random.uniform(0, 25),
                "impact_score": 60 + random.uniform(0, 40),
                "story_type": random.choice(story_types),
                "affected_symbols": [symbol] + random.sample([s for s in symbols if s != symbol], 1),
                "sources": ["Technical Analysis", "Sentiment Data", "Volume Profile"],
                "correlations": [
                    {
                        "symbol": random.choice(symbols),
                        "correlation": random.uniform(-0.8, 0.8),
                        "impact": random.choice(['Strong', 'Moderate', 'Weak'])
                    }
                ],
                "timestamp": datetime.now().isoformat(),
                "author": "AI_NARRATOR"
            }
            
            stories.append(story)
        
        return {
            "success": True,
            "stories": stories,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Market narrator error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        mt5.shutdown()

@app.get("/api/strategy-whisperer/strategies")
async def get_strategy_whisperer_strategies():
    """Strategy Whisperer generated strategies"""
    try:
        # Mock strategies (gerçek sistemde database'den gelir)
        strategies = []
        
        strategy_templates = [
            {
                "name": "ICT Order Block Strategy",
                "description": "Advanced ICT-based strategy using order blocks and fair value gaps",
                "input": "Create a strategy that identifies order blocks and trades the retest with proper risk management",
                "win_rate": 75 + random.uniform(0, 15),
                "profit_factor": 1.5 + random.uniform(0, 0.8)
            },
            {
                "name": "Momentum Breakout System", 
                "description": "High-frequency momentum trading with adaptive parameters",
                "input": "Build a momentum strategy that catches breakouts with volume confirmation",
                "win_rate": 68 + random.uniform(0, 20),
                "profit_factor": 1.3 + random.uniform(0, 0.9)
            }
        ]
        
        for i, template in enumerate(strategy_templates):
            total_trades = 50 + random.randint(0, 100)
            winning_trades = int(total_trades * (template["win_rate"] / 100))
            
            strategy = {
                "name": template["name"],
                "description": template["description"],
                "input": template["input"],
                "status": random.choice(['DRAFT', 'TESTING', 'OPTIMIZED']),
                "backtest": {
                    "total_trades": total_trades,
                    "winning_trades": winning_trades,
                    "losing_trades": total_trades - winning_trades,
                    "win_rate": template["win_rate"],
                    "profit_factor": template["profit_factor"],
                    "max_drawdown": 5 + random.uniform(0, 15),
                    "total_return": 15 + random.uniform(0, 35),
                    "sharpe_ratio": 1.0 + random.uniform(0, 1.5)
                },
                "created_at": (datetime.now() - timedelta(days=i)).isoformat(),
                "deployment": "NOT_DEPLOYED"
            }
            
            strategies.append(strategy)
        
        return {
            "success": True,
            "strategies": strategies,
            "total_strategies": len(strategies),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Strategy whisperer error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002) 