"""
Multi-Broker API Endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict, Any
from datetime import datetime

from backend.modules.multi_broker import (
    BrokerManager, BrokerConfig, BrokerType, 
    OrderType, OrderSide, ConnectionStatus
)

router = APIRouter(prefix="/multi-broker", tags=["multi-broker"])

# Initialize service
broker_manager = BrokerManager()

@router.on_event("startup")
async def startup_broker_manager():
    """Start broker manager service"""
    await broker_manager.start_service()

# Broker Management Endpoints
@router.post("/brokers")
async def add_broker(config_data: Dict[str, Any]):
    """Add a new broker configuration"""
    try:
        config = BrokerConfig(**config_data)
        success = await broker_manager.add_broker(config)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to add broker")
        return {"success": True, "broker_id": config.broker_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/brokers/{broker_id}")
async def remove_broker(broker_id: str):
    """Remove a broker"""
    success = await broker_manager.remove_broker(broker_id)
    if not success:
        raise HTTPException(status_code=404, detail="Broker not found")
    return {"success": True}

@router.get("/brokers")
async def get_broker_list():
    """Get list of all configured brokers"""
    brokers = broker_manager.get_broker_list()
    return {"brokers": brokers, "count": len(brokers)}

@router.get("/brokers/{broker_id}/status")
async def get_broker_status(broker_id: str):
    """Get broker connection status"""
    connection = broker_manager.connections.get(broker_id)
    if not connection:
        raise HTTPException(status_code=404, detail="Broker not found")
    
    return {
        "broker_id": broker_id,
        "status": connection.status,
        "connected_at": connection.connected_at,
        "last_ping": connection.last_ping,
        "ping_latency": connection.ping_latency,
        "account_info": {
            "account_id": connection.account_id,
            "currency": connection.account_currency,
            "balance": connection.balance,
            "equity": connection.equity,
            "margin": connection.margin,
            "free_margin": connection.free_margin
        },
        "statistics": {
            "uptime_percentage": connection.uptime_percentage,
            "total_orders": connection.total_orders,
            "total_trades": connection.total_trades,
            "error_count": connection.error_count
        }
    }

# Connection Management Endpoints
@router.post("/brokers/{broker_id}/connect")
async def connect_broker(broker_id: str):
    """Connect to a broker"""
    success = await broker_manager.connect_broker(broker_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to connect to broker")
    return {"success": True}

@router.post("/brokers/{broker_id}/disconnect")
async def disconnect_broker(broker_id: str):
    """Disconnect from a broker"""
    success = await broker_manager.disconnect_broker(broker_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to disconnect from broker")
    return {"success": True}

@router.get("/connections/status")
async def get_all_connection_status():
    """Get connection status for all brokers"""
    status = broker_manager.get_connection_status()
    return {"connections": status}

# Trading Endpoints
@router.post("/orders")
async def place_order(
    broker_id: str,
    symbol: str,
    side: OrderSide,
    order_type: OrderType,
    quantity: float,
    price: Optional[float] = None,
    stop_loss: Optional[float] = None,
    take_profit: Optional[float] = None
):
    """Place an order through specified broker"""
    try:
        order = await broker_manager.place_order(
            broker_id=broker_id,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_loss=stop_loss,
            take_profit=take_profit
        )
        
        if not order:
            raise HTTPException(status_code=400, detail="Failed to place order")
            
        return order.dict()
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/orders/best-broker")
async def place_order_on_best_broker(
    symbol: str,
    side: OrderSide,
    order_type: OrderType,
    quantity: float,
    price: Optional[float] = None,
    stop_loss: Optional[float] = None,
    take_profit: Optional[float] = None
):
    """Place order on the best available broker"""
    try:
        order = await broker_manager.place_order_on_best_broker(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_loss=stop_loss,
            take_profit=take_profit
        )
        
        if not order:
            raise HTTPException(status_code=400, detail="No suitable broker found")
            
        return order.dict()
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/orders/{broker_id}/{order_id}")
async def cancel_order(broker_id: str, order_id: str):
    """Cancel an order"""
    success = await broker_manager.cancel_order(broker_id, order_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to cancel order")
    return {"success": True}

@router.delete("/positions/{broker_id}/{position_id}")
async def close_position(broker_id: str, position_id: str):
    """Close a position"""
    success = await broker_manager.close_position(broker_id, position_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to close position")
    return {"success": True}

# Data Retrieval Endpoints
@router.get("/positions")
async def get_all_positions():
    """Get positions from all connected brokers"""
    positions = await broker_manager.get_all_positions()
    return {"positions": positions}

@router.get("/orders")
async def get_all_orders():
    """Get orders from all connected brokers"""
    orders = await broker_manager.get_all_orders()
    return {"orders": orders}

@router.get("/market-data/{symbol}")
async def get_market_data(symbol: str, broker_id: Optional[str] = None):
    """Get market data for symbol from brokers"""
    market_data = await broker_manager.get_market_data(symbol, broker_id)
    return {"symbol": symbol, "data": market_data}

@router.get("/best-price/{symbol}")
async def get_best_price(symbol: str, side: OrderSide):
    """Get best price across all brokers"""
    best_price = await broker_manager.get_best_price(symbol, side)
    if not best_price:
        raise HTTPException(status_code=404, detail="No price data available")
    return best_price

@router.get("/account-info/{broker_id}")
async def get_account_info(broker_id: str):
    """Get account information from broker"""
    account_info = await broker_manager.get_account_info(broker_id)
    if not account_info:
        raise HTTPException(status_code=404, detail="Account info not available")
    return account_info.dict()

@router.get("/symbols/{broker_id}")
async def get_symbols(broker_id: str):
    """Get available symbols from broker"""
    symbols = await broker_manager.get_symbols(broker_id)
    return {"symbols": symbols, "count": len(symbols)}

# Performance and Analytics Endpoints
@router.get("/performance")
async def get_performance_stats():
    """Get performance statistics for all brokers"""
    stats = broker_manager.get_performance_stats()
    return {"performance": stats}

@router.get("/analytics/comparison")
async def get_broker_comparison():
    """Get broker comparison analytics"""
    brokers = broker_manager.get_broker_list()
    performance = broker_manager.get_performance_stats()
    
    comparison = []
    for broker in brokers:
        broker_id = broker["broker_id"]
        perf = performance.get(broker_id, {})
        
        comparison.append({
            "broker_id": broker_id,
            "name": broker["name"],
            "type": broker["type"],
            "status": broker["status"],
            "uptime": perf.get("uptime_percentage", 0),
            "avg_latency": perf.get("avg_latency", 0),
            "total_orders": perf.get("total_orders", 0),
            "total_trades": perf.get("total_trades", 0),
            "error_count": perf.get("error_count", 0),
            "supports": {
                "forex": broker["supports_forex"],
                "crypto": broker["supports_crypto"],
                "stocks": broker["supports_stocks"]
            }
        })
    
    return {"comparison": comparison}

@router.get("/analytics/spread-comparison/{symbol}")
async def get_spread_comparison(symbol: str):
    """Get spread comparison across brokers for a symbol"""
    market_data = await broker_manager.get_market_data(symbol)
    
    spreads = []
    for broker_id, data in market_data.items():
        if data.bid and data.ask:
            spread = data.ask - data.bid
            spread_pips = spread * 10000  # Assuming 4-digit pricing
            
            spreads.append({
                "broker_id": broker_id,
                "bid": data.bid,
                "ask": data.ask,
                "spread": spread,
                "spread_pips": spread_pips,
                "timestamp": data.timestamp
            })
    
    # Sort by spread (best first)
    spreads.sort(key=lambda x: x["spread"])
    
    return {
        "symbol": symbol,
        "spreads": spreads,
        "best_broker": spreads[0]["broker_id"] if spreads else None
    }

# Configuration Endpoints
@router.get("/broker-types")
async def get_supported_broker_types():
    """Get list of supported broker types"""
    return {
        "broker_types": [
            {
                "type": BrokerType.MT5,
                "name": "MetaTrader 5",
                "supports_forex": True,
                "supports_crypto": True,
                "supports_stocks": True,
                "requires_credentials": ["login", "password", "server"]
            },
            {
                "type": BrokerType.BINANCE,
                "name": "Binance",
                "supports_forex": False,
                "supports_crypto": True,
                "supports_stocks": False,
                "requires_credentials": ["api_key", "api_secret"]
            },
            {
                "type": BrokerType.BYBIT,
                "name": "Bybit",
                "supports_forex": False,
                "supports_crypto": True,
                "supports_stocks": False,
                "requires_credentials": ["api_key", "api_secret"]
            },
            {
                "type": BrokerType.INTERACTIVE_BROKERS,
                "name": "Interactive Brokers",
                "supports_forex": True,
                "supports_crypto": False,
                "supports_stocks": True,
                "requires_credentials": ["api_key", "api_secret"]
            },
            {
                "type": BrokerType.OANDA,
                "name": "OANDA",
                "supports_forex": True,
                "supports_crypto": False,
                "supports_stocks": False,
                "requires_credentials": ["api_key", "account_id"]
            }
        ]
    }

@router.get("/order-types")
async def get_supported_order_types():
    """Get list of supported order types"""
    return {
        "order_types": [
            {"type": OrderType.MARKET, "name": "Market Order", "description": "Execute immediately at current market price"},
            {"type": OrderType.LIMIT, "name": "Limit Order", "description": "Execute at specified price or better"},
            {"type": OrderType.STOP, "name": "Stop Order", "description": "Execute when price reaches stop level"},
            {"type": OrderType.STOP_LIMIT, "name": "Stop Limit Order", "description": "Combination of stop and limit orders"},
            {"type": OrderType.TRAILING_STOP, "name": "Trailing Stop", "description": "Stop order that follows price movement"}
        ],
        "order_sides": [
            {"side": OrderSide.BUY, "name": "Buy", "description": "Open long position"},
            {"side": OrderSide.SELL, "name": "Sell", "description": "Open short position"}
        ]
    } 