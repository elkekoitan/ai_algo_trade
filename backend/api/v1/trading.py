"""
Trading API endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Request
from typing import List, Dict, Any
from pydantic import BaseModel, Field

from backend.core.logger import setup_logger
from backend.modules.mt5_integration import MT5Service, OrderRequest, OrderType
from backend.core.unified_trading_engine import UnifiedTradingEngine

logger = setup_logger("api.trading")
router = APIRouter()


class PlaceOrderRequest(BaseModel):
    """Request model for placing an order."""
    symbol: str = Field(..., description="Trading symbol")
    order_type: OrderType = Field(..., description="Order type")
    volume: float = Field(..., gt=0, description="Trade volume")
    price: float | None = Field(None, description="Order price (optional)")
    sl: float | None = Field(None, description="Stop loss")
    tp: float | None = Field(None, description="Take profit")
    magic: int = Field(234000, description="Magic number")
    comment: str = Field("ICT Ultra v2", description="Order comment")


class OrderResponse(BaseModel):
    """Response model for order operations."""
    success: bool
    order_id: int | None = None
    message: str
    details: Dict[str, Any] = {}


@router.post("/place_order", response_model=OrderResponse)
async def place_order(request: PlaceOrderRequest, req: Request) -> OrderResponse:
    """
    Place a new trading order.
    """
    try:
        engine = req.app.state.trading_engine
        if not engine or not engine.connected:
            raise HTTPException(status_code=503, detail="MT5 not connected")
        
        # Create order request
        order_req = OrderRequest(
            symbol=request.symbol,
            order_type=request.order_type,
            volume=request.volume,
            price=request.price,
            sl=request.sl,
            tp=request.tp,
            magic=request.magic,
            comment=request.comment
        )
        
        # Place order
        result = await engine.mt5_service.place_order(order_req)
        
        if result.success:
            return OrderResponse(
                success=True,
                order_id=result.order,
                message="Order placed successfully",
                details={
                    "order": result.order,
                    "deal": result.deal,
                    "volume": result.volume,
                    "price": result.price
                }
            )
        else:
            return OrderResponse(
                success=False,
                message=result.error_description,
                details={"retcode": result.retcode}
            )
            
    except Exception as e:
        logger.error(f"Error placing order: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/positions")
async def get_positions(request: Request) -> List[Dict[str, Any]]:
    """
    Get all open positions.
    """
    try:
        engine = request.app.state.trading_engine
        if not engine or not engine.connected:
            raise HTTPException(status_code=503, detail="MT5 not connected")
        
        positions = await engine.mt5_service.get_positions()
        return positions
        
    except Exception as e:
        logger.error(f"Error getting positions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/close_position/{ticket}", response_model=OrderResponse)
async def close_position(ticket: int, request: Request) -> OrderResponse:
    """
    Close a position by ticket number.
    """
    try:
        engine = request.app.state.trading_engine
        if not engine or not engine.connected:
            raise HTTPException(status_code=503, detail="MT5 not connected")
        
        success = await engine.mt5_service.close_position(ticket)
        
        if success:
            return OrderResponse(
                success=True,
                message=f"Position {ticket} closed successfully"
            )
        else:
            return OrderResponse(
                success=False,
                message=f"Failed to close position {ticket}"
            )
            
    except Exception as e:
        logger.error(f"Error closing position: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/account_info")
async def get_account_info(request: Request) -> Dict[str, Any]:
    """
    Get account information.
    """
    try:
        engine = request.app.state.trading_engine
        if not engine or not engine.connected:
            raise HTTPException(status_code=503, detail="MT5 not connected")
        
        account_info = await engine.mt5_service.get_account_info()
        
        if account_info:
            return account_info
        else:
            raise HTTPException(status_code=500, detail="Failed to get account info")
            
    except Exception as e:
        logger.error(f"Error getting account info: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/account")
async def get_account_simple(request: Request) -> Dict[str, Any]:
    """
    Get account information - alias for frontend compatibility.
    """
    return await get_account_info(request)


@router.post("/trade", response_model=OrderResponse)
async def place_trade(request: PlaceOrderRequest, req: Request) -> OrderResponse:
    """
    Place a new trading order for any available instrument.
    """
    try:
        engine = req.app.state.trading_engine
        if not engine or not engine.connected:
            raise HTTPException(status_code=503, detail="MT5 not connected")
        
        # Create order request
        order_req = OrderRequest(
            symbol=request.symbol,
            order_type=request.order_type,
            volume=request.volume,
            price=request.price,
            sl=request.sl,
            tp=request.tp,
            magic=request.magic,
            comment=f"Trade via ICT Ultra v2: {request.comment}"
        )
        
        # Place order
        result = await engine.mt5_service.place_order(order_req)
        
        if result.success:
            return OrderResponse(
                success=True,
                order_id=result.order,
                message=f"{order_req.order_type.value} order for {order_req.volume} lots of {order_req.symbol} placed successfully.",
                details={
                    "order": result.order,
                    "deal": result.deal,
                    "volume": result.volume,
                    "price": result.price
                }
            )
        else:
            return OrderResponse(
                success=False,
                message=result.error_description,
                details={"retcode": result.retcode}
            )
            
    except Exception as e:
        logger.error(f"Error placing trade: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", summary="Get recent trade history")
async def get_trade_history(request: Request):
    """
    Fetches the recent trading history from the MT5 account.
    """
    try:
        engine = request.app.state.trading_engine
        if not engine or not engine.connected:
            raise HTTPException(status_code=503, detail="MT5 service unavailable")
        
        # 30 günlük geçmişi al
        history = await engine.mt5_service.get_trade_history(days=30)
        return history
    except Exception as e:
        logger.error(f"Error fetching trade history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch trade history") 