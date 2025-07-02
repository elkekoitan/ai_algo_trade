"""
Multi-Broker Manager
Universal trading interface supporting multiple brokers
"""
import asyncio
import logging
from typing import List, Optional, Dict, Any, Type
from datetime import datetime, timedelta
import json

from .models import (
    BrokerConfig, BrokerConnection, UniversalOrder, UniversalPosition,
    BrokerType, ConnectionStatus, UniversalSymbol, BrokerAccountInfo,
    MarketData, HistoricalData, BrokerError, OrderType, OrderSide
)
from .adapters import (
    MT5Adapter, BasicAdapter
)
from .adapters.basic_adapter import BaseBrokerAdapter
from ...core.enhanced_event_bus import enhanced_event_bus

logger = logging.getLogger(__name__)

class BrokerManager:
    """Universal broker manager"""
    
    def __init__(self):
        self.brokers: Dict[str, BrokerConfig] = {}
        self.connections: Dict[str, BrokerConnection] = {}
        self.adapters: Dict[str, BaseBrokerAdapter] = {}
        self.is_running = False
        
        # Performance tracking
        self.performance_stats: Dict[str, Dict[str, Any]] = {}
        
        # Error handling
        self.error_history: List[BrokerError] = []
        self.max_error_history = 1000
        
    async def start_service(self):
        """Start broker manager service"""
        self.is_running = True
        logger.info("🔗 Multi-Broker Manager started")
        
        # Initialize default brokers
        await self._initialize_default_brokers()
        
        # Start background tasks
        asyncio.create_task(self._monitor_connections())
        asyncio.create_task(self._sync_market_data())
        asyncio.create_task(self._update_performance_stats())
        
    # Broker Management
    async def add_broker(self, config: BrokerConfig) -> bool:
        """Add a new broker configuration"""
        try:
            # Validate configuration
            if not await self._validate_broker_config(config):
                return False
                
            # Store configuration
            self.brokers[config.broker_id] = config
            
            # Initialize connection
            connection = BrokerConnection(
                broker_id=config.broker_id,
                broker_type=config.broker_type
            )
            self.connections[config.broker_id] = connection
            
            # Create adapter
            adapter = await self._create_adapter(config)
            if adapter:
                self.adapters[config.broker_id] = adapter
                
                # Auto-connect if active
                if config.is_active:
                    await self.connect_broker(config.broker_id)
                    
            logger.info(f"✅ Broker added: {config.name} ({config.broker_type})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add broker: {e}")
            return False
            
    async def remove_broker(self, broker_id: str) -> bool:
        """Remove a broker"""
        try:
            if broker_id in self.connections:
                await self.disconnect_broker(broker_id)
                
            # Remove from all collections
            self.brokers.pop(broker_id, None)
            self.connections.pop(broker_id, None)
            self.adapters.pop(broker_id, None)
            self.performance_stats.pop(broker_id, None)
            
            logger.info(f"✅ Broker removed: {broker_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove broker: {e}")
            return False
            
    async def connect_broker(self, broker_id: str) -> bool:
        """Connect to a broker"""
        try:
            if broker_id not in self.adapters:
                logger.error(f"Adapter not found for broker: {broker_id}")
                return False
                
            adapter = self.adapters[broker_id]
            connection = self.connections[broker_id]
            
            # Update status
            connection.status = ConnectionStatus.CONNECTING
            connection.reconnect_attempts += 1
            
            # Attempt connection
            success = await adapter.connect()
            
            if success:
                connection.status = ConnectionStatus.CONNECTED
                connection.connected_at = datetime.utcnow()
                connection.last_ping = datetime.utcnow()
                connection.error_count = 0
                
                # Get account info
                account_info = await adapter.get_account_info()
                if account_info:
                    connection.account_id = account_info.account_id
                    connection.account_currency = account_info.account_currency
                    connection.balance = account_info.balance
                    connection.equity = account_info.equity
                    
                # Broadcast connection event
                await enhanced_event_bus.publish(
                    "broker:connected",
                    {"broker_id": broker_id, "connection": connection.dict()}
                )
                
                logger.info(f"✅ Connected to broker: {broker_id}")
                return True
            else:
                connection.status = ConnectionStatus.ERROR
                connection.last_error = "Connection failed"
                connection.error_count += 1
                
                logger.error(f"❌ Failed to connect to broker: {broker_id}")
                return False
                
        except Exception as e:
            logger.error(f"Connection error for {broker_id}: {e}")
            if broker_id in self.connections:
                self.connections[broker_id].status = ConnectionStatus.ERROR
                self.connections[broker_id].last_error = str(e)
                self.connections[broker_id].error_count += 1
            return False
            
    async def disconnect_broker(self, broker_id: str) -> bool:
        """Disconnect from a broker"""
        try:
            if broker_id in self.adapters:
                adapter = self.adapters[broker_id]
                await adapter.disconnect()
                
            if broker_id in self.connections:
                connection = self.connections[broker_id]
                connection.status = ConnectionStatus.DISCONNECTED
                connection.connected_at = None
                
                # Broadcast disconnection event
                await enhanced_event_bus.publish(
                    "broker:disconnected",
                    {"broker_id": broker_id}
                )
                
            logger.info(f"✅ Disconnected from broker: {broker_id}")
            return True
            
        except Exception as e:
            logger.error(f"Disconnection error for {broker_id}: {e}")
            return False
            
    # Trading Operations
    async def place_order(
        self,
        broker_id: str,
        symbol: str,
        side: OrderSide,
        order_type: OrderType,
        quantity: float,
        price: Optional[float] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        **kwargs
    ) -> Optional[UniversalOrder]:
        """Place an order through specified broker"""
        try:
            if broker_id not in self.adapters:
                logger.error(f"Adapter not found for broker: {broker_id}")
                return None
                
            adapter = self.adapters[broker_id]
            
            # Check connection
            if not await self._check_broker_connection(broker_id):
                logger.error(f"Broker not connected: {broker_id}")
                return None
                
            # Place order through adapter
            order = await adapter.place_order(
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                **kwargs
            )
            
            if order:
                # Update statistics
                connection = self.connections[broker_id]
                connection.total_orders += 1
                
                # Broadcast order event
                await enhanced_event_bus.publish(
                    "broker:order_placed",
                    {"broker_id": broker_id, "order": order.dict()}
                )
                
                logger.info(f"✅ Order placed: {order.order_id} on {broker_id}")
                return order
                
        except Exception as e:
            logger.error(f"Failed to place order on {broker_id}: {e}")
            await self._log_error(broker_id, "order", str(e), "place_order")
            
        return None
        
    async def cancel_order(self, broker_id: str, order_id: str) -> bool:
        """Cancel an order"""
        try:
            if broker_id not in self.adapters:
                return False
                
            adapter = self.adapters[broker_id]
            success = await adapter.cancel_order(order_id)
            
            if success:
                # Broadcast cancellation event
                await enhanced_event_bus.publish(
                    "broker:order_cancelled",
                    {"broker_id": broker_id, "order_id": order_id}
                )
                
                logger.info(f"✅ Order cancelled: {order_id} on {broker_id}")
                
            return success
            
        except Exception as e:
            logger.error(f"Failed to cancel order {order_id} on {broker_id}: {e}")
            return False
            
    async def close_position(self, broker_id: str, position_id: str) -> bool:
        """Close a position"""
        try:
            if broker_id not in self.adapters:
                return False
                
            adapter = self.adapters[broker_id]
            success = await adapter.close_position(position_id)
            
            if success:
                # Update statistics
                connection = self.connections[broker_id]
                connection.total_trades += 1
                
                # Broadcast position close event
                await enhanced_event_bus.publish(
                    "broker:position_closed",
                    {"broker_id": broker_id, "position_id": position_id}
                )
                
                logger.info(f"✅ Position closed: {position_id} on {broker_id}")
                
            return success
            
        except Exception as e:
            logger.error(f"Failed to close position {position_id} on {broker_id}: {e}")
            return False
            
    # Data Retrieval
    async def get_all_positions(self) -> Dict[str, List[UniversalPosition]]:
        """Get positions from all connected brokers"""
        all_positions = {}
        
        for broker_id, adapter in self.adapters.items():
            if await self._check_broker_connection(broker_id):
                try:
                    positions = await adapter.get_positions()
                    all_positions[broker_id] = positions
                except Exception as e:
                    logger.error(f"Failed to get positions from {broker_id}: {e}")
                    all_positions[broker_id] = []
                    
        return all_positions
        
    async def get_all_orders(self) -> Dict[str, List[UniversalOrder]]:
        """Get orders from all connected brokers"""
        all_orders = {}
        
        for broker_id, adapter in self.adapters.items():
            if await self._check_broker_connection(broker_id):
                try:
                    orders = await adapter.get_orders()
                    all_orders[broker_id] = orders
                except Exception as e:
                    logger.error(f"Failed to get orders from {broker_id}: {e}")
                    all_orders[broker_id] = []
                    
        return all_orders
        
    async def get_market_data(
        self, 
        symbol: str, 
        broker_id: Optional[str] = None
    ) -> Dict[str, MarketData]:
        """Get market data for symbol from brokers"""
        market_data = {}
        
        # If specific broker requested
        if broker_id:
            if broker_id in self.adapters and await self._check_broker_connection(broker_id):
                try:
                    data = await self.adapters[broker_id].get_market_data(symbol)
                    if data:
                        market_data[broker_id] = data
                except Exception as e:
                    logger.error(f"Failed to get market data from {broker_id}: {e}")
        else:
            # Get from all connected brokers
            for broker_id, adapter in self.adapters.items():
                if await self._check_broker_connection(broker_id):
                    try:
                        data = await adapter.get_market_data(symbol)
                        if data:
                            market_data[broker_id] = data
                    except Exception as e:
                        logger.error(f"Failed to get market data from {broker_id}: {e}")
                        
        return market_data
        
    async def get_account_info(self, broker_id: str) -> Optional[BrokerAccountInfo]:
        """Get account information from broker"""
        try:
            if broker_id not in self.adapters:
                return None
                
            if not await self._check_broker_connection(broker_id):
                return None
                
            adapter = self.adapters[broker_id]
            return await adapter.get_account_info()
            
        except Exception as e:
            logger.error(f"Failed to get account info from {broker_id}: {e}")
            return None
            
    async def get_symbols(self, broker_id: str) -> List[UniversalSymbol]:
        """Get available symbols from broker"""
        try:
            if broker_id not in self.adapters:
                return []
                
            if not await self._check_broker_connection(broker_id):
                return []
                
            adapter = self.adapters[broker_id]
            return await adapter.get_symbols()
            
        except Exception as e:
            logger.error(f"Failed to get symbols from {broker_id}: {e}")
            return []
            
    # Multi-Broker Operations
    async def place_order_on_best_broker(
        self,
        symbol: str,
        side: OrderSide,
        order_type: OrderType,
        quantity: float,
        **kwargs
    ) -> Optional[UniversalOrder]:
        """Place order on the best available broker for the symbol"""
        try:
            # Get market data from all brokers
            market_data = await self.get_market_data(symbol)
            
            if not market_data:
                logger.error(f"No market data available for {symbol}")
                return None
                
            # Find best broker based on spread and liquidity
            best_broker = await self._find_best_broker_for_symbol(symbol, market_data)
            
            if best_broker:
                return await self.place_order(
                    best_broker, symbol, side, order_type, quantity, **kwargs
                )
                
        except Exception as e:
            logger.error(f"Failed to place order on best broker: {e}")
            
        return None
        
    async def get_best_price(self, symbol: str, side: OrderSide) -> Optional[Dict[str, Any]]:
        """Get best price across all brokers"""
        try:
            market_data = await self.get_market_data(symbol)
            
            if not market_data:
                return None
                
            best_price = None
            best_broker = None
            
            for broker_id, data in market_data.items():
                price = data.ask if side == OrderSide.BUY else data.bid
                
                if price and (best_price is None or 
                             (side == OrderSide.BUY and price < best_price) or
                             (side == OrderSide.SELL and price > best_price)):
                    best_price = price
                    best_broker = broker_id
                    
            return {
                "price": best_price,
                "broker_id": best_broker,
                "timestamp": datetime.utcnow()
            } if best_price else None
            
        except Exception as e:
            logger.error(f"Failed to get best price: {e}")
            return None
            
    # Status and Monitoring
    def get_connection_status(self) -> Dict[str, ConnectionStatus]:
        """Get connection status for all brokers"""
        return {
            broker_id: connection.status 
            for broker_id, connection in self.connections.items()
        }
        
    def get_broker_list(self) -> List[Dict[str, Any]]:
        """Get list of all configured brokers"""
        broker_list = []
        
        for broker_id, config in self.brokers.items():
            connection = self.connections.get(broker_id)
            
            broker_info = {
                "broker_id": broker_id,
                "name": config.name,
                "type": config.broker_type,
                "status": connection.status if connection else ConnectionStatus.DISCONNECTED,
                "is_demo": config.is_demo,
                "supports_forex": config.supports_forex,
                "supports_crypto": config.supports_crypto,
                "supports_stocks": config.supports_stocks,
                "last_connected": connection.last_connected if connection else None
            }
            
            broker_list.append(broker_info)
            
        return broker_list
        
    def get_performance_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get performance statistics for all brokers"""
        return self.performance_stats.copy()
        
    # Helper Methods
    async def _initialize_default_brokers(self):
        """Initialize default broker configurations"""
        try:
            # MT5 Demo
            mt5_config = BrokerConfig(
                broker_id="mt5_demo",
                broker_type=BrokerType.MT5,
                name="MetaTrader 5 Demo",
                display_name="MT5 Demo Account",
                login="25201110",
                password="e|([rXU1IsiM",
                server="Tickmill-Demo",
                supports_forex=True,
                supports_crypto=True,
                supports_stocks=True,
                is_demo=True
            )
            await self.add_broker(mt5_config)
            
            # Binance (if API keys available)
            binance_config = BrokerConfig(
                broker_id="binance_spot",
                broker_type=BrokerType.BINANCE,
                name="Binance Spot",
                display_name="Binance Spot Trading",
                supports_crypto=True,
                is_demo=True,  # Testnet
                is_active=False  # Disabled by default
            )
            await self.add_broker(binance_config)
            
            logger.info("✅ Default brokers initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize default brokers: {e}")
            
    async def _validate_broker_config(self, config: BrokerConfig) -> bool:
        """Validate broker configuration"""
        try:
            # Check required fields
            if not config.broker_id or not config.broker_type:
                return False
                
            # Check for duplicate broker_id
            if config.broker_id in self.brokers:
                logger.error(f"Broker ID already exists: {config.broker_id}")
                return False
                
            # Validate broker-specific requirements
            if config.broker_type == BrokerType.MT5:
                if not all([config.login, config.password, config.server]):
                    logger.error("MT5 requires login, password, and server")
                    return False
                    
            elif config.broker_type in [BrokerType.BINANCE, BrokerType.BYBIT]:
                if not config.is_demo and not all([config.api_key, config.api_secret]):
                    logger.error(f"{config.broker_type} requires API key and secret")
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Config validation error: {e}")
            return False
            
    async def _create_adapter(self, config: BrokerConfig) -> Optional[BaseBrokerAdapter]:
        """Create appropriate adapter for broker type"""
        try:
            if config.broker_type == BrokerType.MT5:
                return MT5Adapter(config)
            else:
                # For now, return BasicAdapter for unsupported types
                logger.warning(f"Using BasicAdapter for unsupported broker type: {config.broker_type}")
                return BasicAdapter(config)
                
        except Exception as e:
            logger.error(f"Failed to create adapter: {e}")
            return None
            
    async def _check_broker_connection(self, broker_id: str) -> bool:
        """Check if broker is connected"""
        connection = self.connections.get(broker_id)
        return connection and connection.status == ConnectionStatus.CONNECTED
        
    async def _find_best_broker_for_symbol(
        self, 
        symbol: str, 
        market_data: Dict[str, MarketData]
    ) -> Optional[str]:
        """Find best broker for trading a symbol"""
        try:
            best_broker = None
            best_score = -1
            
            for broker_id, data in market_data.items():
                # Calculate score based on spread, volume, and broker reliability
                spread = data.ask - data.bid if data.ask and data.bid else float('inf')
                volume = data.volume or 0
                
                # Get broker performance
                performance = self.performance_stats.get(broker_id, {})
                uptime = performance.get("uptime_percentage", 0)
                avg_latency = performance.get("avg_latency", 1000)
                
                # Calculate composite score (lower is better for spread and latency)
                score = (
                    (1 / (spread + 0.0001)) * 0.4 +  # Lower spread is better
                    volume * 0.2 +                    # Higher volume is better
                    uptime * 0.3 +                    # Higher uptime is better
                    (1 / (avg_latency + 1)) * 0.1     # Lower latency is better
                )
                
                if score > best_score:
                    best_score = score
                    best_broker = broker_id
                    
            return best_broker
            
        except Exception as e:
            logger.error(f"Failed to find best broker: {e}")
            return None
            
    async def _log_error(
        self, 
        broker_id: str, 
        error_type: str, 
        error_message: str, 
        operation: Optional[str] = None
    ):
        """Log broker error"""
        try:
            error = BrokerError(
                broker_id=broker_id,
                error_code="UNKNOWN",
                error_message=error_message,
                error_type=error_type,
                operation=operation
            )
            
            self.error_history.append(error)
            
            # Keep only recent errors
            if len(self.error_history) > self.max_error_history:
                self.error_history = self.error_history[-self.max_error_history:]
                
            # Broadcast error event
            await enhanced_event_bus.publish(
                "broker:error",
                {"error": error.dict()}
            )
            
        except Exception as e:
            logger.error(f"Failed to log error: {e}")
            
    # Background Tasks
    async def _monitor_connections(self):
        """Monitor broker connections and auto-reconnect"""
        while self.is_running:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                for broker_id, connection in self.connections.items():
                    if connection.status == ConnectionStatus.CONNECTED:
                        # Ping broker
                        try:
                            if broker_id in self.adapters:
                                start_time = datetime.utcnow()
                                success = await self.adapters[broker_id].ping()
                                ping_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                                
                                if success:
                                    connection.last_ping = datetime.utcnow()
                                    connection.ping_latency = ping_time
                                else:
                                    # Connection lost
                                    connection.status = ConnectionStatus.ERROR
                                    connection.last_error = "Ping failed"
                                    
                        except Exception as e:
                            logger.warning(f"Ping failed for {broker_id}: {e}")
                            connection.status = ConnectionStatus.ERROR
                            connection.last_error = str(e)
                            
                    elif (connection.status == ConnectionStatus.ERROR and 
                          self.brokers[broker_id].auto_reconnect and
                          connection.reconnect_attempts < 5):
                        # Attempt reconnection
                        logger.info(f"Attempting to reconnect to {broker_id}")
                        await self.connect_broker(broker_id)
                        
            except Exception as e:
                logger.error(f"Connection monitoring error: {e}")
                
    async def _sync_market_data(self):
        """Sync market data from all brokers"""
        while self.is_running:
            try:
                await asyncio.sleep(1)  # Update every second
                
                # Get popular symbols
                popular_symbols = ["EURUSD", "GBPUSD", "USDJPY", "BTCUSD", "ETHUSD"]
                
                for symbol in popular_symbols:
                    market_data = await self.get_market_data(symbol)
                    
                    if market_data:
                        # Broadcast market data update
                        await enhanced_event_bus.publish(
                            "broker:market_data",
                            {"symbol": symbol, "data": market_data}
                        )
                        
            except Exception as e:
                logger.error(f"Market data sync error: {e}")
                await asyncio.sleep(5)
                
    async def _update_performance_stats(self):
        """Update performance statistics"""
        while self.is_running:
            try:
                await asyncio.sleep(300)  # Update every 5 minutes
                
                for broker_id, connection in self.connections.items():
                    # Calculate uptime
                    if connection.connected_at:
                        uptime = (datetime.utcnow() - connection.connected_at).total_seconds()
                        total_time = uptime + (connection.error_count * 60)  # Assume 1 min per error
                        uptime_percentage = (uptime / total_time) * 100 if total_time > 0 else 0
                    else:
                        uptime_percentage = 0
                        
                    # Store performance stats
                    self.performance_stats[broker_id] = {
                        "uptime_percentage": uptime_percentage,
                        "avg_latency": connection.ping_latency or 0,
                        "error_count": connection.error_count,
                        "total_orders": connection.total_orders,
                        "total_trades": connection.total_trades,
                        "last_updated": datetime.utcnow()
                    }
                    
                logger.info("📊 Performance stats updated")
                
            except Exception as e:
                logger.error(f"Performance stats update error: {e}")
                await asyncio.sleep(60) 