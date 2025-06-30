"""
Arka Plan Trade Test Scripti
Sadece MT5 bağlantısı kurar ve temel işlemleri test eder.
Frontend veya karmaşık API bağımlılıkları yoktur.
"""
import asyncio
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime

# --- Ayarlar ---
LOGIN = 25201110
PASSWORD = "e|([rXU1IsiM"
SERVER = "Tickmill-Demo"
SYMBOL = "EURUSD"
VOLUME = 0.01

def print_header(title):
    print("\n" + "="*60)
    print(f" {title.upper()} ".center(60, "="))
    print("="*60)

def print_status(message, success=True):
    icon = "✅" if success else "❌"
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {icon} {message}")

async def run_background_trade_test():
    """Ana test fonksiyonu"""
    print_header("Arka Plan MT5 Trade Testi Başlatılıyor")

    # 1. MT5'i Başlat ve Bağlan
    print_status("MT5 terminaline bağlanılıyor...")
    if not mt5.initialize(login=LOGIN, password=PASSWORD, server=SERVER):
        print_status(f"initialize() başarısız, hata kodu = {mt5.last_error()}", success=False)
        mt5.shutdown()
        return
    print_status("MT5 bağlantısı başarılı.")

    # 2. Hesap Bilgilerini Al
    print_header("Hesap Bilgileri Alınıyor")
    account_info = mt5.account_info()
    if account_info is not None:
        print_status("Hesap bilgileri başarıyla alındı.")
        for key, value in account_info._asdict().items():
            print(f"  - {key}: {value}")
    else:
        print_status(f"account_info() başarısız, hata kodu = {mt5.last_error()}", success=False)
        mt5.shutdown()
        return

    # 3. Sembol Bilgisini Al ve Aktif Et
    print_header(f"{SYMBOL} Sembolü Hazırlanıyor")
    
    symbol_info = mt5.symbol_info(SYMBOL)
    if symbol_info is None:
        print_status(f"{SYMBOL} bulunamadı, muhtemelen sembol listesinde değil.", success=False)
        mt5.shutdown()
        return

    if not symbol_info.visible:
        print_status(f"{SYMBOL} Market Watch'da görünmüyor, görünür yapılıyor...")
        if not mt5.symbol_select(SYMBOL, True):
            print_status(f"{SYMBOL} görünür yapılamadı.", success=False)
            mt5.shutdown()
            return
    print_status(f"{SYMBOL} işlem için hazır.")

    # 4. Basit Bir Alım Emri Gönder
    print_header("Test Alım Emri Gönderiliyor")
    
    point = mt5.symbol_info(SYMBOL).point
    price = mt5.symbol_info_tick(SYMBOL).ask
    
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": VOLUME,
        "type": mt5.ORDER_TYPE_BUY,
        "price": price,
        "sl": price - 100 * point,
        "tp": price + 100 * point,
        "deviation": 10,
        "magic": 234000,
        "comment": "background_test",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    print_status(f"{VOLUME} lot {SYMBOL} için alım emri gönderiliyor...")
    result = mt5.order_send(request)

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print_status(f"order_send başarısız, retcode={result.retcode}", success=False)
        print(f"  - Yorum: {result.comment}")
    else:
        print_status("Emir başarıyla gönderildi.")
        print(f"  - Bilet: {result.order}")
        print(f"  - Fiyat: {result.price}")
        
        # 5. Açık Pozisyonu Kapat
        await asyncio.sleep(5) # Pozisyonun işlenmesi için kısa bir bekleme
        print_header("Test Pozisyonu Kapatılıyor")
        
        positions = mt5.positions_get(symbol=SYMBOL)
        if not positions:
            print_status("Kapatılacak açık pozisyon bulunamadı.", success=False)
        else:
            position = positions[0]
            close_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": SYMBOL,
                "volume": VOLUME,
                "type": mt5.ORDER_TYPE_SELL,
                "position": position.ticket,
                "price": mt5.symbol_info_tick(SYMBOL).bid,
                "deviation": 10,
                "magic": 234000,
                "comment": "background_test_close",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            close_result = mt5.order_send(close_request)
            if close_result.retcode != mt5.TRADE_RETCODE_DONE:
                print_status(f"Pozisyon kapatılamadı, retcode={close_result.retcode}", success=False)
                print(f"  - Yorum: {close_result.comment}")
            else:
                print_status("Test pozisyonu başarıyla kapatıldı.")

    # 6. Bağlantıyı Kapat
    print_header("Test Tamamlandı")
    mt5.shutdown()
    print_status("MT5 bağlantısı kapatıldı.")


if __name__ == "__main__":
    asyncio.run(run_background_trade_test()) 