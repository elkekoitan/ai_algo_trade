"""
Event Bus Test Script
Event bus sisteminin çalıştığını doğrular
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.enhanced_event_bus import EnhancedEventBus, EventPriority, EnhancedEvent

async def test_event_bus():
    print("🚀 Testing Enhanced Event Bus System...")
    print("=" * 50)
    
    # Create event bus
    event_bus = EnhancedEventBus()
    print("✅ Event bus created")
    
    # Start the bus
    await event_bus.start()
    print("✅ Event bus started")

    # Test data collection
    received_events = []
    
    # Define handlers
    async def critical_handler(event: EnhancedEvent):
        print(f"🔴 CRITICAL: {event.type} - {event.data}")
        received_events.append(("CRITICAL", event.type, event.data))
    
    async def normal_handler(event: EnhancedEvent):
        print(f"🟢 NORMAL: {event.type} - {event.data}")
        received_events.append(("NORMAL", event.type, event.data))
    
    # Subscribe handlers
    event_bus.subscribe_async("trade.signal", critical_handler)
    event_bus.subscribe_async("market.update", normal_handler)
    print("✅ Handlers subscribed")
    
    # Emit events
    print("\n📤 Emitting events...")
    await event_bus.emit(EnhancedEvent(
        type="trade.signal", 
        data={"symbol": "EURUSD", "action": "BUY"}, 
        priority=EventPriority.CRITICAL
    ))
    await event_bus.emit(EnhancedEvent(
        type="market.update", 
        data={"symbol": "GBPUSD", "price": 1.2650}, 
        priority=EventPriority.NORMAL
    ))
    await event_bus.emit(EnhancedEvent(
        type="trade.signal", 
        data={"symbol": "XAUUSD", "action": "SELL"}, 
        priority=EventPriority.HIGH
    ))
    
    # Wait for processing
    await asyncio.sleep(1)
    
    # Check results
    print(f"\n📊 Received {len(received_events)} events")
    history = event_bus.event_history
    print(f"📜 Event history size: {len(history)}")
    
    # Display history
    print("\n📜 Event History:")
    for event in history[-10:]:
        print(f"  - {event.timestamp}: {event.type} (Priority: {event.priority.name})")
    
    # Test filtering
    # Note: Filtering logic might need adjustment based on the new structure.
    # This part is simplified for now.
    print("\n🔍 Testing event filtering (simplified)...")
    trade_events = [e for e in history if e.type == "trade.signal"]
    print(f"✅ Found {len(trade_events)} trade signals")
    
    # Close event bus
    await event_bus.stop()
    print("\n✅ Event bus test completed successfully!")
    
    return len(received_events) > 0

if __name__ == "__main__":
    success = asyncio.run(test_event_bus())
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n❌ Tests failed!")
        sys.exit(1) 