import MetaTrader5 as mt5
import time
import os
from datetime import datetime
import logging
import pandas as pd

# --- Ayarlar ---
LOGIN = 25201110
PASSWORD = "e|([rXU1IsiM"
SERVER = "Tickmill-Demo"
SYMBOLS = ["BTCUSD", "ETHUSD"]
VOLUME = 0.01
TIMEFRAME = mt5.TIMEFRAME_M1
TRADE_COOLDOWN_SECONDS = 10 # Her işlem arası bekleme süresi

# --- Loglama Kurulumu ---
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

# --- MT5 Bağlantı Fonksiyonu ---
def connect_to_mt5():
    """MT5'e bağlanır ve oturum açar."""
    logger.info("MT5 terminaline bağlanılıyor...")
    if not mt5.initialize():
        logger.error("initialize() failed, error code = %d", mt5.last_error())
        return False
    
    authorized = mt5.login(LOGIN, PASSWORD, SERVER)
    if not authorized:
        logger.error("failed to connect at account #%d, error code: %d", LOGIN, mt5.last_error())
        return False
        
    logger.info("✅ MT5'e başarıyla bağlandı. Hesap: %d", LOGIN)
    return True

# --- Strateji ve İşlem Fonksiyonları ---
def get_historical_data(symbol, count=10):
    """Belirtilen sembol için geçmiş verileri alır."""
    try:
        rates = mt5.copy_rates_from_pos(symbol, TIMEFRAME, 0, count)
        if rates is None:
            logger.warning(f"{symbol} için veri alınamadı.")
            return None
        return pd.DataFrame(rates)
    except Exception as e:
        logger.error(f"Geçmiş veri alınırken hata: {e}")
        return None

def simple_momentum_strategy(symbol):
    """Basit bir momentum stratejisi. Fiyat artıyorsa al, düşüyorsa sat."""
    df = get_historical_data(symbol)
    if df is None or len(df) < 2:
        return "HOLD"
    
    last_close = df.iloc[-1]['close']
    prev_close = df.iloc[-2]['close']
    
    if last_close > prev_close:
        return "BUY"
    elif last_close < prev_close:
        return "SELL"
    return "HOLD"

def execute_trade(symbol, action):
    """Belirtilen eylemi gerçekleştirir."""
    tick = mt5.symbol_info_tick(symbol)
    if not tick:
        logger.warning(f"{symbol} için anlık fiyat alınamadı.")
        return

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": VOLUME,
        "type": mt5.ORDER_TYPE_BUY if action == "BUY" else mt5.ORDER_TYPE_SELL,
        "price": tick.ask if action == "BUY" else tick.bid,
        "deviation": 20,
        "magic": 234000,
        "comment": "Advanced Trader",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        logger.error(f"❌ {symbol} {action} emri başarısız: {result.comment}")
    else:
        logger.info(f"✅ {symbol} {action} emri başarıyla verildi. Ticket: {result.order}")

def close_all_positions():
    """Tüm açık pozisyonları kapatır."""
    positions = mt5.positions_get()
    if positions is None:
        logger.warning("Açık pozisyon bulunamadı veya alınamadı.")
        return

    for position in positions:
        symbol = position.symbol
        ticket = position.ticket
        volume = position.volume
        order_type = mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(symbol).bid if position.type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(symbol).ask

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": order_type,
            "position": ticket,
            "price": price,
            "deviation": 20,
            "magic": 234000,
            "comment": "Closing all positions",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        mt5.order_send(request)
    logger.info("Tüm açık pozisyonlar kapatıldı.")

# --- Ana Döngü ---
def trading_loop():
    """Ana işlem döngüsü."""
    trade_cycle = 0
    try:
        while True:
            trade_cycle += 1
            logger.info(f"\n--- 🔄 İşlem Döngüsü #{trade_cycle} ---")
            
            # Bağlantıyı kontrol et
            if not mt5.terminal_info():
                logger.warning("MT5 bağlantısı koptu. Yeniden bağlanılıyor...")
                if not connect_to_mt5():
                    time.sleep(60)
                    continue

            # Her sembol için stratejiyi çalıştır
            for symbol in SYMBOLS:
                signal = simple_momentum_strategy(symbol)
                
                if signal != "HOLD":
                    logger.info(f" सिग्नल Tespit Edildi: {symbol} için {signal}")
                    execute_trade(symbol, signal)
                    # Her işlemden sonra kısa bir bekleme
                    time.sleep(TRADE_COOLDOWN_SECONDS) 
            
            # Genel bekleme
            time.sleep(5)

    except KeyboardInterrupt:
        logger.info("\n🛑 Trader durduruldu. Pozisyonlar kapatılıyor...")
        close_all_positions()
        mt5.shutdown()
        logger.info("👋 MT5 bağlantısı kapatıldı. İyi günler!")

if __name__ == "__main__":
    if connect_to_mt5():
        trading_loop()
    else:
        logger.critical("Sistem başlatılamadı. Lütfen MT5 bağlantınızı kontrol edin.") 