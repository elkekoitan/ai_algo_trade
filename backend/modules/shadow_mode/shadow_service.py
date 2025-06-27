"""
Shadow Mode Service
Ana Shadow Mode hizmet orchestrator'ı
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional

from .models import ShadowModeState, ShadowModeStatus, ShadowAlert
from .institutional_tracker import InstitutionalTracker
from .whale_detector import WhaleDetector
from .dark_pool_monitor import DarkPoolMonitor
from .stealth_executor import StealthExecutor
from .pattern_analyzer import PatternAnalyzer

logger = logging.getLogger(__name__)

class ShadowModeService:
    """
    Shadow Mode ana hizmet sınıfı
    Tüm bileşenleri koordine eder
    """
    
    def __init__(self):
        self.state = ShadowModeState(
            status=ShadowModeStatus.INACTIVE,
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
            self.state.status = ShadowModeStatus.ACTIVE
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
            self.state.status = ShadowModeStatus.INACTIVE
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
            
            while self.state.status in [ShadowModeStatus.ACTIVE, ShadowModeStatus.STEALTH, ShadowModeStatus.HUNTING]:
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
            if self.state.status == ShadowModeStatus.INACTIVE:
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
                'status': self.state.status.value,
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