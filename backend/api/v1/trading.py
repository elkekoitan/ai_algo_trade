"""
Trading API endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from pydantic import BaseModel, Field

from backend.core.logger import setup_logger
from backend.modules.mt5_integration import MT5Service, OrderRequest, OrderType

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
async def place_order(request: PlaceOrderRequest) -> OrderResponse:
    """
    Place a new trading order.
    """
    try:
        # Get MT5 service from app state (will be injected in main.py)
        from backend.main import get_mt5_service
        mt5_service = await get_mt5_service()
        
        if not mt5_service.is_connected:
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
        result = await mt5_service.place_order(order_req)
        
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
async def get_positions() -> List[Dict[str, Any]]:
    """
    Get all open positions.
    """
    try:
        from backend.main import get_mt5_service
        mt5_service = await get_mt5_service()
        
        if not mt5_service.is_connected:
            raise HTTPException(status_code=503, detail="MT5 not connected")
        
        positions = await mt5_service.get_positions()
        return positions
        
    except Exception as e:
        logger.error(f"Error getting positions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/close_position/{ticket}", response_model=OrderResponse)
async def close_position(ticket: int) -> OrderResponse:
    """
    Close a position by ticket number.
    """
    try:
        from backend.main import get_mt5_service
        mt5_service = await get_mt5_service()
        
        if not mt5_service.is_connected:
            raise HTTPException(status_code=503, detail="MT5 not connected")
        
        success = await mt5_service.close_position(ticket)
        
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
async def get_account_info() -> Dict[str, Any]:
    """
    Get account information.
    """
    try:
        from backend.main import get_mt5_service
        mt5_service = await get_mt5_service()
        
        if not mt5_service.is_connected:
            raise HTTPException(status_code=503, detail="MT5 not connected")
        
        account_info = await mt5_service.refresh_account_info()
        
        if account_info:
            return {
                "login": account_info.login,
                "balance": account_info.balance,
                "equity": account_info.equity,
                "margin": account_info.margin,
                "margin_free": account_info.margin_free,
                "margin_level": account_info.margin_level,
                "profit": account_info.profit,
                "leverage": account_info.leverage,
                "currency": account_info.currency,
                "server": account_info.server,
                "company": account_info.company,
                "margin_used_percent": account_info.margin_used_percent
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to get account info")
            
    except Exception as e:
        logger.error(f"Error getting account info: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 