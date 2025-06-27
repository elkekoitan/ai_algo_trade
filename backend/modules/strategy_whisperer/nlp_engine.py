"""
Natural Language Processing Engine for Strategy Whisperer
"""

import os
import re
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import openai
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser

from backend.core.logger import get_logger
from .models import (
    StrategyIntent, Language, StrategyType, 
    IndicatorType, TimeFrame, TradingCondition
)

logger = get_logger(__name__)


class NLPEngine:
    """Natural language processing for strategy creation"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        if not self.api_key:
            logger.warning("OpenAI API key not found. Using mock mode.")
            self.mock_mode = True
        else:
            self.mock_mode = False
            openai.api_key = self.api_key
            self.llm = ChatOpenAI(
                model="gpt-4",
                temperature=0.3,
                openai_api_key=self.api_key
            )
        
        # Financial terms dictionary
        self.financial_terms = self._load_financial_terms()
        
        # Intent patterns
        self.intent_patterns = self._create_intent_patterns()
    
    def _load_financial_terms(self) -> Dict[str, List[str]]:
        """Load financial terminology dictionary"""
        return {
            "buy_signals": ["al", "buy", "long", "gir", "pozisyon aç", "alım"],
            "sell_signals": ["sat", "sell", "short", "çık", "pozisyon kapat", "satım"],
            "indicators": {
                "RSI": ["rsi", "relative strength", "göreceli güç"],
                "MACD": ["macd", "moving average convergence"],
                "MA": ["ma", "moving average", "hareketli ortalama", "sma", "ema"],
                "BOLLINGER": ["bollinger", "band", "bant"],
                "STOCHASTIC": ["stochastic", "stokastik"],
                "ATR": ["atr", "average true range", "ortalama gerçek aralık"],
                "ADX": ["adx", "trend güç", "trend strength"]
            },
            "timeframes": {
                "M1": ["1 dakika", "1 minute", "1m", "m1"],
                "M5": ["5 dakika", "5 minute", "5m", "m5"],
                "M15": ["15 dakika", "15 minute", "15m", "m15"],
                "M30": ["30 dakika", "30 minute", "30m", "m30"],
                "H1": ["1 saat", "1 hour", "1h", "h1", "saatlik"],
                "H4": ["4 saat", "4 hour", "4h", "h4"],
                "D1": ["günlük", "daily", "1d", "d1"],
                "W1": ["haftalık", "weekly", "1w", "w1"]
            },
            "conditions": {
                "above": ["üstünde", "üzerinde", "above", "over", "büyük"],
                "below": ["altında", "below", "under", "küçük"],
                "crosses_above": ["yukarı keser", "crosses above", "golden cross"],
                "crosses_below": ["aşağı keser", "crosses below", "death cross"]
            }
        }
    
    def _create_intent_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Create regex patterns for intent recognition"""
        return {
            "trend_following": [
                re.compile(r"trend.*takip|trend.*follow", re.I),
                re.compile(r"trendle.*git|go.*with.*trend", re.I)
            ],
            "mean_reversion": [
                re.compile(r"ortalama.*dön|mean.*reversion", re.I),
                re.compile(r"aşırı.*al|aşırı.*sat|overbought|oversold", re.I)
            ],
            "breakout": [
                re.compile(r"kırılım|breakout|destek.*kır|direnç.*kır", re.I),
                re.compile(r"seviye.*kır|level.*break", re.I)
            ],
            "scalping": [
                re.compile(r"scalp|hızlı.*al.*sat|quick.*trade", re.I),
                re.compile(r"kısa.*vadeli|short.*term", re.I)
            ]
        }
    
    async def process_input(self, text: str, language: Language = Language.TURKISH) -> StrategyIntent:
        """Process natural language input"""
        try:
            if self.mock_mode:
                return self._mock_process_input(text, language)
            
            # Detect intent and extract entities
            intent_type = self._detect_strategy_type(text)
            entities = self._extract_entities(text)
            confidence = self._calculate_confidence(text, entities)
            
            # Check what clarifications are needed
            clarifications = self._check_clarifications_needed(entities)
            
            return StrategyIntent(
                raw_text=text,
                language=language,
                detected_type=intent_type,
                confidence=confidence,
                entities=entities,
                clarifications_needed=clarifications
            )
            
        except Exception as e:
            logger.error(f"Error processing input: {str(e)}")
            raise
    
    def _detect_strategy_type(self, text: str) -> Optional[StrategyType]:
        """Detect strategy type from text"""
        text_lower = text.lower()
        
        # Check patterns
        for strategy_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if pattern.search(text):
                    return StrategyType(strategy_type)
        
        # Check keywords
        if any(word in text_lower for word in ["rsi", "macd", "ortalama"]):
            if "aşırı" in text_lower or "overbought" in text_lower:
                return StrategyType.MEAN_REVERSION
            else:
                return StrategyType.TREND_FOLLOWING
        
        return None
    
    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities from text"""
        entities = {
            "indicators": [],
            "conditions": [],
            "timeframe": None,
            "risk_params": {},
            "numbers": []
        }
        
        text_lower = text.lower()
        
        # Extract indicators
        for indicator, keywords in self.financial_terms["indicators"].items():
            if any(keyword in text_lower for keyword in keywords):
                entities["indicators"].append(indicator)
        
        # Extract timeframe
        for tf, keywords in self.financial_terms["timeframes"].items():
            if any(keyword in text_lower for keyword in keywords):
                entities["timeframe"] = tf
                break
        
        # Extract numbers
        numbers = re.findall(r'\b\d+(?:\.\d+)?\b', text)
        entities["numbers"] = [float(n) for n in numbers]
        
        # Extract conditions
        for condition, keywords in self.financial_terms["conditions"].items():
            if any(keyword in text_lower for keyword in keywords):
                entities["conditions"].append(condition)
        
        return entities
    
    def _calculate_confidence(self, text: str, entities: Dict[str, Any]) -> float:
        """Calculate confidence score for intent"""
        score = 0.0
        
        # Check for indicators
        if entities["indicators"]:
            score += 0.3
        
        # Check for conditions
        if entities["conditions"]:
            score += 0.2
        
        # Check for timeframe
        if entities["timeframe"]:
            score += 0.2
        
        # Check for numbers (parameters)
        if entities["numbers"]:
            score += 0.2
        
        # Check text length and structure
        if len(text.split()) > 5:
            score += 0.1
        
        return min(score, 1.0)
    
    def _check_clarifications_needed(self, entities: Dict[str, Any]) -> List[str]:
        """Check what clarifications are needed"""
        clarifications = []
        
        if not entities["indicators"]:
            clarifications.append("Hangi teknik göstergeyi kullanmak istersiniz?")
        
        if not entities["timeframe"]:
            clarifications.append("Hangi zaman diliminde işlem yapmak istersiniz?")
        
        if not entities.get("risk_params"):
            clarifications.append("Risk yönetimi için lot büyüklüğü veya yüzde belirtmek ister misiniz?")
        
        if entities["indicators"] and not entities["numbers"]:
            clarifications.append("Gösterge parametreleri için değerler belirtmek ister misiniz?")
        
        return clarifications
    
    def _mock_process_input(self, text: str, language: Language) -> StrategyIntent:
        """Mock processing for testing without API"""
        # Simple mock logic
        entities = self._extract_entities(text)
        
        return StrategyIntent(
            raw_text=text,
            language=language,
            detected_type=StrategyType.TREND_FOLLOWING,
            confidence=0.85,
            entities=entities,
            clarifications_needed=self._check_clarifications_needed(entities)
        )
    
    async def clarify_intent(self, intent: StrategyIntent, clarification: str) -> StrategyIntent:
        """Process clarification and update intent"""
        try:
            # Add clarification to original text
            updated_text = f"{intent.raw_text} {clarification}"
            
            # Re-process with additional context
            new_entities = self._extract_entities(updated_text)
            
            # Merge entities
            for key, value in new_entities.items():
                if isinstance(value, list):
                    intent.entities[key] = list(set(intent.entities.get(key, []) + value))
                elif value is not None:
                    intent.entities[key] = value
            
            # Update confidence
            intent.confidence = self._calculate_confidence(updated_text, intent.entities)
            
            # Re-check clarifications
            intent.clarifications_needed = self._check_clarifications_needed(intent.entities)
            
            return intent
            
        except Exception as e:
            logger.error(f"Error clarifying intent: {str(e)}")
            raise
    
    async def generate_strategy_description(self, intent: StrategyIntent) -> str:
        """Generate human-readable strategy description"""
        try:
            indicators = intent.entities.get("indicators", [])
            timeframe = intent.entities.get("timeframe", "H1")
            conditions = intent.entities.get("conditions", [])
            
            description = f"Bu strateji {timeframe} zaman diliminde "
            
            if indicators:
                description += f"{', '.join(indicators)} göstergelerini kullanarak "
            
            if intent.detected_type:
                type_names = {
                    StrategyType.TREND_FOLLOWING: "trend takip",
                    StrategyType.MEAN_REVERSION: "ortalamaya dönüş",
                    StrategyType.BREAKOUT: "kırılım",
                    StrategyType.SCALPING: "scalping"
                }
                description += f"{type_names.get(intent.detected_type, 'özel')} yaklaşımı ile "
            
            description += "işlem yapar."
            
            return description
            
        except Exception as e:
            logger.error(f"Error generating description: {str(e)}")
            return "Strateji açıklaması oluşturulamadı." 