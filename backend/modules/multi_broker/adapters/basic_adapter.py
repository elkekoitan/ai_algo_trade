"""
Basic Broker Adapter
Generic adapter implementation
"""

from typing import Dict, List, Optional, Any
from .mt5_adapter import BrokerAdapter
import logging

logger = logging.getLogger(__name__)

class BasicAdapter(BrokerAdapter):
    """Basic broker adapter for testing and development"""
    
    def __init__(self, broker_name: str = "basic"):
        self.broker_name = broker_name
        self.connected = False
        logger.info(f"BasicAdapter initialized for {broker_name}")
    
    async def connect(self) -> bool:
        """Connect to broker"""
        try:
            self.connected = True
            logger.info(f"BasicAdapter connected to {self.broker_name}")
            return True
        except Exception as e:
            logger.error(f"BasicAdapter connection failed: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from broker"""
        try:
            self.connected = False
            logger.info(f"BasicAdapter disconnected from {self.broker_name}")
            return True
        except Exception as e:
            logger.error(f"BasicAdapter disconnect failed: {e}")
            return False
    
    async def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        if not self.connected:
            return {}
        
        return {
            "broker": self.broker_name,
            "balance": 5000.0,
            "equity": 5000.0,
            "margin": 0.0,
            "free_margin": 5000.0,
            "currency": "USD"
        }
    
    async def place_order(self, symbol: str, order_type: str, volume: float, **kwargs) -> Dict[str, Any]:
        """Place order"""
        if not self.connected:
            return {"success": False, "error": "Not connected"}
        
        return {
            "success": True,
            "ticket": 54321,
            "symbol": symbol,
            "type": order_type,
            "volume": volume,
            "price": kwargs.get("price", 1.0000),
            "broker": self.broker_name
        } 