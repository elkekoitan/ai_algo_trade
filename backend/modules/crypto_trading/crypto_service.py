"""
Crypto Trading Service
Tickmill Demo hesapta crypto işlemleri için özel servis
"""

import asyncio
import MetaTrader5 as mt5
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import pandas as pd
import sys
import os

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.append(backend_path)

from modules.mt5_integration.service import MT5Service
from modules.ai_intelligence.gemini_service import GeminiAIService

class CryptoTradingService:
    def __init__(self):
        self.mt5_service = MT5Service()
        self.gemini_ai = GeminiAIService()
        
        # Tickmill Demo'da mevcut crypto semboller
        self.crypto_symbols = [
            "BTCUSD",   # Bitcoin
            "ETHUSD",   # Ethereum
            "ADAUSD",   # Cardano
            "DOTUSD",   # Polkadot
            "LTCUSD",   # Litecoin
            "XRPUSD",   # Ripple
        ]
        
        self.active_trades = {}
        self.last_analysis = None
        
    async def initialize_crypto_trading(self):
        """Crypto trading sistemini başlat"""
        try:
            # MT5 bağlantısını kontrol et
            if not await self.mt5_service.connect():
                raise Exception("MT5 bağlantısı başarısız")
            
            # Crypto sembolleri için market watch'a ekle
            for symbol in self.crypto_symbols:
                await self.add_symbol_to_market_watch(symbol)
            
            print("✅ Crypto Trading sistemi başlatıldı")
            print(f"📊 İzlenen crypto'lar: {', '.join(self.crypto_symbols)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Crypto trading başlatma hatası: {e}")
            return False

    async def add_symbol_to_market_watch(self, symbol: str):
        """Sembolü market watch'a ekle"""
        try:
            if not mt5.symbol_select(symbol, True):
                print(f"⚠️ {symbol} sembolü eklenemedi veya mevcut değil")
            else:
                print(f"✅ {symbol} market watch'a eklendi")
        except Exception as e:
            print(f"❌ {symbol} ekleme hatası: {e}")

    async def get_crypto_market_data(self) -> Dict:
        """Tüm crypto'lar için piyasa verilerini al"""
        market_data = {
            "timestamp": datetime.now().isoformat(),
            "symbols": {}
        }
        
        for symbol in self.crypto_symbols:
            try:
                # Güncel fiyat bilgileri
                tick = mt5.symbol_info_tick(symbol)
                if tick is None:
                    continue
                
                # OHLC verileri (son 100 bar)
                rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 100)
                if rates is None or len(rates) == 0:
                    continue
                
                df = pd.DataFrame(rates)
                df['time'] = pd.to_datetime(df['time'], unit='s')
                
                # Teknik göstergeler hesapla
                df['sma_20'] = df['close'].rolling(20).mean()
                df['sma_50'] = df['close'].rolling(50).mean()
                df['rsi'] = self.calculate_rsi(df['close'])
                
                market_data["symbols"][symbol] = {
                    "current_price": {
                        "bid": tick.bid,
                        "ask": tick.ask,
                        "spread": tick.ask - tick.bid
                    },
                    "ohlc": {
                        "open": float(df.iloc[-1]['open']),
                        "high": float(df.iloc[-1]['high']),
                        "low": float(df.iloc[-1]['low']),
                        "close": float(df.iloc[-1]['close'])
                    },
                    "technical_indicators": {
                        "sma_20": float(df.iloc[-1]['sma_20']) if not pd.isna(df.iloc[-1]['sma_20']) else None,
                        "sma_50": float(df.iloc[-1]['sma_50']) if not pd.isna(df.iloc[-1]['sma_50']) else None,
                        "rsi": float(df.iloc[-1]['rsi']) if not pd.isna(df.iloc[-1]['rsi']) else None,
                        "trend": "UP" if df.iloc[-1]['close'] > df.iloc[-1]['sma_20'] else "DOWN"
                    },
                    "volume": int(df.iloc[-1]['tick_volume']),
                    "change_24h": self.calculate_24h_change(df)
                }
                
            except Exception as e:
                print(f"❌ {symbol} veri alma hatası: {e}")
                continue
        
        return market_data

    def calculate_rsi(self, prices, period=14):
        """RSI hesapla"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def calculate_24h_change(self, df):
        """24 saatlik değişim hesapla"""
        if len(df) < 288:  # 24 saat * 12 (5 dakikalık barlar)
            return 0.0
        
        current_price = df.iloc[-1]['close']
        price_24h_ago = df.iloc[-288]['close']
        return ((current_price - price_24h_ago) / price_24h_ago) * 100

    async def analyze_and_trade(self):
        """Piyasa analizi yap ve trading kararları ver"""
        try:
            # 1. Piyasa verilerini al
            market_data = await self.get_crypto_market_data()
            
            if not market_data["symbols"]:
                print("❌ Piyasa verisi alınamadı")
                return
            
            # 2. Gemini AI ile analiz yap
            analysis = await self.gemini_ai.analyze_crypto_market(market_data)
            self.last_analysis = analysis
            
            print(f"🧠 AI Analiz Tamamlandı: {analysis.get('market_sentiment', 'UNKNOWN')}")
            
            # 3. Trading sinyallerini işle
            for signal in analysis.get("signals", []):
                await self.process_trading_signal(signal)
            
            return analysis
            
        except Exception as e:
            print(f"❌ Analiz ve trading hatası: {e}")
            return None

    async def process_trading_signal(self, signal: Dict):
        """Trading sinyalini işle ve gerekirse işlem aç"""
        symbol = signal.get("symbol")
        action = signal.get("action")
        confidence = signal.get("confidence", 0.0)
        
        if confidence < 0.7:  # Düşük güven seviyesi
            print(f"⚠️ {symbol}: Düşük güven seviyesi ({confidence:.2f}), işlem atlandı")
            return
        
        if action == "BUY":
            await self.open_buy_trade(signal)
        elif action == "SELL":
            await self.open_sell_trade(signal)
        elif action == "HOLD":
            print(f"📊 {symbol}: HOLD sinyali - mevcut pozisyon korunuyor")

    async def open_buy_trade(self, signal: Dict):
        """Long pozisyon aç"""
        symbol = signal.get("symbol")
        lot_size = signal.get("lot_size", 0.01)
        stop_loss = signal.get("stop_loss")
        take_profit = signal.get("take_profit")
        
        try:
            # Sembol bilgilerini al
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                print(f"❌ {symbol} sembol bilgisi alınamadı")
                return
            
            # Güncel fiyat
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                print(f"❌ {symbol} fiyat bilgisi alınamadı")
                return
            
            # Trade request oluştur
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot_size,
                "type": mt5.ORDER_TYPE_BUY,
                "price": tick.ask,
                "sl": stop_loss if stop_loss else 0,
                "tp": take_profit if take_profit else 0,
                "deviation": 20,
                "magic": 123456,
                "comment": f"AI_CRYPTO_BUY_{signal.get('confidence', 0):.2f}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # İşlemi gönder
            result = mt5.order_send(request)
            
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"✅ {symbol} BUY işlemi açıldı:")
                print(f"   📈 Lot: {lot_size}")
                print(f"   💰 Fiyat: {tick.ask}")
                print(f"   🛡️ SL: {stop_loss}")
                print(f"   🎯 TP: {take_profit}")
                print(f"   🤖 Güven: {signal.get('confidence', 0):.2f}")
                
                # Aktif işlemlere ekle
                self.active_trades[result.order] = {
                    "symbol": symbol,
                    "type": "BUY",
                    "volume": lot_size,
                    "open_price": tick.ask,
                    "open_time": datetime.now(),
                    "signal": signal
                }
            else:
                print(f"❌ {symbol} BUY işlemi başarısız: {result.retcode}")
                
        except Exception as e:
            print(f"❌ {symbol} BUY işlemi hatası: {e}")

    async def open_sell_trade(self, signal: Dict):
        """Short pozisyon aç"""
        symbol = signal.get("symbol")
        lot_size = signal.get("lot_size", 0.01)
        stop_loss = signal.get("stop_loss")
        take_profit = signal.get("take_profit")
        
        try:
            # Sembol bilgilerini al
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                print(f"❌ {symbol} sembol bilgisi alınamadı")
                return
            
            # Güncel fiyat
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                print(f"❌ {symbol} fiyat bilgisi alınamadı")
                return
            
            # Trade request oluştur
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot_size,
                "type": mt5.ORDER_TYPE_SELL,
                "price": tick.bid,
                "sl": stop_loss if stop_loss else 0,
                "tp": take_profit if take_profit else 0,
                "deviation": 20,
                "magic": 123456,
                "comment": f"AI_CRYPTO_SELL_{signal.get('confidence', 0):.2f}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # İşlemi gönder
            result = mt5.order_send(request)
            
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"✅ {symbol} SELL işlemi açıldı:")
                print(f"   📉 Lot: {lot_size}")
                print(f"   💰 Fiyat: {tick.bid}")
                print(f"   🛡️ SL: {stop_loss}")
                print(f"   🎯 TP: {take_profit}")
                print(f"   🤖 Güven: {signal.get('confidence', 0):.2f}")
                
                # Aktif işlemlere ekle
                self.active_trades[result.order] = {
                    "symbol": symbol,
                    "type": "SELL",
                    "volume": lot_size,
                    "open_price": tick.bid,
                    "open_time": datetime.now(),
                    "signal": signal
                }
            else:
                print(f"❌ {symbol} SELL işlemi başarısız: {result.retcode}")
                
        except Exception as e:
            print(f"❌ {symbol} SELL işlemi hatası: {e}")

    async def get_active_positions(self):
        """Aktif pozisyonları getir"""
        try:
            positions = mt5.positions_get()
            if positions is None:
                return []
            
            crypto_positions = []
            for pos in positions:
                if pos.symbol in self.crypto_symbols:
                    crypto_positions.append({
                        "ticket": pos.ticket,
                        "symbol": pos.symbol,
                        "type": "BUY" if pos.type == 0 else "SELL",
                        "volume": pos.volume,
                        "open_price": pos.price_open,
                        "current_price": pos.price_current,
                        "profit": pos.profit,
                        "swap": pos.swap,
                        "open_time": datetime.fromtimestamp(pos.time),
                        "comment": pos.comment
                    })
            
            return crypto_positions
            
        except Exception as e:
            print(f"❌ Pozisyon bilgisi alma hatası: {e}")
            return []

    async def start_auto_trading(self, interval_minutes: int = 5):
        """Otomatik trading döngüsünü başlat"""
        print(f"🚀 Crypto Auto Trading başlatıldı (Her {interval_minutes} dakikada)")
        
        while True:
            try:
                print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - Analiz döngüsü başlıyor...")
                
                # Analiz ve trading
                analysis = await self.analyze_and_trade()
                
                # Mevcut pozisyonları göster
                positions = await self.get_active_positions()
                if positions:
                    print(f"📊 Aktif pozisyonlar: {len(positions)}")
                    for pos in positions:
                        profit_emoji = "💚" if pos["profit"] > 0 else "❤️"
                        print(f"   {profit_emoji} {pos['symbol']} {pos['type']}: {pos['profit']:.2f} USD")
                
                # Bekleme
                await asyncio.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                print("\n🛑 Auto trading durduruldu")
                break
            except Exception as e:
                print(f"❌ Auto trading hatası: {e}")
                await asyncio.sleep(60)  # Hata durumunda 1 dakika bekle 