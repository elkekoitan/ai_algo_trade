"""
Sanal-Süpürge Core Service

Main service managing grid trading strategy execution.
Handles session lifecycle, grid calculations, and real-time trading logic.
"""

import asyncio
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
import json

from ...core.enhanced_event_bus import EventBus
from ...mt5_integration.service import MT5Service
from .models import (
    GridConfig, TradingSession, PerformanceMetrics, 
    GridLevel, CopyTradeSignal, GridCalculationResult
)
from .grid_calculator import GridCalculator
from .copy_trading_service import CopyTradingService, CopyAccount


class SanalSupurgeService:
    """Main service for Sanal-Süpürge grid trading strategy"""
    
    def __init__(self, event_bus: EventBus, mt5_service: MT5Service):
        self.event_bus = event_bus
        self.mt5_service = mt5_service
        self.grid_calculator = GridCalculator()
        self.copy_trading_service = CopyTradingService(event_bus)
        self.logger = logging.getLogger(__name__)
        
        # Active sessions storage
        self.active_sessions: Dict[str, TradingSession] = {}
        
        # Performance tracking
        self.performance_metrics: Dict[str, PerformanceMetrics] = {}
        
        # Real-time price tracking
        self.current_prices: Dict[str, float] = {}
        
        # Configuration
        self.price_update_interval = 0.1  # 100ms for scalping
        self.session_check_interval = 1.0  # 1 second
        
        # Setup event listeners
        self._setup_event_listeners()
        
        # Background tasks
        self._price_monitor_task = None
        self._session_monitor_task = None
        
        # Initialize copy accounts
        self._initialize_copy_accounts()
    
    def _setup_event_listeners(self):
        """Setup event bus listeners"""
        self.event_bus.subscribe("mt5.price.updated", self._handle_price_update)
        self.event_bus.subscribe("mt5.order.executed", self._handle_order_executed)
        self.event_bus.subscribe("mt5.position.closed", self._handle_position_closed)
        self.event_bus.subscribe("sanal_supurge.session.start", self._handle_session_start)
        self.event_bus.subscribe("sanal_supurge.session.stop", self._handle_session_stop)
    
    def _initialize_copy_accounts(self):
        """Initialize copy trading accounts from memory"""
        # Master account (source)
        master_account = CopyAccount(
            account_id="master",
            login="25201110",
            password="e|([rXU1IsiM",
            server="Tickmill-Demo",
            is_active=True,
            risk_multiplier=1.0
        )
        
        # Copy accounts
        copy_account_1 = CopyAccount(
            account_id="copy_1",
            login="25216036", 
            password="oB9UY1&,B=^9",
            server="Tickmill-Demo",
            is_active=True,
            risk_multiplier=1.0
        )
        
        copy_account_2 = CopyAccount(
            account_id="copy_2",
            login="25216037",
            password="L[.Sdo4QRxx2", 
            server="Tickmill-Demo",
            is_active=True,
            risk_multiplier=1.0
        )
        
        # Register accounts
        self.copy_trading_service.register_copy_account(master_account)
        self.copy_trading_service.register_copy_account(copy_account_1)
        self.copy_trading_service.register_copy_account(copy_account_2)
    
    async def start_service(self):
        """Start the Sanal-Süpürge service"""
        self.logger.info("Starting Sanal-Süpürge service...")
        
        # Start copy trading service
        await self.copy_trading_service.start_service()
        
        # Start background monitoring tasks
        if self._price_monitor_task is None or self._price_monitor_task.done():
            self._price_monitor_task = asyncio.create_task(self._monitor_prices())
        
        if self._session_monitor_task is None or self._session_monitor_task.done():
            self._session_monitor_task = asyncio.create_task(self._monitor_sessions())
        
        self.logger.info("Sanal-Süpürge service started successfully")
    
    async def stop_service(self):
        """Stop the Sanal-Süpürge service"""
        self.logger.info("Stopping Sanal-Süpürge service...")
        
        # Stop copy trading service
        await self.copy_trading_service.stop_service()
        
        # Stop background tasks
        if self._price_monitor_task and not self._price_monitor_task.done():
            self._price_monitor_task.cancel()
        
        if self._session_monitor_task and not self._session_monitor_task.done():
            self._session_monitor_task.cancel()
        
        # Stop all active sessions
        for session_id in list(self.active_sessions.keys()):
            await self.stop_session(session_id)
        
        self.logger.info("Sanal-Süpürge service stopped")
    
    async def create_session(self, config: GridConfig) -> str:
        """Create a new trading session"""
        session_id = str(uuid.uuid4())
        
        session = TradingSession(
            id=session_id,
            config=config,
            is_active=False
        )
        
        self.active_sessions[session_id] = session
        
        self.logger.info(f"Created trading session: {session_id}")
        return session_id
    
    async def start_session(self, session_id: str) -> bool:
        """Start a trading session"""
        if session_id not in self.active_sessions:
            return False
            
        session = self.active_sessions[session_id]
        session.is_active = True
        session.started_at = datetime.now()
        
        self.logger.info(f"Started trading session: {session_id}")
        return True
    
    async def stop_session(self, session_id: str) -> bool:
        """Stop a trading session"""
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        
        if not session.is_active:
            return False  # Already stopped
        
        # Close all open positions for this session
        await self._close_all_session_positions(session)
        
        # Stop session
        session.is_active = False
        session.ended_at = datetime.now()
        
        self.logger.info(f"Stopped trading session: {session_id}")
        
        # Emit event
        self.event_bus.emit("sanal_supurge.session.stopped", {
            "session_id": session_id,
            "symbol": session.config.instrument.symbol,
            "duration_minutes": (session.ended_at - session.started_at).total_seconds() / 60,
            "timestamp": session.ended_at.isoformat()
        })
        
        return True
    
    async def calculate_grid(self, config: GridConfig, current_price: float) -> GridCalculationResult:
        """Calculate grid analysis for given configuration"""
        return self.grid_calculator.calculate_grid(config, current_price)
    
    async def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get current session status"""
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id]
        metrics = self.performance_metrics.get(session_id)
        
        # Get current price
        symbol = session.config.instrument.symbol
        current_price = self.current_prices.get(symbol, 0)
        
        return {
            "session_id": session_id,
            "is_active": session.is_active,
            "started_at": session.started_at.isoformat() if session.started_at else None,
            "symbol": symbol,
            "current_price": current_price,
            "total_buy_orders": session.total_buy_orders,
            "total_sell_orders": session.total_sell_orders,
            "realized_pnl": session.realized_pnl,
            "unrealized_pnl": session.unrealized_pnl,
            "active_buy_levels": len(session.current_buy_levels),
            "active_sell_levels": len(session.current_sell_levels),
            "performance_metrics": metrics.dict() if metrics else None
        }
    
    async def _monitor_prices(self):
        """Monitor price updates for all active sessions"""
        while True:
            try:
                # Get unique symbols from active sessions
                symbols = set()
                for session in self.active_sessions.values():
                    if session.is_active:
                        symbols.add(session.config.instrument.symbol)
                
                # Update prices for all symbols
                for symbol in symbols:
                    try:
                        price_data = await self.mt5_service.get_current_price(symbol)
                        if price_data and price_data.get("success"):
                            bid = price_data.get("bid", 0)
                            ask = price_data.get("ask", 0)
                            current_price = (bid + ask) / 2
                            
                            # Update stored price
                            old_price = self.current_prices.get(symbol)
                            self.current_prices[symbol] = current_price
                            
                            # Emit price update event if price changed
                            if old_price != current_price:
                                self.event_bus.emit("sanal_supurge.price.updated", {
                                    "symbol": symbol,
                                    "price": current_price,
                                    "bid": bid,
                                    "ask": ask,
                                    "timestamp": datetime.now().isoformat()
                                })
                    
                    except Exception as e:
                        self.logger.error(f"Error updating price for {symbol}: {e}")
                
                await asyncio.sleep(self.price_update_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in price monitoring: {e}")
                await asyncio.sleep(1)
    
    async def _monitor_sessions(self):
        """Monitor active sessions for grid triggers and management"""
        while True:
            try:
                for session in list(self.active_sessions.values()):
                    if session.is_active:
                        await self._check_session_triggers(session)
                        await self._update_session_metrics(session)
                
                await asyncio.sleep(self.session_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in session monitoring: {e}")
                await asyncio.sleep(1)
    
    async def _check_session_triggers(self, session: TradingSession):
        """Check for grid level triggers in a session"""
        symbol = session.config.instrument.symbol
        current_price = self.current_prices.get(symbol)
        
        if current_price is None:
            return
        
        # Check buy levels
        if session.config.buy_enabled and session.buy_reference_price:
            await self._check_buy_levels(session, current_price)
        
        # Check sell levels  
        if session.config.sell_enabled and session.sell_reference_price:
            await self._check_sell_levels(session, current_price)
        
        # Check TP/SL levels
        await self._check_tp_sl_levels(session, current_price)
    
    async def _check_buy_levels(self, session: TradingSession, current_price: float):
        """Check buy grid level triggers"""
        # Implementation would check each buy level and trigger orders
        # This is simplified - full implementation would match HAYALETV6 logic
        pass
    
    async def _check_sell_levels(self, session: TradingSession, current_price: float):
        """Check sell grid level triggers"""
        # Implementation would check each sell level and trigger orders
        # This is simplified - full implementation would match HAYALETV6 logic
        pass
    
    async def _check_tp_sl_levels(self, session: TradingSession, current_price: float):
        """Check take profit and stop loss levels"""
        # Implementation would check TP/SL triggers and close positions
        pass
    
    def _validate_session_config(self, config: GridConfig) -> bool:
        """Validate session configuration"""
        if not config.grid_levels:
            return False
        
        if config.risk_settings.balance <= 0:
            return False
        
        if not config.instrument.symbol:
            return False
        
        return True
    
    async def _get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for symbol"""
        try:
            price_data = await self.mt5_service.get_current_price(symbol)
            if price_data and price_data.get("success"):
                bid = price_data.get("bid", 0)
                ask = price_data.get("ask", 0)
                return (bid + ask) / 2
        except Exception as e:
            self.logger.error(f"Error getting price for {symbol}: {e}")
        
        return None
    
    async def _initialize_grid_levels(self, session: TradingSession, current_price: float):
        """Initialize grid levels for session"""
        # Calculate optimized grid levels
        calculation_result = await self.calculate_grid(session.config, current_price)
        
        # Set TP/SL levels based on first level
        if session.config.grid_levels:
            first_level = session.config.grid_levels[0]
            tick_size = session.config.instrument.tick_size
            
            # Buy TP/SL
            session.buy_tp_level = current_price + (first_level.tp_points * tick_size)
            session.buy_sl_level = current_price - (first_level.sl_points * tick_size)
            
            # Sell TP/SL  
            session.sell_tp_level = current_price - (first_level.tp_points * tick_size)
            session.sell_sl_level = current_price + (first_level.sl_points * tick_size)
    
    async def _close_all_session_positions(self, session: TradingSession):
        """Close all positions for a session"""
        symbol = session.config.instrument.symbol
        comment = session.config.position_comment
        
        try:
            await self.mt5_service.close_all_positions(symbol=symbol, comment=comment)
        except Exception as e:
            self.logger.error(f"Error closing positions for session {session.id}: {e}")
    
    async def _update_session_metrics(self, session: TradingSession):
        """Update performance metrics for session"""
        if session.id not in self.performance_metrics:
            return
        
        metrics = self.performance_metrics[session.id]
        metrics.timestamp = datetime.now()
        
        # Update basic metrics
        metrics.active_buy_levels = len(session.current_buy_levels)
        metrics.active_sell_levels = len(session.current_sell_levels)
        metrics.total_pnl = session.realized_pnl + session.unrealized_pnl
    
    async def _handle_price_update(self, data: Dict[str, Any]):
        """Handle price update event"""
        symbol = data.get("symbol")
        price = data.get("price")
        
        if symbol and price:
            self.current_prices[symbol] = price
    
    async def _handle_order_executed(self, data: Dict[str, Any]):
        """Handle order executed event"""
        self.logger.debug(f"Order executed: {data}")
    
    async def _handle_position_closed(self, data: Dict[str, Any]):
        """Handle position closed event"""
        self.logger.debug(f"Position closed: {data}")
    
    async def _handle_session_start(self, data: Dict[str, Any]):
        """Handle session start event"""
        session_id = data.get("session_id")
        if session_id:
            await self.start_session(session_id)
    
    async def _handle_session_stop(self, data: Dict[str, Any]):
        """Handle session stop event"""
        session_id = data.get("session_id")
        if session_id:
            await self.stop_session(session_id) 