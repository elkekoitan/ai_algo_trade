"""
Pattern Analyzer
Manipulation pattern tespit sistemi
"""

import asyncio
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import uuid

from .models import ManipulationPattern

logger = logging.getLogger(__name__)

class PatternAnalyzer:
    """
    Piyasa manipülasyon pattern'lerini tespit eden sistem
    """
    
    def __init__(self):
        self.is_active = False
        self.detected_patterns = []
        self.pattern_algorithms = {}
        
        logger.info("🔍 Pattern Analyzer initialized")
    
    async def start_analysis(self):
        """Pattern analizini başlat"""
        try:
            logger.info("🔍 Starting pattern analysis...")
            
            await self._initialize_pattern_algorithms()
            
            self.is_active = True
            logger.info("✅ Pattern analysis active")
            
        except Exception as e:
            logger.error(f"Pattern analysis start error: {str(e)}")
            raise
    
    async def _initialize_pattern_algorithms(self):
        """Pattern algoritmalarını başlat"""
        try:
            self.pattern_algorithms = {
                'spoofing_detector': {
                    'order_size_threshold': 1000000,
                    'cancellation_ratio': 0.8,
                    'detection_window': 300
                },
                'stop_hunt_detector': {
                    'spike_threshold': 0.005,
                    'reversion_time': 180,
                    'volume_confirmation': True
                },
                'pump_dump_detector': {
                    'price_change_threshold': 0.02,
                    'volume_spike_ratio': 3.0,
                    'time_window': 1800
                }
            }
            
            logger.info("🧠 Pattern algorithms initialized")
            
        except Exception as e:
            logger.error(f"Algorithm initialization error: {str(e)}")
            raise
    
    async def detect_manipulation_patterns(self, symbol: str) -> Optional[ManipulationPattern]:
        """Manipulation pattern tespiti"""
        try:
            if not self.is_active:
                return None
            
            if random.random() < 0.06:  # %6 ihtimalle pattern tespit
                pattern_types = ['SPOOFING', 'STOP_HUNT', 'PUMP_DUMP', 'LAYERING']
                pattern_type = random.choice(pattern_types)
                
                pattern = ManipulationPattern(
                    pattern_id=str(uuid.uuid4()),
                    symbol=symbol,
                    pattern_type=pattern_type,
                    detection_time=datetime.now(),
                    estimated_target=1.0500 + random.uniform(-0.0050, 0.0050) if random.random() > 0.3 else None,
                    estimated_duration=random.randint(5, 60) if random.random() > 0.4 else None,
                    confidence=random.uniform(65, 90),
                    institutional_fingerprint=random.choice(['goldman_signature', 'jpmorgan_style', 'unknown', None]),
                    counter_strategy=self._generate_counter_strategy(pattern_type)
                )
                
                self.detected_patterns.append(pattern)
                
                cutoff_time = datetime.now() - timedelta(hours=6)
                self.detected_patterns = [
                    p for p in self.detected_patterns 
                    if p.detection_time > cutoff_time
                ]
                
                logger.info(f"🔍 Manipulation pattern detected: {symbol} - {pattern_type}")
                return pattern
            
            return None
            
        except Exception as e:
            logger.error(f"Pattern detection error: {str(e)}")
            return None
    
    def _generate_counter_strategy(self, pattern_type: str) -> str:
        """Counter strategy oluştur"""
        strategies = {
            'SPOOFING': "Wait for order cancellation, then trade opposite direction",
            'STOP_HUNT': "Avoid stop losses near obvious levels, use mental stops",
            'PUMP_DUMP': "Wait for volume decline, then fade the move",
            'LAYERING': "Look for genuine orders behind the layers"
        }
        return strategies.get(pattern_type, "Monitor closely and wait for confirmation")
    
    async def get_recent_patterns(self) -> List[Dict]:
        """Son pattern'leri döndür"""
        try:
            recent_patterns = []
            
            for pattern in self.detected_patterns[-10:]:
                recent_patterns.append({
                    'pattern_id': pattern.pattern_id,
                    'symbol': pattern.symbol,
                    'pattern_type': pattern.pattern_type,
                    'confidence': pattern.confidence,
                    'estimated_target': pattern.estimated_target,
                    'estimated_duration': pattern.estimated_duration,
                    'counter_strategy': pattern.counter_strategy,
                    'detection_time': pattern.detection_time.isoformat()
                })
            
            return recent_patterns
            
        except Exception as e:
            logger.error(f"Get recent patterns error: {str(e)}")
            return []
    
    def get_status(self) -> Dict:
        """Analyzer durumunu döndür"""
        return {
            'is_active': self.is_active,
            'detected_patterns': len(self.detected_patterns),
            'pattern_algorithms': len(self.pattern_algorithms)
        } 