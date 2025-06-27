"""
Risk Calculator for Adaptive Trade Manager

Calculates dynamic, real-time risk metrics for open positions.
"""
from typing import Dict, List, Optional
import numpy as np

from backend.core.logger import get_logger
from .models import ManagedPosition, RiskMetrics, MarketCondition, RiskLevel
from .position_monitor import PositionMonitor
from .market_analyzer import MarketAnalyzer

logger = get_logger(__name__)

class RiskCalculator:
    def __init__(self, position_monitor: PositionMonitor, market_analyzer: MarketAnalyzer):
        self.position_monitor = position_monitor
        self.market_analyzer = market_analyzer

    async def calculate_risk_for_all_positions(self) -> List[RiskMetrics]:
        """Calculates risk for every currently managed position."""
        all_metrics = []
        positions = await self.position_monitor.get_all_positions()
        for pos in positions:
            metrics = await self.calculate_risk_for_position(pos)
            all_metrics.append(metrics)
        return all_metrics

    async def calculate_risk_for_position(self, position: ManagedPosition) -> RiskMetrics:
        """Calculates a comprehensive risk profile for a single position."""
        market_condition = await self.market_analyzer.get_market_condition(position.symbol)
        
        # --- Individual Risk Components (0-100 scale) ---
        
        # 1. Volatility Risk
        volatility_risk = self._calculate_volatility_risk(market_condition.volatility)

        # 2. Drawdown Risk (based on current P&L)
        drawdown_risk = self._calculate_drawdown_risk(position)

        # 3. News Event Risk
        news_risk, news_impact_level = self._calculate_news_risk(market_condition.upcoming_events)
        
        # --- Weighted Risk Score ---
        weights = {
            "volatility": 0.4,
            "drawdown": 0.4,
            "news": 0.2,
        }
        
        risk_score = (
            volatility_risk * weights["volatility"] +
            drawdown_risk * weights["drawdown"] +
            news_risk * weights["news"]
        )
        
        risk_level = self._get_risk_level(risk_score)

        return RiskMetrics(
            position_ticket=position.ticket,
            risk_level=risk_level,
            risk_score=round(risk_score, 2),
            volatility_index=market_condition.volatility,
            drawdown_percent=self._get_position_drawdown(position),
            value_at_risk=self._calculate_var(position, market_condition.volatility),
            news_impact_level=news_impact_level,
            correlation_warnings={} # To be implemented
        )

    def _calculate_volatility_risk(self, volatility_index: float) -> float:
        """Converts volatility index to a 0-100 risk score."""
        # Example: 0.1 vol = 50 score. Scales exponentially.
        score = np.power(volatility_index * 10, 2) * 5
        return min(max(score, 0), 100)

    def _calculate_drawdown_risk(self, position: ManagedPosition) -> float:
        """Calculates risk based on current position drawdown."""
        if position.pnl >= 0:
            return 0.0 # No drawdown if in profit
        
        # How close is it to a hypothetical 5% account loss?
        # This is a simplified example. A real implementation would use account balance.
        hypothetical_account = 10000
        stop_out_pnl = -0.05 * hypothetical_account
        
        if position.pnl <= stop_out_pnl:
            return 100.0
            
        risk_percentage = (position.pnl / stop_out_pnl)
        return min(risk_percentage * 100, 100)

    def _get_position_drawdown(self, position: ManagedPosition) -> float:
        """Gets the drawdown percentage of a single position."""
        # This is simplified; a real version would track max equity of the position
        if position.pnl < 0:
            # Assuming a simple relation to open price for drawdown %
            return abs(position.pnl / (position.open_price * position.volume * 100)) * 100
        return 0.0

    def _calculate_news_risk(self, upcoming_events: List[Dict[str, Any]]) -> (float, int):
        """Calculates risk from upcoming news events."""
        if not upcoming_events:
            return 0.0, 0

        # Find the highest impact event
        max_impact = max(event.get('impact', 0) for event in upcoming_events)
        
        risk_map = {0: 0, 1: 30, 2: 70, 3: 100}
        return risk_map.get(max_impact, 0), max_impact

    def _get_risk_level(self, score: float) -> RiskLevel:
        """Categorizes a numeric risk score into a risk level."""
        if score > 80:
            return RiskLevel.CRITICAL
        if score > 60:
            return RiskLevel.HIGH
        if score > 30:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW

    def _calculate_var(self, position: ManagedPosition, volatility: float) -> float:
        """
        Calculates a simplified Value at Risk (VaR).
        This is a placeholder for a proper statistical VaR calculation.
        """
        # Simplified VaR: position value * volatility * confidence level (e.g., 1.65 for 95%)
        position_value = position.open_price * position.volume * 100000 # Assuming standard lots
        daily_std_dev = volatility / 100 # Rough approximation
        var = position_value * daily_std_dev * 1.65
        return round(var, 2) 