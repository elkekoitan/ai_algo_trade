"""
Correlation Engine for Market Narrator
Analyzes relationships between symbols and creates influence maps
"""

import asyncio
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import numpy as np

from .models import InfluenceNode, CorrelationData, AssetClass, InfluenceLevel
from ..mt5_integration.service import MT5Service

logger = logging.getLogger(__name__)

class CorrelationEngine:
    """Analyzes correlations and creates influence maps between market symbols"""
    
    def __init__(self):
        self.correlation_cache = {}
        self.influence_cache = {}
        self.cache_expiry = 300  # 5 minutes
        
        # Symbol relationships mapping
        self.symbol_relationships = {
            "EURUSD": {
                "negatively_correlated": ["DXY", "USDCHF"],
                "positively_correlated": ["GBPUSD", "AUDUSD"],
                "influenced_by": ["EUR", "USD", "ECB", "FED"]
            },
            "GBPUSD": {
                "negatively_correlated": ["DXY"],
                "positively_correlated": ["EURUSD", "AUDUSD"],
                "influenced_by": ["GBP", "USD", "BOE", "FED"]
            },
            "XAUUSD": {
                "negatively_correlated": ["DXY", "USDJPY"],
                "positively_correlated": ["SILVER", "EURUSD"],
                "influenced_by": ["USD", "FED", "INFLATION", "RISK_SENTIMENT"]
            },
            "BTCUSD": {
                "negatively_correlated": ["DXY"],
                "positively_correlated": ["XAUUSD", "RISK_ASSETS"],
                "influenced_by": ["TECH_SENTIMENT", "RISK_APPETITE", "REGULATION"]
            }
        }
        
        logger.info("🔗 Correlation Engine initialized")
    
    async def calculate_correlations(
        self, 
        symbol: str, 
        timeframe: str = "1D", 
        min_correlation: float = 0.5
    ) -> List[CorrelationData]:
        """Calculate correlations for a symbol with other symbols"""
        try:
            cache_key = f"{symbol}_{timeframe}_{min_correlation}"
            
            # Check cache
            if self._is_cached(cache_key):
                return self.correlation_cache[cache_key]["data"]
            
            # Get related symbols
            related_symbols = self._get_related_symbols(symbol)
            correlations = []
            
            for related_symbol in related_symbols:
                try:
                    # Calculate correlation (mocked for now)
                    correlation_value = await self._calculate_pair_correlation(
                        symbol, related_symbol, timeframe
                    )
                    
                    if abs(correlation_value) >= min_correlation:
                        correlation_data = CorrelationData(
                            symbol_a=symbol,
                            symbol_b=related_symbol,
                            correlation=correlation_value,
                            timeframe=timeframe,
                            confidence=0.85,  # Mock confidence
                            timestamp=datetime.now()
                        )
                        correlations.append(correlation_data)
                        
                except Exception as e:
                    logger.error(f"Error calculating correlation {symbol}-{related_symbol}: {e}")
            
            # Cache result
            self.correlation_cache[cache_key] = {
                "data": correlations,
                "timestamp": datetime.now()
            }
            
            return correlations
            
        except Exception as e:
            logger.error(f"Error calculating correlations for {symbol}: {e}")
            return []
    
    async def generate_influence_map(
        self, 
        symbol: str, 
        depth: int = 2
    ) -> List[InfluenceNode]:
        """Generate influence map showing symbol relationships"""
        try:
            cache_key = f"influence_{symbol}_{depth}"
            
            # Check cache
            if self._is_cached(cache_key):
                return self.influence_cache[cache_key]["data"]
            
            influence_nodes = []
            
            # Create center node
            center_node = InfluenceNode(
                id=symbol,
                symbol=symbol,
                asset_class=self._get_asset_class(symbol),
                current_impact=0.0,  # Center node impact
                influence_level=InfluenceLevel.HIGH,
                connections=[]
            )
            influence_nodes.append(center_node)
            
            # Add related symbols
            related_symbols = self._get_related_symbols(symbol, depth)
            
            for related_symbol in related_symbols:
                # Calculate influence metrics
                impact = await self._calculate_influence_impact(symbol, related_symbol)
                influence_level = self._determine_influence_level(abs(impact))
                
                influence_node = InfluenceNode(
                    id=related_symbol,
                    symbol=related_symbol,
                    asset_class=self._get_asset_class(related_symbol),
                    current_impact=impact,
                    influence_level=influence_level,
                    connections=[symbol]
                )
                influence_nodes.append(influence_node)
            
            # Cache result
            self.influence_cache[cache_key] = {
                "data": influence_nodes,
                "timestamp": datetime.now()
            }
            
            return influence_nodes
            
        except Exception as e:
            logger.error(f"Error generating influence map for {symbol}: {e}")
            return []
    
    async def _calculate_pair_correlation(
        self, 
        symbol_a: str, 
        symbol_b: str, 
        timeframe: str
    ) -> float:
        """Calculate correlation between two symbols"""
        try:
            # Mock correlation calculation
            # In real implementation, this would fetch historical data and calculate
            
            # Use predefined relationships
            relationships = self.symbol_relationships.get(symbol_a, {})
            
            if symbol_b in relationships.get("positively_correlated", []):
                return np.random.uniform(0.6, 0.9)
            elif symbol_b in relationships.get("negatively_correlated", []):
                return np.random.uniform(-0.9, -0.6)
            else:
                return np.random.uniform(-0.3, 0.3)
                
        except Exception as e:
            logger.error(f"Error calculating pair correlation: {e}")
            return 0.0
    
    async def _calculate_influence_impact(
        self, 
        center_symbol: str, 
        influenced_symbol: str
    ) -> float:
        """Calculate how much center_symbol influences influenced_symbol"""
        try:
            # Mock influence calculation
            relationships = self.symbol_relationships.get(center_symbol, {})
            
            if influenced_symbol in relationships.get("positively_correlated", []):
                return np.random.uniform(0.4, 0.8)
            elif influenced_symbol in relationships.get("negatively_correlated", []):
                return np.random.uniform(-0.8, -0.4)
            else:
                return np.random.uniform(-0.2, 0.2)
                
        except Exception as e:
            logger.error(f"Error calculating influence impact: {e}")
            return 0.0
    
    def _get_related_symbols(self, symbol: str, depth: int = 1) -> List[str]:
        """Get symbols related to the given symbol"""
        try:
            relationships = self.symbol_relationships.get(symbol, {})
            related = []
            
            # Add directly correlated symbols
            related.extend(relationships.get("positively_correlated", []))
            related.extend(relationships.get("negatively_correlated", []))
            
            # Add influenced symbols
            influenced_by = relationships.get("influenced_by", [])
            related.extend(influenced_by)
            
            # For depth > 1, add symbols related to related symbols
            if depth > 1:
                for rel_symbol in list(related):
                    if rel_symbol in self.symbol_relationships:
                        sub_related = self._get_related_symbols(rel_symbol, depth - 1)
                        related.extend(sub_related)
            
            # Remove duplicates and the original symbol
            related = list(set(related))
            if symbol in related:
                related.remove(symbol)
            
            # Limit to reasonable number
            return related[:10]
            
        except Exception as e:
            logger.error(f"Error getting related symbols: {e}")
            return ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"]  # Default fallback
    
    def _get_asset_class(self, symbol: str) -> AssetClass:
        """Determine asset class for a symbol"""
        if symbol.endswith("USD") or len(symbol) == 6:
            return AssetClass.FX
        elif symbol in ["XAUUSD", "XAGUSD", "GOLD", "SILVER"]:
            return AssetClass.COMMODITY
        elif symbol in ["BTCUSD", "ETHUSD", "BTC", "ETH"]:
            return AssetClass.CRYPTO
        elif symbol in ["US30", "US500", "NAS100", "SPX"]:
            return AssetClass.INDEX
        else:
            return AssetClass.EQUITY
    
    def _determine_influence_level(self, impact: float) -> InfluenceLevel:
        """Determine influence level based on impact value"""
        if impact >= 0.7:
            return InfluenceLevel.CRITICAL
        elif impact >= 0.5:
            return InfluenceLevel.HIGH
        elif impact >= 0.3:
            return InfluenceLevel.MEDIUM
        else:
            return InfluenceLevel.LOW
    
    def _is_cached(self, cache_key: str) -> bool:
        """Check if data is cached and still valid"""
        if cache_key not in self.correlation_cache:
            return False
        
        cached_time = self.correlation_cache[cache_key]["timestamp"]
        return (datetime.now() - cached_time).seconds < self.cache_expiry
    
    def get_status(self) -> Dict:
        """Get correlation engine status"""
        return {
            "status": "operational",
            "cached_correlations": len(self.correlation_cache),
            "cached_influences": len(self.influence_cache),
            "supported_symbols": len(self.symbol_relationships)
        } 