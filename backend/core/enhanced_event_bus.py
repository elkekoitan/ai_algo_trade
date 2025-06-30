"""
Enhanced Event Bus System
Gelişmiş event yönetimi: priority, filtering, persistence, replay
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import uuid
from collections import defaultdict
import logging
from asyncio import PriorityQueue
import pickle
from typing import Dict, List, Callable, Any, Optional, Set, Union

logger = logging.getLogger(__name__)

class EventPriority(Enum):
    """Event öncelik seviyeleri"""
    CRITICAL = 1  # System critical events
    HIGH = 2      # Trading signals, risk alerts
    NORMAL = 3    # Regular updates
    LOW = 4       # Logging, metrics

class EventTypes:
    """Standard event types"""
    # Market events
    PRICE_UPDATE = "market.price_update"
    CANDLE_CLOSED = "market.candle_closed"
    
    # Trading events
    SIGNAL_GENERATED = "trading.signal_generated"
    ORDER_PLACED = "trading.order_placed"
    POSITION_OPENED = "trading.position_opened"
    POSITION_CLOSED = "trading.position_closed"
    
    # System events
    MT5_CONNECTED = "system.mt5_connected"
    MT5_DISCONNECTED = "system.mt5_disconnected"
    ENGINE_STARTED = "system.engine_started"
    ENGINE_STOPPED = "system.engine_stopped"

@dataclass
class EnhancedEvent:
    """Gelişmiş event yapısı"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: str = ""
    data: dict = field(default_factory=dict)
    priority: EventPriority = EventPriority.NORMAL
    source: str = "unknown"
    timestamp: datetime = field(default_factory=datetime.now)
    tags: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    
    def __lt__(self, other):
        """Priority queue sorting"""
        return self.priority.value < other.priority.value

class EventFilter:
    """Event filtering system"""
    
    def __init__(self, event_type: str = None, source: str = None, 
                 priority: EventPriority = None, tags: list = None):
        self.event_type = event_type
        self.source = source
        self.priority = priority
        self.tags = tags or []
    
    def matches(self, event: EnhancedEvent) -> bool:
        """Check if event matches filter"""
        if self.event_type and self.event_type != event.type:
            return False
        if self.source and self.source != event.source:
            return False
        if self.priority and self.priority != event.priority:
            return False
        if self.tags and not any(tag in event.tags for tag in self.tags):
            return False
        return True

class EnhancedEventBus:
    """
    Gelişmiş Event Bus Sistemi
    - Priority handling
    - Filtering
    - Persistence
    - Replay capability
    - Performance monitoring
    """
    
    def __init__(self):
        self.subscribers: dict = defaultdict(list)
        self.async_subscribers: dict = defaultdict(list)
        self.filters: dict = {}
        
        # Priority queues for different priorities
        self.priority_queues = {
            priority: PriorityQueue() for priority in EventPriority
        }
        
        # Event storage
        self.event_history: list = []
        self.max_history = 10000
        
        # Performance metrics
        self.metrics = {
            "events_processed": 0,
            "events_failed": 0,
            "average_processing_time": 0.0,
            "subscribers_count": 0
        }
        
        # State
        self.is_running = False
        self.processing_tasks = []
    
    async def start(self):
        """Start event bus"""
        if self.is_running:
            return
            
        self.is_running = True
        
        # Start processing tasks for each priority
        for priority in EventPriority:
            task = asyncio.create_task(self._process_priority_queue(priority))
            self.processing_tasks.append(task)
        
        # Start metrics task
        self.processing_tasks.append(
            asyncio.create_task(self._update_metrics())
        )
        
        logger.info("🚀 Enhanced Event Bus started")
    
    async def stop(self):
        """Stop event bus"""
        self.is_running = False
        
        # Cancel all processing tasks
        for task in self.processing_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.processing_tasks, return_exceptions=True)
        
        logger.info("🛑 Enhanced Event Bus stopped")
    
    def subscribe(self, event_type: str, callback: callable, 
                  event_filter: EventFilter = None):
        """Subscribe to events (sync)"""
        self.subscribers[event_type].append(callback)
        if event_filter:
            self.filters[f"{event_type}_{id(callback)}"] = event_filter
        self.metrics["subscribers_count"] = sum(len(subs) for subs in self.subscribers.values())
    
    def subscribe_async(self, event_type: str, callback: Callable, 
                       event_filter: EventFilter = None):
        """Subscribe to events (async)"""
        self.async_subscribers[event_type].append(callback)
        if event_filter:
            self.filters[f"{event_type}_{id(callback)}"] = event_filter
        self.metrics["subscribers_count"] = sum(len(subs) for subs in self.async_subscribers.values())
    
    async def emit(self, event: Union['EnhancedEvent', str], data: dict = None,
                   priority: 'EventPriority' = EventPriority.NORMAL, source: str = "unknown"):
        """Emit an event.
        Backward-compatible: can be called either with a fully-constructed
        `EnhancedEvent` instance *or* the legacy `(event_type, data, priority)`
        signature that many modules still use.
        """
        # Legacy signature support
        if isinstance(event, str):
            event = EnhancedEvent(
                type=event,
                data=data or {},
                priority=priority,
                source=source
            )
        # Proceed with normal logic (unchanged apart from parameter name)
        if not self.is_running:
            logger.warning("Event bus not running, dropping event")
            return
        
        # Add to history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)
        
        # Add to appropriate priority queue
        await self.priority_queues[event.priority].put(event)
        
        logger.debug(f"Event emitted: {event.type} (Priority: {event.priority.name})")
    
    async def _process_priority_queue(self, priority: EventPriority):
        """Process events from priority queue"""
        queue = self.priority_queues[priority]
        
        while self.is_running:
            try:
                # Get event from queue (waits until an item is available)
                event = await queue.get()
                
                start_time = datetime.now()
                
                # Process sync subscribers
                for callback in self.subscribers.get(event.type, []):
                    if self._should_process_event(event, callback):
                        try:
                            callback(event)
                        except Exception as e:
                            logger.error(f"Sync subscriber error: {e}")
                            self.metrics["events_failed"] += 1
                
                # Process async subscribers
                for callback in self.async_subscribers.get(event.type, []):
                    if self._should_process_event(event, callback):
                        try:
                            await callback(event)
                        except Exception as e:
                            logger.error(f"Async subscriber error: {e}")
                            self.metrics["events_failed"] += 1
                
                # Update metrics
                processing_time = (datetime.now() - start_time).total_seconds()
                self.metrics["events_processed"] += 1
                if self.metrics["events_processed"] > 0:
                    self.metrics["average_processing_time"] = (
                        (self.metrics["average_processing_time"] * (self.metrics["events_processed"] - 1) + processing_time) /
                        self.metrics["events_processed"]
                    )
                
                queue.task_done()

            except asyncio.CancelledError:
                logger.info(f"Task for priority {priority.name} was cancelled.")
                break
            except Exception as e:
                logger.error(f"Priority queue processing error in {priority.name}: {e}")
                await asyncio.sleep(1)
    
    def _should_process_event(self, event: EnhancedEvent, callback: callable) -> bool:
        """Check if event should be processed by callback"""
        filter_key = f"{event.type}_{id(callback)}"
        if filter_key in self.filters:
            return self.filters[filter_key].matches(event)
        return True
    
    async def _update_metrics(self):
        """Update performance metrics"""
        while self.is_running:
            try:
                await asyncio.sleep(30)  # Update every 30 seconds
            except Exception as e:
                logger.error(f"Metrics update error: {e}")
                await asyncio.sleep(30)
    
    def get_metrics(self) -> dict:
        """Get current metrics"""
        return {
            **self.metrics,
            "queue_sizes": {
                priority.name: queue.qsize() 
                for priority, queue in self.priority_queues.items()
            },
            "history_size": len(self.event_history),
            "is_running": self.is_running
        }

    # ---------------------------------------------------------------------
    # Utility helpers for external modules
    # ---------------------------------------------------------------------

    def get_event_history(self, limit: int = 100, event_type: str = None):
        """Return up to `limit` most recent events, optionally filtered by type."""
        if event_type:
            filtered = [e for e in self.event_history if e.type == event_type]
        else:
            filtered = self.event_history
        return [e.__dict__ for e in filtered[-limit:]]

    # Provide `_handlers` attribute expected by some legacy code (read-only)
    @property
    def _handlers(self):
        """Aggregate sync + async subscribers for legacy compatibility."""
        combined = {}
        for etype, subs in {**self.subscribers, **self.async_subscribers}.items():
            combined.setdefault(etype, []).extend(subs)
        return combined 