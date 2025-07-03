"""
High-Speed Copy Trading Service for Sanal-Süpürge

Optimized for scalping with ultra-low latency signal processing.
Handles HAYALETV6 EA signals and distributes to copy accounts.
"""

import asyncio
import time
import uuid
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime, timedelta
import json
import logging
from dataclasses import dataclass, asdict

from ...core.enhanced_event_bus import EventBus
from ...mt5_integration.service import MT5Service
from .models import CopyTradeSignal, TradingSession, GridLevel


@dataclass
class CopyAccount:
    """Copy trading account configuration"""
    account_id: str
    login: str
    password: str
    server: str
    is_active: bool = True
    risk_multiplier: float = 1.0
    max_lot_multiplier: float = 1.0
    allowed_symbols: List[str] = None
    
    def __post_init__(self):
        if self.allowed_symbols is None:
            self.allowed_symbols = []


class CopyTradingService:
    """Ultra-fast copy trading service optimized for scalping"""
    
    def __init__(self, event_bus: EventBus, mt5_service: MT5Service):
        self.event_bus = event_bus
        self.mt5_service = mt5_service
        self.logger = logging.getLogger(__name__)
        
        # Copy accounts registry
        self.copy_accounts: Dict[str, CopyAccount] = {}
        
        # Active sessions tracking
        self.active_sessions: Dict[str, TradingSession] = {}
        
        # Signal queue for high-speed processing
        self.signal_queue = asyncio.Queue(maxsize=1000)
        
        # Performance metrics
        self.execution_times: List[float] = []
        self.failed_executions: int = 0
        self.successful_executions: int = 0
        
        # Configuration
        self.max_execution_time_ms = 50  # Target max 50ms execution
        self.signal_batch_size = 10
        self.retry_attempts = 3
        self.retry_delay_ms = 10
        
        # Event subscriptions
        self._setup_event_listeners()
        
        # Start signal processor
        self._processing_task = None
    
    def _setup_event_listeners(self):
        """Setup event bus listeners for trading signals"""
        self.event_bus.subscribe("sanal_supurge.signal.created", self._handle_signal_created)
        self.event_bus.subscribe("sanal_supurge.level.triggered", self._handle_level_triggered)
        self.event_bus.subscribe("sanal_supurge.position.closed", self._handle_position_closed)
        self.event_bus.subscribe("mt5.order.executed", self._handle_order_executed)
        self.event_bus.subscribe("mt5.order.failed", self._handle_order_failed)
    
    async def start_service(self):
        """Start the copy trading service"""
        if self._processing_task is None or self._processing_task.done():
            self._processing_task = asyncio.create_task(self._process_signals())
            self.logger.info("Copy trading service started")
    
    async def stop_service(self):
        """Stop the copy trading service"""
        if self._processing_task and not self._processing_task.done():
            self._processing_task.cancel()
            try:
                await self._processing_task
            except asyncio.CancelledError:
                pass
        self.logger.info("Copy trading service stopped")
    
    def register_copy_account(self, account: CopyAccount):
        """Register a new copy trading account"""
        self.copy_accounts[account.account_id] = account
        self.logger.info(f"Registered copy account: {account.account_id}")
        
        # Emit event
        self.event_bus.emit("copy_trading.account.registered", {
            "account_id": account.account_id,
            "login": account.login,
            "server": account.server
        })
    
    def unregister_copy_account(self, account_id: str):
        """Unregister a copy trading account"""
        if account_id in self.copy_accounts:
            del self.copy_accounts[account_id]
            self.logger.info(f"Unregistered copy account: {account_id}")
            
            # Emit event
            self.event_bus.emit("copy_trading.account.unregistered", {
                "account_id": account_id
            })
    
    async def create_signal(
        self,
        source_account: str,
        symbol: str,
        action: str,
        order_type: str,
        lot_size: float,
        entry_price: float,
        level: int
    ) -> str:
        """Create a new copy trading signal"""
        
        signal = CopyTradeSignal(
            signal_id=str(uuid.uuid4()),
            source_account=source_account,
            symbol=symbol,
            action=action,
            order_type=order_type,
            lot_size=lot_size,
            entry_price=entry_price,
            level=level,
            position_comment="HayaletSüpürge",
            timestamp=datetime.now()
        )
        
        await self.signal_queue.put(signal)
        return signal.signal_id
    
    async def _process_signals(self):
        """Main signal processing loop - optimized for speed"""
        while True:
            try:
                # Process signals in batches for efficiency
                signals = []
                
                # Collect batch of signals
                try:
                    # Get first signal (blocks if queue empty)
                    signal = await self.signal_queue.get()
                    signals.append(signal)
                    
                    # Get additional signals without blocking
                    for _ in range(self.signal_batch_size - 1):
                        try:
                            signal = self.signal_queue.get_nowait()
                            signals.append(signal)
                        except asyncio.QueueEmpty:
                            break
                
                except asyncio.CancelledError:
                    break
                
                # Process batch
                if signals:
                    await self._process_signal_batch(signals)
                
            except Exception as e:
                self.logger.error(f"Error in signal processing loop: {e}")
                await asyncio.sleep(0.001)  # Minimal delay before retry
    
    async def _process_signal_batch(self, signals: List[CopyTradeSignal]):
        """Process a batch of signals efficiently"""
        start_time = time.perf_counter()
        
        # Group signals by symbol for optimization
        signals_by_symbol = {}
        for signal in signals:
            if signal.symbol not in signals_by_symbol:
                signals_by_symbol[signal.symbol] = []
            signals_by_symbol[signal.symbol].append(signal)
        
        # Process each symbol group
        tasks = []
        for symbol, symbol_signals in signals_by_symbol.items():
            task = asyncio.create_task(self._process_symbol_signals(symbol, symbol_signals))
            tasks.append(task)
        
        # Wait for all symbol groups to complete
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Record processing time
        processing_time = (time.perf_counter() - start_time) * 1000
        self.execution_times.append(processing_time)
        
        # Keep only recent execution times (for performance monitoring)
        if len(self.execution_times) > 1000:
            self.execution_times = self.execution_times[-100:]
        
        self.logger.debug(f"Processed batch of {len(signals)} signals in {processing_time:.2f}ms")
    
    async def _process_symbol_signals(self, symbol: str, signals: List[CopyTradeSignal]):
        """Process signals for a specific symbol"""
        
        for signal in signals:
            start_time = time.perf_counter()
            
            try:
                # Execute signal on all eligible copy accounts
                execution_tasks = []
                
                for account in self.copy_accounts.values():
                    if not account.is_active:
                        continue
                    
                    if account.allowed_symbols and symbol not in account.allowed_symbols:
                        continue
                    
                    task = asyncio.create_task(
                        self._execute_signal_on_account(signal, account)
                    )
                    execution_tasks.append(task)
                
                # Execute on all accounts concurrently
                if execution_tasks:
                    results = await asyncio.gather(*execution_tasks, return_exceptions=True)
                    
                    # Process results
                    successful = 0
                    failed = 0
                    
                    for result in results:
                        if isinstance(result, Exception):
                            failed += 1
                            self.logger.error(f"Signal execution failed: {result}")
                        else:
                            successful += 1
                    
                    # Update metrics
                    self.successful_executions += successful
                    self.failed_executions += failed
                    
                    # Mark signal as executed
                    signal.executed = True
                    signal.execution_time = datetime.now()
                    signal.execution_latency_ms = (time.perf_counter() - start_time) * 1000
                    
                    # Emit completion event
                    self.event_bus.emit("copy_trading.signal.executed", {
                        "signal_id": signal.signal_id,
                        "successful_copies": successful,
                        "failed_copies": failed,
                        "latency_ms": signal.execution_latency_ms
                    })
                
            except Exception as e:
                signal.error_message = str(e)
                self.logger.error(f"Error processing signal {signal.signal_id}: {e}")
    
    async def _execute_signal_on_account(self, signal: CopyTradeSignal, account: CopyAccount):
        """Execute a signal on a specific copy account"""
        
        # Calculate adjusted lot size
        adjusted_lot_size = self._calculate_adjusted_lot_size(signal.lot_size, account)
        
        # Prepare order parameters
        order_params = {
            "symbol": signal.symbol,
            "order_type": signal.order_type,
            "lot_size": adjusted_lot_size,
            "price": signal.entry_price,
            "sl": signal.stop_loss,
            "tp": signal.take_profit,
            "comment": f"{signal.position_comment}_L{signal.level}_{account.account_id}",
            "account_login": account.login
        }
        
        # Execute with retry logic
        for attempt in range(self.retry_attempts):
            try:
                if signal.action == "open":
                    result = await self.mt5_service.place_order_async(**order_params)
                elif signal.action == "close":
                    result = await self.mt5_service.close_position_async(
                        symbol=signal.symbol,
                        comment=signal.position_comment,
                        account_login=account.login
                    )
                elif signal.action == "modify":
                    result = await self.mt5_service.modify_position_async(
                        symbol=signal.symbol,
                        new_sl=signal.stop_loss,
                        new_tp=signal.take_profit,
                        account_login=account.login
                    )
                else:
                    raise ValueError(f"Unknown action: {signal.action}")
                
                if result.get("success"):
                    return result
                else:
                    raise Exception(result.get("error", "Unknown execution error"))
                    
            except Exception as e:
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(self.retry_delay_ms / 1000)
                    continue
                else:
                    raise e
    
    def _calculate_adjusted_lot_size(self, base_lot_size: float, account: CopyAccount) -> float:
        """Calculate adjusted lot size for copy account"""
        adjusted_lot = base_lot_size * account.risk_multiplier
        
        # Apply maximum lot multiplier
        if account.max_lot_multiplier > 0:
            max_allowed = base_lot_size * account.max_lot_multiplier
            adjusted_lot = min(adjusted_lot, max_allowed)
        
        # Ensure minimum lot size
        adjusted_lot = max(adjusted_lot, 0.01)
        
        # Round to 2 decimal places
        return round(adjusted_lot, 2)
    
    async def _handle_signal_created(self, data: Dict[str, Any]):
        """Handle signal created event"""
        # This would be called when HAYALETV6 EA creates a signal
        await self.create_signal(
            source_account=data.get("source_account", "master"),
            symbol=data.get("symbol"),
            action="open",
            order_type=data.get("order_type"),
            lot_size=data.get("lot_size"),
            entry_price=data.get("entry_price"),
            level=data.get("level"),
            take_profit=data.get("take_profit"),
            stop_loss=data.get("stop_loss"),
            position_comment=data.get("position_comment", "HayaletSüpürge")
        )
    
    async def _handle_level_triggered(self, data: Dict[str, Any]):
        """Handle grid level triggered event"""
        # Create signal when a grid level is triggered
        await self.create_signal(
            source_account=data.get("source_account", "master"),
            symbol=data.get("symbol"),
            action="open",
            order_type=data.get("direction", "buy"),
            lot_size=data.get("lot_size"),
            entry_price=data.get("current_price"),
            level=data.get("level"),
            take_profit=data.get("take_profit"),
            stop_loss=data.get("stop_loss"),
            position_comment=data.get("position_comment", "HayaletSüpürge")
        )
    
    async def _handle_position_closed(self, data: Dict[str, Any]):
        """Handle position closed event"""
        # Create close signal when positions are closed
        await self.create_signal(
            source_account=data.get("source_account", "master"),
            symbol=data.get("symbol"),
            action="close",
            order_type=data.get("direction", "buy"),
            lot_size=0,  # Not relevant for close
            entry_price=data.get("close_price"),
            level=0,  # Not relevant for close
            position_comment=data.get("position_comment", "HayaletSüpürge")
        )
    
    async def _handle_order_executed(self, data: Dict[str, Any]):
        """Handle order executed event"""
        self.logger.debug(f"Order executed: {data}")
    
    async def _handle_order_failed(self, data: Dict[str, Any]):
        """Handle order failed event"""
        self.logger.warning(f"Order failed: {data}")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get copy trading performance metrics"""
        if self.execution_times:
            avg_execution_time = sum(self.execution_times) / len(self.execution_times)
            max_execution_time = max(self.execution_times)
            min_execution_time = min(self.execution_times)
        else:
            avg_execution_time = max_execution_time = min_execution_time = 0
        
        total_executions = self.successful_executions + self.failed_executions
        success_rate = (self.successful_executions / total_executions * 100) if total_executions > 0 else 0
        
        return {
            "total_copy_accounts": len(self.copy_accounts),
            "active_copy_accounts": len([a for a in self.copy_accounts.values() if a.is_active]),
            "successful_executions": self.successful_executions,
            "failed_executions": self.failed_executions,
            "success_rate_percent": round(success_rate, 2),
            "avg_execution_time_ms": round(avg_execution_time, 2),
            "max_execution_time_ms": round(max_execution_time, 2),
            "min_execution_time_ms": round(min_execution_time, 2),
            "signal_queue_size": self.signal_queue.qsize(),
            "target_execution_time_ms": self.max_execution_time_ms
        } 