"""
MT5 service for connection management and trading operations.
"""

import MetaTrader5 as mt5
from typing import Optional, List, Dict, Any
import asyncio
from datetime import datetime
import pandas as pd

from backend.core.logger import setup_logger
from backend.core.events import event_bus, Event, EventTypes
from .models import (
    MT5Config, SymbolInfo, AccountInfo, 
    OrderRequest, OrderResult, OrderType
)

logger = setup_logger("mt5_service")


class MT5Service:
    """
    Service for handling all MT5 operations.
    """
    
    def __init__(self, config: MT5Config):
        self.config = config
        self._connected = False
        self._account_info: Optional[AccountInfo] = None
        
    async def connect(self) -> bool:
        """
        Connect to MT5 terminal.
        """
        try:
            # Initialize MT5
            if not mt5.initialize():
                logger.error("MT5 initialization failed")
                return False
                
            # Login to account
            if not mt5.login(
                login=self.config.login,
                password=self.config.password,
                server=self.config.server,
                timeout=self.config.timeout
            ):
                logger.error(f"MT5 login failed: {mt5.last_error()}")
                mt5.shutdown()
                return False
                
            self._connected = True
            logger.info(f"Connected to MT5: {self.config.server} (Login: {self.config.login})")
            
            # Emit connection event
            await event_bus.emit_async(
                Event(EventTypes.MT5_CONNECTED, {
                    "login": self.config.login,
                    "server": self.config.server
                })
            )
            
            # Load account info
            await self.refresh_account_info()
            
            return True
            
        except Exception as e:
            logger.error(f"MT5 connection error: {e}")
            return False
            
    async def disconnect(self):
        """
        Disconnect from MT5 terminal.
        """
        if self._connected:
            mt5.shutdown()
            self._connected = False
            logger.info("Disconnected from MT5")
            
            # Emit disconnection event
            await event_bus.emit_async(
                Event(EventTypes.MT5_DISCONNECTED, {})
            )
            
    @property
    def is_connected(self) -> bool:
        """Check if connected to MT5."""
        return self._connected and mt5.terminal_info() is not None
        
    async def refresh_account_info(self) -> Optional[AccountInfo]:
        """
        Refresh account information.
        """
        if not self.is_connected:
            return None
            
        info = mt5.account_info()
        if info is None:
            return None
            
        self._account_info = AccountInfo(
            login=info.login,
            balance=info.balance,
            equity=info.equity,
            margin=info.margin,
            margin_free=info.margin_free,
            margin_level=info.margin_level if info.margin_level else 0,
            profit=info.profit,
            leverage=info.leverage,
            currency=info.currency,
            server=info.server,
            company=info.company
        )
        
        return self._account_info
        
    async def get_symbol_info(self, symbol: str) -> Optional[SymbolInfo]:
        """
        Get symbol information.
        """
        if not self.is_connected:
            return None
            
        info = mt5.symbol_info(symbol)
        if info is None:
            return None
            
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            return None
            
        return SymbolInfo(
            name=info.name,
            point=info.point,
            digits=info.digits,
            spread=info.spread,
            bid=tick.bid,
            ask=tick.ask,
            volume_min=info.volume_min,
            volume_max=info.volume_max,
            volume_step=info.volume_step,
            trade_mode=info.trade_mode
        )
        
    async def get_rates(
        self, 
        symbol: str, 
        timeframe: int, 
        count: int = 100
    ) -> Optional[pd.DataFrame]:
        """
        Get historical rates for a symbol.
        
        Args:
            symbol: Symbol name
            timeframe: MT5 timeframe constant
            count: Number of bars to retrieve
            
        Returns:
            DataFrame with OHLCV data
        """
        if not self.is_connected:
            return None
            
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
        if rates is None:
            return None
            
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df
        
    async def place_order(self, request: OrderRequest) -> OrderResult:
        """
        Place an order.
        """
        if not self.is_connected:
            return OrderResult(
                success=False,
                comment="Not connected to MT5"
            )
            
        # Get symbol info for price
        symbol_info = await self.get_symbol_info(request.symbol)
        if not symbol_info:
            return OrderResult(
                success=False,
                comment="Symbol not found"
            )
            
        # Set price if not provided
        if request.price is None:
            if request.order_type in [OrderType.BUY, OrderType.BUY_STOP]:
                request.price = symbol_info.ask
            else:
                request.price = symbol_info.bid
                
        # Convert to MT5 request
        mt5_request = request.to_mt5_request()
        
        # Send order
        result = mt5.order_send(mt5_request)
        
        if result is None:
            return OrderResult(
                success=False,
                comment="Order send failed"
            )
            
        order_result = OrderResult(
            success=result.retcode == 10009,  # TRADE_RETCODE_DONE
            order=result.order if hasattr(result, 'order') else None,
            deal=result.deal if hasattr(result, 'deal') else None,
            volume=result.volume if hasattr(result, 'volume') else None,
            price=result.price if hasattr(result, 'price') else None,
            comment=result.comment if hasattr(result, 'comment') else None,
            request_id=result.request_id if hasattr(result, 'request_id') else None,
            retcode=result.retcode if hasattr(result, 'retcode') else None
        )
        
        # Log result
        if order_result.success:
            logger.info(f"Order placed successfully: {order_result.order}")
            
            # Emit order placed event
            await event_bus.emit_async(
                Event(EventTypes.ORDER_PLACED, {
                    "order_id": order_result.order,
                    "symbol": request.symbol,
                    "type": request.order_type.value,
                    "volume": order_result.volume,
                    "price": order_result.price
                })
            )
        else:
            logger.error(
                f"Order failed: {order_result.error_description} "
                f"(retcode: {order_result.retcode})"
            )
            
        return order_result
        
    async def get_positions(self) -> List[Dict[str, Any]]:
        """
        Get all open positions.
        """
        if not self.is_connected:
            return []
            
        positions = mt5.positions_get()
        if positions is None:
            return []
            
        return [
            {
                "ticket": pos.ticket,
                "symbol": pos.symbol,
                "type": "BUY" if pos.type == 0 else "SELL",
                "volume": pos.volume,
                "price": pos.price_open,
                "sl": pos.sl,
                "tp": pos.tp,
                "profit": pos.profit,
                "swap": pos.swap,
                "commission": pos.commission,
                "magic": pos.magic,
                "comment": pos.comment,
                "time": datetime.fromtimestamp(pos.time)
            }
            for pos in positions
        ]
        
    async def close_position(self, ticket: int) -> bool:
        """
        Close a position by ticket.
        """
        if not self.is_connected:
            return False
            
        position = mt5.positions_get(ticket=ticket)
        if not position:
            logger.error(f"Position {ticket} not found")
            return False
            
        pos = position[0]
        
        # Create close request
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "position": ticket,
            "symbol": pos.symbol,
            "volume": pos.volume,
            "type": mt5.ORDER_TYPE_SELL if pos.type == 0 else mt5.ORDER_TYPE_BUY,
            "deviation": 20,
            "magic": self.config.login,
            "comment": f"Close #{ticket}"
        }
        
        result = mt5.order_send(request)
        
        if result and result.retcode == 10009:
            logger.info(f"Position {ticket} closed successfully")
            
            # Emit position closed event
            await event_bus.emit_async(
                Event(EventTypes.POSITION_CLOSED, {
                    "ticket": ticket,
                    "symbol": pos.symbol,
                    "profit": pos.profit
                })
            )
            return True
        else:
            logger.error(f"Failed to close position {ticket}")
            return False 