"""
Event bus system for inter-module communication in ICT Ultra v2.
"""

from typing import Dict, List, Callable, Any
import asyncio
from dataclasses import dataclass
from datetime import datetime
import uuid


@dataclass
class Event:
    """Base event class."""
    id: str
    timestamp: datetime
    type: str
    data: Dict[str, Any]
    
    def __init__(self, type: str, data: Dict[str, Any]):
        self.id = str(uuid.uuid4())
        self.timestamp = datetime.utcnow()
        self.type = type
        self.data = data


class EventBus:
    """
    Simple event bus for decoupled communication between modules.
    """
    
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
        self._async_handlers: Dict[str, List[Callable]] = {}
        
    def register(self, event_type: str, handler: Callable):
        """Register a synchronous event handler."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        
    def register_async(self, event_type: str, handler: Callable):
        """Register an asynchronous event handler."""
        if event_type not in self._async_handlers:
            self._async_handlers[event_type] = []
        self._async_handlers[event_type].append(handler)
        
    def emit(self, event: Event):
        """Emit an event synchronously."""
        handlers = self._handlers.get(event.type, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                print(f"Error in handler {handler.__name__}: {e}")
                
    async def emit_async(self, event: Event):
        """Emit an event asynchronously."""
        # Handle sync handlers
        handlers = self._handlers.get(event.type, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                print(f"Error in handler {handler.__name__}: {e}")
                
        # Handle async handlers
        async_handlers = self._async_handlers.get(event.type, [])
        tasks = []
        for handler in async_handlers:
            tasks.append(handler(event))
            
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)


# Global event bus instance
event_bus = EventBus()


# Common event types
class EventTypes:
    """Common event types used across the system."""
    
    # Trading events
    SIGNAL_DETECTED = "signal.detected"
    ORDER_PLACED = "order.placed"
    ORDER_FILLED = "order.filled"
    ORDER_CANCELLED = "order.cancelled"
    POSITION_OPENED = "position.opened"
    POSITION_CLOSED = "position.closed"
    
    # Market data events
    PRICE_UPDATE = "market.price_update"
    CANDLE_CLOSED = "market.candle_closed"
    
    # System events
    MT5_CONNECTED = "system.mt5_connected"
    MT5_DISCONNECTED = "system.mt5_disconnected"
    ERROR_OCCURRED = "system.error" 