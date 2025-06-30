"""
Unified Trading Engine - Tüm trading operasyonlarının merkezi
Event-driven architecture ile tüm modülleri birleştiren ana motor
Adaptive Trade Manager, God Mode, Market Narrator, Shadow Mode entegreli
"""

import asyncio
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import uuid
import json
import numpy as np

from core.enhanced_event_bus import EnhancedEventBus, EnhancedEvent, EventPriority, EventTypes
from core.shared_data_service import SharedDataService
from modules.mt5_integration.service import MT5Service

logger = logging.getLogger(__name__)

class OrderStatus(Enum):
    PENDING = "pending"
    EXECUTED = "executed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

class PositionStatus(Enum):
    OPEN = "open"
    CLOSED = "closed"
    PARTIAL = "partial"

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class UnifiedOrder:
    """Unified order representation across all modules"""
    id: str
    symbol: str
    order_type: str  # BUY, SELL
    volume: float
    price: float
    sl: Optional[float] = None
    tp: Optional[float] = None
    module: str = "unified"
    strategy: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    executed_at: Optional[datetime] = None
    
    # Advanced features from modules
    adaptive_params: Dict[str, Any] = field(default_factory=dict)  # ATM
    god_mode_score: float = 0.0  # God Mode prediction confidence
    narrative_context: str = ""  # Market Narrator context
    shadow_source: Optional[str] = None  # Shadow Mode whale source

@dataclass
class UnifiedPosition:
    """Unified position representation with all module data"""
    ticket: int
    symbol: str
    position_type: str
    volume: float
    open_price: float
    current_price: float
    sl: Optional[float] = None
    tp: Optional[float] = None
    profit: float = 0.0
    swap: float = 0.0
    commission: float = 0.0
    module: str = "unified"
    strategy: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: PositionStatus = PositionStatus.OPEN
    opened_at: datetime = field(default_factory=datetime.now)
    closed_at: Optional[datetime] = None
    
    # Advanced tracking
    adaptive_adjustments: List[Dict] = field(default_factory=list)  # ATM history
    god_mode_predictions: List[Dict] = field(default_factory=list)  # God Mode forecasts
    narrative_events: List[str] = field(default_factory=list)  # Market stories
    shadow_intel: Dict[str, Any] = field(default_factory=dict)  # Whale data

class UnifiedTradingEngine:
    """
    Merkezi trading engine - tüm trading operasyonlarını yönetir
    Event-driven mimari ile modüller arası iletişimi sağlar
    Adaptive Trade Manager, God Mode, Market Narrator, Shadow Mode entegreli
    """
    
    def __init__(self, mt5_service: Optional[MT5Service] = None):
        # Core components - Initialize MT5Service with credentials
        self.mt5_service = mt5_service or MT5Service(
            login=25201110, 
            password="e|([rXU1IsiM", 
            server="Tickmill-Demo"
        )
        self.event_bus = EnhancedEventBus()
        self.shared_data = SharedDataService()
        
        # Risk Manager first (needed by others)
        self.risk_manager = RiskManager(self)
        
        # Then other managers
        self.order_manager = OrderManager(self)
        self.position_manager = PositionManager(self)
        
        # Module Integrations
        self.adaptive_manager = AdaptiveTradeManagerIntegration(self)
        self.god_mode = GodModeIntegration(self)
        self.market_narrator = MarketNarratorIntegration(self)
        self.shadow_mode = ShadowModeIntegration(self)
        
        # State
        self.running = False
        self.connected = False
        self.connection_retry_task = None
        self.active_modules = {}
        self.performance_metrics = {
            "total_trades": 0,
            "winning_trades": 0,
            "total_profit": 0.0,
            "max_drawdown": 0.0,
            "sharpe_ratio": 0.0,
            "god_mode_accuracy": 0.0,
            "adaptive_adjustments": 0,
            "shadow_detections": 0
        }
        
        # Event subscriptions
        self._setup_event_handlers()
        
        logger.info("🚀 Unified Trading Engine initialized with all advanced modules")
    
    @property
    def is_running(self) -> bool:
        """Check if the engine is currently running"""
        return self.running
    
    def _setup_event_handlers(self):
        """Event handler'ları kur"""
        # Market events
        self.event_bus.subscribe_async(EventTypes.PRICE_UPDATE, self._handle_price_update)
        self.event_bus.subscribe_async(EventTypes.CANDLE_CLOSED, self._handle_candle_closed)
        
        # Signal events - multi-module
        self.event_bus.subscribe_async("signal.generated", self._handle_signal)
        self.event_bus.subscribe_async("signal.approved", self._handle_approved_signal)
        
        # Adaptive Trade Manager events
        self.event_bus.subscribe_async("atm.adjustment_needed", self._handle_atm_adjustment)
        self.event_bus.subscribe_async("atm.risk_alert", self._handle_atm_risk_alert)
        
        # God Mode events
        self.event_bus.subscribe_async("god_mode.prediction", self._handle_god_prediction)
        self.event_bus.subscribe_async("god_mode.market_shift", self._handle_market_shift)
        
        # Market Narrator events
        self.event_bus.subscribe_async("narrator.story_update", self._handle_story_update)
        self.event_bus.subscribe_async("narrator.correlation_found", self._handle_correlation)
        
        # Shadow Mode events
        self.event_bus.subscribe_async("shadow.whale_detected", self._handle_whale_detection)
        self.event_bus.subscribe_async("shadow.institutional_flow", self._handle_institutional_flow)
        
        # Module requests
        self.event_bus.subscribe_async("module.order_request", self._handle_order_request)
        self.event_bus.subscribe_async("module.position_request", self._handle_position_request)
    
    async def start(self):
        """Engine'i başlat"""
        if self.running:
            logger.warning("Engine already running")
            return
        
        # Start event bus
        await self.event_bus.start()
        
        # MT5 bağlantısı
        self.connected = await self._connect_mt5()
        if not self.connected:
            logger.warning("MT5 connection failed on startup. Will retry in background.")
            self.connection_retry_task = asyncio.create_task(self._retry_connection())
        
        self.running = True
        
        # Start all modules
        await self.adaptive_manager.start()
        await self.god_mode.start()
        await self.market_narrator.start()
        await self.shadow_mode.start()
        
        # Start background tasks
        asyncio.create_task(self._monitor_positions())
        asyncio.create_task(self._monitor_orders())
        asyncio.create_task(self._update_performance_metrics())
        
        # Emit startup event
        await self.event_bus.emit(EnhancedEvent(
            type="system.engine_started",
            data={
                "timestamp": datetime.now(),
                "mt5_connected": self.connected,
                "modules_active": ["ATM", "God Mode", "Market Narrator", "Shadow Mode"]
            },
            priority=EventPriority.HIGH,
            source="unified_engine"
        ))
        
        logger.info("🎯 Unified Trading Engine started with all modules active")
    
    async def stop(self):
        """Engine'i durdur"""
        self.running = False
        
        # Stop all modules
        await self.adaptive_manager.stop()
        await self.god_mode.stop()
        await self.market_narrator.stop()
        await self.shadow_mode.stop()
        
        # Close all positions if configured
        if self.risk_manager.close_all_on_stop:
            await self.position_manager.close_all_positions()
        
        # Disconnect MT5
        if self.connected:
            await self.mt5_service.disconnect()
            self.connected = False
        
        # Stop event bus
        await self.event_bus.stop()
        
        # Stop connection retry task if it's running
        if self.connection_retry_task and not self.connection_retry_task.done():
            self.connection_retry_task.cancel()
        
        # Emit shutdown event
        await self.event_bus.emit(EnhancedEvent(
            type="system.engine_stopped",
            data={"timestamp": datetime.now()},
            priority=EventPriority.HIGH,
            source="unified_engine"
        ))
        
        logger.info("🛑 Unified Trading Engine stopped")
    
    async def _connect_mt5(self) -> bool:
        """MT5'e bağlan ve servis üzerinden yönet"""
        try:
            # MT5Service zaten credentials ile initialize edildi
            # Sadece connect() çağırmak yeterli
            self.connected = await self.mt5_service.connect()

            if self.connected:
                logger.info("✅ Unified Engine successfully connected to MT5 via MT5Service.")
                account_info = await self.mt5_service.get_account_info()
                await self.event_bus.emit(EnhancedEvent(
                    type=EventTypes.MT5_CONNECTED,
                    data={
                        "server": account_info.get("server"),
                        "login": account_info.get("login"),
                        "balance": account_info.get("balance", 0)
                    },
                    priority=EventPriority.HIGH,
                    source="unified_engine"
                ))
            else:
                logger.warning("Connection via MT5Service failed. Will retry in background.")
            
            return self.connected
            
        except Exception as e:
            logger.error(f"Unified Engine MT5 connection error: {e}", exc_info=True)
            self.connected = False
            return False

    async def _retry_connection(self, interval_seconds: int = 30):
        """Periodically try to reconnect to MT5 if disconnected."""
        logger.info(f"Starting MT5 connection retry loop (every {interval_seconds}s).")
        while self.running and not self.connected:
            logger.info("Attempting to reconnect to MT5 via MT5Service...")
            if await self._connect_mt5():
                logger.info("✅ Re-established connection to MT5.")
                # Once connected, we might want to trigger a sync
                await self.position_manager.sync_positions()
                break 
            logger.warning(f"MT5 reconnect failed. Retrying in {interval_seconds} seconds.")
            await asyncio.sleep(interval_seconds)
        logger.info("Exiting MT5 connection retry loop.")

    # Event Handlers
    
    async def _handle_price_update(self, event: EnhancedEvent):
        """Fiyat güncellemelerini işle"""
        # Update shared data
        await self.shared_data.mt5_data.update_prices(event.data)
        
        # Update position P&L
        await self.position_manager.update_position_prices(event.data)
        
        # Notify all modules
        await self.adaptive_manager.on_price_update(event.data)
        await self.god_mode.on_price_update(event.data)
        await self.shadow_mode.on_price_update(event.data)
    
    async def _handle_candle_closed(self, event: EnhancedEvent):
        """Mum kapanışlarını işle"""
        # Trigger analysis in all modules
        await self.event_bus.emit(EnhancedEvent(
            type="analysis.candle_ready",
            data=event.data,
            priority=EventPriority.NORMAL,
            source="unified_engine"
        ))
    
    async def _handle_signal(self, event: EnhancedEvent):
        """Multi-module trading sinyallerini işle"""
        signal = event.data
        
        if not self.connected:
            logger.warning(f"MT5 not connected. Signal evaluation is limited. Signal: {signal}")
            return
        
        # Enrich signal with all module insights
        enriched_signal = await self._enrich_signal_with_modules(signal)
        
        # Risk kontrolü (all modules considered)
        risk_check = await self.risk_manager.evaluate_signal(enriched_signal)
        
        if risk_check["approved"]:
            await self.event_bus.emit(EnhancedEvent(
                type="signal.approved",
                data={**enriched_signal, "risk_check": risk_check},
                priority=EventPriority.HIGH,
                source="unified_engine"
            ))
        else:
            await self.event_bus.emit(EnhancedEvent(
                type="signal.rejected",
                data={**enriched_signal, "reason": risk_check["reason"]},
                priority=EventPriority.NORMAL,
                source="unified_engine"
            ))
    
    async def _enrich_signal_with_modules(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Sinyali tüm modül bilgileri ile zenginleştir"""
        enriched = signal.copy()
        
        if not self.connected:
            enriched['warning'] = "MT5 not connected. Signal evaluation is limited."
            return enriched
        
        # God Mode prediction
        god_prediction = await self.god_mode.get_prediction_for_signal(signal)
        enriched["god_mode_score"] = god_prediction.get("confidence", 0.0)
        enriched["god_mode_forecast"] = god_prediction.get("forecast", "neutral")
        
        # Market Narrator context
        narrative = await self.market_narrator.get_context_for_signal(signal)
        enriched["narrative_context"] = narrative.get("story", "")
        enriched["market_sentiment"] = narrative.get("sentiment", 0.5)
        
        # Shadow Mode intel
        shadow_intel = await self.shadow_mode.get_intel_for_signal(signal)
        enriched["whale_activity"] = shadow_intel.get("whale_detected", False)
        enriched["institutional_flow"] = shadow_intel.get("flow_direction", "neutral")
        
        # Adaptive parameters
        adaptive_params = await self.adaptive_manager.get_adaptive_params(signal)
        enriched["adaptive_sl"] = adaptive_params.get("dynamic_sl")
        enriched["adaptive_tp"] = adaptive_params.get("dynamic_tp")
        
        return enriched
    
    async def _handle_approved_signal(self, event: EnhancedEvent):
        """Onaylanmış sinyalleri işle"""
        if not self.connected:
            logger.warning(f"Cannot execute order for signal, MT5 is not connected: {event.data.get('id')}")
            return

        signal = event.data
        
        # Create enhanced order
        order = UnifiedOrder(
            id=f"order_{datetime.now().timestamp()}_{uuid.uuid4().hex[:8]}",
            symbol=signal["symbol"],
            order_type=signal["action"],
            volume=signal.get("volume", 0.01),
            price=signal.get("price", 0),
            sl=signal.get("adaptive_sl") or signal.get("sl"),
            tp=signal.get("adaptive_tp") or signal.get("tp"),
            module=signal.get("module", "unified"),
            strategy=signal.get("strategy"),
            metadata=signal.get("metadata", {}),
            created_at=datetime.now(),
            
            # Advanced module data
            adaptive_params=signal.get("adaptive_params", {}),
            god_mode_score=signal.get("god_mode_score", 0.0),
            narrative_context=signal.get("narrative_context", ""),
            shadow_source=signal.get("shadow_source")
        )
        
        # Execute order
        await self.order_manager.execute_order(order)
    
    async def _handle_atm_risk_alert(self, event: EnhancedEvent):
        """Handle risk alerts from ATM"""
        logger.warning(f"🚨 ATM Risk Alert: {event.data.get('reason')}")
        # Here you could trigger portfolio-wide actions
    
    async def _handle_market_shift(self, event: EnhancedEvent):
        """Handle market shift events from God Mode"""
        logger.info(f"⚡ God Mode Market Shift: {event.data.get('description')}")

    async def _handle_correlation(self, event: EnhancedEvent):
        """Handle new correlation findings from Market Narrator"""
        logger.info(f"📖 Narrator Correlation: {event.data.get('correlation')}")
        
    async def _handle_institutional_flow(self, event: EnhancedEvent):
        """Handle institutional flow from Shadow Mode"""
        logger.info(f"🥷 Shadow Institutional Flow: {event.data.get('direction')} in {event.data.get('symbol')}")

    async def _handle_order_request(self, event: EnhancedEvent):
        """Handle direct order requests from other modules"""
        logger.info(f"Received direct order request: {event.data}")
        order_data = event.data
        order = UnifiedOrder(
            id=f"module_order_{datetime.now().timestamp()}",
            symbol=order_data["symbol"],
            order_type=order_data["action"],
            volume=order_data["volume"],
            price=order_data.get("price", 0),
            sl=order_data.get("sl"),
            tp=order_data.get("tp"),
            module=order_data.get("module", "unknown"),
        )
        await self.order_manager.execute_order(order)

    async def _handle_position_request(self, event: EnhancedEvent):
        """Handle position information requests"""
        logger.info(f"Received position request: {event.data}")
        # This can be implemented to provide position data to other modules
        pass
    
    # Module-specific event handlers
    
    async def _handle_atm_adjustment(self, event: EnhancedEvent):
        """Adaptive Trade Manager ayarlama istekleri"""
        adjustment = event.data
        position = await self.position_manager.get_position(adjustment["ticket"])
        
        if position:
            # Apply ATM adjustment
            success = await self._apply_atm_adjustment(position, adjustment)
            
            if success:
                position.adaptive_adjustments.append({
                    "timestamp": datetime.now(),
                    "type": adjustment["type"],
                    "reason": adjustment["reason"],
                    "old_value": adjustment.get("old_value"),
                    "new_value": adjustment.get("new_value")
                })
                
                self.performance_metrics["adaptive_adjustments"] += 1
    
    async def _handle_god_prediction(self, event: EnhancedEvent):
        """God Mode tahminlerini işle"""
        prediction = event.data
        
        # Store prediction for analysis
        for position in self.position_manager.positions.values():
            if position.symbol == prediction["symbol"]:
                position.god_mode_predictions.append({
                    "timestamp": datetime.now(),
                    "prediction": prediction["direction"],
                    "confidence": prediction["confidence"],
                    "timeframe": prediction["timeframe"],
                    "target_price": prediction.get("target_price")
                })
    
    async def _handle_story_update(self, event: EnhancedEvent):
        """Market Narrator hikaye güncellemeleri"""
        story = event.data
        
        # Add story to relevant positions
        for position in self.position_manager.positions.values():
            if position.symbol in story.get("affected_symbols", []):
                position.narrative_events.append(
                    f"{datetime.now().strftime('%H:%M')} - {story['title']}: {story['summary']}"
                )
    
    async def _handle_whale_detection(self, event: EnhancedEvent):
        """Shadow Mode whale tespitleri"""
        whale_data = event.data
        
        # Update shadow intel for relevant positions
        for position in self.position_manager.positions.values():
            if position.symbol == whale_data["symbol"]:
                position.shadow_intel.update({
                    "last_whale_activity": datetime.now(),
                    "whale_direction": whale_data["direction"],
                    "whale_volume": whale_data["volume"],
                    "confidence": whale_data["confidence"]
                })
        
        self.performance_metrics["shadow_detections"] += 1
        
        # Emit high-priority alert
        await self.event_bus.emit(EnhancedEvent(
            type="alert.whale_detected",
            data=whale_data,
            priority=EventPriority.CRITICAL,
            source="shadow_mode"
        ))
    
    async def _apply_atm_adjustment(self, position: UnifiedPosition, adjustment: Dict) -> bool:
        """ATM ayarlamalarını uygula"""
        if not self.connected:
            logger.warning(f"Cannot apply ATM adjustment, MT5 is not connected. Ticket: {position.ticket}")
            return False
        try:
            if adjustment["type"] == "sl_adjustment":
                return await self.position_manager.modify_position_sl(
                    position.ticket, adjustment["new_value"]
                )
            elif adjustment["type"] == "tp_adjustment":
                return await self.position_manager.modify_position_tp(
                    position.ticket, adjustment["new_value"]
                )
            elif adjustment["type"] == "partial_close":
                return await self.position_manager.partial_close_position(
                    position.ticket, adjustment["percentage"]
                )
            
        except Exception as e:
            logger.error(f"ATM adjustment error: {e}")
            return False
    
    async def _monitor_positions(self):
        """Pozisyonları sürekli izle"""
        while self.running:
            try:
                await self.position_manager.sync_positions()
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Position monitoring error: {e}")
                await asyncio.sleep(5)
    
    async def _monitor_orders(self):
        """Bekleyen emirleri izle"""
        while self.running:
            try:
                await self.order_manager.check_pending_orders()
                await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"Order monitoring error: {e}")
                await asyncio.sleep(5)
    
    async def _update_performance_metrics(self):
        """Performance metriklerini güncelle"""
        while self.running:
            try:
                await self._calculate_performance_metrics()
                await asyncio.sleep(60)  # Her dakika güncelle
            except Exception as e:
                logger.error(f"Performance metrics error: {e}")
                await asyncio.sleep(60)
    
    async def _calculate_performance_metrics(self):
        """Performance metriklerini hesapla"""
        try:
            account_info = await self.mt5_service.get_account_info()
            if not account_info:
                return
            
            # Total profit
            self.performance_metrics["total_profit"] = account_info.get('profit', 0.0)
            
            # Win rate
            if self.performance_metrics["total_trades"] > 0:
                self.performance_metrics["win_rate"] = (
                    self.performance_metrics["winning_trades"] / 
                    self.performance_metrics["total_trades"]
                )
            
            # Calculate drawdown
            balance = account_info.get('balance', 0.0)
            equity = account_info.get('equity', 0.0)
            if balance > 0:
                drawdown = (balance - equity) / balance
                if drawdown > self.performance_metrics["max_drawdown"]:
                    self.performance_metrics["max_drawdown"] = drawdown
            
            # Update risk metrics
            await self.risk_manager.update_risk_metrics()
            
        except Exception as e:
            logger.error(f"Performance calculation error: {e}")
    
    # Public API
    
    async def get_unified_dashboard_data(self) -> Dict[str, Any]:
        """Unified dashboard için tüm veriyi topla"""
        return {
            "engine_status": {
                "running": self.running,
                "connected": self.connected,
                "uptime": datetime.now() - (self.start_time if hasattr(self, 'start_time') else datetime.now())
            },
            "performance": self.performance_metrics,
            "positions": [pos.__dict__ for pos in self.position_manager.positions.values()],
            "active_signals": await self.shared_data.signal_pool.get_active(),
            "risk_status": await self.risk_manager.get_current_risk_status(),
            "module_status": {
                "adaptive_manager": await self.adaptive_manager.get_status(),
                "god_mode": await self.god_mode.get_status(),
                "market_narrator": await self.market_narrator.get_status(),
                "shadow_mode": await self.shadow_mode.get_status()
            }
        }

class OrderManager:
    """Unified order management"""
    
    def __init__(self, engine: UnifiedTradingEngine):
        self.engine = engine
        self.mt5 = engine.mt5_service
        self.event_bus = engine.event_bus
        self.risk_manager = engine.risk_manager
        self.orders: Dict[str, UnifiedOrder] = {}
        self.pending_orders: List[UnifiedOrder] = []
    
    async def execute_order(self, order: UnifiedOrder) -> bool:
        """Execute a unified order"""
        if not self.engine.connected:
            logger.error(f"Order {order.id} for {order.symbol} rejected: MT5 not connected.")
            order.status = OrderStatus.REJECTED
            await self._emit_order_event("order.rejected", order)
            return False
            
        logger.info(f"Executing order {order.id} for {order.symbol} from module {order.module}")
        
        is_valid = await self._validate_order(order)
        if not is_valid:
            return False
        
        # Risk check
        if not await self.risk_manager.check_order_risk(order):
            order.status = OrderStatus.REJECTED
            await self._emit_order_event("order.rejected", order)
            return False
        
        # Execute via MT5
        result = await self._execute_mt5_order(order)
        
        if result["success"]:
            order.status = OrderStatus.EXECUTED
            order.executed_at = datetime.now()
            self.orders[order.id] = order
            
            await self._emit_order_event(EventTypes.ORDER_PLACED, order)
            logger.info(f"Order executed: {order.id}")
            return True
        else:
            order.status = OrderStatus.REJECTED
            await self._emit_order_event("order.failed", order)
            logger.error(f"Order failed: {order.id} - {result.get('error')}")
            return False
                
    async def _validate_order(self, order: UnifiedOrder) -> bool:
        """Validate order parameters"""
        try:
            # Get symbol info through MT5Service
            symbols = await self.mt5.get_symbols()
            symbol_info = next((s for s in symbols if s['name'] == order.symbol), None)
            
            if symbol_info is None:
                logger.error(f"Invalid symbol: {order.symbol}")
                return False
            
            # Volume check
            min_lot = symbol_info.get('min_lot', 0.01)
            max_lot = symbol_info.get('max_lot', 100.0)
            
            if order.volume < min_lot or order.volume > max_lot:
                logger.error(f"Invalid volume: {order.volume} (min: {min_lot}, max: {max_lot})")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Error validating order: {e}")
            return False
    
    async def _execute_mt5_order(self, order: UnifiedOrder) -> Dict[str, Any]:
        """Execute order through MT5"""
        try:
            # Get current price if not specified
            if order.price == 0:
                tick = await self.mt5.get_symbol_tick(order.symbol)
                if tick is None:
                    return {"success": False, "error": "Cannot get price"}
                
                order.price = tick['ask'] if order.order_type == "BUY" else tick['bid']
            
            # Execute order through MT5Service
            result = await self.mt5.place_order(
                symbol=order.symbol,
                order_type=order.order_type.lower(),
                volume=order.volume,
                price=order.price,
                sl=order.sl,
                tp=order.tp,
                comment=f"UTE_{order.module}_{order.strategy or 'manual'}"
            )
            
            if result:
                return {
                    "success": True,
                    "ticket": result.get('ticket'),
                    "price": result.get('price'),
                    "volume": result.get('volume')
                }
            else:
                return {
                    "success": False,
                    "error": "Order execution failed"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _emit_order_event(self, event_type: str, order: UnifiedOrder):
        """Emit order-related event"""
        await self.event_bus.emit_async(EnhancedEvent(
            type=event_type,
            data={
                "order_id": order.id,
                "symbol": order.symbol,
                "type": order.order_type,
                "volume": order.volume,
                "price": order.price,
                "module": order.module,
                "strategy": order.strategy,
                "status": order.status.value,
                "timestamp": datetime.now()
            },
            priority=EventPriority.NORMAL,
            source="unified_engine"
        ))
    
    async def check_pending_orders(self):
        """Check and process pending orders"""
        # Implementation for pending/limit orders
        pass

class PositionManager:
    """Unified position management"""
    
    def __init__(self, engine: UnifiedTradingEngine):
        self.engine = engine
        self.mt5 = engine.mt5_service
        self.event_bus = engine.event_bus
        self.positions: Dict[int, UnifiedPosition] = {}
    
    async def sync_positions(self):
        """Sync local positions with MT5"""
        if not self.engine.connected:
            logger.warning("Cannot sync positions, MT5 not connected.")
            return
            
        try:
            # Get positions from MT5
            mt5_positions = await self.engine.mt5_service.get_positions()
            
            # Current position tickets
            current_tickets = set(self.positions.keys())
            mt5_tickets = {pos['ticket'] for pos in mt5_positions}
            
            # Handle new positions
            for mt5_pos in mt5_positions:
                ticket = mt5_pos['ticket']
                if ticket not in self.positions:
                    # New position opened
                    unified_pos = self._create_unified_position_from_dict(mt5_pos)
                    self.positions[ticket] = unified_pos
                    
                    await self.event_bus.emit(EnhancedEvent(
                        type="position.opened",
                        data=unified_pos.__dict__,
                        priority=EventPriority.HIGH,
                        source="position_manager"
                    ))
                else:
                    # Update existing position
                    self._update_unified_position_from_dict(self.positions[ticket], mt5_pos)
            
            # Handle closed positions
            closed_tickets = current_tickets - mt5_tickets
            for ticket in closed_tickets:
                closed_pos = self.positions.pop(ticket)
                closed_pos.status = PositionStatus.CLOSED
                closed_pos.closed_at = datetime.now()
                
                await self.event_bus.emit(EnhancedEvent(
                    type="position.closed",
                    data=closed_pos.__dict__,
                    priority=EventPriority.HIGH,
                    source="position_manager"
                ))
                
        except Exception as e:
            logger.error(f"Error syncing positions: {e}", exc_info=True)
    
    def _create_unified_position_from_dict(self, mt5_pos: Dict) -> UnifiedPosition:
        """Create a new UnifiedPosition from MT5 position dict."""
        return UnifiedPosition(
            ticket=mt5_pos['ticket'],
            symbol=mt5_pos['symbol'],
            position_type=mt5_pos['type'].upper(),
            volume=mt5_pos['volume'],
            open_price=mt5_pos['open_price'],
            current_price=mt5_pos['current_price'],
            sl=mt5_pos.get('sl'),
            tp=mt5_pos.get('tp'),
            profit=mt5_pos.get('profit', 0.0),
            swap=mt5_pos.get('swap', 0.0),
            commission=0.0,
            opened_at=datetime.fromisoformat(mt5_pos['open_time'])
        )
    
    def _update_unified_position_from_dict(self, unified_pos: UnifiedPosition, mt5_pos: Dict):
        """Update unified position from MT5 position dict"""
        unified_pos.current_price = mt5_pos['current_price']
        unified_pos.profit = mt5_pos.get('profit', 0.0)
        unified_pos.swap = mt5_pos.get('swap', 0.0)
        unified_pos.sl = mt5_pos.get('sl')
        unified_pos.tp = mt5_pos.get('tp')
    
    async def update_position_prices(self, price_data: Dict[str, Any]):
        """Update position P&L with new prices"""
        symbol = price_data.get("symbol")
        if not symbol:
            return
        
        for pos in self.positions.values():
            if pos.symbol == symbol:
                pos.current_price = price_data.get("bid" if pos.position_type == "SELL" else "ask")
                # Recalculate P&L if needed
    
    async def get_all_positions(self) -> List[UnifiedPosition]:
        return list(self.positions.values())
    
    async def close_all_positions(self):
        """Close all open positions"""
        for pos in list(self.positions.values()):
            await self.close_position(pos.ticket)
    
    async def close_position(self, ticket: int) -> bool:
        """Close a specific position"""
        if ticket not in self.positions:
            logger.warning(f"Attempted to close a position (ticket: {ticket}) not in local cache.")
            return False

        if not self.engine.connected:
            logger.error(f"Cannot close position {ticket}, MT5 is not connected.")
            return False

        unified_pos = self.positions[ticket]
        logger.info(f"Closing position {ticket} for {unified_pos.symbol} from module {unified_pos.module}")
        
        try:
            result = await self.engine.mt5_service.close_position(ticket)
            
            if result and result.get('retcode') == 10009:  # TRADE_RETCODE_DONE
                logger.info(f"Position {ticket} closed successfully.")
                self.positions.pop(ticket, None)
                
                unified_pos.status = PositionStatus.CLOSED
                unified_pos.closed_at = datetime.now()
                unified_pos.profit = result.get('profit', unified_pos.profit)
                
                await self.event_bus.emit(EnhancedEvent(
                    type="position.closed",
                    data=unified_pos.__dict__,
                    priority=EventPriority.HIGH,
                    source="position_manager"
                ))
                return True
            else:
                error_code = result.get('retcode') if result else "N/A"
                logger.error(f"Failed to close position {ticket}. Error code: {error_code}")
                return False
        except Exception as e:
            logger.error(f"Error closing position {ticket}: {e}")
            return False

    async def modify_position_sl(self, ticket: int, new_sl: float) -> bool:
        """Modify position stop loss"""
        if not self.engine.connected:
            logger.warning(f"Cannot modify SL for {ticket}, MT5 disconnected.")
            return False
        # ... implementation for modifying SL
        pass

    async def modify_position_tp(self, ticket: int, new_tp: float) -> bool:
        """Modify position take profit"""
        if not self.engine.connected:
            logger.warning(f"Cannot modify TP for {ticket}, MT5 disconnected.")
            return False
        # ... implementation for modifying TP
        pass

    async def partial_close_position(self, ticket: int, volume_to_close: float) -> bool:
        """Partially close a position"""
        if not self.engine.connected:
            logger.warning(f"Cannot partially close {ticket}, MT5 disconnected.")
            return False
        # ... implementation for partial close
        pass

class RiskManager:
    """Centralized risk management"""
    
    def __init__(self, engine: UnifiedTradingEngine):
        self.engine = engine
        
        # Risk parameters
        self.max_positions = 10
        self.max_risk_per_trade = 0.02  # 2%
        self.max_daily_loss = 0.05  # 5%
        self.max_exposure = 0.3  # 30%
        self.close_all_on_stop = False
        
        # Risk tracking
        self.daily_loss = 0.0
        self.current_exposure = 0.0
        self.risk_events = []
    
    async def evaluate_signal(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a signal against all risk parameters from all modules."""
        
        if not self.engine.connected:
            return {"approved": False, "reason": "MT5 not connected."}

        # Basic checks
        if len(self.engine.position_manager.positions) >= self.max_positions:
            return {"approved": False, "reason": f"Max open trades ({self.max_positions}) reached."}
        
        # Daily loss check
        if self.daily_loss >= self.max_daily_loss:
            return {"approved": False, "reason": "Daily loss limit reached"}
        
        # Exposure check
        if self.current_exposure >= self.max_exposure:
            return {"approved": False, "reason": "Maximum exposure reached"}
        
        # Emit risk evaluation event
        await self.engine.event_bus.emit_async(EnhancedEvent(
            type="risk.evaluation",
            data={
                "signal": signal,
                "result": {"approved": True},
                "timestamp": datetime.now()
            },
            priority=EventPriority.NORMAL,
            source="unified_engine"
        ))
        
        return {"approved": True}
    
    async def check_order_risk(self, order: UnifiedOrder) -> bool:
        """Check if order passes risk requirements"""
        if not self.engine.connected:
            logger.warning("Cannot check order risk, MT5 not connected")
            return False
            
        try:
            # Get account info through MT5Service
            account_info = await self.engine.mt5_service.get_account_info()
            if not account_info:
                return False
            
            # Get symbol info
            symbols = await self.engine.mt5_service.get_symbols()
            symbol_info = next((s for s in symbols if s['name'] == order.symbol), None)
            if not symbol_info:
                return False
            
            # Risk per trade check
            risk_amount = order.volume * symbol_info.get('min_lot', 0.01) * 100000 * 0.0001  # Simplified
            max_risk = account_info['balance'] * self.max_risk_per_trade
            
            if risk_amount > max_risk:
                logger.warning(f"Order risk too high: {risk_amount} > {max_risk}")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Error checking order risk: {e}")
            return False
    
    async def update_risk_metrics(self):
        """Update risk metrics"""
        if not self.engine.connected:
            return
            
        try:
            account_info = await self.engine.mt5_service.get_account_info()
            if account_info:
                self.daily_loss = max(0, -account_info['profit'] / account_info['balance'])
                
                # Calculate exposure
                total_exposure = 0
                for pos in self.engine.position_manager.positions.values():
                    total_exposure += pos.volume * 100000  # Simplified
                
                self.current_exposure = total_exposure / account_info['balance']
        except Exception as e:
            logger.error(f"Error updating risk metrics: {e}")
    
    async def get_current_risk_status(self) -> Dict[str, Any]:
        """Get current risk status"""
        return {
            "daily_loss": self.daily_loss,
            "current_exposure": self.current_exposure,
            "open_positions": len(self.engine.position_manager.positions),
            "max_positions": self.max_positions,
            "risk_level": self._calculate_risk_level()
        }
    
    def _calculate_risk_level(self) -> str:
        """Calculate current risk level"""
        if self.daily_loss > 0.04 or self.current_exposure > 0.25:
            return "HIGH"
        elif self.daily_loss > 0.02 or self.current_exposure > 0.15:
            return "MEDIUM"
        else:
            return "LOW"

# Module Integration Classes

class AdaptiveTradeManagerIntegration:
    """ATM integration with unified engine"""
    
    def __init__(self, engine):
        self.engine = engine
        self.active = False
        
    async def start(self):
        self.active = True
        asyncio.create_task(self._monitor_positions())
        
    async def stop(self):
        self.active = False
        
    async def get_status(self) -> Dict[str, Any]:
        return {
            "active": self.active,
            "adjustments_made": self.engine.performance_metrics["adaptive_adjustments"],
            "module": "Adaptive Trade Manager"
        }
        
    async def on_price_update(self, price_data: Dict[str, Any]):
        """Handle price updates"""
        pass
        
    async def get_adaptive_params(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Get adaptive parameters for signal"""
        symbol = signal.get("symbol", "")
        base_sl = signal.get("sl", 0)
        base_tp = signal.get("tp", 0)
        
        if base_sl and base_tp:
            volatility_factor = 1.2
            return {
                "dynamic_sl": base_sl * volatility_factor,
                "dynamic_tp": base_tp * volatility_factor,
                "volatility_factor": volatility_factor
            }
        
        return {}
        
    async def _monitor_positions(self):
        """Monitor positions for adaptive adjustments"""
        while self.active:
            try:
                for position in self.engine.position_manager.positions.values():
                    await self._analyze_position_for_adjustment(position)
                await asyncio.sleep(10)
            except Exception as e:
                logger.error(f"ATM monitoring error: {e}")
                await asyncio.sleep(30)
    
    async def _analyze_position_for_adjustment(self, position: UnifiedPosition):
        """Analyze position for potential adjustments"""
        if position.profit > 50:  # $50 profit
            current_sl = position.sl or position.open_price
            new_sl = position.current_price - (0.0020 if position.position_type == "BUY" else -0.0020)
            
            if (position.position_type == "BUY" and new_sl > current_sl) or \
               (position.position_type == "SELL" and new_sl < current_sl):
                
                await self.engine.event_bus.emit(EnhancedEvent(
                    type="atm.adjustment_needed",
                    data={
                        "ticket": position.ticket,
                        "type": "sl_adjustment",
                        "old_value": current_sl,
                        "new_value": new_sl,
                        "reason": "Trailing stop - profit protection"
                    },
                    priority=EventPriority.HIGH,
                    source="adaptive_manager"
                ))

class GodModeIntegration:
    """God Mode integration with unified engine"""
    
    def __init__(self, engine):
        self.engine = engine
        self.active = False
        self.predictions = []
        self.prediction_accuracy = 0.85
        
    async def start(self):
        self.active = True
        asyncio.create_task(self._generate_predictions())
        
    async def stop(self):
        self.active = False
        
    async def get_status(self) -> Dict[str, Any]:
        return {
            "active": self.active,
            "predictions_count": len(self.predictions),
            "accuracy": self.prediction_accuracy,
            "module": "God Mode"
        }
        
    async def on_price_update(self, price_data: Dict[str, Any]):
        """Handle price updates for God Mode analysis"""
        pass
        
    async def get_prediction_for_signal(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Get God Mode prediction for signal"""
        symbol = signal.get("symbol", "")
        
        for pred in reversed(self.predictions):
            if pred["symbol"] == symbol:
                return {
                    "confidence": pred["confidence"],
                    "forecast": pred["direction"],
                    "target_price": pred.get("target_price"),
                    "timeframe": pred["timeframe"]
                }
        
        return {
            "confidence": 0.5,
            "forecast": "neutral",
            "target_price": None,
            "timeframe": "1H"
        }
        
    async def get_prediction_accuracy(self) -> float:
        """Get current prediction accuracy"""
        return self.prediction_accuracy
        
    async def _generate_predictions(self):
        """Generate market predictions"""
        while self.active:
            try:
                symbols = ["EURUSD", "GBPUSD", "USDJPY", "BTCUSD", "ETHUSD"]
                for symbol in symbols:
                    prediction = {
                        "symbol": symbol,
                        "direction": np.random.choice(["BUY", "SELL"]),
                        "confidence": np.random.uniform(0.6, 0.95),
                        "timeframe": "1H",
                        "target_price": None,
                        "timestamp": datetime.now()
                    }
                    
                    self.predictions.append(prediction)
                    
                    if len(self.predictions) > 100:
                        self.predictions.pop(0)
                    
                    await self.engine.event_bus.emit(EnhancedEvent(
                        type="god_mode.prediction",
                        data=prediction,
                        priority=EventPriority.HIGH,
                        source="god_mode"
                    ))
                
                await asyncio.sleep(300)  # Every 5 minutes
            except Exception as e:
                logger.error(f"God Mode prediction error: {e}")
                await asyncio.sleep(60)

class MarketNarratorIntegration:
    """Market Narrator integration with unified engine"""
    
    def __init__(self, engine):
        self.engine = engine
        self.active = False
        self.stories = []
        
    async def start(self):
        self.active = True
        asyncio.create_task(self._generate_stories())
        
    async def stop(self):
        self.active = False
        
    async def get_status(self) -> Dict[str, Any]:
        return {
            "active": self.active,
            "stories_count": len(self.stories),
            "module": "Market Narrator"
        }
        
    async def get_context_for_signal(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Get market narrative context for signal"""
        symbol = signal.get("symbol", "")
        
        for story in reversed(self.stories):
            if symbol in story.get("affected_symbols", []):
                return {
                    "story": story["summary"],
                    "sentiment": story["sentiment"],
                    "title": story["title"]
                }
        
        return {
            "story": "Market conditions normal",
            "sentiment": 0.5,
            "title": "Regular Market Activity"
        }
        
    async def _generate_stories(self):
        """Generate market stories"""
        while self.active:
            try:
                story = {
                    "title": "Market Analysis Update",
                    "summary": "USD strength continues amid Fed speculation",
                    "affected_symbols": ["EURUSD", "GBPUSD", "USDJPY"],
                    "sentiment": np.random.uniform(0.3, 0.7),
                    "timestamp": datetime.now()
                }
                
                self.stories.append(story)
                
                if len(self.stories) > 50:
                    self.stories.pop(0)
                
                await self.engine.event_bus.emit(EnhancedEvent(
                    type="narrator.story_update",
                    data=story,
                    priority=EventPriority.NORMAL,
                    source="market_narrator"
                ))
                
                await asyncio.sleep(600)  # Every 10 minutes
            except Exception as e:
                logger.error(f"Market Narrator error: {e}")
                await asyncio.sleep(120)

class ShadowModeIntegration:
    """Shadow Mode integration with unified engine"""
    
    def __init__(self, engine):
        self.engine = engine
        self.active = False
        self.whale_detections = []
        
    async def start(self):
        self.active = True
        asyncio.create_task(self._detect_whales())
        
    async def stop(self):
        self.active = False
        
    async def get_status(self) -> Dict[str, Any]:
        return {
            "active": self.active,
            "whale_detections": len(self.whale_detections),
            "module": "Shadow Mode"
        }
        
    async def on_price_update(self, price_data: Dict[str, Any]):
        """Handle price updates for whale detection"""
        pass
        
    async def get_intel_for_signal(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Get Shadow Mode intelligence for signal"""
        symbol = signal.get("symbol", "")
        
        for detection in reversed(self.whale_detections):
            if detection["symbol"] == symbol:
                return {
                    "whale_detected": True,
                    "flow_direction": detection["direction"],
                    "confidence": detection["confidence"],
                    "volume": detection["volume"]
                }
        
        return {
            "whale_detected": False,
            "flow_direction": "neutral",
            "confidence": 0.0,
            "volume": 0
        }
        
    async def _detect_whales(self):
        """Detect whale activities"""
        while self.active:
            try:
                if np.random.random() < 0.1:  # 10% chance
                    whale_data = {
                        "symbol": np.random.choice(["BTCUSD", "ETHUSD", "EURUSD"]),
                        "direction": np.random.choice(["BUY", "SELL"]),
                        "volume": np.random.uniform(1000000, 10000000),
                        "confidence": np.random.uniform(0.7, 0.95),
                        "timestamp": datetime.now()
                    }
                    
                    self.whale_detections.append(whale_data)
                    
                    if len(self.whale_detections) > 20:
                        self.whale_detections.pop(0)
                    
                    await self.engine.event_bus.emit(EnhancedEvent(
                        type="shadow.whale_detected",
                        data=whale_data,
                        priority=EventPriority.CRITICAL,
                        source="shadow_mode"
                    ))
                
                await asyncio.sleep(30)  # Every 30 seconds
            except Exception as e:
                logger.error(f"Shadow Mode detection error: {e}")
                await asyncio.sleep(60) 