"""
Google Gemini 2.5 Pro AI Intelligence Service
Crypto market analysis and trading decision engine
"""

import os
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
from google import genai
from google.genai import types

class GeminiAIService:
    def __init__(self):
        # Gemini API key'i environment'dan al
        api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyA_I6AtQI7xLjFBgLDkBpANfc8DNBPFIuo')
        os.environ['GOOGLE_API_KEY'] = api_key
        
        self.client = genai.Client()
        self.model = "gemini-2.5-pro"
        
    async def analyze_crypto_market(self, crypto_data: Dict) -> Dict:
        """
        Crypto piyasasını analiz et ve trading sinyalleri üret
        """
        prompt = f"""
        Sen bir profesyonel crypto trader ve AI analistisin. Aşağıdaki crypto verilerini analiz et:

        CRYPTO VERİLERİ:
        {json.dumps(crypto_data, indent=2)}

        GÖREVLER:
        1. Teknik analiz yap (trend, support/resistance, momentum)
        2. Her crypto için trading sinyali ver (BUY/SELL/HOLD)
        3. Risk seviyesi belirle (LOW/MEDIUM/HIGH)
        4. Hedef fiyat ve stop loss öner
        5. Pozisyon büyüklüğü öner (0.01-0.1 lot arası)

        ÇIKTI FORMATI (JSON):
        {{
            "analysis_time": "2024-01-01 12:00:00",
            "market_sentiment": "BULLISH/BEARISH/NEUTRAL",
            "signals": [
                {{
                    "symbol": "BTCUSD",
                    "action": "BUY/SELL/HOLD",
                    "confidence": 0.85,
                    "entry_price": 50000.0,
                    "stop_loss": 48000.0,
                    "take_profit": 52000.0,
                    "lot_size": 0.05,
                    "risk_level": "MEDIUM",
                    "reasoning": "Teknik analiz nedenleri..."
                }}
            ],
            "market_overview": "Genel piyasa durumu analizi..."
        }}

        SADECE JSON FORMATINDA YANIT VER, BAŞKA BİR ŞEY YAZMA.
        """

        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,  # Düşük temperature for consistent analysis
                    max_output_tokens=2048
                )
            )
            
            # JSON parse et
            analysis_text = response.text.strip()
            if analysis_text.startswith("```json"):
                analysis_text = analysis_text[7:-3]
            elif analysis_text.startswith("```"):
                analysis_text = analysis_text[3:-3]
                
            analysis = json.loads(analysis_text)
            return analysis
            
        except Exception as e:
            print(f"Gemini analiz hatası: {e}")
            return self._get_fallback_analysis()

    async def generate_crypto_strategy(self, market_conditions: Dict) -> Dict:
        """
        Piyasa koşullarına göre crypto trading stratejisi üret
        """
        prompt = f"""
        Crypto piyasa koşulları:
        {json.dumps(market_conditions, indent=2)}

        Aşağıdaki crypto çiftleri için hafta sonu trading stratejisi oluştur:
        - BTCUSD (Bitcoin)
        - ETHUSD (Ethereum) 
        - ADAUSD (Cardano)
        - DOTUSD (Polkadot)

        Her crypto için:
        1. Scalping stratejisi (5-15 dakika)
        2. Swing trading stratejisi (1-4 saat)
        3. Risk yönetimi kuralları
        4. Otomatik trading parametreleri

        JSON formatında detaylı strateji döndür.
        """

        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=3072
                )
            )
            
            strategy_text = response.text.strip()
            if strategy_text.startswith("```json"):
                strategy_text = strategy_text[7:-3]
            elif strategy_text.startswith("```"):
                strategy_text = strategy_text[3:-3]
                
            strategy = json.loads(strategy_text)
            return strategy
            
        except Exception as e:
            print(f"Strateji üretim hatası: {e}")
            return self._get_fallback_strategy()

    async def real_time_crypto_decision(self, live_data: Dict) -> Dict:
        """
        Gerçek zamanlı crypto trading kararı ver
        """
        prompt = f"""
        CANLI CRYPTO VERİLERİ:
        {json.dumps(live_data, indent=2)}

        ACIL TRADING KARARI VER:
        
        Mevcut piyasa durumuna göre:
        1. Hangi crypto'da işlem açılmalı?
        2. Long mu Short mu?
        3. Lot büyüklüğü ne olmalı?
        4. Stop Loss ve Take Profit seviyeleri?
        5. İşlem açma zamanı (şimdi mi, bekle mi)?

        HIZLI KARAR JSON FORMATI:
        {{
            "decision": "OPEN_TRADE/WAIT/CLOSE_POSITIONS",
            "symbol": "BTCUSD",
            "direction": "BUY/SELL",
            "urgency": "HIGH/MEDIUM/LOW",
            "lot_size": 0.05,
            "entry_price": 50000.0,
            "stop_loss": 49000.0,
            "take_profit": 51500.0,
            "reasoning": "Karar gerekçesi...",
            "execute_immediately": true
        }}
        """

        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.05,  # Çok düşük temperature for decisive action
                    max_output_tokens=1024
                )
            )
            
            decision_text = response.text.strip()
            if decision_text.startswith("```json"):
                decision_text = decision_text[7:-3]
            elif decision_text.startswith("```"):
                decision_text = decision_text[3:-3]
                
            decision = json.loads(decision_text)
            return decision
            
        except Exception as e:
            print(f"Karar verme hatası: {e}")
            return {"decision": "WAIT", "reasoning": f"AI hatası: {e}"}

    def _get_fallback_analysis(self) -> Dict:
        """Fallback analiz verisi"""
        return {
            "analysis_time": datetime.now().isoformat(),
            "market_sentiment": "NEUTRAL",
            "signals": [
                {
                    "symbol": "BTCUSD",
                    "action": "HOLD",
                    "confidence": 0.5,
                    "entry_price": 0.0,
                    "stop_loss": 0.0,
                    "take_profit": 0.0,
                    "lot_size": 0.01,
                    "risk_level": "LOW",
                    "reasoning": "AI servis hatası - güvenli mod"
                }
            ],
            "market_overview": "AI analiz servisi geçici olarak kullanılamıyor"
        }

    def _get_fallback_strategy(self) -> Dict:
        """Fallback strateji verisi"""
        return {
            "strategy_name": "Conservative Crypto Trading",
            "timeframe": "1H",
            "risk_level": "LOW",
            "strategies": {
                "BTCUSD": {
                    "scalping": {"enabled": False},
                    "swing": {"enabled": True, "lot_size": 0.01}
                }
            }
        } 