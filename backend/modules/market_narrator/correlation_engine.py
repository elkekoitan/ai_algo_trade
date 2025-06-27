"""
Correlation Engine for the Market Narrator

Finds statistical relationships between different assets.
"""
import pandas as pd
from scipy.stats import pearsonr
from typing import List, Dict, Tuple

from backend.core.logger import get_logger
from backend.modules.mt5_integration.service import MT5Service

logger = get_logger(__name__)

class CorrelationEngine:
    def __init__(self, mt5_service: MT5Service):
        self.mt5 = mt5_service
        # Key assets to track for cross-market analysis
        self.tracked_assets = ["EURUSD", "XAUUSD", "USDJPY", "BTCUSD"]

    async def find_significant_correlations(self, period: int = 50) -> Dict[str, List[Tuple[str, float]]]:
        """
        Finds significant correlations between the main tracked assets.
        
        Returns:
            A dictionary where keys are asset symbols and values are lists of 
            (correlated_asset, correlation_coefficient) tuples.
        """
        if not self.mt5.connected:
            logger.warning("Correlation Engine: MT5 not connected. Skipping analysis.")
            return {}

        # 1. Fetch data for all tracked assets
        asset_data = {}
        for asset in self.tracked_assets:
            rates = self.mt5.get_rates(asset, "H1", period)
            if rates is not None and not rates.empty:
                asset_data[asset] = rates['close']
        
        if len(asset_data) < 2:
            logger.warning("Not enough asset data to run correlation analysis.")
            return {}
            
        # 2. Create a unified DataFrame
        df = pd.DataFrame(asset_data).dropna()

        # 3. Calculate all-pairs correlation
        correlation_matrix = df.corr()
        
        # 4. Find significant relationships
        significant_correlations = {}
        for asset1 in correlation_matrix.columns:
            correlations = []
            for asset2 in correlation_matrix.columns:
                if asset1 == asset2:
                    continue
                
                corr_value = correlation_matrix.loc[asset1, asset2]
                
                # We consider a correlation significant if its absolute value is > 0.7
                if abs(corr_value) > 0.7:
                    correlations.append((asset2, round(corr_value, 2)))
            
            if correlations:
                significant_correlations[asset1] = correlations
        
        logger.info(f"Found significant correlations: {significant_correlations}")
        return significant_correlations 