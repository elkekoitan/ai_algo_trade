"""
Shadow Mode Service
Ana Shadow Mode hizmet orchestrator'ı
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import uuid
try:
    import numpy as np
    import pandas as pd
except ImportError:
    # Mock numpy and pandas if not available
    class MockNP:
        def mean(self, values): 
            return sum(values) / len(values) if values else 0
        def random(self):
            import random
            return type('Random', (), {'uniform': lambda a, b: random.uniform(a, b)})()
    
    class MockPD:
        def DataFrame(self, data):
            return type('DataFrame', (), {
                'empty': len(data) == 0 if isinstance(data, list) else False,
                'rolling': lambda window: type('Rolling', (), {
                    'mean': lambda: data,
                    'std': lambda: data
                })(),
                'pct_change': lambda: data,
                'groupby': lambda col: [(0, data)],
                'tail': lambda n: data[-n:] if isinstance(data, list) else data
            })()
    
    np = MockNP()
    pd = MockPD()

from dataclasses import dataclass

from .models import (
    WhaleDetection, WhaleSize, DarkPoolActivity, InstitutionalFlow, 
    InstitutionalType, OrderType, StealthOrder, ShadowAnalytics,
    WhaleAlert, ShadowModeStatus, ShadowModeState, ShadowAlert, ShadowMetrics, ShadowModeConfig,
    ShadowModeStatusResponse
)
from .institutional_tracker import InstitutionalTracker
from .whale_detector import WhaleDetector
from .dark_pool_monitor import DarkPoolMonitor
from .stealth_executor import StealthExecutor
from .pattern_analyzer import PatternAnalyzer
from ..mt5_integration.service import MT5Service

logger = logging.getLogger(__name__)

@dataclass
class VolumeAnalysis:
    symbol: str
    volume_sma_10: float
    volume_sma_50: float
    volume_ratio: float
    unusual_volume: bool
    volume_profile: Dict[str, float]

class ShadowModeService:
    """
    Shadow Mode ana hizmet sınıfı
    Tüm bileşenleri koordine eder
    """
    
    def __init__(self, mt5_service: MT5Service):
        self.mt5_service = mt5_service
        self.whale_threshold_min = 100000  # $100k minimum for whale detection
        self.dark_pool_threshold = 0.15  # 15% dark pool activity threshold
        self.institutional_flow_window = 60  # 60 minutes window
        
        # In-memory storage for real-time data
        self.whale_detections: List[WhaleDetection] = []
        self.dark_pool_activities: List[DarkPoolActivity] = []
        self.institutional_flows: List[InstitutionalFlow] = []
        self.stealth_orders: List[StealthOrder] = []
        
        # Analysis caches
        self.volume_cache: Dict[str, VolumeAnalysis] = {}
        self.last_analysis_time: Dict[str, datetime] = {}
        
        self.state = ShadowModeState(
            status="inactive",
            stealth_level=5,
            last_update=datetime.now()
        )
        
        # Initialize components
        self.institutional_tracker = InstitutionalTracker()
        self.whale_detector = WhaleDetector()
        self.dark_pool_monitor = DarkPoolMonitor()
        self.stealth_executor = StealthExecutor()
        self.pattern_analyzer = PatternAnalyzer()
        
        self.monitoring_task = None
        
        logger.info("🥷 Shadow Mode Service initialized")
    
    async def activate_shadow_mode(self, stealth_level: int = 5) -> Dict:
        """Shadow Mode'u aktifleştir"""
        try:
            logger.info(f"🥷 Activating Shadow Mode - Stealth Level: {stealth_level}")
            
            # Update state
            self.state.status = "active"
            self.state.stealth_level = stealth_level
            self.state.last_update = datetime.now()
            
            # Start all components
            await self.institutional_tracker.start_tracking()
            await self.whale_detector.start_detection()
            await self.dark_pool_monitor.start_monitoring()
            await self.stealth_executor.start_execution_engine()
            await self.pattern_analyzer.start_analysis()
            
            # Start monitoring loop
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            logger.info("✅ Shadow Mode activated successfully")
            
            return {
                'status': 'activated',
                'stealth_level': stealth_level,
                'message': 'Büyük oyuncuların gölgesinde hareket etmeye başladık',
                'components_active': 5
            }
            
        except Exception as e:
            logger.error(f"Shadow Mode activation error: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    async def deactivate_shadow_mode(self) -> Dict:
        """Shadow Mode'u deaktifleştir"""
        try:
            logger.info("🥷 Deactivating Shadow Mode...")
            
            # Update state
            self.state.status = "inactive"
            self.state.last_update = datetime.now()
            
            # Stop monitoring loop
            if self.monitoring_task:
                self.monitoring_task.cancel()
                self.monitoring_task = None
            
            # Stop all components
            await self.institutional_tracker.stop_tracking()
            await self.whale_detector.stop_detection()
            await self.dark_pool_monitor.stop_monitoring()
            
            logger.info("✅ Shadow Mode deactivated")
            
            return {
                'status': 'deactivated',
                'message': 'Shadow Mode kapatıldı'
            }
            
        except Exception as e:
            logger.error(f"Shadow Mode deactivation error: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    async def _monitoring_loop(self):
        """Ana izleme döngüsü"""
        try:
            logger.info("🔍 Shadow Mode monitoring loop started")
            
            while self.state.status in ["active", "stealth", "hunting"]:
                # Monitor major symbols
                symbols = self.state.config.symbols_to_monitor
                
                for symbol in symbols:
                    # Detect institutional flows
                    flow = await self.institutional_tracker.detect_institutional_flow(symbol)
                    if flow:
                        self.state.active_flows.append(flow)
                        await self._generate_alert('INSTITUTIONAL_FLOW', f'Kurumsal akış tespit edildi: {symbol}', symbol)
                    
                    # Detect whales
                    whale = await self.whale_detector.detect_whale_activity(symbol)
                    if whale:
                        self.state.active_detections.append(whale)
                        await self._generate_alert('WHALE_DETECTED', f'Whale tespit edildi: {symbol} - {whale.whale_size.value}', symbol)
                    
                    # Monitor dark pools
                    dark_activity = await self.dark_pool_monitor.detect_dark_pool_activity(symbol)
                    if dark_activity:
                        self.state.dark_pool_activities.append(dark_activity)
                        await self._generate_alert('DARK_POOL', f'Dark pool aktivitesi: {symbol}', symbol)
                    
                    # Detect manipulation patterns
                    pattern = await self.pattern_analyzer.detect_manipulation_patterns(symbol)
                    if pattern:
                        self.state.manipulation_patterns.append(pattern)
                        await self._generate_alert('MANIPULATION', f'Manipulation pattern: {symbol} - {pattern.pattern_type}', symbol)
                
                # Update metrics
                await self._update_metrics()
                
                # Update state timestamp
                self.state.last_update = datetime.now()
                
                # Wait before next cycle
                await asyncio.sleep(5)  # 5 second monitoring cycle
                
        except asyncio.CancelledError:
            logger.info("🛑 Shadow Mode monitoring loop cancelled")
        except Exception as e:
            logger.error(f"Monitoring loop error: {str(e)}")
    
    async def _generate_alert(self, alert_type: str, message: str, symbol: str = None):
        """Alert oluştur"""
        try:
            alert = ShadowAlert(
                alert_id=f"shadow_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{alert_type.lower()}",
                alert_type=alert_type,
                priority='HIGH' if alert_type in ['WHALE_DETECTED', 'MANIPULATION'] else 'MEDIUM',
                title=f"🥷 Shadow Alert: {alert_type}",
                message=message,
                symbol=symbol,
                stealth_required=self.state.stealth_level >= 7,
                created_at=datetime.now()
            )
            
            self.state.recent_alerts.append(alert)
            
            # Keep only recent alerts
            if len(self.state.recent_alerts) > 50:
                self.state.recent_alerts = self.state.recent_alerts[-50:]
            
            logger.info(f"🚨 Shadow Alert: {message}")
            
        except Exception as e:
            logger.error(f"Alert generation error: {str(e)}")
    
    async def _update_metrics(self):
        """Metrikleri güncelle"""
        try:
            self.state.metrics.total_whales_detected = len(self.state.active_detections)
            self.state.metrics.institutions_monitored = len(set(
                flow.institution_type for flow in self.state.active_flows
            ))
            
            # Calculate detection accuracy (simulated)
            if self.state.active_detections:
                high_confidence_detections = len([
                    d for d in self.state.active_detections if d.confidence > 80
                ])
                self.state.metrics.detection_accuracy = (
                    high_confidence_detections / len(self.state.active_detections)
                ) * 100
            
            # Calculate stealth success rate
            stealth_orders = [o for o in self.state.stealth_orders if o.stealth_level >= 7]
            if stealth_orders:
                successful_stealth = len([o for o in stealth_orders if o.status == "COMPLETED"])
                self.state.metrics.stealth_success_rate = (
                    successful_stealth / len(stealth_orders)
                ) * 100
            
        except Exception as e:
            logger.error(f"Metrics update error: {str(e)}")
    
    async def create_stealth_order(self, symbol: str, side: str, quantity: float) -> Dict:
        """Gizli emir oluştur"""
        try:
            if self.state.status == "inactive":
                return {'error': 'Shadow Mode is not active'}
            
            stealth_order = await self.stealth_executor.create_stealth_order(
                symbol=symbol,
                side=side,
                total_quantity=quantity,
                stealth_level=self.state.stealth_level
            )
            
            if stealth_order:
                self.state.stealth_orders.append(stealth_order)
                await self._generate_alert(
                    'STEALTH_ORDER', 
                    f'Gizli emir oluşturuldu: {symbol} {side} {quantity}',
                    symbol
                )
                
                return {
                    'status': 'created',
                    'order_id': stealth_order.order_id,
                    'stealth_level': stealth_order.stealth_level
                }
            else:
                return {'error': 'Failed to create stealth order'}
                
        except Exception as e:
            logger.error(f"Stealth order creation error: {str(e)}")
            return {'error': str(e)}
    
    async def get_shadow_state(self) -> Dict:
        """Shadow Mode durumunu döndür"""
        try:
            return {
                'status': self.state.status,
                'stealth_level': self.state.stealth_level,
                'active_components': {
                    'institutional_tracker': self.institutional_tracker.get_status(),
                    'whale_detector': self.whale_detector.get_status(),
                    'dark_pool_monitor': self.dark_pool_monitor.get_status(),
                    'stealth_executor': self.stealth_executor.get_status(),
                    'pattern_analyzer': self.pattern_analyzer.get_status()
                },
                'recent_activity': {
                    'whale_detections': len(self.state.active_detections),
                    'institutional_flows': len(self.state.active_flows),
                    'dark_pool_activities': len(self.state.dark_pool_activities),
                    'manipulation_patterns': len(self.state.manipulation_patterns),
                    'stealth_orders': len(self.state.stealth_orders)
                },
                'metrics': {
                    'total_whales_detected': self.state.metrics.total_whales_detected,
                    'detection_accuracy': self.state.metrics.detection_accuracy,
                    'stealth_success_rate': self.state.metrics.stealth_success_rate,
                    'institutions_monitored': self.state.metrics.institutions_monitored
                },
                'last_update': self.state.last_update.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Get shadow state error: {str(e)}")
            return {'error': str(e)}
    
    async def get_recent_alerts(self) -> List[Dict]:
        """Son alertleri döndür"""
        try:
            alerts = []
            for alert in self.state.recent_alerts[-10:]:
                alerts.append({
                    'alert_id': alert.alert_id,
                    'type': alert.alert_type,
                    'priority': alert.priority,
                    'title': alert.title,
                    'message': alert.message,
                    'symbol': alert.symbol,
                    'stealth_required': alert.stealth_required,
                    'created_at': alert.created_at.isoformat()
                })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Get recent alerts error: {str(e)}")
            return []
    
    async def get_whale_detections(self) -> List[Dict]:
        """Whale tespitlerini döndür"""
        try:
            return await self.whale_detector.get_active_whales()
        except Exception as e:
            logger.error(f"Get whale detections error: {str(e)}")
            return []
    
    async def get_dark_pool_summary(self) -> Dict:
        """Dark pool özetini döndür"""
        try:
            return await self.dark_pool_monitor.get_activity_summary()
        except Exception as e:
            logger.error(f"Get dark pool summary error: {str(e)}")
            return {}
    
    async def get_institutional_flow_summary(self) -> Dict:
        """Kurumsal akış özetini döndür"""
        try:
            return await self.institutional_tracker.get_flow_summary()
        except Exception as e:
            logger.error(f"Get institutional flow summary error: {str(e)}")
            return {} 

    async def detect_whales(self, symbol: str = "BTCUSD") -> List[WhaleDetection]:
        """Detect whale activity based on volume and value analysis"""
        try:
            # Get recent tick data
            ticks = await self.mt5_service.get_tick_data(symbol, 1000)
            if not ticks:
                return []

            # Convert to DataFrame for analysis
            df = pd.DataFrame(ticks)
            if df.empty:
                return []

            # Calculate rolling volume metrics
            df['volume_sma'] = df['volume'].rolling(window=10).mean()
            df['volume_std'] = df['volume'].rolling(window=10).std()
            df['volume_zscore'] = (df['volume'] - df['volume_sma']) / df['volume_std']
            
            # Calculate trade value
            df['trade_value'] = df['volume'] * df['bid']  # Using bid price
            
            # Whale detection criteria
            whale_mask = (
                (df['trade_value'] >= self.whale_threshold_min) &  # Minimum value
                (df['volume_zscore'] > 2.0) &  # Unusual volume
                (df['volume'] > df['volume_sma'] * 3)  # 3x average volume
            )
            
            whale_trades = df[whale_mask].tail(10)  # Latest 10 whale trades
            
            whales = []
            for _, trade in whale_trades.iterrows():
                whale_size = self._classify_whale_size(trade['trade_value'])
                confidence = min(0.95, trade['volume_zscore'] / 10.0)
                impact_score = min(100, trade['volume_zscore'] * 10)
                
                # Determine order type based on price movement
                order_type = OrderType.BUY if trade['ask'] > trade['bid'] else OrderType.SELL
                
                whale = WhaleDetection(
                    id=str(uuid.uuid4()),
                    timestamp=datetime.fromtimestamp(trade['time']),
                    symbol=symbol,
                    size=whale_size,
                    volume=float(trade['volume']),
                    value=float(trade['trade_value']),
                    order_type=order_type,
                    price=float(trade['bid']),
                    confidence=float(confidence),
                    impact_score=float(impact_score),
                    spread_analysis={
                        "spread": float(trade['ask'] - trade['bid']),
                        "spread_ratio": float((trade['ask'] - trade['bid']) / trade['bid'])
                    },
                    volume_profile={
                        "volume_zscore": float(trade['volume_zscore']),
                        "volume_ratio": float(trade['volume'] / trade['volume_sma'])
                    },
                    time_analysis={
                        "time_of_day": trade['time'] % 86400,  # Seconds since midnight
                        "market_session": self._get_market_session(trade['time'])
                    }
                )
                whales.append(whale)
            
            # Store in memory
            self.whale_detections.extend(whales)
            # Keep only last 24 hours
            cutoff_time = datetime.now() - timedelta(hours=24)
            self.whale_detections = [w for w in self.whale_detections if w.timestamp > cutoff_time]
            
            return whales
            
        except Exception as e:
            logger.error(f"Error detecting whales: {e}")
            return []

    async def monitor_dark_pools(self, symbol: str = "BTCUSD") -> List[DarkPoolActivity]:
        """Monitor dark pool activity and hidden liquidity"""
        try:
            # Get order book data
            book_data = await self.mt5_service.get_order_book(symbol)
            if not book_data:
                return []

            # Get recent trade data
            ticks = await self.mt5_service.get_tick_data(symbol, 500)
            if not ticks:
                return []

            df = pd.DataFrame(ticks)
            
            # Calculate visible vs hidden volume indicators
            visible_volume = df['volume'].sum()
            
            # Estimate hidden volume based on:
            # 1. Price gaps without corresponding volume
            # 2. Volume clustering analysis
            # 3. Spread patterns
            
            df['price_change'] = df['bid'].pct_change()
            df['volume_change'] = df['volume'].pct_change()
            
            # Find price movements without proportional volume
            hidden_volume_indicator = df['price_change'].abs() > df['volume_change'].abs() * 0.5
            estimated_hidden_volume = df[hidden_volume_indicator]['volume'].sum() * 2
            
            dark_pool_ratio = min(100, (estimated_hidden_volume / visible_volume) * 100) if visible_volume > 0 else 0
            
            # Only report if significant dark pool activity
            if dark_pool_ratio > self.dark_pool_threshold:
                activity = DarkPoolActivity(
                    id=str(uuid.uuid4()),
                    timestamp=datetime.now(),
                    symbol=symbol,
                    hidden_volume=float(estimated_hidden_volume),
                    visible_volume=float(visible_volume),
                    dark_pool_ratio=float(dark_pool_ratio),
                    liquidity_depth=float(len(book_data.get('bids', [])) + len(book_data.get('asks', []))),
                    execution_quality=float(np.random.uniform(75, 95)),  # Simulated for now
                    fragmentation_score=float(dark_pool_ratio / 2),
                    price_improvement=float(np.random.uniform(0.1, 0.5))  # Simulated
                )
                
                self.dark_pool_activities.append(activity)
                return [activity]
            
            return []
            
        except Exception as e:
            logger.error(f"Error monitoring dark pools: {e}")
            return []

    async def track_institutional_flows(self, symbol: str = "BTCUSD") -> List[InstitutionalFlow]:
        """Track institutional vs retail trading flows"""
        try:
            # Get extended timeframe data
            ticks = await self.mt5_service.get_tick_data(symbol, 2000)
            if not ticks:
                return []

            df = pd.DataFrame(ticks)
            
            # Institutional flow indicators:
            # 1. Large block sizes
            # 2. Consistent direction over time
            # 3. Off-market timing
            # 4. Low frequency, high volume
            
            # Calculate flow metrics
            df['volume_ma'] = df['volume'].rolling(window=50).mean()
            df['is_large_block'] = df['volume'] > df['volume_ma'] * 5
            df['hour'] = pd.to_datetime(df['time'], unit='s').dt.hour
            df['is_institutional_hour'] = df['hour'].isin([22, 23, 0, 1, 2, 3])  # Off-hours
            
            # Group trades by time windows
            df['time_group'] = (df['time'] // 300) * 300  # 5-minute groups
            
            flows = []
            for time_group, group in df.groupby('time_group'):
                if len(group) < 5:  # Need sufficient trades
                    continue
                
                # Calculate flow characteristics
                large_blocks = group[group['is_large_block']]
                institutional_trades = group[group['is_institutional_hour']]
                
                if len(large_blocks) > 0:
                    # Determine flow direction
                    buy_volume = large_blocks[large_blocks['ask'] > large_blocks['bid']]['volume'].sum()
                    sell_volume = large_blocks[large_blocks['ask'] <= large_blocks['bid']]['volume'].sum()
                    
                    if buy_volume > sell_volume * 1.5:
                        flow_direction = OrderType.BUY
                        flow_strength = min(100, (buy_volume / (buy_volume + sell_volume)) * 100)
                    elif sell_volume > buy_volume * 1.5:
                        flow_direction = OrderType.SELL
                        flow_strength = min(100, (sell_volume / (buy_volume + sell_volume)) * 100)
                    else:
                        continue  # No clear direction
                    
                    # Estimate institution type based on patterns
                    institution_type = self._classify_institution_type(large_blocks)
                    
                    flow = InstitutionalFlow(
                        id=str(uuid.uuid4()),
                        timestamp=datetime.fromtimestamp(time_group),
                        symbol=symbol,
                        institution_type=institution_type,
                        flow_direction=flow_direction,
                        flow_strength=float(flow_strength),
                        volume_estimate=float(large_blocks['volume'].sum()),
                        duration_minutes=5,  # 5-minute window
                        retail_vs_institutional=float(len(institutional_trades) / len(group)),
                        momentum_score=float(min(100, flow_strength * 1.2)),
                        correlation_with_price=float(np.random.uniform(0.6, 0.9))  # Simulated
                    )
                    flows.append(flow)
            
            # Store and clean old data
            self.institutional_flows.extend(flows[-10:])  # Keep last 10 flows
            cutoff_time = datetime.now() - timedelta(hours=4)
            self.institutional_flows = [f for f in self.institutional_flows if f.timestamp > cutoff_time]
            
            return flows[-5:]  # Return latest 5 flows
            
        except Exception as e:
            logger.error(f"Error tracking institutional flows: {e}")
            return []

    async def generate_shadow_analytics(self, symbol: str = "BTCUSD") -> ShadowAnalytics:
        """Generate comprehensive shadow analytics"""
        try:
            # Get recent detections
            recent_whales = [w for w in self.whale_detections if w.timestamp > datetime.now() - timedelta(hours=24)]
            recent_dark_pools = [d for d in self.dark_pool_activities if d.timestamp > datetime.now() - timedelta(hours=4)]
            recent_flows = [f for f in self.institutional_flows if f.timestamp > datetime.now() - timedelta(hours=4)]
            
            # Calculate whale metrics
            whale_activity_score = min(100, len(recent_whales) * 5)
            whale_sentiment = self._calculate_whale_sentiment(recent_whales)
            whale_volume_24h = sum(w.volume for w in recent_whales)
            
            # Calculate dark pool metrics
            dark_pool_intensity = np.mean([d.dark_pool_ratio for d in recent_dark_pools]) if recent_dark_pools else 0
            hidden_liquidity = sum(d.hidden_volume for d in recent_dark_pools)
            market_fragmentation = np.mean([d.fragmentation_score for d in recent_dark_pools]) if recent_dark_pools else 0
            
            # Calculate institutional metrics
            institutional_pressure = np.mean([f.flow_strength for f in recent_flows]) if recent_flows else 0
            smart_money_flow = self._calculate_smart_money_flow(recent_flows)
            retail_sentiment = 100 - institutional_pressure  # Inverse relationship
            
            # Market impact predictions
            predicted_impact = min(100, (whale_activity_score + institutional_pressure) / 2)
            volatility_forecast = min(100, dark_pool_intensity + whale_activity_score / 2)
            trend_strength = abs(smart_money_flow)
            
            analytics = ShadowAnalytics(
                timestamp=datetime.now(),
                symbol=symbol,
                whale_activity_score=float(whale_activity_score),
                whale_sentiment=float(whale_sentiment),
                whale_volume_24h=float(whale_volume_24h),
                dark_pool_intensity=float(dark_pool_intensity),
                hidden_liquidity=float(hidden_liquidity),
                market_fragmentation=float(market_fragmentation),
                institutional_pressure=float(institutional_pressure),
                smart_money_flow=float(smart_money_flow),
                retail_sentiment=float(retail_sentiment),
                predicted_impact=float(predicted_impact),
                volatility_forecast=float(volatility_forecast),
                trend_strength=float(trend_strength)
            )
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error generating shadow analytics: {e}")
            return ShadowAnalytics(
                timestamp=datetime.now(),
                symbol=symbol,
                whale_activity_score=0,
                whale_sentiment=0,
                whale_volume_24h=0,
                dark_pool_intensity=0,
                hidden_liquidity=0,
                market_fragmentation=0,
                institutional_pressure=0,
                smart_money_flow=0,
                retail_sentiment=50,
                predicted_impact=0,
                volatility_forecast=0,
                trend_strength=0
            )

    async def get_shadow_status(self) -> ShadowModeStatusResponse:
        """Get current Shadow Mode system status"""
        try:
            # Calculate 24h metrics
            cutoff_time = datetime.now() - timedelta(hours=24)
            whales_24h = len([w for w in self.whale_detections if w.timestamp > cutoff_time])
            
            # Count active components
            dark_pools_monitored = len(set(d.symbol for d in self.dark_pool_activities))
            flows_tracked = len(self.institutional_flows)
            stealth_active = len([o for o in self.stealth_orders if o.status != "completed"])
            
            # Calculate system health (0-100)
            system_health = 100.0
            if self.state.status == "inactive":
                system_health = 0.0
            elif self.state.status == "active":
                system_health = 85.0
            elif self.state.status == "stealth":
                system_health = 95.0
            
            return ShadowModeStatusResponse(
                status=self.state.status,
                whales_detected_24h=whales_24h,
                dark_pools_monitored=dark_pools_monitored,
                institutional_flows_tracked=flows_tracked,
                stealth_orders_active=stealth_active,
                system_health=system_health,
                last_update=self.state.last_update
            )
        except Exception as e:
            logger.error(f"Error getting shadow status: {e}")
            raise

    # Helper methods
    def _classify_whale_size(self, value: float) -> WhaleSize:
        """Classify whale size based on trade value"""
        if value >= 5000000:  # $5M+
            return WhaleSize.MASSIVE
        elif value >= 1000000:  # $1M+
            return WhaleSize.LARGE
        elif value >= 500000:  # $500k+
            return WhaleSize.MEDIUM
        else:  # $100k+
            return WhaleSize.SMALL

    def _classify_institution_type(self, trades_df) -> InstitutionalType:
        """Classify institution type based on trading patterns"""
        # Simplified classification logic
        avg_volume = trades_df['volume'].mean()
        if avg_volume > 100:
            return InstitutionalType.INVESTMENT_BANK
        elif avg_volume > 50:
            return InstitutionalType.HEDGE_FUND
        elif avg_volume > 20:
            return InstitutionalType.PENSION_FUND
        else:
            return InstitutionalType.RETAIL_CLUSTER

    def _get_market_session(self, timestamp: float) -> str:
        """Get market session based on timestamp"""
        hour = datetime.fromtimestamp(timestamp).hour
        if 22 <= hour or hour < 6:
            return "asian"
        elif 6 <= hour < 14:
            return "london"
        else:
            return "new_york"

    def _calculate_whale_sentiment(self, whales: List[WhaleDetection]) -> float:
        """Calculate overall whale sentiment (-100 to +100)"""
        if not whales:
            return 0
        
        buy_volume = sum(w.volume for w in whales if w.order_type == OrderType.BUY)
        sell_volume = sum(w.volume for w in whales if w.order_type == OrderType.SELL)
        total_volume = buy_volume + sell_volume
        
        if total_volume == 0:
            return 0
        
        sentiment = ((buy_volume - sell_volume) / total_volume) * 100
        return max(-100, min(100, sentiment))

    def _calculate_smart_money_flow(self, flows: List[InstitutionalFlow]) -> float:
        """Calculate smart money flow direction (-100 to +100)"""
        if not flows:
            return 0
        
        buy_strength = sum(f.flow_strength for f in flows if f.flow_direction == OrderType.BUY)
        sell_strength = sum(f.flow_strength for f in flows if f.flow_direction == OrderType.SELL)
        total_strength = buy_strength + sell_strength
        
        if total_strength == 0:
            return 0
        
        flow = ((buy_strength - sell_strength) / total_strength) * 100
        return max(-100, min(100, flow)) 