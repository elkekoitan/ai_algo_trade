"""
AI-powered market story generation using Gemini
"""

import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import google.generativeai as genai

from backend.core.logger import setup_logger
from .models import MarketStory, NewsEvent, StoryType, InfluenceLevel

logger = setup_logger(__name__)


class StoryGenerator:
    """Generate market narratives using Gemini AI"""
    
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
        
        # Story templates for fallback
        self.story_templates = self._load_story_templates()
    
    def _load_story_templates(self) -> Dict[str, str]:
        """Load story templates for different market scenarios"""
        return {
            "whale_activity": """
            🐋 **Büyük Oyuncu Aktivitesi Tespit Edildi**
            
            {symbol} paritesinde {volume:,.0f} USD büyüklüğünde bir {order_type} pozisyonu tespit edildi.
            
            📊 **Analiz Detayları:**
            - Whale Boyutu: {whale_size}
            - Impact Score: {impact_score}/10
            - Güven Seviyesi: %{confidence:.1f}
            
            💡 **Değerlendirme:** {evaluation}
            """,
            "technical_analysis": """
            📈 **Teknik Analiz Güncellemesi**
            
            {symbol} için güncellenen teknik göstergeler:
            
            📋 **Gösterge Durumu:**
            - RSI: {rsi_value}
            - MACD: {macd_status}
            - Trend: {trend_direction}
            
            🎯 **Öneriler:** {recommendations}
            """,
            "market_sentiment": """
            🌡️ **Piyasa Duygusu Analizi**
            
            {symbol} için güncel sentiment analizi:
            
            📊 **Sentiment Metrikleri:**
            - Genel Duygu: {sentiment_score}
            - Sosyal Medya: {social_sentiment}
            - Haber Etkisi: {news_impact}
            
            📝 **Özet:** {summary}
            """
        }
    
    async def generate_story(
        self,
        story_type: StoryType,
        symbol: str,
        data: Dict[str, Any],
        language: str = "turkish"
    ) -> MarketStory:
        """Generate a market story using Gemini AI"""
        try:
            if self.mock_mode:
                return self._generate_mock_story(story_type, symbol, data)
            
            # Generate story with Gemini
            story_content = await self._generate_with_gemini(story_type, symbol, data, language)
            
            if story_content:
                return self._create_story_object(story_type, symbol, story_content, data)
            else:
                # Fallback to template
                return self._generate_template_story(story_type, symbol, data)
                
        except Exception as e:
            logger.error(f"Error generating story: {str(e)}")
            return self._generate_template_story(story_type, symbol, data)
    
    async def _generate_with_gemini(
        self,
        story_type: StoryType,
        symbol: str,
        data: Dict[str, Any],
        language: str
    ) -> Optional[str]:
        """Use Gemini to generate market story"""
        try:
            # Prepare context based on story type
            context = self._prepare_context(story_type, symbol, data)
            
            prompt = f"""
            Create a professional market analysis story in {language} based on the following information:
            
            Story Type: {story_type}
            Symbol: {symbol}
            Context: {context}
            
            Requirements:
            1. Write in {language} language
            2. Use professional financial terminology
            3. Include specific data points and metrics
            4. Provide actionable insights
            5. Keep it concise but informative (200-300 words)
            6. Use appropriate emojis for visual appeal
            7. Structure with clear sections (Analysis, Data, Recommendations)
            
            Make the story engaging and informative for traders and investors.
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Gemini story generation error: {str(e)}")
            return None

    def _prepare_context(self, story_type: StoryType, symbol: str, data: Dict[str, Any]) -> str:
        """Prepare context string for Gemini prompt"""
        if story_type == StoryType.WHALE_ACTIVITY:
            return f"""
            Whale Detection Data:
            - Volume: ${data.get('volume', 0):,.0f}
            - Order Type: {data.get('order_type', 'Unknown')}
            - Whale Size: {data.get('whale_size', 'Unknown')}
            - Impact Score: {data.get('impact_score', 0)}/10
            - Confidence: {data.get('confidence', 0):.1%}
            - Price Level: {data.get('price_level', 'N/A')}
            """
        elif story_type == StoryType.TECHNICAL_ANALYSIS:
            return f"""
            Technical Indicators:
            - RSI: {data.get('rsi', 'N/A')}
            - MACD: {data.get('macd', 'N/A')}
            - Moving Averages: {data.get('ma_status', 'N/A')}
            - Trend Direction: {data.get('trend', 'Unknown')}
            - Support/Resistance: {data.get('levels', 'N/A')}
            """
        elif story_type == StoryType.MARKET_SENTIMENT:
            return f"""
            Sentiment Analysis:
            - Overall Sentiment: {data.get('sentiment_score', 'Neutral')}
            - Social Media Buzz: {data.get('social_sentiment', 'N/A')}
            - News Impact: {data.get('news_impact', 'N/A')}
            - Institutional Flow: {data.get('institutional_flow', 'N/A')}
            """
        else:
            return json.dumps(data, indent=2)
    
    def _generate_template_story(
        self,
        story_type: StoryType,
        symbol: str,
        data: Dict[str, Any]
    ) -> MarketStory:
        """Generate story using templates (fallback)"""
        try:
            if story_type == StoryType.WHALE_ACTIVITY:
                template = self.story_templates["whale_activity"]
                content = template.format(
                    symbol=symbol,
                    volume=data.get('volume', 0),
                    order_type=data.get('order_type', 'UNKNOWN'),
                    whale_size=data.get('whale_size', 'UNKNOWN'),
                    impact_score=data.get('impact_score', 0),
                    confidence=data.get('confidence', 0) * 100,
                    evaluation=self._generate_evaluation(data)
                )
            elif story_type == StoryType.TECHNICAL_ANALYSIS:
                template = self.story_templates["technical_analysis"]
                content = template.format(
                    symbol=symbol,
                    rsi_value=data.get('rsi', 'N/A'),
                    macd_status=data.get('macd', 'N/A'),
                    trend_direction=data.get('trend', 'SIDEWAYS'),
                    recommendations=self._generate_tech_recommendations(data)
                )
            else:
                template = self.story_templates["market_sentiment"]
                content = template.format(
                    symbol=symbol,
                    sentiment_score=data.get('sentiment_score', 'NEUTRAL'),
                    social_sentiment=data.get('social_sentiment', 'N/A'),
                    news_impact=data.get('news_impact', 'LOW'),
                    summary=self._generate_sentiment_summary(data)
                )
            
            return self._create_story_object(story_type, symbol, content, data)
            
        except Exception as e:
            logger.error(f"Template story generation error: {str(e)}")
            raise
    
    def _generate_mock_story(
        self,
        story_type: StoryType,
        symbol: str,
        data: Dict[str, Any]
    ) -> MarketStory:
        """Generate mock story for testing"""
        mock_content = f"""
        🤖 **Mock Story - {story_type.value}**
        
        Bu {symbol} için otomatik oluşturulan test hikayesidir.
        
        📊 **Test Verileri:**
        - Story Type: {story_type.value}
        - Symbol: {symbol}
        - Generated At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        💡 **Not:** Gerçek AI story generation için Gemini API key gereklidir.
        """
        
        return self._create_story_object(story_type, symbol, mock_content, data)
    
    def _create_story_object(
        self,
        story_type: StoryType,
        symbol: str,
        content: str,
        data: Dict[str, Any]
    ) -> MarketStory:
        """Create MarketStory object"""
        return MarketStory(
            story_id=f"story_{int(datetime.now().timestamp())}",
            title=self._generate_title(story_type, symbol),
            content=content,
            story_type=story_type,
            symbol=symbol,
            influence_level=self._calculate_influence_level(data),
            confidence_score=data.get('confidence', 0.7),
            data_sources=data.get('sources', []),
            related_events=data.get('events', []),
            generated_at=datetime.now()
        )
    
    def _generate_title(self, story_type: StoryType, symbol: str) -> str:
        """Generate story title"""
        title_templates = {
            StoryType.WHALE_ACTIVITY: f"🐋 {symbol} - Büyük Oyuncu Aktivitesi",
            StoryType.TECHNICAL_ANALYSIS: f"📈 {symbol} - Teknik Analiz Güncellemesi",
            StoryType.MARKET_SENTIMENT: f"🌡️ {symbol} - Piyasa Duygusu Analizi",
            StoryType.NEWS_IMPACT: f"📰 {symbol} - Haber Etkisi Analizi",
            StoryType.RISK_ALERT: f"⚠️ {symbol} - Risk Uyarısı"
        }
        return title_templates.get(story_type, f"📊 {symbol} - Piyasa Analizi")
    
    def _calculate_influence_level(self, data: Dict[str, Any]) -> InfluenceLevel:
        """Calculate influence level based on data"""
        impact_score = data.get('impact_score', 0)
        volume = data.get('volume', 0)
        confidence = data.get('confidence', 0)
        
        # Combine factors to determine influence level
        combined_score = (impact_score * 0.4 + min(volume / 1000000, 10) * 0.3 + confidence * 10 * 0.3)
        
        if combined_score >= 8:
            return InfluenceLevel.CRITICAL
        elif combined_score >= 6:
            return InfluenceLevel.HIGH
        elif combined_score >= 4:
            return InfluenceLevel.MEDIUM
        else:
            return InfluenceLevel.LOW
    
    def _generate_evaluation(self, data: Dict[str, Any]) -> str:
        """Generate evaluation text for whale activity"""
        impact = data.get('impact_score', 0)
        confidence = data.get('confidence', 0)
        
        if impact >= 8 and confidence >= 0.8:
            return "Yüksek güvenilirlik ile kritik seviye etki bekleniyor. Yakın takip önerilir."
        elif impact >= 6:
            return "Orta-yüksek seviye etki potansiyeli. Pozisyon ayarlaması değerlendirilebilir."
        elif impact >= 4:
            return "Sınırlı etki bekleniyor. Normal izleme süreci yeterli."
        else:
            return "Düşük etki seviyesi. Rutin piyasa aktivitesi kapsamında."
    
    def _generate_tech_recommendations(self, data: Dict[str, Any]) -> str:
        """Generate technical analysis recommendations"""
        trend = data.get('trend', '').lower()
        rsi = data.get('rsi', 50)
        
        recommendations = []
        
        if trend == 'bullish':
            recommendations.append("Yükseliş trendi devam ediyor")
        elif trend == 'bearish':
            recommendations.append("Düşüş trendi gözleniyor")
        
        if isinstance(rsi, (int, float)):
            if rsi > 70:
                recommendations.append("RSI aşırı alım bölgesinde")
            elif rsi < 30:
                recommendations.append("RSI aşırı satım bölgesinde")
        
        return ". ".join(recommendations) if recommendations else "Mevcut seviyeler takip edilmelidir"
    
    def _generate_sentiment_summary(self, data: Dict[str, Any]) -> str:
        """Generate sentiment analysis summary"""
        sentiment = data.get('sentiment_score', 'NEUTRAL').upper()
        
        summaries = {
            'BULLISH': "Genel piyasa duygusu olumlu. Alıcı baskısı güçlü.",
            'BEARISH': "Piyasa duygusu olumsuz. Satış baskısı görülüyor.",
            'NEUTRAL': "Karışık sinyaller. Dikkatli izleme önerilir.",
            'POSITIVE': "Pozitif sentiment hakim. Yükseliş potansiyeli var.",
            'NEGATIVE': "Negatif duygu ağırlıkta. Risk yönetimi önemli."
        }
        
        return summaries.get(sentiment, "Piyasa duygusu analiz ediliyor.") 