"""
AI Optimization Engine for Adaptive Trade Manager

The core decision-making component that recommends adaptive actions.
"""
from typing import Optional

from backend.core.logger import get_logger
from .models import ManagedPosition, RiskMetrics, MarketCondition, AdaptiveAction, ActionType, MarketRegime

logger = get_logger(__name__)

class OptimizationEngine:

    async def generate_recommendation(self, position: ManagedPosition, risk: RiskMetrics, market: MarketCondition) -> AdaptiveAction:
        """
        Generates the best adaptive action for a given position and its context.
        This is the core AI logic.
        """
        
        # --- Rule-Based Decision Tree ---
        # This acts as a baseline and safety net.
        
        # 1. Critical News Event
        if risk.news_impact_level == 3:
            return self._handle_critical_news(position, risk)
            
        # 2. Critical Risk Score
        if risk.risk_score > 80:
            return self._handle_critical_risk(position, risk, market)

        # 3. High Risk Score
        if risk.risk_score > 60:
            return self._handle_high_risk(position, risk, market)

        # 4. Opportunity Seeking (if risk is low)
        if risk.risk_score < 30 and position.pnl > 0:
            return self._seek_opportunity(position, risk, market)

        # Default action: Do nothing
        return AdaptiveAction(
            action_type=ActionType.DO_NOTHING,
            description="Market conditions and risk level are stable. No action required.",
            confidence=0.8,
            reasoning="All risk metrics are within acceptable parameters."
        )

    def _handle_critical_news(self, position: ManagedPosition, risk: RiskMetrics) -> AdaptiveAction:
        """Handle an impending high-impact news event."""
        if position.pnl > 0:
            return AdaptiveAction(
                action_type=ActionType.PARTIAL_CLOSE,
                description="Secure 50% of profit before high-impact news.",
                confidence=0.95,
                parameters={"percentage": 50},
                reasoning=f"Critical news event imminent. High probability of extreme volatility. Securing profits reduces risk.",
                predicted_outcome="Reduces exposure and protects unrealized gains from news spike."
            )
        else:
            return AdaptiveAction(
                action_type=ActionType.FULL_CLOSE,
                description="Close position to avoid unpredictable news-driven volatility.",
                confidence=0.90,
                reasoning=f"Position is in loss with critical news approaching. Best to cut losses and avoid further risk.",
                predicted_outcome="Prevents potentially large losses from adverse news reaction."
            )
            
    def _handle_critical_risk(self, position: ManagedPosition, risk: RiskMetrics, market: MarketCondition) -> AdaptiveAction:
        """Handle a critically high risk score."""
        reason = f"Critical risk score ({risk.risk_score}) detected due to high volatility and drawdown."
        if position.pnl > 0:
            # In profit but risk is critical -> Take profit
            return AdaptiveAction(
                action_type=ActionType.ADJUST_SL,
                description="Move Stop Loss to break-even to secure position.",
                confidence=0.98,
                parameters={"price": position.open_price},
                reasoning=reason + " Locking in break-even eliminates risk of loss.",
                predicted_outcome="Position becomes risk-free, allowing further upside potential."
            )
        else:
            # In loss and risk is critical -> Cut losses
            return AdaptiveAction(
                action_type=ActionType.FULL_CLOSE,
                description="Close position immediately to prevent further losses.",
                confidence=0.95,
                reasoning=reason + " Market conditions are highly unfavorable.",
                predicted_outcome="Prevents catastrophic loss by cutting the position at a manageable level."
            )

    def _handle_high_risk(self, position: ManagedPosition, risk: RiskMetrics, market: MarketCondition) -> AdaptiveAction:
        """Handle a high risk score."""
        reason = f"High risk score ({risk.risk_score}) detected."
        # If trending against us, suggest tightening SL
        if (market.regime == MarketRegime.TRENDING_UP and position.position_type == 'sell') or \
           (market.regime == MarketRegime.TRENDING_DOWN and position.position_type == 'buy'):
            
            new_sl = position.open_price if position.pnl > 0 else (position.current_price + position.stop_loss) / 2
            return AdaptiveAction(
                action_type=ActionType.ADJUST_SL,
                description="Tighten Stop Loss as market is trending against the position.",
                confidence=0.85,
                parameters={"price": new_sl},
                reasoning=reason + " Strong counter-trend movement observed.",
                predicted_outcome="Reduces potential loss if the counter-trend continues."
            )
        
        # Default high-risk action
        return AdaptiveAction(
            action_type=ActionType.PARTIAL_CLOSE,
            description="Close 25% of the position to reduce exposure.",
            confidence=0.80,
            parameters={"percentage": 25},
            reasoning=reason + " De-risking by taking some off the table.",
            predicted_outcome="Lowers overall portfolio risk while keeping the position active."
        )

    def _seek_opportunity(self, position: ManagedPosition, risk: RiskMetrics, market: MarketCondition) -> AdaptiveAction:
        """Looks for opportunities when a position is in profit and risk is low."""
        # If trending with us, suggest trailing stop
        if (market.regime == MarketRegime.TRENDING_UP and position.position_type == 'buy') or \
           (market.regime == MarketRegime.TRENDING_DOWN and position.position_type == 'sell'):
            
            return AdaptiveAction(
                action_type=ActionType.ADJUST_TP,
                description="Activate dynamic trailing stop to capture more profit.",
                confidence=0.90,
                parameters={"trailing_pips": 20}, # Example value
                reasoning=f"Strong trend ({market.regime.value}) in favor of the position with low risk.",
                predicted_outcome="Maximizes profit potential by following the trend."
            )
        
        # If ranging, suggest taking partial profit near resistance/support
        if market.regime == MarketRegime.RANGING:
             return AdaptiveAction(
                action_type=ActionType.PARTIAL_CLOSE,
                description="Take 50% profit as market is ranging and may reverse.",
                confidence=0.80,
                parameters={"percentage": 50},
                reasoning="Market is in a ranging phase, increasing the chance of a reversal from range highs/lows.",
                predicted_outcome="Secures realized gains while leaving part of the position to run."
            )

        return AdaptiveAction(
            action_type=ActionType.DO_NOTHING,
            description="Conditions are favorable. Hold position.",
            confidence=0.7,
            reasoning="Position is profitable and risk metrics are low."
        ) 