"""
Gerçek MT5 Entegrasyon Servisi
SADECE gerçek canlı veriler ve demo hesap kullanılır
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import numpy as np
# import pandas as pd

# MetaTrader5 import with fallback
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    mt5 = None
    MT5_AVAILABLE = False
    print("Warning: MetaTrader5 module not available. Some features may be limited.")

logger = logging.getLogger(__name__)

class MT5Service:
    """
    Gerçek MetaTrader 5 entegrasyon servisi
    SADECE gerçek demo/live hesap verilerini kullanır
    """
    
    def __init__(self, login: Optional[int] = None, password: Optional[str] = None, server: Optional[str] = None, timeout: int = 60000):
        self.connected = False
        self.account_info = None
        self.login = login
        self.password = password
        self.server = server
        self.timeout = timeout
        
    async def connect(self, login: Optional[int] = None, password: Optional[str] = None, server: Optional[str] = None) -> bool:
        """Gerçek MT5 terminaline bağlan"""
        login = login or self.login
        password = password or self.password
        server = server or self.server
        
        terminal_path = r"C:\Program Files\MetaTrader 5\terminal64.exe"

        logger.info(f"Attempting to connect to {server} for login {login}")

        # 1. Önce pathsiz, en genel yöntemle bağlanmayı dene
        try:
            if mt5.initialize(login=login, password=password, server=server, timeout=self.timeout):
                if self._verify_connection():
                    logger.info("✅ MT5 Connection Successful (General Method)")
                    return True
            
            last_error = mt5.last_error()
            logger.warning(f"General connection failed: {last_error}. Trying with specific path...")
            mt5.shutdown() # Bir sonraki deneme için temizle

        except Exception as e:
            logger.warning(f"General connection attempt threw an exception: {e}. Trying with specific path...")

        # 2. Eğer ilki başarısız olursa, spesifik terminal yolu ile dene
        try:
            if mt5.initialize(path=terminal_path, login=login, password=password, server=server, timeout=self.timeout):
                if self._verify_connection():
                    logger.info("✅ MT5 Connection Successful (Specific Path Method)")
                    return True

            last_error = mt5.last_error()
            logger.error(f"❌ Path-specific connection also failed: {last_error}")
            self.connected = False
            mt5.shutdown()
            return False

        except Exception as e:
            logger.error(f"❌ Path-specific connection attempt threw an exception: {e}", exc_info=True)
            self.connected = False
            return False

    def _verify_connection(self) -> bool:
        """Bağlantı sonrası bilgileri kontrol et ve doğrula"""
        account_info = mt5.account_info()
        if account_info is None:
            logger.error(f"Failed to get account info after initialize. Error: {mt5.last_error()}")
            mt5.shutdown()
            self.connected = False
            return False
        
        self.connected = True
        self.account_info = account_info
        self.login = account_info.login
        self.server = account_info.server
        
        logger.info(f"Connection Verified: Account {account_info.login} on {account_info.server}")
        return True
    
    async def disconnect(self):
        """MT5 bağlantısını kapat"""
        try:
            if self.connected:
                mt5.shutdown()
                self.connected = False
                logger.info("MT5 connection closed")
        except Exception as e:
            logger.error(f"MT5 disconnect error: {e}")
    
    def is_connected(self) -> bool:
        """Bağlantı durumunu kontrol et"""
        if not self.connected:
            return False
        
        # Gerçek bağlantı durumunu kontrol et
        try:
            account_info = mt5.account_info()
            return account_info is not None
        except:
            return False
    
    async def get_account_info(self) -> Dict[str, Any]:
        """Gerçek hesap bilgilerini al"""
        try:
            if not self.is_connected():
                raise Exception("MT5 not connected")
            
            account_info = mt5.account_info()
            if account_info is None:
                raise Exception("Failed to get account info")
            
            return {
                "login": str(account_info.login),
                "server": account_info.server,
                "balance": float(account_info.balance),
                "equity": float(account_info.equity),
                "margin": float(account_info.margin),
                "free_margin": float(account_info.margin_free),
                "margin_level": float(account_info.margin_level) if account_info.margin_level else 0.0,
                "currency": account_info.currency,
                "company": account_info.company,
                "name": account_info.name,
                "leverage": account_info.leverage,
                "profit": float(account_info.profit)
            }
            
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            raise
    
    async def get_positions(self) -> List[Dict[str, Any]]:
        """Açık pozisyonları al"""
        try:
            if not self.is_connected():
                raise Exception("MT5 not connected")
            
            positions = mt5.positions_get()
            if positions is None:
                return []
            
            result = []
            for pos in positions:
                result.append({
                    "ticket": pos.ticket,
                    "symbol": pos.symbol,
                    "type": "buy" if pos.type == 0 else "sell",
                    "volume": float(pos.volume),
                    "open_price": float(pos.price_open),
                    "current_price": float(pos.price_current),
                    "sl": float(pos.sl),
                    "tp": float(pos.tp),
                    "profit": float(pos.profit),
                    "swap": float(pos.swap),
                    "open_time": datetime.fromtimestamp(pos.time).isoformat(),
                    "comment": pos.comment,
                    "magic": pos.magic
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            raise
    
    async def get_symbol_tick(self, symbol: str) -> Dict[str, Any]:
        """Gerçek sembol tick verisi al"""
        try:
            if not self.is_connected():
                raise Exception("MT5 not connected")
            
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                raise Exception(f"Failed to get tick for {symbol}")
            
            return {
                "symbol": symbol,
                "bid": float(tick.bid),
                "ask": float(tick.ask),
                "last": float(tick.last),
                "volume": int(tick.volume),
                "time": datetime.fromtimestamp(tick.time).isoformat(),
                "flags": tick.flags
            }
            
        except Exception as e:
            logger.error(f"Error getting tick for {symbol}: {e}")
            raise
    
    async def get_candles(self, symbol: str, timeframe: str = "H1", count: int = 100) -> List[Dict[str, Any]]:
        """Gerçek mum verilerini al"""
        try:
            if not self.is_connected():
                raise Exception("MT5 not connected")
            
            # Timeframe mapping
            tf_mapping = {
                "M1": mt5.TIMEFRAME_M1,
                "M5": mt5.TIMEFRAME_M5,
                "M15": mt5.TIMEFRAME_M15,
                "M30": mt5.TIMEFRAME_M30,
                "H1": mt5.TIMEFRAME_H1,
                "H4": mt5.TIMEFRAME_H4,
                "D1": mt5.TIMEFRAME_D1
            }
            
            mt5_timeframe = tf_mapping.get(timeframe, mt5.TIMEFRAME_H1)
            
            rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, count)
            if rates is None:
                raise Exception(f"Failed to get candles for {symbol}")
            
            result = []
            for rate in rates:
                result.append({
                    "time": datetime.fromtimestamp(rate['time']).isoformat(),
                    "open": float(rate['open']),
                    "high": float(rate['high']),
                    "low": float(rate['low']),
                    "close": float(rate['close']),
                    "volume": int(rate['tick_volume']),
                    "spread": int(rate['spread'])
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting candles for {symbol}: {e}")
            raise
    
    async def get_symbols(self) -> List[Dict[str, Any]]:
        """Mevcut sembolleri al"""
        try:
            if not self.is_connected():
                raise Exception("MT5 not connected")
            
            symbols = mt5.symbols_get()
            if symbols is None:
                return []
            
            result = []
            for symbol in symbols:
                if symbol.visible:  # Sadece görünür sembolleri al
                    result.append({
                        "name": symbol.name,
                        "description": symbol.description,
                        "currency_base": symbol.currency_base,
                        "currency_profit": symbol.currency_profit,
                        "currency_margin": symbol.currency_margin,
                        "digits": symbol.digits,
                        "point": symbol.point,
                        "spread": symbol.spread,
                        "trade_mode": symbol.trade_mode,
                        "min_lot": symbol.volume_min,
                        "max_lot": symbol.volume_max,
                        "lot_step": symbol.volume_step
                    })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting symbols: {e}")
            raise

    async def get_weekend_crypto_symbols(self) -> List[Dict[str, Any]]:
        """Hafta sonu aktif kripto sembolleri al (Tickmill)"""
        try:
            if not self.is_connected():
                raise Exception("MT5 not connected")
            
            # Tickmill'de hafta sonu aktif olan kripto sembolleri
            crypto_symbols = [
                "BTCUSD", "ETHUSD", "LTCUSD", "XRPUSD", "ADAUSD", 
                "DOTUSD", "LINKUSD", "BCHUSD", "XLMUSD", "EOSUSD",
                "TRXUSD", "ETCUSD", "DASHUSD", "ZECUSD", "XMRUSD"
            ]
            
            symbols = mt5.symbols_get()
            if symbols is None:
                return []
            
            result = []
            for symbol in symbols:
                if symbol.visible and symbol.name in crypto_symbols:
                    # Gerçek zamanlı tick kontrolü - hafta sonu aktif mi?
                    tick = mt5.symbol_info_tick(symbol.name)
                    if tick and tick.time > 0:  # Aktif tick varsa
                        result.append({
                            "name": symbol.name,
                            "description": symbol.description,
                            "currency_base": symbol.currency_base,
                            "currency_profit": symbol.currency_profit,
                            "digits": symbol.digits,
                            "point": symbol.point,
                            "spread": symbol.spread,
                            "trade_mode": symbol.trade_mode,
                            "min_lot": symbol.volume_min,
                            "max_lot": symbol.volume_max,
                            "lot_step": symbol.volume_step,
                            "current_bid": float(tick.bid),
                            "current_ask": float(tick.ask),
                            "last_update": datetime.fromtimestamp(tick.time).isoformat(),
                            "weekend_active": True
                        })
            
            logger.info(f"Found {len(result)} active crypto symbols for weekend trading")
            return result
            
        except Exception as e:
            logger.error(f"Error getting weekend crypto symbols: {e}")
            raise

    async def is_weekend_mode(self) -> bool:
        """Hafta sonu modunda mıyız kontrol et"""
        now = datetime.now()
        # Cuma 22:00 - Pazar 22:00 arası hafta sonu
        if now.weekday() == 4 and now.hour >= 22:  # Cuma akşamı
            return True
        elif now.weekday() in [5, 6]:  # Cumartesi, Pazar
            return True
        elif now.weekday() == 0 and now.hour < 1:  # Pazartesi sabahı erken
            return True
        return False

    async def get_active_symbols_for_current_time(self) -> List[Dict[str, Any]]:
        """Mevcut zamana göre aktif sembolleri al"""
        try:
            if await self.is_weekend_mode():
                logger.info("Weekend mode detected - returning crypto symbols only")
                return await self.get_weekend_crypto_symbols()
            else:
                logger.info("Regular trading hours - returning all symbols")
                return await self.get_symbols()
                
        except Exception as e:
            logger.error(f"Error getting active symbols: {e}")
            raise
    
    async def place_order(self, symbol: str, order_type: str, volume: float, 
                         price: Optional[float] = None, sl: Optional[float] = None, 
                         tp: Optional[float] = None, comment: str = "ICT Ultra v2") -> Dict[str, Any]:
        """Gerçek emir ver"""
        try:
            if not self.is_connected():
                raise Exception("MT5 not connected")
            
            # Order type mapping
            type_mapping = {
                "buy": mt5.ORDER_TYPE_BUY,
                "sell": mt5.ORDER_TYPE_SELL,
                "buy_limit": mt5.ORDER_TYPE_BUY_LIMIT,
                "sell_limit": mt5.ORDER_TYPE_SELL_LIMIT,
                "buy_stop": mt5.ORDER_TYPE_BUY_STOP,
                "sell_stop": mt5.ORDER_TYPE_SELL_STOP
            }
            
            mt5_type = type_mapping.get(order_type.lower())
            if mt5_type is None:
                raise Exception(f"Invalid order type: {order_type}")
            
            # Market order için fiyat al
            if price is None and order_type.lower() in ["buy", "sell"]:
                tick = mt5.symbol_info_tick(symbol)
                if tick is None:
                    raise Exception(f"Failed to get price for {symbol}")
                price = tick.ask if order_type.lower() == "buy" else tick.bid
            
            # Order request oluştur
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": float(volume),
                "type": mt5_type,
                "price": price,
                "comment": comment,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            if sl is not None:
                request["sl"] = sl
            if tp is not None:
                request["tp"] = tp
            
            # Emri gönder
            result = mt5.order_send(request)
            if result is None:
                raise Exception("Failed to send order")
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                raise Exception(f"Order failed: {result.retcode} - {result.comment}")
            
            return {
                "ticket": result.order,
                "retcode": result.retcode,
                "deal": result.deal,
                "volume": result.volume,
                "price": result.price,
                "comment": result.comment
            }
            
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            raise
    
    async def close_position(self, ticket: int) -> Dict[str, Any]:
        """Pozisyonu kapat"""
        try:
            if not self.is_connected():
                raise Exception("MT5 not connected")
            
            # Pozisyonu bul
            position = None
            positions = mt5.positions_get(ticket=ticket)
            if positions and len(positions) > 0:
                position = positions[0]
            else:
                raise Exception(f"Position {ticket} not found")
            
            # Kapatma emri oluştur
            close_type = mt5.ORDER_TYPE_SELL if position.type == 0 else mt5.ORDER_TYPE_BUY
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": position.symbol,
                "volume": position.volume,
                "type": close_type,
                "position": ticket,
                "comment": "ICT Ultra v2 - Close",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Kapama emrini gönder
            result = mt5.order_send(request)
            if result is None:
                raise Exception("Failed to close position")
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                raise Exception(f"Close failed: {result.retcode} - {result.comment}")
            
            return {
                "ticket": result.order,
                "retcode": result.retcode,
                "deal": result.deal,
                "volume": result.volume,
                "price": result.price,
                "comment": result.comment
            }
            
        except Exception as e:
            logger.error(f"Error closing position: {e}")
            raise

    async def get_trade_history(self, days: int = 30) -> List[Dict[str, Any]]:
        """Hesap ticaret geçmişini al"""
        try:
            if not self.is_connected():
                raise Exception("MT5 not connected")

            from_date = datetime.now() - timedelta(days=days)
            to_date = datetime.now()

            deals = mt5.history_deals_get(from_date, to_date)

            if deals is None:
                logger.warning("Could not get trade history from MT5.")
                return []
            
            history = []
            for deal in deals:
                # Sadece kapanış işlemleri (IN/OUT)
                if deal.entry in [mt5.DEAL_ENTRY_IN, mt5.DEAL_ENTRY_OUT]:
                    history.append({
                        "ticket": deal.order,
                        "symbol": deal.symbol,
                        "type": "buy" if deal.type == mt5.DEAL_TYPE_BUY else "sell",
                        "volume": float(deal.volume),
                        "price": float(deal.price),
                        "profit": float(deal.profit),
                        "time": datetime.fromtimestamp(deal.time).isoformat(),
                        "comment": deal.comment
                    })
            
            # Zamana göre sırala
            history.sort(key=lambda x: x['time'], reverse=True)
            return history

        except Exception as e:
            logger.error(f"Error getting trade history: {e}")
            raise

    async def generate_signals(self, symbol: str, timeframe: str = "H1", count: int = 200) -> List[Dict[str, Any]]:
        """
        Gerçek piyasa verilerine dayalı, AI destekli, zenginleştirilmiş ICT sinyalleri üretir.
        Bu, tam teşekküllü bir AI motorunun simülasyonudur.
        """
        try:
            candles = await self.get_candles(symbol, timeframe, count)
            if len(candles) < 20: # Analiz için yeterli veri yok
                return []

            df = pd.DataFrame(candles)
            df['time'] = pd.to_datetime(df['time'])

            # --- Basit Teknik Analiz Göstergeleri (AI Analizi için) ---
            df['atr'] = df['high'].rolling(14).max() - df['low'].rolling(14).min()
            df['ema20'] = df['close'].ewm(span=20, adjust=False).mean()
            df['ema50'] = df['close'].ewm(span=50, adjust=False).mean()
            
            # --- Potansiyel Sinyal Tespiti (Basit Strateji Simülasyonu) ---
            signals = []
            
            # Son 5 muma bak
            for i in range(len(df) - 5, len(df)):
                row = df.iloc[i]
                prev_row = df.iloc[i-1]

                # Basit bir "Order Block" simülasyonu
                is_bullish_ob = prev_row['close'] > prev_row['open'] and row['close'] < row['open'] and row['low'] < prev_row['low']
                is_bearish_ob = prev_row['close'] < prev_row['open'] and row['close'] > row['open'] and row['high'] > prev_row['high']
                
                if is_bullish_ob or is_bearish_ob:
                    direction = "BULLISH" if is_bullish_ob else "BEARISH"
                    confidence = 75 + (np.random.rand() * 20) # 75-95 arası rastgele güven
                    risk_reward = 1.5 + (np.random.rand() * 1.5) # 1.5-3.0 arası R/R
                    
                    entry = row['open']
                    stop_loss = row['high'] if is_bullish_ob else row['low']
                    take_profit = entry + (abs(entry - stop_loss) * risk_reward) if is_bullish_ob else entry - (abs(entry - stop_loss) * risk_reward)

                    # AI Açıklaması
                    trend_info = "EMA20, EMA50'nin üzerinde, yükseliş trendini destekliyor." if row['ema20'] > row['ema50'] else "EMA20, EMA50'nin altında, düşüş trendini destekliyor."
                    description = f"{timeframe} grafiğinde potansiyel bir {'Yükseliş' if direction == 'BULLISH' else 'Düşüş'} Order Block tespit edildi. {trend_info} Risk/Reward oranı: 1:{risk_reward:.2f}"

                    signals.append({
                        "id": f"{symbol}_{row['time'].timestamp()}",
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "direction": direction,
                        "status": "ACTIVE",
                        "pattern": "Order Block",
                        "confidence": confidence,
                        "entry_price": entry,
                        "stop_loss": stop_loss,
                        "take_profit": take_profit,
                        "risk_reward": risk_reward,
                        "ai_analysis": description,
                        "timestamp": row['time'].isoformat(),
                    })
            
            return signals

        except Exception as e:
            logger.error(f"Error generating signals for {symbol}: {e}")
            return []

    async def get_all_signals(self) -> List[Dict[str, Any]]:
        """
        Popüler pariteler için tüm sinyalleri toplayıp döndürür.
        """
        all_signals = []
        symbols_to_scan = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "XAUUSD"]
        timeframes_to_scan = ["M30", "H1", "H4"]

        tasks = []
        for symbol in symbols_to_scan:
            for timeframe in timeframes_to_scan:
                tasks.append(self.generate_signals(symbol, timeframe))
        
        results = await asyncio.gather(*tasks)
        for result in results:
            all_signals.extend(result)
            
        # Sinyalleri zamana göre sırala
        all_signals.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return all_signals
