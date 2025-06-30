"""
Risk Calculator for Adaptive Trade Manager

Calculates dynamic, real-time risk metrics for open positions.
"""
from typing import Dict, List, Any, Optional, Tuple
import asyncio
import logging
from datetime import datetime, timedelta
import math

try:
    import numpy as np
except ImportError:
    # Mock numpy if not available
    class MockNP:
        def mean(self, values): 
            return sum(values) / len(values) if values else 0
        def std(self, values):
            if not values:
                return 0
            mean_val = self.mean(values)
            return math.sqrt(sum((x - mean_val) ** 2 for x in values) / len(values))
        def percentile(self, values, q):
            if not values:
                return 0
            sorted_vals = sorted(values)
            index = int(len(sorted_vals) * q / 100)
            return sorted_vals[min(index, len(sorted_vals) - 1)]
    np = MockNP()

from backend.core.logger import setup_logger
from .models import (
    ManagedPosition, RiskMetrics, MarketCondition, RiskLevel,
    DynamicPosition, AdaptiveSettings,
    TradeAlert, AlertRule, AlertSeverity
)
from .position_monitor import PositionMonitor
from .market_analyzer import MarketAnalyzer

logger = logging.getLogger(__name__)

class RiskCalculator:
    """Advanced risk calculator with real-time analysis and AI-driven insights"""
    
    def __init__(self, position_monitor: PositionMonitor, market_analyzer: MarketAnalyzer, mt5_service=None):
        self.position_monitor = position_monitor
        self.market_analyzer = market_analyzer
        self.mt5_service = mt5_service
        self.settings = AdaptiveSettings()
        self.alert_rules: List[AlertRule] = []
        self.risk_history: List[Dict] = []
        self.initialize_default_rules()

    def initialize_default_rules(self):
        """Initialize default risk alert rules"""
        self.alert_rules = [
            AlertRule(
                rule_id="portfolio_risk_high",
                name="High Portfolio Risk",
                description="Portfolio risk exceeds 15%",
                metric="portfolio_risk_percentage",
                threshold=15.0,
                comparison="greater_than",
                severity=AlertSeverity.WARNING,
                auto_adjust=True,
                notify_user=True
            ),
            AlertRule(
                rule_id="portfolio_risk_critical",
                name="Critical Portfolio Risk",
                description="Portfolio risk exceeds 25%",
                metric="portfolio_risk_percentage",
                threshold=25.0,
                comparison="greater_than",
                severity=AlertSeverity.CRITICAL,
                auto_adjust=True,
                notify_user=True
            ),
            AlertRule(
                rule_id="margin_level_low",
                name="Low Margin Level",
                description="Margin level below 200%",
                metric="margin_level",
                threshold=200.0,
                comparison="less_than",
                severity=AlertSeverity.WARNING,
                auto_adjust=False,
                notify_user=True
            ),
            AlertRule(
                rule_id="drawdown_high",
                name="High Drawdown",
                description="Maximum drawdown exceeds 10%",
                metric="max_drawdown",
                threshold=10.0,
                comparison="greater_than",
                severity=AlertSeverity.CRITICAL,
                auto_adjust=True,
                notify_user=True
            ),
            AlertRule(
                rule_id="var_exceeded",
                name="Value at Risk Exceeded",
                description="Daily VaR limit exceeded",
                metric="var_95",
                threshold=5.0,
                comparison="greater_than",
                severity=AlertSeverity.WARNING,
                auto_adjust=False,
                notify_user=True
            )
        ]

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

    def _calculate_news_risk(self, upcoming_events: List[Dict[str, Any]]) -> Tuple[float, int]:
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

    async def calculate_real_time_risk(
        self, 
        positions: List[DynamicPosition],
        account_info: Dict
    ) -> RiskMetrics:
        """Calculate comprehensive real-time risk metrics"""
        try:
            # Basic account metrics
            account_balance = account_info.get('balance', 0)
            equity = account_info.get('equity', 0)
            margin_used = account_info.get('margin', 0)
            free_margin = account_info.get('free_margin', 0)
            margin_level = account_info.get('margin_level', 0)
            
            # Portfolio risk calculations
            total_risk = sum(pos.risk_amount for pos in positions)
            risk_percentage = (total_risk / equity * 100) if equity > 0 else 0
            
            # Maximum drawdown calculation
            max_drawdown = await self._calculate_max_drawdown(positions, account_info)
            
            # Value at Risk (95%)
            var_95 = await self._calculate_var_95(positions)
            
            # Position metrics
            open_positions = len([p for p in positions if p.status.value in ['open', 'monitoring']])
            correlation_score = await self._calculate_correlation_score(positions)
            diversification_ratio = await self._calculate_diversification_ratio(positions)
            
            # Overall risk assessment
            overall_risk_level = await self._assess_overall_risk(
                risk_percentage, margin_level, max_drawdown, var_95, correlation_score
            )
            
            # Generate recommendation
            recommendation = await self._generate_risk_recommendation(
                overall_risk_level, risk_percentage, margin_level, positions
            )
            
            risk_metrics = RiskMetrics(
                account_balance=account_balance,
                equity=equity,
                margin_used=margin_used,
                free_margin=free_margin,
                margin_level=margin_level,
                total_risk=total_risk,
                risk_percentage=risk_percentage,
                max_drawdown=max_drawdown,
                var_95=var_95,
                open_positions=open_positions,
                correlation_score=correlation_score,
                diversification_ratio=diversification_ratio,
                overall_risk_level=overall_risk_level,
                recommendation=recommendation
            )
            
            # Store in history
            self.risk_history.append({
                'timestamp': datetime.now(),
                'risk_percentage': risk_percentage,
                'margin_level': margin_level,
                'max_drawdown': max_drawdown,
                'var_95': var_95
            })
            
            # Keep only last 24 hours
            cutoff_time = datetime.now() - timedelta(hours=24)
            self.risk_history = [r for r in self.risk_history if r['timestamp'] > cutoff_time]
            
            return risk_metrics
            
        except Exception as e:
            logger.error(f"Error calculating real-time risk: {e}")
            return self._get_default_risk_metrics()

    async def check_risk_alerts(
        self, 
        risk_metrics: RiskMetrics,
        positions: List[DynamicPosition]
    ) -> List[TradeAlert]:
        """Check all risk alert rules and generate alerts"""
        try:
            alerts = []
            current_time = datetime.now()
            
            # Prepare metrics for rule checking
            metric_values = {
                'portfolio_risk_percentage': risk_metrics.risk_percentage,
                'margin_level': risk_metrics.margin_level,
                'max_drawdown': risk_metrics.max_drawdown,
                'var_95': risk_metrics.var_95,
                'correlation_score': risk_metrics.correlation_score,
                'open_positions': risk_metrics.open_positions
            }
            
            for rule in self.alert_rules:
                if not rule.enabled:
                    continue
                
                # Check cooldown
                if (rule.last_triggered and 
                    current_time - rule.last_triggered < timedelta(minutes=rule.cooldown_minutes)):
                    continue
                
                # Get metric value
                metric_value = metric_values.get(rule.metric, 0)
                
                # Check if rule is triggered
                triggered = False
                if rule.comparison == "greater_than" and metric_value > rule.threshold:
                    triggered = True
                elif rule.comparison == "less_than" and metric_value < rule.threshold:
                    triggered = True
                elif rule.comparison == "equals" and abs(metric_value - rule.threshold) < 0.001:
                    triggered = True
                
                if triggered:
                    # Generate alert
                    alert = TradeAlert(
                        alert_id=f"alert_{rule.rule_id}_{int(current_time.timestamp())}",
                        rule_id=rule.rule_id,
                        severity=rule.severity,
                        title=rule.name,
                        message=f"{rule.description} - Current value: {metric_value:.2f}",
                        metric_value=metric_value,
                        threshold=rule.threshold,
                        affected_positions=[pos.position_id for pos in positions],
                        recommended_action=await self._get_recommended_action(rule, metric_value, positions),
                        created_at=current_time
                    )
                    
                    alerts.append(alert)
                    
                    # Update rule last triggered time
                    rule.last_triggered = current_time
                    
                    logger.warning(f"Risk alert triggered: {rule.name} - {metric_value:.2f}")
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error checking risk alerts: {e}")
            return []

    async def calculate_position_risk(
        self, 
        position: DynamicPosition,
        market_data: Dict,
        account_equity: float
    ) -> Dict[str, float]:
        """Calculate detailed risk metrics for a specific position"""
        try:
            current_price = position.current_price
            entry_price = position.entry_price
            position_size = position.position_size
            
            # Basic risk calculations
            position_value = position_size * current_price
            unrealized_pnl = position.unrealized_pnl
            
            # Stop loss risk
            if position.stop_loss:
                stop_loss_risk = abs(current_price - position.stop_loss) * position_size
            else:
                # Use volatility-based estimate
                volatility = market_data.get('volatility', 0.02)
                stop_loss_risk = position_value * volatility * 2
            
            # Risk as percentage of account
            risk_percentage = (stop_loss_risk / account_equity * 100) if account_equity > 0 else 0
            
            # Market risk (beta-adjusted)
            market_beta = market_data.get('beta', 1.0)
            market_risk = stop_loss_risk * market_beta
            
            # Liquidity risk
            liquidity_score = market_data.get('liquidity_score', 0.8)
            liquidity_risk_multiplier = max(1.0, 2.0 - liquidity_score)
            liquidity_adjusted_risk = stop_loss_risk * liquidity_risk_multiplier
            
            # Time-based risk
            time_held = (datetime.now() - position.entry_time).total_seconds() / 3600  # hours
            time_decay_factor = 1 + (time_held / 168) * 0.1  # Weekly decay
            
            # Volatility risk
            volatility = market_data.get('volatility', 0.02)
            volatility_risk = position_value * volatility
            
            # Risk-reward ratio
            if position.take_profit:
                potential_profit = abs(position.take_profit - entry_price) * position_size
                risk_reward_ratio = potential_profit / stop_loss_risk if stop_loss_risk > 0 else 0
            else:
                risk_reward_ratio = 0
            
            return {
                'position_value': position_value,
                'stop_loss_risk': stop_loss_risk,
                'risk_percentage': risk_percentage,
                'market_risk': market_risk,
                'liquidity_adjusted_risk': liquidity_adjusted_risk,
                'volatility_risk': volatility_risk,
                'time_decay_factor': time_decay_factor,
                'risk_reward_ratio': risk_reward_ratio,
                'overall_risk_score': min(100, risk_percentage * 5)  # Scale to 0-100
            }
            
        except Exception as e:
            logger.error(f"Error calculating position risk: {e}")
            return {
                'position_value': 0,
                'stop_loss_risk': 0,
                'risk_percentage': 0,
                'market_risk': 0,
                'liquidity_adjusted_risk': 0,
                'volatility_risk': 0,
                'time_decay_factor': 1.0,
                'risk_reward_ratio': 0,
                'overall_risk_score': 0
            }

    async def calculate_optimal_stop_loss(
        self, 
        position: DynamicPosition,
        market_data: Dict,
        max_risk_percentage: float = 0.02
    ) -> float:
        """Calculate optimal stop loss based on risk management and market conditions"""
        try:
            current_price = position.current_price
            entry_price = position.entry_price
            position_size = position.position_size
            
            # Determine position direction
            is_long = current_price >= entry_price
            
            # Risk-based stop loss
            max_risk_amount = position_size * current_price * max_risk_percentage
            if is_long:
                risk_based_stop = current_price - (max_risk_amount / position_size)
            else:
                risk_based_stop = current_price + (max_risk_amount / position_size)
            
            # Volatility-based stop loss
            volatility = market_data.get('volatility', 0.02)
            atr_multiplier = 2.0  # 2x Average True Range
            volatility_distance = current_price * volatility * atr_multiplier
            
            if is_long:
                volatility_based_stop = current_price - volatility_distance
            else:
                volatility_based_stop = current_price + volatility_distance
            
            # Technical analysis based stop loss
            support_level = market_data.get('support_level')
            resistance_level = market_data.get('resistance_level')
            
            if is_long and support_level:
                technical_stop = support_level * 0.995  # 0.5% below support
            elif not is_long and resistance_level:
                technical_stop = resistance_level * 1.005  # 0.5% above resistance
            else:
                technical_stop = volatility_based_stop
            
            # Choose the most conservative (closest to current price)
            stop_candidates = [risk_based_stop, volatility_based_stop, technical_stop]
            
            if is_long:
                optimal_stop = max(stop_candidates)  # Highest for long positions
                # Ensure stop is below current price
                optimal_stop = min(optimal_stop, current_price * 0.99)
            else:
                optimal_stop = min(stop_candidates)  # Lowest for short positions
                # Ensure stop is above current price
                optimal_stop = max(optimal_stop, current_price * 1.01)
            
            return optimal_stop
            
        except Exception as e:
            logger.error(f"Error calculating optimal stop loss: {e}")
            return position.stop_loss or current_price * 0.95

    async def _calculate_max_drawdown(self, positions: List[DynamicPosition], account_info: Dict) -> float:
        """Calculate maximum drawdown"""
        try:
            if not self.risk_history:
                return 0
            
            # Get equity history from risk history
            equity_values = []
            for record in self.risk_history[-50:]:  # Last 50 records
                equity_values.append(account_info.get('equity', 0))
            
            if len(equity_values) < 2:
                return 0
            
            # Calculate running maximum and drawdown
            running_max = equity_values[0]
            max_drawdown = 0
            
            for equity in equity_values:
                running_max = max(running_max, equity)
                drawdown = (running_max - equity) / running_max * 100 if running_max > 0 else 0
                max_drawdown = max(max_drawdown, drawdown)
            
            return max_drawdown
            
        except Exception as e:
            logger.error(f"Error calculating max drawdown: {e}")
            return 0

    async def _calculate_var_95(self, positions: List[DynamicPosition]) -> float:
        """Calculate Value at Risk at 95% confidence level"""
        try:
            if not positions:
                return 0
            
            # Get position returns
            returns = []
            for position in positions:
                if position.position_size > 0:
                    position_return = position.unrealized_pnl / (position.position_size * position.entry_price)
                    returns.append(position_return)
            
            if not returns:
                return 0
            
            # Calculate VaR at 95% confidence level
            var_95 = np.percentile(returns, 5) * -1  # 5th percentile (worst 5%)
            
            # Convert to monetary value
            total_value = sum(pos.position_size * pos.current_price for pos in positions)
            var_amount = var_95 * total_value
            
            return max(0, var_amount)
            
        except Exception as e:
            logger.error(f"Error calculating VaR 95: {e}")
            return 0

    async def _calculate_correlation_score(self, positions: List[DynamicPosition]) -> float:
        """Calculate portfolio correlation score"""
        try:
            if len(positions) < 2:
                return 0
            
            # Group positions by symbol
            symbols = list(set(pos.symbol for pos in positions))
            
            if len(symbols) == 1:
                return 1.0  # Perfect correlation if all same symbol
            
            # Simplified correlation calculation
            # In production, would use actual price correlation data
            correlation_sum = 0
            pairs = 0
            
            for i, symbol1 in enumerate(symbols):
                for j, symbol2 in enumerate(symbols[i+1:], i+1):
                    # Mock correlation based on symbol similarity
                    if symbol1[:3] == symbol2[:3]:  # Same base currency
                        correlation = 0.7
                    elif 'USD' in symbol1 and 'USD' in symbol2:
                        correlation = 0.4
                    else:
                        correlation = 0.2
                    
                    correlation_sum += correlation
                    pairs += 1
            
            avg_correlation = correlation_sum / pairs if pairs > 0 else 0
            return min(1.0, max(0, avg_correlation))
            
        except Exception as e:
            logger.error(f"Error calculating correlation score: {e}")
            return 0.5

    async def _calculate_diversification_ratio(self, positions: List[DynamicPosition]) -> float:
        """Calculate portfolio diversification ratio"""
        try:
            if not positions:
                return 1.0
            
            # Number of unique symbols
            unique_symbols = len(set(pos.symbol for pos in positions))
            total_positions = len(positions)
            
            # Calculate concentration
            symbol_weights = {}
            total_value = sum(pos.position_size * pos.current_price for pos in positions)
            
            for pos in positions:
                weight = (pos.position_size * pos.current_price) / total_value
                symbol_weights[pos.symbol] = symbol_weights.get(pos.symbol, 0) + weight
            
            # Herfindahl-Hirschman Index (concentration measure)
            hhi = sum(weight ** 2 for weight in symbol_weights.values())
            
            # Diversification ratio (lower HHI = higher diversification)
            diversification_ratio = 1 / hhi if hhi > 0 else 1
            
            # Normalize to 0-1 scale
            max_diversification = len(symbol_weights)
            normalized_ratio = min(1.0, diversification_ratio / max_diversification)
            
            return normalized_ratio
            
        except Exception as e:
            logger.error(f"Error calculating diversification ratio: {e}")
            return 0.5

    async def _assess_overall_risk(
        self, 
        risk_percentage: float,
        margin_level: float, 
        max_drawdown: float,
        var_95: float, 
        correlation_score: float
    ) -> RiskLevel:
        """Assess overall portfolio risk level"""
        try:
            risk_factors = []
            
            # Risk percentage assessment
            if risk_percentage > 25:
                risk_factors.append(4)  # Critical
            elif risk_percentage > 15:
                risk_factors.append(3)  # High
            elif risk_percentage > 10:
                risk_factors.append(2)  # Medium
            elif risk_percentage > 5:
                risk_factors.append(1)  # Low
            else:
                risk_factors.append(0)  # Very low
            
            # Margin level assessment
            if margin_level < 150:
                risk_factors.append(4)  # Critical
            elif margin_level < 200:
                risk_factors.append(3)  # High
            elif margin_level < 300:
                risk_factors.append(2)  # Medium
            elif margin_level < 500:
                risk_factors.append(1)  # Low
            else:
                risk_factors.append(0)  # Very low
            
            # Drawdown assessment
            if max_drawdown > 20:
                risk_factors.append(4)  # Critical
            elif max_drawdown > 15:
                risk_factors.append(3)  # High
            elif max_drawdown > 10:
                risk_factors.append(2)  # Medium
            elif max_drawdown > 5:
                risk_factors.append(1)  # Low
            else:
                risk_factors.append(0)  # Very low
            
            # Correlation assessment
            if correlation_score > 0.8:
                risk_factors.append(3)  # High concentration risk
            elif correlation_score > 0.6:
                risk_factors.append(2)  # Medium
            elif correlation_score > 0.4:
                risk_factors.append(1)  # Low
            else:
                risk_factors.append(0)  # Well diversified
            
            # Calculate overall risk
            avg_risk = sum(risk_factors) / len(risk_factors)
            
            if avg_risk >= 3.5:
                return RiskLevel.CRITICAL
            elif avg_risk >= 2.5:
                return RiskLevel.HIGH
            elif avg_risk >= 1.5:
                return RiskLevel.MEDIUM
            elif avg_risk >= 0.5:
                return RiskLevel.LOW
            else:
                return RiskLevel.VERY_LOW
                
        except Exception as e:
            logger.error(f"Error assessing overall risk: {e}")
            return RiskLevel.MEDIUM

    async def _generate_risk_recommendation(
        self, 
        risk_level: RiskLevel,
        risk_percentage: float, 
        margin_level: float,
        positions: List[DynamicPosition]
    ) -> str:
        """Generate risk management recommendation"""
        try:
            if risk_level == RiskLevel.CRITICAL:
                return "IMMEDIATE ACTION REQUIRED: Close some positions and reduce risk exposure"
            elif risk_level == RiskLevel.HIGH:
                return "High risk detected: Consider reducing position sizes or closing losing trades"
            elif risk_level == RiskLevel.MEDIUM:
                return "Moderate risk: Monitor positions closely and consider tightening stops"
            elif risk_level == RiskLevel.LOW:
                return "Low risk: Current risk management is appropriate"
            else:
                return "Very low risk: Consider increasing position sizes if opportunities arise"
                
        except Exception as e:
            logger.error(f"Error generating risk recommendation: {e}")
            return "Risk analysis in progress"

    async def _get_recommended_action(
        self, 
        rule: AlertRule, 
        metric_value: float,
        positions: List[DynamicPosition]
    ) -> str:
        """Get recommended action for triggered alert"""
        try:
            if rule.rule_id == "portfolio_risk_high":
                return "Reduce position sizes by 20% or close most risky positions"
            elif rule.rule_id == "portfolio_risk_critical":
                return "IMMEDIATE: Close at least 50% of positions to reduce risk"
            elif rule.rule_id == "margin_level_low":
                return "Close some positions or add margin to avoid margin call"
            elif rule.rule_id == "drawdown_high":
                return "Review trading strategy and consider reducing position sizes"
            elif rule.rule_id == "var_exceeded":
                return "Daily risk limit exceeded - avoid new positions today"
            else:
                return "Review portfolio and adjust positions as needed"
                
        except Exception as e:
            logger.error(f"Error getting recommended action: {e}")
            return "Manual review required"

    def _get_default_risk_metrics(self) -> RiskMetrics:
        """Get default risk metrics in case of error"""
        return RiskMetrics(
            account_balance=0,
            equity=0,
            margin_used=0,
            free_margin=0,
            margin_level=0,
            total_risk=0,
            risk_percentage=0,
            max_drawdown=0,
            var_95=0,
            open_positions=0,
            correlation_score=0,
            diversification_ratio=0,
            overall_risk_level=RiskLevel.MEDIUM,
            recommendation="Risk calculation unavailable"
        ) 