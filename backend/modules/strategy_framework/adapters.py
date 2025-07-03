"""
Event Bus Adapters for Strategy Framework

Provides adapters for connecting strategies to the event bus system.
Enables cross-module communication and real-time event handling.
"""

from typing import Dict, Any, List, Callable, Optional
from datetime import datetime
import asyncio
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class StrategyEventType(str, Enum):
    """Standard strategy event types"""
    # Performance events
    PERFORMANCE_UPDATE = "strategy.performance.update"
    PERFORMANCE_ALERT = "strategy.performance.alert"
    PERFORMANCE_DEGRADATION = "strategy.performance.degradation"
    
    # Optimization events
    OPTIMIZATION_REQUESTED = "strategy.optimization.requested"
    OPTIMIZATION_COMPLETED = "strategy.optimization.completed"
    PARAMETERS_UPDATED = "strategy.parameters.updated"
    
    # Trading events
    SIGNAL_GENERATED = "strategy.signal.generated"
    POSITION_OPENED = "strategy.position.opened"
    POSITION_CLOSED = "strategy.position.closed"
    POSITION_MODIFIED = "strategy.position.modified"
    
    # Risk events
    RISK_ALERT = "strategy.risk.alert"
    DRAWDOWN_WARNING = "strategy.risk.drawdown"
    EXPOSURE_LIMIT = "strategy.risk.exposure"
    
    # Status events
    STRATEGY_STARTED = "strategy.status.started"
    STRATEGY_STOPPED = "strategy.status.stopped"
    STRATEGY_ERROR = "strategy.status.error"


class CrossModuleEventType(str, Enum):
    """Cross-module event types for integration"""
    # God Mode events
    GOD_MODE_PREDICTION = "god_mode.prediction.available"
    GOD_MODE_ANOMALY = "god_mode.anomaly.detected"
    
    # Shadow Mode events
    SHADOW_INSTITUTIONAL = "shadow_mode.institutional.detected"
    SHADOW_DARK_POOL = "shadow_mode.darkpool.activity"
    
    # Market Narrator events
    NARRATOR_STORY = "market_narrator.story.relevant"
    NARRATOR_SENTIMENT = "market_narrator.sentiment.shift"
    
    # Adaptive Trade Manager events
    ATM_SUGGESTION = "adaptive_trade_manager.suggestion"
    ATM_RISK_UPDATE = "adaptive_trade_manager.risk.update"
    
    # Market Context events
    MARKET_VOLATILITY = "market.volatility.changed"
    MARKET_NEWS = "market.news.impact"
    MARKET_REGIME = "market.regime.change"


class EventBusAdapter:
    """
    Adapter for connecting strategies to the event bus.
    Handles event routing, filtering, and transformation.
    """
    
    def __init__(self, event_bus, strategy_id: str):
        self.event_bus = event_bus
        self.strategy_id = strategy_id
        self._subscriptions: Dict[str, List[Callable]] = {}
        self._event_queue = asyncio.Queue()
        self._running = False
        
    async def start(self):
        """Start the event adapter"""
        self._running = True
        asyncio.create_task(self._process_events())
        logger.info(f"EventBusAdapter started for strategy {self.strategy_id}")
    
    async def stop(self):
        """Stop the event adapter"""
        self._running = False
        # Unsubscribe from all events
        for event_type in list(self._subscriptions.keys()):
            await self.unsubscribe(event_type)
        logger.info(f"EventBusAdapter stopped for strategy {self.strategy_id}")
    
    async def emit(self, event_type: str, data: Dict[str, Any]):
        """
        Emit an event to the event bus.
        
        Args:
            event_type: Type of event
            data: Event data
        """
        # Add strategy context
        event_data = {
            "strategy_id": self.strategy_id,
            "timestamp": datetime.now().isoformat(),
            **data
        }
        
        # Emit to event bus
        if self.event_bus:
            await self.event_bus.emit(event_type, event_data)
    
    async def subscribe(self, event_type: str, handler: Callable):
        """
        Subscribe to an event type.
        
        Args:
            event_type: Event type to subscribe to
            handler: Async function to handle the event
        """
        if event_type not in self._subscriptions:
            self._subscriptions[event_type] = []
            
            # Subscribe to event bus
            if self.event_bus:
                await self.event_bus.subscribe(
                    event_type,
                    lambda data: self._queue_event(event_type, data)
                )
        
        self._subscriptions[event_type].append(handler)
        logger.debug(f"Strategy {self.strategy_id} subscribed to {event_type}")
    
    async def unsubscribe(self, event_type: str, handler: Callable = None):
        """
        Unsubscribe from an event type.
        
        Args:
            event_type: Event type to unsubscribe from
            handler: Specific handler to remove (None removes all)
        """
        if event_type in self._subscriptions:
            if handler:
                self._subscriptions[event_type].remove(handler)
            else:
                del self._subscriptions[event_type]
                
                # Unsubscribe from event bus
                if self.event_bus:
                    await self.event_bus.unsubscribe(event_type)
    
    async def request(self, event_type: str, data: Dict[str, Any], timeout: float = 5.0) -> Optional[Any]:
        """
        Make a request to another module and wait for response.
        
        Args:
            event_type: Request event type
            data: Request data
            timeout: Response timeout in seconds
            
        Returns:
            Response data or None if timeout
        """
        if not self.event_bus:
            return None
        
        # Create response event
        response_event = f"{event_type}.response.{self.strategy_id}"
        response_future = asyncio.Future()
        
        # Subscribe to response
        async def response_handler(response_data):
            response_future.set_result(response_data)
        
        await self.subscribe(response_event, response_handler)
        
        try:
            # Send request
            await self.emit(event_type, {
                **data,
                "response_event": response_event
            })
            
            # Wait for response
            response = await asyncio.wait_for(response_future, timeout=timeout)
            return response
            
        except asyncio.TimeoutError:
            logger.warning(f"Request timeout for {event_type}")
            return None
        finally:
            await self.unsubscribe(response_event, response_handler)
    
    def _queue_event(self, event_type: str, data: Dict[str, Any]):
        """Queue an event for processing"""
        if self._running:
            self._event_queue.put_nowait((event_type, data))
    
    async def _process_events(self):
        """Process queued events"""
        while self._running:
            try:
                # Get event from queue
                event_type, data = await asyncio.wait_for(
                    self._event_queue.get(),
                    timeout=1.0
                )
                
                # Process event
                if event_type in self._subscriptions:
                    for handler in self._subscriptions[event_type]:
                        try:
                            if asyncio.iscoroutinefunction(handler):
                                await handler(data)
                            else:
                                handler(data)
                        except Exception as e:
                            logger.error(f"Error handling event {event_type}: {e}")
                            
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing events: {e}")


class StrategyEventHandler:
    """
    Base class for handling strategy events with built-in patterns.
    """
    
    def __init__(self, adapter: EventBusAdapter):
        self.adapter = adapter
        self._handlers: Dict[str, Callable] = {}
        
    async def setup(self):
        """Setup event handlers"""
        # Subscribe to standard strategy events
        await self.adapter.subscribe(
            StrategyEventType.PERFORMANCE_UPDATE,
            self.on_performance_update
        )
        
        await self.adapter.subscribe(
            StrategyEventType.RISK_ALERT,
            self.on_risk_alert
        )
        
        # Subscribe to cross-module events
        await self.adapter.subscribe(
            CrossModuleEventType.GOD_MODE_PREDICTION,
            self.on_god_mode_prediction
        )
        
        await self.adapter.subscribe(
            CrossModuleEventType.SHADOW_INSTITUTIONAL,
            self.on_shadow_institutional
        )
        
        await self.adapter.subscribe(
            CrossModuleEventType.NARRATOR_STORY,
            self.on_market_story
        )
        
        await self.adapter.subscribe(
            CrossModuleEventType.MARKET_VOLATILITY,
            self.on_market_volatility
        )
    
    # Standard event handlers (to be overridden)
    
    async def on_performance_update(self, data: Dict[str, Any]):
        """Handle performance update events"""
        pass
    
    async def on_risk_alert(self, data: Dict[str, Any]):
        """Handle risk alert events"""
        pass
    
    async def on_god_mode_prediction(self, data: Dict[str, Any]):
        """Handle God Mode predictions"""
        pass
    
    async def on_shadow_institutional(self, data: Dict[str, Any]):
        """Handle Shadow Mode institutional activity"""
        pass
    
    async def on_market_story(self, data: Dict[str, Any]):
        """Handle Market Narrator stories"""
        pass
    
    async def on_market_volatility(self, data: Dict[str, Any]):
        """Handle market volatility changes"""
        pass
    
    # Helper methods for common patterns
    
    async def request_god_mode_prediction(self, symbol: str, timeframe: str) -> Optional[Dict[str, Any]]:
        """Request prediction from God Mode"""
        return await self.adapter.request(
            "god_mode.get_prediction",
            {
                "symbol": symbol,
                "timeframe": timeframe
            }
        )
    
    async def request_shadow_mode_flow(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Request institutional flow from Shadow Mode"""
        return await self.adapter.request(
            "shadow_mode.get_institutional_flow",
            {"symbol": symbol}
        )
    
    async def request_market_narrative(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Request current narrative from Market Narrator"""
        return await self.adapter.request(
            "market_narrator.get_current_narrative",
            {"symbol": symbol}
        )
    
    async def emit_performance_metric(self, metric_name: str, value: float, metadata: Dict[str, Any] = None):
        """Emit a performance metric"""
        await self.adapter.emit(
            StrategyEventType.PERFORMANCE_UPDATE,
            {
                "metric": metric_name,
                "value": value,
                "metadata": metadata or {}
            }
        )
    
    async def emit_risk_warning(self, risk_type: str, severity: str, message: str):
        """Emit a risk warning"""
        await self.adapter.emit(
            StrategyEventType.RISK_ALERT,
            {
                "risk_type": risk_type,
                "severity": severity,
                "message": message
            }
        )
    
    async def emit_signal(self, signal_data: Dict[str, Any]):
        """Emit a trading signal"""
        await self.adapter.emit(
            StrategyEventType.SIGNAL_GENERATED,
            signal_data
        ) 