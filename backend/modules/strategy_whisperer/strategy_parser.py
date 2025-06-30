"""
Strategy Parser - Converts natural language intent to strategy parameters
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import re

from backend.core.logger import setup_logger
from .models import (
    StrategyIntent, StrategyParameters, TradingCondition,
    IndicatorType, TimeFrame, OrderType, RiskType, StrategyType
)

logger = setup_logger(__name__)


class StrategyParser:
    """Parse strategy intent into executable parameters"""
    
    def __init__(self):
        # Default parameter mappings
        self.default_params = {
            "RSI": {"period": 14, "overbought": 70, "oversold": 30},
            "MACD": {"fast": 12, "slow": 26, "signal": 9},
            "MA": {"period": 20},
            "EMA": {"period": 20},
            "SMA": {"period": 20},
            "BOLLINGER": {"period": 20, "deviation": 2},
            "STOCHASTIC": {"k_period": 14, "d_period": 3, "slowing": 3},
            "ATR": {"period": 14},
            "ADX": {"period": 14}
        }
        
        # Condition mappings
        self.condition_map = {
            "above": ">",
            "below": "<",
            "equals": "==",
            "crosses_above": "crosses_above",
            "crosses_below": "crosses_below",
            "üstünde": ">",
            "altında": "<",
            "eşit": "=="
        }
    
    async def parse_intent(self, intent: StrategyIntent) -> StrategyParameters:
        """Parse intent into strategy parameters"""
        try:
            # Generate strategy name
            name = self._generate_strategy_name(intent)
            
            # Parse components
            timeframe = self._parse_timeframe(intent)
            entry_conditions = self._parse_entry_conditions(intent)
            exit_conditions = self._parse_exit_conditions(intent)
            risk_params = self._parse_risk_parameters(intent)
            
            # Create strategy parameters
            params = StrategyParameters(
                name=name,
                description=await self._generate_description(intent),
                type=intent.detected_type or StrategyType.TREND_FOLLOWING,
                symbol="EURUSD",  # Default symbol
                timeframe=timeframe,
                entry_conditions=entry_conditions,
                entry_logic="AND",  # Default to AND logic
                exit_conditions=exit_conditions,
                exit_logic="OR",  # Default to OR logic
                risk_type=risk_params["type"],
                risk_value=risk_params["value"],
                stop_loss_pips=risk_params.get("stop_loss"),
                take_profit_pips=risk_params.get("take_profit"),
                trailing_stop=risk_params.get("trailing_stop"),
                max_positions=1
            )
            
            # Validate parameters
            validation_errors = self._validate_parameters(params)
            if validation_errors:
                params.is_valid = False
                params.validation_errors = validation_errors
            
            return params
            
        except Exception as e:
            logger.error(f"Error parsing intent: {str(e)}")
            raise
    
    def _generate_strategy_name(self, intent: StrategyIntent) -> str:
        """Generate a meaningful strategy name"""
        indicators = intent.entities.get("indicators", [])
        timeframe = intent.entities.get("timeframe", "H1")
        
        if indicators:
            indicator_part = "_".join(indicators[:2])  # Max 2 indicators
        else:
            indicator_part = "Custom"
        
        strategy_type = intent.detected_type or StrategyType.TREND_FOLLOWING
        type_part = strategy_type.value.split("_")[0].capitalize()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        
        return f"{type_part}_{indicator_part}_{timeframe}_{timestamp}"
    
    def _parse_timeframe(self, intent: StrategyIntent) -> TimeFrame:
        """Parse timeframe from intent"""
        timeframe = intent.entities.get("timeframe")
        
        if timeframe and hasattr(TimeFrame, timeframe):
            return TimeFrame(timeframe)
        
        # Default based on strategy type
        if intent.detected_type == StrategyType.SCALPING:
            return TimeFrame.M5
        elif intent.detected_type == StrategyType.SWING:
            return TimeFrame.H4
        else:
            return TimeFrame.H1
    
    def _parse_entry_conditions(self, intent: StrategyIntent) -> List[TradingCondition]:
        """Parse entry conditions from intent"""
        conditions = []
        indicators = intent.entities.get("indicators", [])
        numbers = intent.entities.get("numbers", [])
        condition_types = intent.entities.get("conditions", [])
        
        # RSI strategy pattern
        if "RSI" in indicators:
            rsi_params = self.default_params["RSI"].copy()
            
            # Update with extracted numbers if available
            if numbers:
                if len(numbers) >= 1:
                    rsi_params["period"] = int(numbers[0])
                if len(numbers) >= 2:
                    rsi_params["oversold"] = numbers[1]
                if len(numbers) >= 3:
                    rsi_params["overbought"] = numbers[2]
            
            # Check for buy/sell signals in text
            text_lower = intent.raw_text.lower()
            if any(word in text_lower for word in ["al", "buy", "oversold", "aşırı satım"]):
                conditions.append(TradingCondition(
                    indicator=IndicatorType.RSI,
                    parameters=rsi_params,
                    comparison="<",
                    value=rsi_params["oversold"],
                    timeframe=self._parse_timeframe(intent)
                ))
        
        # MACD strategy pattern
        if "MACD" in indicators:
            macd_params = self.default_params["MACD"].copy()
            
            conditions.append(TradingCondition(
                indicator=IndicatorType.MACD,
                parameters=macd_params,
                comparison="crosses_above",
                value=0,  # Signal line
                timeframe=self._parse_timeframe(intent)
            ))
        
        # Moving Average patterns
        ma_types = ["MA", "EMA", "SMA"]
        for ma_type in ma_types:
            if ma_type in indicators:
                ma_params = self.default_params[ma_type].copy()
                
                # Price above/below MA
                comparison = ">" if "above" in condition_types or "üstünde" in condition_types else "<"
                
                conditions.append(TradingCondition(
                    indicator=IndicatorType(ma_type),
                    parameters=ma_params,
                    comparison=comparison,
                    value=0,  # 0 means price relative to indicator
                    timeframe=self._parse_timeframe(intent)
                ))
        
        # If no conditions found, add a default
        if not conditions:
            conditions.append(TradingCondition(
                indicator=IndicatorType.RSI,
                parameters=self.default_params["RSI"],
                comparison="<",
                value=30,
                timeframe=self._parse_timeframe(intent)
            ))
        
        return conditions
    
    def _parse_exit_conditions(self, intent: StrategyIntent) -> List[TradingCondition]:
        """Parse exit conditions from intent"""
        conditions = []
        indicators = intent.entities.get("indicators", [])
        
        # Mirror entry conditions for exit
        entry_conditions = self._parse_entry_conditions(intent)
        
        for entry in entry_conditions:
            # Reverse the logic for exits
            if entry.indicator == IndicatorType.RSI:
                exit_value = 70 if entry.value < 50 else 30
                exit_comparison = ">" if entry.comparison == "<" else "<"
                
                conditions.append(TradingCondition(
                    indicator=entry.indicator,
                    parameters=entry.parameters,
                    comparison=exit_comparison,
                    value=exit_value,
                    timeframe=entry.timeframe
                ))
            
            elif entry.indicator in [IndicatorType.MA, IndicatorType.EMA, IndicatorType.SMA]:
                # Reverse MA crossover
                exit_comparison = "<" if entry.comparison == ">" else ">"
                
                conditions.append(TradingCondition(
                    indicator=entry.indicator,
                    parameters=entry.parameters,
                    comparison=exit_comparison,
                    value=0,
                    timeframe=entry.timeframe
                ))
        
        return conditions
    
    def _parse_risk_parameters(self, intent: StrategyIntent) -> Dict[str, Any]:
        """Parse risk management parameters"""
        numbers = intent.entities.get("numbers", [])
        text_lower = intent.raw_text.lower()
        
        risk_params = {
            "type": RiskType.PERCENT_BALANCE,
            "value": 1.0,  # Default 1% risk
            "stop_loss": 50,  # Default 50 pips
            "take_profit": 100,  # Default 100 pips
            "trailing_stop": None
        }
        
        # Check for risk type mentions
        if "lot" in text_lower:
            risk_params["type"] = RiskType.FIXED_LOT
            risk_params["value"] = 0.01  # Default micro lot
        elif "%" in text_lower or "yüzde" in text_lower:
            risk_params["type"] = RiskType.PERCENT_BALANCE
            # Look for percentage in numbers
            for num in numbers:
                if 0 < num <= 10:  # Reasonable risk percentage
                    risk_params["value"] = num
                    break
        
        # Look for stop loss mentions
        if "stop" in text_lower or "zarar durdur" in text_lower:
            # Find number near stop mention
            for num in numbers:
                if 10 <= num <= 200:  # Reasonable pip range
                    risk_params["stop_loss"] = num
                    break
        
        # Look for take profit mentions
        if "take profit" in text_lower or "kar al" in text_lower:
            for num in numbers:
                if 20 <= num <= 500:  # Reasonable pip range
                    risk_params["take_profit"] = num
                    break
        
        # Trailing stop
        if "trailing" in text_lower or "takip eden" in text_lower:
            risk_params["trailing_stop"] = 20  # Default 20 pips
        
        return risk_params
    
    def _validate_parameters(self, params: StrategyParameters) -> List[str]:
        """Validate strategy parameters"""
        errors = []
        
        # Check entry conditions
        if not params.entry_conditions:
            errors.append("Giriş koşulları tanımlanmamış")
        
        # Check risk parameters
        if params.risk_value <= 0:
            errors.append("Risk değeri pozitif olmalı")
        
        if params.risk_type == RiskType.PERCENT_BALANCE and params.risk_value > 10:
            errors.append("Risk yüzdesi çok yüksek (>10%)")
        
        # Check stop loss
        if params.stop_loss_pips and params.stop_loss_pips < 5:
            errors.append("Stop loss çok yakın (<5 pips)")
        
        # Check take profit
        if params.take_profit_pips and params.stop_loss_pips:
            if params.take_profit_pips < params.stop_loss_pips:
                errors.append("Take profit, stop loss'tan küçük olamaz")
        
        return errors
    
    async def _generate_description(self, intent: StrategyIntent) -> str:
        """Generate detailed strategy description"""
        indicators = intent.entities.get("indicators", [])
        timeframe = intent.entities.get("timeframe", "H1")
        
        desc = f"Bu strateji {timeframe} zaman diliminde "
        
        if indicators:
            desc += f"{', '.join(indicators)} göstergelerini kullanarak "
        
        if intent.detected_type == StrategyType.TREND_FOLLOWING:
            desc += "trend yönünde işlem açar. "
        elif intent.detected_type == StrategyType.MEAN_REVERSION:
            desc += "aşırı alım/satım bölgelerinde ters işlem açar. "
        elif intent.detected_type == StrategyType.BREAKOUT:
            desc += "önemli seviyelerin kırılımında işlem açar. "
        
        desc += "Risk yönetimi ve otomatik stop loss/take profit içerir."
        
        return desc
    
    async def refine_parameters(self, params: StrategyParameters, feedback: str) -> StrategyParameters:
        """Refine parameters based on user feedback"""
        try:
            feedback_lower = feedback.lower()
            
            # Adjust risk parameters
            if "risk" in feedback_lower:
                numbers = re.findall(r'\b\d+(?:\.\d+)?\b', feedback)
                if numbers:
                    params.risk_value = float(numbers[0])
            
            # Adjust timeframe
            timeframe_keywords = {
                "M1": ["1 dakika", "1m"],
                "M5": ["5 dakika", "5m"],
                "M15": ["15 dakika", "15m"],
                "M30": ["30 dakika", "30m"],
                "H1": ["1 saat", "1h"],
                "H4": ["4 saat", "4h"],
                "D1": ["günlük", "1d"],
            }
            
            for tf, keywords in timeframe_keywords.items():
                if any(kw in feedback_lower for kw in keywords):
                    params.timeframe = TimeFrame(tf)
                    # Update all conditions with new timeframe
                    for cond in params.entry_conditions + params.exit_conditions:
                        cond.timeframe = TimeFrame(tf)
                    break
            
            # Re-validate
            params.validation_errors = self._validate_parameters(params)
            params.is_valid = len(params.validation_errors) == 0
            
            return params
            
        except Exception as e:
            logger.error(f"Error refining parameters: {str(e)}")
            return params 