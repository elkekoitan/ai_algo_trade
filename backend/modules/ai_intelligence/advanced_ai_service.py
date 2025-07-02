"""
Advanced AI Intelligence Service
Integration with GPT-4, Gemini Pro, and Claude for enhanced trading intelligence
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import json
import openai
import google.generativeai as genai
from anthropic import Anthropic

from ...core.config.settings import get_settings
from ..mt5_integration.service import MT5Service
from ...core.enhanced_event_bus import enhanced_event_bus

logger = logging.getLogger(__name__)
settings = get_settings()

class AdvancedAIService:
    """Advanced AI service with multiple LLM providers"""
    
    def __init__(self):
        self.mt5_service = MT5Service()
        self.market_context = {}
        self.ai_insights = {}
        
        # Initialize AI clients
        self._init_ai_clients()
        
    def _init_ai_clients(self):
        """Initialize AI service clients"""
        try:
            # OpenAI GPT-4
            if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
                openai.api_key = settings.OPENAI_API_KEY
                self.openai_client = openai
                logger.info("✅ OpenAI GPT-4 initialized")
            else:
                logger.warning("⚠️ OpenAI API key not found")
                
            # Google Gemini Pro
            if hasattr(settings, 'GEMINI_API_KEY') and settings.GEMINI_API_KEY:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.gemini_model = genai.GenerativeModel('gemini-pro')
                logger.info("✅ Google Gemini Pro initialized")
            else:
                logger.warning("⚠️ Gemini API key not found")
                
            # Anthropic Claude
            if hasattr(settings, 'ANTHROPIC_API_KEY') and settings.ANTHROPIC_API_KEY:
                self.anthropic_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
                logger.info("✅ Anthropic Claude initialized")
            else:
                logger.warning("⚠️ Anthropic API key not found")
                
        except Exception as e:
            logger.error(f"Failed to initialize AI clients: {e}")
            
    # Market Analysis with AI
    async def analyze_market_with_ai(
        self, 
        symbol: str, 
        timeframe: str = "H1",
        analysis_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """Comprehensive market analysis using multiple AI models"""
        try:
            # Get market data
            market_data = await self._get_market_data(symbol, timeframe)
            
            # Run parallel analysis with different AI models
            tasks = []
            
            # GPT-4 Technical Analysis
            if hasattr(self, 'openai_client'):
                tasks.append(self._gpt4_technical_analysis(market_data))
                
            # Gemini Pro Sentiment Analysis  
            if hasattr(self, 'gemini_model'):
                tasks.append(self._gemini_sentiment_analysis(market_data))
                
            # Claude Strategic Analysis
            if hasattr(self, 'anthropic_client'):
                tasks.append(self._claude_strategic_analysis(market_data))
                
            # Execute all analyses in parallel
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Combine results
                combined_analysis = {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "analysis_timestamp": datetime.utcnow().isoformat(),
                    "technical_analysis": results[0] if len(results) > 0 and not isinstance(results[0], Exception) else None,
                    "sentiment_analysis": results[1] if len(results) > 1 and not isinstance(results[1], Exception) else None,
                    "strategic_analysis": results[2] if len(results) > 2 and not isinstance(results[2], Exception) else None,
                    "ai_consensus": self._calculate_ai_consensus(results),
                    "confidence_score": self._calculate_confidence(results)
                }
                
                # Store in cache
                self.ai_insights[f"{symbol}_{timeframe}"] = combined_analysis
                
                return combined_analysis
            else:
                return {"error": "No AI services available"}
                
        except Exception as e:
            logger.error(f"AI market analysis failed: {e}")
            return {"error": str(e)}
            
    async def _gpt4_technical_analysis(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Technical analysis using GPT-4"""
        try:
            prompt = f"""
            Analyze the following market data for technical trading signals:
            
            Symbol: {market_data['symbol']}
            Current Price: {market_data['current_price']}
            Price Data (last 50 bars): {market_data['price_history'][-50:]}
            Volume Data: {market_data['volume_data'][-10:]}
            RSI: {market_data.get('rsi', 'N/A')}
            MACD: {market_data.get('macd', 'N/A')}
            Moving Averages: {market_data.get('moving_averages', 'N/A')}
            
            Provide:
            1. Technical signal (BUY/SELL/HOLD)
            2. Confidence level (0-100)
            3. Key support/resistance levels
            4. Risk assessment
            5. Entry/exit strategy
            6. Stop loss and take profit recommendations
            
            Return analysis in JSON format.
            """
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert technical analyst with 20+ years of experience. Provide concise, actionable trading analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            analysis_text = response.choices[0].message.content
            
            # Try to parse JSON response
            try:
                return json.loads(analysis_text)
            except:
                # If not JSON, structure the response
                return {
                    "source": "GPT-4",
                    "analysis": analysis_text,
                    "signal": "HOLD",  # Default
                    "confidence": 70
                }
                
        except Exception as e:
            logger.error(f"GPT-4 analysis failed: {e}")
            return {"source": "GPT-4", "error": str(e)}
            
    async def _gemini_sentiment_analysis(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sentiment analysis using Gemini Pro"""
        try:
            prompt = f"""
            Analyze market sentiment for {market_data['symbol']} based on:
            
            Recent Price Action: {market_data['price_history'][-20:]}
            Volume Profile: {market_data['volume_data'][-10:]}
            Market News Context: {market_data.get('news_sentiment', 'Neutral')}
            
            Provide sentiment analysis including:
            1. Overall market sentiment (Bullish/Bearish/Neutral)
            2. Sentiment strength (0-100)
            3. Fear/Greed index
            4. Social media sentiment
            5. Institutional vs Retail sentiment
            6. Key sentiment drivers
            
            Format as JSON with clear metrics.
            """
            
            response = await asyncio.to_thread(
                self.gemini_model.generate_content, prompt
            )
            
            analysis_text = response.text
            
            # Parse or structure response
            try:
                return json.loads(analysis_text)
            except:
                return {
                    "source": "Gemini Pro",
                    "sentiment": "Neutral",
                    "strength": 50,
                    "analysis": analysis_text
                }
                
        except Exception as e:
            logger.error(f"Gemini analysis failed: {e}")
            return {"source": "Gemini Pro", "error": str(e)}
            
    async def _claude_strategic_analysis(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Strategic analysis using Claude"""
        try:
            prompt = f"""
            Provide strategic trading analysis for {market_data['symbol']}:
            
            Market Context:
            - Current Price: {market_data['current_price']}
            - 24h Change: {market_data.get('daily_change', 0)}%
            - Weekly Trend: {market_data.get('weekly_trend', 'Neutral')}
            - Key Levels: {market_data.get('key_levels', {})}
            
            Deliver strategic insights:
            1. Market regime analysis (Trending/Ranging/Volatile)
            2. Long-term trend assessment
            3. Risk-adjusted strategy recommendations
            4. Portfolio allocation suggestions
            5. Hedging recommendations
            6. Market correlation analysis
            
            Provide actionable strategic guidance in JSON format.
            """
            
            response = await asyncio.to_thread(
                self.anthropic_client.messages.create,
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                messages=[
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ]
            )
            
            analysis_text = response.content[0].text
            
            try:
                return json.loads(analysis_text)
            except:
                return {
                    "source": "Claude",
                    "strategy": "Conservative",
                    "analysis": analysis_text
                }
                
        except Exception as e:
            logger.error(f"Claude analysis failed: {e}")
            return {"source": "Claude", "error": str(e)}
            
    # Voice Trading with AI
    async def process_voice_command(self, audio_data: bytes, user_id: str) -> Dict[str, Any]:
        """Process voice trading commands"""
        try:
            # Convert speech to text (using OpenAI Whisper)
            if hasattr(self, 'openai_client'):
                transcript = await self._speech_to_text(audio_data)
                
                # Process trading command with AI
                command_analysis = await self._analyze_trading_command(transcript)
                
                if command_analysis.get("is_trading_command"):
                    # Execute trading action
                    result = await self._execute_voice_trade(command_analysis, user_id)
                    return result
                else:
                    # Provide market information
                    info = await self._provide_market_info(command_analysis)
                    return info
            else:
                return {"error": "Voice processing not available"}
                
        except Exception as e:
            logger.error(f"Voice command processing failed: {e}")
            return {"error": str(e)}
            
    async def _speech_to_text(self, audio_data: bytes) -> str:
        """Convert speech to text using Whisper"""
        try:
            # This would use OpenAI Whisper API
            # For now, return mock transcript
            return "Buy EURUSD with 0.1 lot size"
        except Exception as e:
            logger.error(f"Speech to text failed: {e}")
            return ""
            
    async def _analyze_trading_command(self, text: str) -> Dict[str, Any]:
        """Analyze voice command for trading intent"""
        try:
            prompt = f"""
            Analyze this voice command for trading intent: "{text}"
            
            Extract:
            1. Is this a trading command? (true/false)
            2. Action (buy/sell/close/info)
            3. Symbol (if mentioned)
            4. Volume/lot size (if mentioned)
            5. Price level (if mentioned)
            6. Stop loss (if mentioned)
            7. Take profit (if mentioned)
            8. Confidence in parsing (0-100)
            
            Return as JSON.
            """
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert at parsing trading voice commands. Be precise and conservative."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.1
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Command analysis failed: {e}")
            return {"is_trading_command": False, "error": str(e)}
            
    # AI Trading Mentor
    async def get_ai_mentor_advice(
        self, 
        user_id: str, 
        question: str,
        trading_history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Get personalized trading advice from AI mentor"""
        try:
            # Get user's trading profile
            user_profile = await self._get_user_trading_profile(user_id)
            
            # Prepare context
            context = f"""
            User Profile:
            - Experience Level: {user_profile.get('experience', 'Beginner')}
            - Risk Tolerance: {user_profile.get('risk_tolerance', 'Medium')}
            - Trading Style: {user_profile.get('trading_style', 'Swing')}
            - Recent Performance: {user_profile.get('recent_performance', 'Neutral')}
            
            Question: {question}
            """
            
            if trading_history:
                context += f"\nRecent Trades: {trading_history[-5:]}"
            
            # Get advice from multiple AI models
            gpt_advice = await self._get_gpt_mentor_advice(context)
            gemini_advice = await self._get_gemini_mentor_advice(context)
            
            # Combine and personalize advice
            combined_advice = {
                "question": question,
                "personalized_advice": self._combine_mentor_advice(gpt_advice, gemini_advice),
                "risk_assessment": self._assess_advice_risk(user_profile, question),
                "learning_resources": await self._suggest_learning_resources(question),
                "practice_suggestions": await self._suggest_practice_trades(user_profile),
                "mentor_confidence": 85,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return combined_advice
            
        except Exception as e:
            logger.error(f"AI mentor advice failed: {e}")
            return {"error": str(e)}
            
    # Helper Methods
    async def _get_market_data(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """Get comprehensive market data"""
        try:
            # Get real market data from MT5
            ticks = await self.mt5_service.get_market_data(symbol)
            
            return {
                "symbol": symbol,
                "current_price": ticks[-1]["bid"] if ticks else 1.0,
                "price_history": [t["bid"] for t in ticks[-100:]] if ticks else [],
                "volume_data": [t.get("volume", 1) for t in ticks[-50:]] if ticks else [],
                "daily_change": 0.5,  # Calculate from real data
                "weekly_trend": "Bullish",
                "key_levels": {"support": 1.0900, "resistance": 1.1000},
                "rsi": 55.5,
                "macd": {"value": 0.0012, "signal": 0.0008},
                "moving_averages": {"ma20": 1.0945, "ma50": 1.0920}
            }
            
        except Exception as e:
            logger.error(f"Failed to get market data: {e}")
            return {"symbol": symbol, "error": str(e)}
            
    def _calculate_ai_consensus(self, results: List[Any]) -> Dict[str, Any]:
        """Calculate consensus from multiple AI analyses"""
        valid_results = [r for r in results if not isinstance(r, Exception) and "error" not in r]
        
        if not valid_results:
            return {"consensus": "HOLD", "agreement": 0}
            
        # Extract signals
        signals = []
        for result in valid_results:
            if isinstance(result, dict):
                signal = result.get("signal", result.get("sentiment", "NEUTRAL"))
                signals.append(signal)
                
        # Calculate consensus
        if not signals:
            return {"consensus": "HOLD", "agreement": 0}
            
        # Count signal types
        signal_counts = {}
        for signal in signals:
            signal_counts[signal] = signal_counts.get(signal, 0) + 1
            
        # Find majority
        majority_signal = max(signal_counts.keys(), key=lambda k: signal_counts[k])
        agreement_pct = (signal_counts[majority_signal] / len(signals)) * 100
        
        return {
            "consensus": majority_signal,
            "agreement": agreement_pct,
            "signal_distribution": signal_counts
        }
        
    def _calculate_confidence(self, results: List[Any]) -> float:
        """Calculate overall confidence from AI results"""
        valid_results = [r for r in results if not isinstance(r, Exception) and "error" not in r]
        
        if not valid_results:
            return 0.0
            
        confidences = []
        for result in valid_results:
            if isinstance(result, dict):
                conf = result.get("confidence", result.get("strength", 50))
                confidences.append(conf)
                
        return sum(confidences) / len(confidences) if confidences else 50.0 