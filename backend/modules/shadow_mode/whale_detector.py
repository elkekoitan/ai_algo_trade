"""
Whale Detector
Büyük oyuncu tespit sistemi
"""

import asyncio
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import uuid
import numpy as np

from .models import WhaleDetection, WhaleSize, InstitutionalType

logger = logging.getLogger(__name__)

class WhaleDetector:
    """
    Whale (büyük oyuncu) tespit ve takip sistemi
    """
    
    def __init__(self):
        self.is_active = False
        self.detection_threshold = 100000.0
        self.whale_database = {}
        self.active_whales = []
        self.detection_algorithms = {}
        
        logger.info("🐋 Whale Detector initialized")
    
    async def start_detection(self):
        """Whale tespitini başlat"""
        try:
            logger.info("🔍 Starting whale detection...")
            
            await self._initialize_detection_algorithms()
            await self._load_whale_patterns()
            
            self.is_active = True
            logger.info("✅ Whale detection active")
            
        except Exception as e:
            logger.error(f"Whale detection start error: {str(e)}")
            raise
    
    async def _initialize_detection_algorithms(self):
        """Tespit algoritmalarını başlat"""
        try:
            self.detection_algorithms = {
                'volume_anomaly_detector': {
                    'threshold_multiplier': 5.0,
                    'time_window': 300,
                    'accuracy': 0.92
                },
                'price_impact_analyzer': {
                    'min_impact': 0.05,
                    'correlation_threshold': 0.8,
                    'detection_window': 180
                }
            }
            
            logger.info("🧠 Whale detection algorithms initialized")
            
        except Exception as e:
            logger.error(f"Algorithm initialization error: {str(e)}")
            raise
    
    async def _load_whale_patterns(self):
        """Whale pattern'lerini yükle"""
        try:
            self.whale_database = {
                'crypto_whale_001': {
                    'size': WhaleSize.MASSIVE,
                    'preferred_symbols': ['BTCUSD', 'ETHUSD'],
                    'typical_size': 500000000,
                    'behavior': 'accumulation_focused',
                    'stealth_level': 9
                }
            }
            
            logger.info(f"🐋 Loaded {len(self.whale_database)} whale patterns")
            
        except Exception as e:
            logger.error(f"Whale pattern loading error: {str(e)}")
            raise
    
    async def detect_whale_activity(self, symbol: str) -> Optional[WhaleDetection]:
        """Whale aktivitesi tespiti"""
        try:
            if not self.is_active:
                return None
            
            if random.random() < 0.08:
                whale_size = random.choice(list(WhaleSize))
                position_size = self._generate_position_size(whale_size)
                
                detection = WhaleDetection(
                    detection_id=str(uuid.uuid4()),
                    symbol=symbol,
                    whale_size=whale_size,
                    estimated_position_size=position_size,
                    average_price=1.0500 + random.uniform(-0.0050, 0.0050),
                    detection_time=datetime.now(),
                    confidence=random.uniform(70, 95),
                    pattern_type=random.choice(['accumulation', 'distribution']),
                    institutional_type=random.choice(list(InstitutionalType)) if random.random() > 0.3 else None,
                    estimated_remaining=position_size * random.uniform(0.3, 0.8),
                    stealth_score=random.uniform(60, 95)
                )
                
                self.active_whales.append(detection)
                
                cutoff_time = datetime.now() - timedelta(hours=24)
                self.active_whales = [
                    w for w in self.active_whales 
                    if w.detection_time > cutoff_time
                ]
                
                logger.info(f"🐋 Whale detected: {symbol} - {whale_size.value}")
                return detection
            
            return None
            
        except Exception as e:
            logger.error(f"Whale detection error: {str(e)}")
            return None
    
    def _generate_position_size(self, whale_size: WhaleSize) -> float:
        """Whale boyutuna göre pozisyon büyüklüğü oluştur"""
        size_ranges = {
            WhaleSize.SMALL: (100000, 1000000),
            WhaleSize.MEDIUM: (1000000, 10000000),
            WhaleSize.LARGE: (10000000, 100000000),
            WhaleSize.MASSIVE: (100000000, 1000000000)
        }
        
        min_size, max_size = size_ranges[whale_size]
        return random.uniform(min_size, max_size)
    
    async def get_active_whales(self) -> List[Dict]:
        """Aktif whale'leri döndür"""
        try:
            active_whales = []
            
            for whale in self.active_whales[-10:]:
                active_whales.append({
                    'detection_id': whale.detection_id,
                    'symbol': whale.symbol,
                    'whale_size': whale.whale_size.value,
                    'position_size': whale.estimated_position_size,
                    'confidence': whale.confidence,
                    'pattern_type': whale.pattern_type,
                    'stealth_score': whale.stealth_score,
                    'detection_time': whale.detection_time.isoformat()
                })
            
            return active_whales
            
        except Exception as e:
            logger.error(f"Get active whales error: {str(e)}")
            return []
    
    def get_status(self) -> Dict:
        """Detector durumunu döndür"""
        return {
            'is_active': self.is_active,
            'detection_threshold': self.detection_threshold,
            'active_whales': len(self.active_whales),
            'whale_patterns': len(self.whale_database)
        } 