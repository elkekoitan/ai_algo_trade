"""
MQL5 Code Generator for Strategy Whisperer
"""

import os
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
import google.generativeai as genai
from pydantic import BaseModel

from backend.core.logger import setup_logger
from .models import (
    StrategyIntent, StrategyType, 
    IndicatorType, TimeFrame, TradingCondition
)

logger = setup_logger(__name__)


class CodeSection(BaseModel):
    """Code section for organization"""
    name: str
    code: str
    line_start: int
    line_end: int


class MQL5Strategy(BaseModel):
    """Complete MQL5 strategy object"""
    name: str
    description: str
    full_code: str
    sections: List[CodeSection]
    indicators_used: List[str]
    timeframe: str
    confidence: float


class MQL5Generator:
    """Generate MQL5 code from strategy intents"""
    
    def __init__(self):
        # Updated Gemini API key
        self.api_key = os.getenv("GEMINI_API_KEY", "AIzaSyDNKT7NQTf8VX2PmEYa3TLjH9v_4K2sQWE")
        if not self.api_key:
            logger.warning("Gemini API key not found. Using mock mode.")
            self.mock_mode = True
        else:
            self.mock_mode = False
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # MQL5 templates
        self.base_template = self._load_base_template()
        self.indicator_templates = self._load_indicator_templates()
    
    def _load_base_template(self) -> str:
        """Load base MQL5 EA template"""
        return '''
//+------------------------------------------------------------------+
//|                                            AI_Generated_Strategy |
//|                                 AI Algo Trade - Strategy Whisperer |
//|                                                                  |
//+------------------------------------------------------------------+
#property copyright "AI Algo Trade"
#property link      "https://ai-algo-trade.com"
#property version   "1.00"
#property strict

//--- input parameters
input double LotSize = 0.1;
input int StopLoss = 50;
input int TakeProfit = 100;
input int MagicNumber = 123456;

//--- global variables
{GLOBAL_VARIABLES}

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
{INIT_CODE}
   return(INIT_SUCCEEDED);
}
            
//+------------------------------------------------------------------+
//| Expert deinitialization function                               |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
{DEINIT_CODE}
}

//+------------------------------------------------------------------+
//| Expert tick function                                            |
//+------------------------------------------------------------------+
void OnTick()
{
{TICK_CODE}
}

//+------------------------------------------------------------------+
//| Trading function                                               |
//+------------------------------------------------------------------+
{TRADING_FUNCTIONS}

//+------------------------------------------------------------------+
//| Utility functions                                              |
//+------------------------------------------------------------------+
{UTILITY_FUNCTIONS}
'''
    
    def _load_indicator_templates(self) -> Dict[str, str]:
        """Load indicator code templates"""
        return {
            "RSI": '''
// RSI Indicator
double GetRSI(int period = 14, int shift = 0)
{
    return iRSI(_Symbol, _Period, period, PRICE_CLOSE, shift);
}
''',
            "MACD": '''
// MACD Indicator
double GetMACD(int fast = 12, int slow = 26, int signal = 9, int mode = MODE_MAIN, int shift = 0)
{
    return iMACD(_Symbol, _Period, fast, slow, signal, PRICE_CLOSE, mode, shift);
}
''',
            "MA": '''
// Moving Average
double GetMA(int period = 20, int method = MODE_SMA, int shift = 0)
{
    return iMA(_Symbol, _Period, period, 0, method, PRICE_CLOSE, shift);
}
''',
            "BOLLINGER": '''
// Bollinger Bands
double GetBollinger(int period = 20, double deviation = 2.0, int mode = MODE_MAIN, int shift = 0)
{
    return iBands(_Symbol, _Period, period, deviation, 0, PRICE_CLOSE, mode, shift);
}
'''
        }
    
    async def generate_mql5_code(self, intent: StrategyIntent, strategy_name: str = "AI_Strategy") -> MQL5Strategy:
        """Generate complete MQL5 strategy code"""
        try:
            if self.mock_mode:
                return self._generate_template_code(intent, strategy_name)
            
            # Use Gemini for advanced code generation
            gemini_code = await self._generate_with_gemini(intent, strategy_name)
            
            if gemini_code:
                return self._parse_generated_code(gemini_code, intent, strategy_name)
            else:
                # Fallback to template
                return self._generate_template_code(intent, strategy_name)
                
        except Exception as e:
            logger.error(f"Error generating MQL5 code: {str(e)}")
            return self._generate_template_code(intent, strategy_name)
    
    async def _generate_with_gemini(self, intent: StrategyIntent, strategy_name: str) -> Optional[str]:
        """Use Gemini to generate MQL5 code"""
        try:
            indicators = intent.entities.get("indicators", [])
            timeframe = intent.entities.get("timeframe", "H1")
            conditions = intent.entities.get("conditions", [])
            numbers = intent.entities.get("numbers", [])
            
            prompt = f"""
            Generate a complete MQL5 Expert Advisor code for the following trading strategy:
            
            Strategy Name: {strategy_name}
            Strategy Type: {intent.detected_type}
            Indicators: {indicators}
            Timeframe: {timeframe}
            Conditions: {conditions}
            Parameters: {numbers}
            Original Description: "{intent.raw_text}"
            
            Requirements:
            1. Include proper MQL5 syntax and structure
            2. Add input parameters for customization
            3. Implement proper error handling
            4. Add meaningful comments
            5. Include position management (stop loss, take profit)
            6. Use proper MQL5 functions for indicators
            7. Implement entry and exit logic based on the strategy
            
            The code should be production-ready and follow MQL5 best practices.
            
            Generate ONLY the MQL5 code, no explanations.
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Gemini code generation error: {str(e)}")
            return None
    
    def _generate_template_code(self, intent: StrategyIntent, strategy_name: str) -> MQL5Strategy:
        """Generate code using templates (fallback method)"""
        try:
            indicators = intent.entities.get("indicators", [])
            timeframe = intent.entities.get("timeframe", "H1")
            
            # Start with base template
            code = self.base_template
            
            # Generate sections
            global_vars = self._generate_global_variables(indicators)
            init_code = self._generate_init_code(indicators)
            tick_code = self._generate_tick_code(intent)
            trading_functions = self._generate_trading_functions(intent)
            utility_functions = self._generate_utility_functions(indicators)
            
            # Replace placeholders
            code = code.replace("{GLOBAL_VARIABLES}", global_vars)
            code = code.replace("{INIT_CODE}", init_code)
            code = code.replace("{DEINIT_CODE}", "   // Cleanup code")
            code = code.replace("{TICK_CODE}", tick_code)
            code = code.replace("{TRADING_FUNCTIONS}", trading_functions)
            code = code.replace("{UTILITY_FUNCTIONS}", utility_functions)
            
            # Create sections
            sections = [
                CodeSection(
                    name="Headers",
                    code=self._extract_headers(code),
                    line_start=1,
                    line_end=20
                ),
                CodeSection(
                    name="Input Parameters",
                    code=self._extract_inputs(code),
                    line_start=21,
                    line_end=30
                ),
                CodeSection(
                    name="Trading Logic",
                    code=self._extract_trading_logic(code),
                    line_start=50,
                    line_end=100
                )
            ]
            
            return MQL5Strategy(
                name=strategy_name,
                description=f"AI Generated Strategy based on {intent.detected_type}",
                full_code=code,
                sections=sections,
                indicators_used=indicators,
                timeframe=timeframe,
                confidence=intent.confidence
            )
            
        except Exception as e:
            logger.error(f"Template generation error: {str(e)}")
            raise
    
    def _parse_generated_code(self, code: str, intent: StrategyIntent, strategy_name: str) -> MQL5Strategy:
        """Parse Gemini-generated code into MQL5Strategy object"""
        try:
            # Clean up the code
            code = self._clean_generated_code(code)
            
            # Extract sections
            sections = self._extract_code_sections(code)
            
            return MQL5Strategy(
                name=strategy_name,
                description=f"AI Generated Strategy using Gemini",
                full_code=code,
                sections=sections,
                indicators_used=intent.entities.get("indicators", []),
                timeframe=intent.entities.get("timeframe", "H1"),
                confidence=intent.confidence
            )
            
        except Exception as e:
            logger.error(f"Code parsing error: {str(e)}")
            raise
    
    def _clean_generated_code(self, code: str) -> str:
        """Clean and format generated code"""
        # Remove markdown code blocks if present
        code = re.sub(r'```(?:mql5|cpp)?\n?', '', code)
        code = re.sub(r'```\n?', '', code)
        
        # Ensure proper line endings
        code = code.replace('\r\n', '\n').replace('\r', '\n')
        
        # Remove excessive whitespace
        lines = [line.rstrip() for line in code.split('\n')]
        code = '\n'.join(lines)
        
        return code
    
    def _extract_code_sections(self, code: str) -> List[CodeSection]:
        """Extract logical sections from generated code"""
        sections = []
        lines = code.split('\n')
        
        current_section = None
        section_start = 0
        
        for i, line in enumerate(lines):
            # Detect section headers
            if '//+------------------------------------------------------------------+' in line:
                if current_section:
                    # End previous section
                    section_code = '\n'.join(lines[section_start:i])
                    sections.append(CodeSection(
                        name=current_section,
                        code=section_code,
                        line_start=section_start + 1,
                        line_end=i
                    ))
                
                # Start new section
                if i + 1 < len(lines):
                    section_name = lines[i + 1].strip('//| ')
                    current_section = section_name
                    section_start = i
        
        # Add final section
        if current_section:
            section_code = '\n'.join(lines[section_start:])
            sections.append(CodeSection(
                name=current_section,
                code=section_code,
                line_start=section_start + 1,
                line_end=len(lines)
            ))
        
        return sections
    
    def _generate_global_variables(self, indicators: List[str]) -> str:
        """Generate global variable declarations"""
        vars_code = []
        
        for indicator in indicators:
            if indicator == "RSI":
                vars_code.append("int rsi_period = 14;")
            elif indicator == "MACD":
                vars_code.append("int macd_fast = 12;")
                vars_code.append("int macd_slow = 26;")
                vars_code.append("int macd_signal = 9;")
            elif indicator == "MA":
                vars_code.append("int ma_period = 20;")
        
        return "\n".join(f"   {var}" for var in vars_code)
    
    def _generate_init_code(self, indicators: List[str]) -> str:
        """Generate initialization code"""
        return "   Print(\"AI Strategy initialized with indicators: \", ArraySize(indicators));"
    
    def _generate_tick_code(self, intent: StrategyIntent) -> str:
        """Generate main tick processing code"""
        return '''
   // Check for new bar
   static datetime last_bar_time = 0;
   if (Time[0] == last_bar_time) return;
   last_bar_time = Time[0];
   
   // Trading logic
   if (ShouldOpenBuy())
   {
       OpenBuyOrder();
   }
   else if (ShouldOpenSell())
   {
       OpenSellOrder();
   }
'''
    
    def _generate_trading_functions(self, intent: StrategyIntent) -> str:
        """Generate trading functions"""
        return '''
bool ShouldOpenBuy()
{
    // Add buy conditions based on strategy
    return false;
}

bool ShouldOpenSell()
{
    // Add sell conditions based on strategy
    return false;
}

void OpenBuyOrder()
{
    double price = Ask;
    double sl = price - StopLoss * _Point;
    double tp = price + TakeProfit * _Point;
    
    int ticket = OrderSend(_Symbol, OP_BUY, LotSize, price, 3, sl, tp, "AI Strategy Buy", MagicNumber, 0, clrGreen);
}

void OpenSellOrder()
{
    double price = Bid;
    double sl = price + StopLoss * _Point;
    double tp = price - TakeProfit * _Point;
    
    int ticket = OrderSend(_Symbol, OP_SELL, LotSize, price, 3, sl, tp, "AI Strategy Sell", MagicNumber, 0, clrRed);
}
'''
    
    def _generate_utility_functions(self, indicators: List[str]) -> str:
        """Generate utility functions"""
        functions = []
        
        for indicator in indicators:
            if indicator in self.indicator_templates:
                functions.append(self.indicator_templates[indicator])
        
        return "\n".join(functions)
    
    def _extract_headers(self, code: str) -> str:
        """Extract header section"""
        lines = code.split('\n')
        header_lines = []
        for line in lines:
            if line.startswith('#property') or line.startswith('//'):
                header_lines.append(line)
            elif line.strip() and not line.startswith('//'):
                break
        return '\n'.join(header_lines)
    
    def _extract_inputs(self, code: str) -> str:
        """Extract input parameters section"""
        lines = code.split('\n')
        input_lines = []
        in_input_section = False
        
        for line in lines:
            if line.startswith('input '):
                in_input_section = True
                input_lines.append(line)
            elif in_input_section and line.strip() == '':
                continue
            elif in_input_section and not line.startswith('input '):
                break
        
        return '\n'.join(input_lines)
    
    def _extract_trading_logic(self, code: str) -> str:
        """Extract main trading logic"""
        lines = code.split('\n')
        logic_lines = []
        in_logic_section = False
        
        for line in lines:
            if 'OnTick()' in line:
                in_logic_section = True
            elif in_logic_section:
                logic_lines.append(line)
                if line.strip() == '}' and len([l for l in logic_lines if l.strip() == '{']) == len([l for l in logic_lines if l.strip() == '}']):
                    break
        
        return '\n'.join(logic_lines) 