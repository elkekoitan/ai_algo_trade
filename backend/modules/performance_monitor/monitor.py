import asyncio
import time
import psutil
import redis
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict, deque
import json
import logging

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, int]
    active_connections: int
    response_times: Dict[str, float]
    error_rates: Dict[str, float]
    throughput: Dict[str, int]

@dataclass
class TradingMetrics:
    timestamp: datetime
    mt5_latency: float
    order_execution_time: float
    signal_processing_time: float
    active_positions: int
    orders_per_minute: int
    api_calls_per_minute: int
    websocket_connections: int

class PerformanceMonitor:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.metrics_history = deque(maxlen=1000)  # Keep last 1000 metrics
        self.alert_thresholds = {
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'response_time': 2.0,  # seconds
            'error_rate': 5.0,     # percentage
            'mt5_latency': 100.0   # milliseconds
        }
        self.is_monitoring = False
        self.monitoring_task = None
        
    async def start_monitoring(self, interval: int = 5):
        """Start continuous performance monitoring"""
        if self.is_monitoring:
            return
            
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitor_loop(interval))
        logger.info("Performance monitoring started")
        
    async def stop_monitoring(self):
        """Stop performance monitoring"""
        self.is_monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        logger.info("Performance monitoring stopped")
        
    async def _monitor_loop(self, interval: int):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                # Collect system metrics
                system_metrics = await self._collect_system_metrics()
                
                # Collect trading metrics
                trading_metrics = await self._collect_trading_metrics()
                
                # Store metrics
                await self._store_metrics(system_metrics, trading_metrics)
                
                # Check alerts
                await self._check_alerts(system_metrics, trading_metrics)
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(interval)
    
    async def _collect_system_metrics(self) -> PerformanceMetrics:
        """Collect system performance metrics"""
        # CPU usage
        cpu_usage = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_usage = disk.percent
        
        # Network I/O
        network = psutil.net_io_counters()
        network_io = {
            'bytes_sent': network.bytes_sent,
            'bytes_recv': network.bytes_recv,
            'packets_sent': network.packets_sent,
            'packets_recv': network.packets_recv
        }
        
        # Active connections (estimate)
        active_connections = len(psutil.net_connections())
        
        # Get response times from Redis cache
        response_times = await self._get_response_times()
        
        # Get error rates from Redis cache
        error_rates = await self._get_error_rates()
        
        # Get throughput from Redis cache
        throughput = await self._get_throughput()
        
        return PerformanceMetrics(
            timestamp=datetime.utcnow(),
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            disk_usage=disk_usage,
            network_io=network_io,
            active_connections=active_connections,
            response_times=response_times,
            error_rates=error_rates,
            throughput=throughput
        )
    
    async def _collect_trading_metrics(self) -> TradingMetrics:
        """Collect trading-specific metrics"""
        try:
            # Get MT5 latency from cache
            mt5_latency = await self._get_mt5_latency()
            
            # Get order execution times
            order_execution_time = await self._get_avg_order_execution_time()
            
            # Get signal processing times
            signal_processing_time = await self._get_avg_signal_processing_time()
            
            # Get active positions count
            active_positions = await self._get_active_positions_count()
            
            # Get orders per minute
            orders_per_minute = await self._get_orders_per_minute()
            
            # Get API calls per minute
            api_calls_per_minute = await self._get_api_calls_per_minute()
            
            # Get WebSocket connections
            websocket_connections = await self._get_websocket_connections()
            
            return TradingMetrics(
                timestamp=datetime.utcnow(),
                mt5_latency=mt5_latency,
                order_execution_time=order_execution_time,
                signal_processing_time=signal_processing_time,
                active_positions=active_positions,
                orders_per_minute=orders_per_minute,
                api_calls_per_minute=api_calls_per_minute,
                websocket_connections=websocket_connections
            )
        except Exception as e:
            logger.error(f"Error collecting trading metrics: {e}")
            return TradingMetrics(
                timestamp=datetime.utcnow(),
                mt5_latency=0.0,
                order_execution_time=0.0,
                signal_processing_time=0.0,
                active_positions=0,
                orders_per_minute=0,
                api_calls_per_minute=0,
                websocket_connections=0
            )
    
    async def _store_metrics(self, system_metrics: PerformanceMetrics, trading_metrics: TradingMetrics):
        """Store metrics in Redis and memory"""
        # Store in memory
        self.metrics_history.append({
            'system': system_metrics,
            'trading': trading_metrics
        })
        
        # Store in Redis with TTL (24 hours)
        metrics_data = {
            'system': {
                'timestamp': system_metrics.timestamp.isoformat(),
                'cpu_usage': system_metrics.cpu_usage,
                'memory_usage': system_metrics.memory_usage,
                'disk_usage': system_metrics.disk_usage,
                'network_io': system_metrics.network_io,
                'active_connections': system_metrics.active_connections,
                'response_times': system_metrics.response_times,
                'error_rates': system_metrics.error_rates,
                'throughput': system_metrics.throughput
            },
            'trading': {
                'timestamp': trading_metrics.timestamp.isoformat(),
                'mt5_latency': trading_metrics.mt5_latency,
                'order_execution_time': trading_metrics.order_execution_time,
                'signal_processing_time': trading_metrics.signal_processing_time,
                'active_positions': trading_metrics.active_positions,
                'orders_per_minute': trading_metrics.orders_per_minute,
                'api_calls_per_minute': trading_metrics.api_calls_per_minute,
                'websocket_connections': trading_metrics.websocket_connections
            }
        }
        
        timestamp_key = int(datetime.utcnow().timestamp())
        await self.redis.setex(
            f"performance_metrics:{timestamp_key}",
            86400,  # 24 hours TTL
            json.dumps(metrics_data)
        )
    
    async def _check_alerts(self, system_metrics: PerformanceMetrics, trading_metrics: TradingMetrics):
        """Check if any metrics exceed alert thresholds"""
        alerts = []
        
        # System alerts
        if system_metrics.cpu_usage > self.alert_thresholds['cpu_usage']:
            alerts.append({
                'type': 'HIGH_CPU_USAGE',
                'value': system_metrics.cpu_usage,
                'threshold': self.alert_thresholds['cpu_usage'],
                'severity': 'WARNING'
            })
        
        if system_metrics.memory_usage > self.alert_thresholds['memory_usage']:
            alerts.append({
                'type': 'HIGH_MEMORY_USAGE',
                'value': system_metrics.memory_usage,
                'threshold': self.alert_thresholds['memory_usage'],
                'severity': 'CRITICAL'
            })
        
        # Trading alerts
        if trading_metrics.mt5_latency > self.alert_thresholds['mt5_latency']:
            alerts.append({
                'type': 'HIGH_MT5_LATENCY',
                'value': trading_metrics.mt5_latency,
                'threshold': self.alert_thresholds['mt5_latency'],
                'severity': 'WARNING'
            })
        
        # Response time alerts
        for endpoint, response_time in system_metrics.response_times.items():
            if response_time > self.alert_thresholds['response_time']:
                alerts.append({
                    'type': 'SLOW_RESPONSE_TIME',
                    'endpoint': endpoint,
                    'value': response_time,
                    'threshold': self.alert_thresholds['response_time'],
                    'severity': 'WARNING'
                })
        
        # Error rate alerts
        for endpoint, error_rate in system_metrics.error_rates.items():
            if error_rate > self.alert_thresholds['error_rate']:
                alerts.append({
                    'type': 'HIGH_ERROR_RATE',
                    'endpoint': endpoint,
                    'value': error_rate,
                    'threshold': self.alert_thresholds['error_rate'],
                    'severity': 'CRITICAL'
                })
        
        # Send alerts if any
        if alerts:
            await self._send_alerts(alerts)
    
    async def _send_alerts(self, alerts: List[Dict]):
        """Send performance alerts"""
        for alert in alerts:
            # Store alert in Redis
            alert_data = {
                **alert,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            await self.redis.lpush(
                "performance_alerts",
                json.dumps(alert_data)
            )
            
            # Keep only last 100 alerts
            await self.redis.ltrim("performance_alerts", 0, 99)
            
            logger.warning(f"Performance Alert: {alert}")
    
    # Helper methods for getting cached metrics
    async def _get_response_times(self) -> Dict[str, float]:
        """Get average response times for endpoints"""
        try:
            data = await self.redis.hgetall("response_times")
            return {k.decode(): float(v.decode()) for k, v in data.items()} if data else {}
        except:
            return {}
    
    async def _get_error_rates(self) -> Dict[str, float]:
        """Get error rates for endpoints"""
        try:
            data = await self.redis.hgetall("error_rates")
            return {k.decode(): float(v.decode()) for k, v in data.items()} if data else {}
        except:
            return {}
    
    async def _get_throughput(self) -> Dict[str, int]:
        """Get throughput for endpoints"""
        try:
            data = await self.redis.hgetall("throughput")
            return {k.decode(): int(v.decode()) for k, v in data.items()} if data else {}
        except:
            return {}
    
    async def _get_mt5_latency(self) -> float:
        """Get current MT5 latency"""
        try:
            latency = await self.redis.get("mt5_latency")
            return float(latency.decode()) if latency else 0.0
        except:
            return 0.0
    
    async def _get_avg_order_execution_time(self) -> float:
        """Get average order execution time"""
        try:
            time_data = await self.redis.get("avg_order_execution_time")
            return float(time_data.decode()) if time_data else 0.0
        except:
            return 0.0
    
    async def _get_avg_signal_processing_time(self) -> float:
        """Get average signal processing time"""
        try:
            time_data = await self.redis.get("avg_signal_processing_time")
            return float(time_data.decode()) if time_data else 0.0
        except:
            return 0.0
    
    async def _get_active_positions_count(self) -> int:
        """Get active positions count"""
        try:
            count = await self.redis.get("active_positions_count")
            return int(count.decode()) if count else 0
        except:
            return 0
    
    async def _get_orders_per_minute(self) -> int:
        """Get orders per minute"""
        try:
            count = await self.redis.get("orders_per_minute")
            return int(count.decode()) if count else 0
        except:
            return 0
    
    async def _get_api_calls_per_minute(self) -> int:
        """Get API calls per minute"""
        try:
            count = await self.redis.get("api_calls_per_minute")
            return int(count.decode()) if count else 0
        except:
            return 0
    
    async def _get_websocket_connections(self) -> int:
        """Get active WebSocket connections"""
        try:
            count = await self.redis.get("websocket_connections")
            return int(count.decode()) if count else 0
        except:
            return 0
    
    async def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        if not self.metrics_history:
            return {}
        
        latest = self.metrics_history[-1]
        
        return {
            'system': {
                'cpu_usage': latest['system'].cpu_usage,
                'memory_usage': latest['system'].memory_usage,
                'disk_usage': latest['system'].disk_usage,
                'active_connections': latest['system'].active_connections
            },
            'trading': {
                'mt5_latency': latest['trading'].mt5_latency,
                'order_execution_time': latest['trading'].order_execution_time,
                'active_positions': latest['trading'].active_positions,
                'orders_per_minute': latest['trading'].orders_per_minute
            },
            'alerts': await self._get_recent_alerts()
        }
    
    async def _get_recent_alerts(self) -> List[Dict]:
        """Get recent performance alerts"""
        try:
            alerts_data = await self.redis.lrange("performance_alerts", 0, 9)  # Last 10 alerts
            return [json.loads(alert.decode()) for alert in alerts_data]
        except:
            return []

# Global performance monitor instance
performance_monitor = None

async def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance"""
    global performance_monitor
    if performance_monitor is None:
        import redis.asyncio as redis
        redis_client = redis.Redis(host='localhost', port=6379, db=2)
        performance_monitor = PerformanceMonitor(redis_client)
        await performance_monitor.start_monitoring()
    return performance_monitor 