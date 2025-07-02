"""
Fixed Natural Language Processing Engine for Strategy Whisperer
"""

import os
import re
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

# Use relative import
try:
    from ...core.logger import setup_logger
except ImportError:
    # Fallback for different import contexts
    import logging
    def setup_logger(name):
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        return logger

logger = setup_logger(__name__)


class StrategyType(str, Enum):
    TREND_FOLLOWING = "trend_following"
    MEAN_REVERSION = "mean_reversion"
    BREAKOUT = "breakout"
    SCALPING = "scalping"


class TimeFrame(str, Enum):
    M1 = "M1"
    M5 = "M5"
    M15 = "M15"
    M30 = "M30"
    H1 = "H1"
    H4 = "H4"
    D1 = "D1"


class Language(str, Enum):
    TURKISH = "turkish"
    ENGLISH = "english"


class TradingCondition(str, Enum):
    BUY = "buy"
    SELL = "sell"
    CLOSE = "close"


class NLPEngine:
    """Natural language processing for strategy creation"""
    
    def __init__(self):
        self.supported_languages = [Language.TURKISH, Language.ENGLISH]
        self.strategy_patterns = self._load_patterns()
        
    def _load_patterns(self) -> Dict[str, List[str]]:
        """Load strategy patterns for NLP"""
        return {
            "buy_signals": [
                r"buy when (.*)",
                r"al.*zaman (.*)",
                r"long.*when (.*)",
                r"satın al.*eğer (.*)"
            ],
            "sell_signals": [
                r"sell when (.*)",
                r"sat.*zaman (.*)",
                r"short.*when (.*)",
                r"sat.*eğer (.*)"
            ],
            "indicators": {
                "rsi": [r"rsi", r"relative strength"],
                "macd": [r"macd", r"moving average convergence"],
                "ema": [r"ema", r"exponential moving average"],
                "sma": [r"sma", r"simple moving average"],
                "bollinger": [r"bollinger", r"bb"],
                "stochastic": [r"stochastic", r"stoch"]
            }
        }
    
    def parse_strategy(self, text: str, language: Language = Language.ENGLISH) -> Dict[str, Any]:
        """Parse natural language strategy description"""
        text = text.lower()
        
        strategy = {
            "type": self._detect_strategy_type(text),
            "conditions": [],
            "timeframe": self._detect_timeframe(text),
            "risk_management": self._extract_risk_params(text),
            "indicators": self._extract_indicators(text)
        }
        
        # Extract buy conditions
        for pattern in self.strategy_patterns["buy_signals"]:
            matches = re.findall(pattern, text)
            for match in matches:
                strategy["conditions"].append({
                    "type": TradingCondition.BUY,
                    "condition": match
                })
        
        # Extract sell conditions
        for pattern in self.strategy_patterns["sell_signals"]:
            matches = re.findall(pattern, text)
            for match in matches:
                strategy["conditions"].append({
                    "type": TradingCondition.SELL,
                    "condition": match
                })
        
        return strategy
    
    def _detect_strategy_type(self, text: str) -> StrategyType:
        """Detect the type of trading strategy"""
        if any(word in text for word in ["trend", "momentum", "breakout"]):
            return StrategyType.TREND_FOLLOWING
        elif any(word in text for word in ["mean reversion", "overbought", "oversold"]):
            return StrategyType.MEAN_REVERSION
        elif any(word in text for word in ["scalp", "quick", "fast"]):
            return StrategyType.SCALPING
        else:
            return StrategyType.TREND_FOLLOWING
    
    def _detect_timeframe(self, text: str) -> TimeFrame:
        """Detect the preferred timeframe"""
        timeframes = {
            "m1": TimeFrame.M1,
            "m5": TimeFrame.M5,
            "m15": TimeFrame.M15,
            "m30": TimeFrame.M30,
            "h1": TimeFrame.H1,
            "h4": TimeFrame.H4,
            "d1": TimeFrame.D1,
            "daily": TimeFrame.D1,
            "hourly": TimeFrame.H1
        }
        
        for key, value in timeframes.items():
            if key in text.lower():
                return value
        
        return TimeFrame.H1  # Default
    
    def _extract_indicators(self, text: str) -> List[str]:
        """Extract mentioned indicators"""
        found_indicators = []
        
        for indicator, patterns in self.strategy_patterns["indicators"].items():
            for pattern in patterns:
                if re.search(pattern, text.lower()):
                    found_indicators.append(indicator)
                    break
        
        return found_indicators
    
    def _extract_risk_params(self, text: str) -> Dict[str, Any]:
        """Extract risk management parameters"""
        risk_params = {
            "stop_loss": None,
            "take_profit": None,
            "risk_per_trade": 1.0  # Default 1%
        }
        
        # Extract stop loss
        sl_pattern = r"stop loss.*?(\d+\.?\d*)\s*(?:pips?|%)"
        sl_match = re.search(sl_pattern, text.lower())
        if sl_match:
            risk_params["stop_loss"] = float(sl_match.group(1))
        
        # Extract take profit
        tp_pattern = r"take profit.*?(\d+\.?\d*)\s*(?:pips?|%)"
        tp_match = re.search(tp_pattern, text.lower())
        if tp_match:
            risk_params["take_profit"] = float(tp_match.group(1))
        
        # Extract risk per trade
        risk_pattern = r"risk.*?(\d+\.?\d*)\s*%"
        risk_match = re.search(risk_pattern, text.lower())
        if risk_match:
            risk_params["risk_per_trade"] = float(risk_match.group(1))
        
        return risk_params
    
    def generate_strategy_summary(self, parsed_strategy: Dict[str, Any]) -> str:
        """Generate human-readable strategy summary"""
        summary = f"Strategy Type: {parsed_strategy['type'].value}\n"
        summary += f"Timeframe: {parsed_strategy['timeframe'].value}\n"
        summary += f"Indicators: {', '.join(parsed_strategy['indicators'])}\n\n"
        
        summary += "Trading Conditions:\n"
        for condition in parsed_strategy['conditions']:
            summary += f"- {condition['type'].value.upper()}: {condition['condition']}\n"
        
        summary += f"\nRisk Management:\n"
        risk = parsed_strategy['risk_management']
        if risk['stop_loss']:
            summary += f"- Stop Loss: {risk['stop_loss']} pips\n"
        if risk['take_profit']:
            summary += f"- Take Profit: {risk['take_profit']} pips\n"
        summary += f"- Risk per Trade: {risk['risk_per_trade']}%\n"
        
        return summary 