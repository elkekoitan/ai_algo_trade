"""
Simple FastAPI application for ICT Ultra v2
Minimal version for testing without complex dependencies
"""

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    import uvicorn
    from datetime import datetime
    import json
    import logging
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Please install: pip install fastapi uvicorn")
    exit(1)

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="ICT Ultra v2: Algo Forge Edition",
    description="Advanced algorithmic trading platform (Simple Mode)",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data for testing
mock_account_data = {
    "login": 25201110,
    "balance": 10000.0,
    "equity": 10000.0,
    "margin": 0.0,
    "free_margin": 10000.0,
    "margin_level": 0.0,
    "profit": 0.0,
    "server": "Tickmill-Demo",
    "currency": "USD",
    "leverage": 500
}

mock_signals = [
    {
        "id": "signal_1",
        "type": "order_block",
        "symbol": "EURUSD",
        "timeframe": "H1",
        "direction": "bullish",
        "score": 85,
        "confidence": 82,
        "entry_price": 1.1000,
        "sl_price": 1.0980,
        "tp_price": 1.1040,
        "timestamp": datetime.now().isoformat(),
        "status": "active"
    },
    {
        "id": "signal_2",
        "type": "fair_value_gap",
        "symbol": "GBPUSD",
        "timeframe": "M30",
        "direction": "bearish",
        "score": 78,
        "confidence": 75,
        "entry_price": 1.2500,
        "sl_price": 1.2520,
        "tp_price": 1.2450,
        "timestamp": datetime.now().isoformat(),
        "status": "active"
    }
]

# Health check
@app.get("/health")
@app.get("/api/v1/health")
async def health_check():
    """System health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "mt5_connected": True,  # Mock connection
        "services": {
            "api": "online",
            "mt5_integration": "active",
            "auto_trader": "active",
            "performance_analytics": "active",
            "market_scanner": "active",
            "ict_signals": "active"
        }
    }

# Account info
@app.get("/api/v1/trading/account")
async def get_account_info():
    """Get account information"""
    return mock_account_data

# Market data quote
@app.get("/api/v1/market-data/quote/{symbol}")
async def get_quote(symbol: str):
    """Get real-time quote for symbol"""
    import random
    
    base_prices = {
        "EURUSD": 1.1000,
        "GBPUSD": 1.2500,
        "USDJPY": 150.00,
        "XAUUSD": 2000.00,
        "BTCUSD": 45000.00
    }
    
    base_price = base_prices.get(symbol, 1.0000)
    spread = random.uniform(0.00001, 0.00005)
    change = random.uniform(-0.001, 0.001)
    
    return {
        "symbol": symbol,
        "bid": base_price - spread/2,
        "ask": base_price + spread/2,
        "spread": spread * 100000,  # in points
        "change": change,
        "change_pct": (change / base_price) * 100,
        "volume": random.randint(1000, 10000),
        "time": datetime.now().isoformat()
    }

# ICT Signals
@app.get("/api/v1/signals/ict")
async def get_ict_signals(timeframe: str = "H1", limit: int = 20):
    """Get ICT signals"""
    return {
        "success": True,
        "signals": mock_signals[:limit],
        "total": len(mock_signals),
        "timeframe": timeframe
    }

# Trading positions
@app.get("/api/v1/trading/positions")
async def get_positions():
    """Get open positions"""
    return []  # No open positions in demo

# AutoTrader status
@app.get("/api/v1/auto-trader/status")
async def get_autotrader_status():
    """Get AutoTrader status"""
    return {
        "success": True,
        "active_sessions": 0,
        "total_sessions": 0,
        "status": "ready"
    }

# Scanner opportunities
@app.get("/api/v1/scanner/opportunities")
async def get_opportunities(
    symbols: str = "EURUSD,GBPUSD,USDJPY",
    timeframes: str = "M15,M30,H1",
    min_strength: float = 70.0
):
    """Get trading opportunities"""
    import random
    
    symbol_list = symbols.split(",")
    opportunities = []
    
    for i, symbol in enumerate(symbol_list[:5]):  # Limit to 5 for demo
        opportunity = {
            "id": f"opp_{symbol}_{i}",
            "symbol": symbol,
            "timeframe": "H1",
            "signal_type": random.choice(["order_block", "fair_value_gap", "breaker_block"]),
            "direction": random.choice(["bullish", "bearish"]),
            "strength": random.uniform(70, 95),
            "confidence": random.uniform(75, 90),
            "entry_price": random.uniform(1.0, 2.0),
            "sl_price": random.uniform(0.9, 1.1),
            "tp_price": random.uniform(1.1, 2.1),
            "risk_reward": random.uniform(1.5, 3.0),
            "timestamp": datetime.now().isoformat(),
            "status": "active",
            "market_structure": "Higher High Formation",
            "volume_confirmation": random.choice([True, False]),
            "price_action_score": random.uniform(70, 95)
        }
        opportunities.append(opportunity)
    
    return {
        "success": True,
        "opportunities": opportunities,
        "total_found": len(opportunities),
        "scan_time": datetime.now().isoformat()
    }

# Scanner overview
@app.get("/api/v1/scanner/overview")
async def get_market_overview(symbols: str = "EURUSD,GBPUSD,USDJPY"):
    """Get market overview"""
    import random
    
    symbol_list = symbols.split(",")
    overview = []
    
    for symbol in symbol_list:
        market = {
            "symbol": symbol,
            "price": random.uniform(1.0, 2.0),
            "change": random.uniform(-0.01, 0.01),
            "change_pct": random.uniform(-1.0, 1.0),
            "volume": random.randint(10000, 100000),
            "volatility": random.uniform(0.5, 2.0),
            "trend": random.choice(["bullish", "bearish", "sideways"]),
            "signals_count": random.randint(0, 5),
            "last_signal": "Order Block - 5 min ago",
            "market_session": "london"
        }
        overview.append(market)
    
    return {
        "success": True,
        "overview": overview,
        "total_symbols": len(overview),
        "timestamp": datetime.now().isoformat()
    }

# Performance metrics
@app.get("/api/v1/performance/summary")
async def get_performance_summary():
    """Get performance summary"""
    return {
        "success": True,
        "total_return": 1250.00,
        "total_return_pct": 12.5,
        "total_trades": 45,
        "win_rate": 68.9,
        "profit_factor": 1.85,
        "sharpe_ratio": 2.1,
        "max_drawdown": 5.2,
        "timestamp": datetime.now().isoformat()
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "ICT Ultra v2: Algo Forge Edition (Simple Mode)",
        "version": "2.0.0",
        "status": "online",
        "docs": "/docs",
        "health": "/health",
        "note": "Running in simple mode with mock data"
    }

if __name__ == "__main__":
    print("🚀 Starting ICT Ultra v2 Backend (Simple Mode)")
    print("📊 API Documentation: http://localhost:8001/docs")
    print("🔧 Using mock data for demonstration")
    
    uvicorn.run(
        "simple_main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    ) 