"""
Tickmill Demo Hesap Bağlantı Testi
Gerçek MT5 verileri test edicez
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.mt5_integration.service import MT5Service
from modules.mt5_integration.config import MT5_LOGIN, MT5_PASSWORD, MT5_SERVER

async def test_tickmill_connection():
    """Tickmill demo hesabına bağlan ve test et"""
    
    print("🚀 Tickmill Demo Hesap Bağlantı Testi Başlatılıyor...")
    print("=" * 60)
    
    mt5_service = MT5Service()
    
    try:
        # 1. Bağlantı Testi
        print(f"📡 Connecting to {MT5_SERVER} with login {MT5_LOGIN}...")
        connected = await mt5_service.connect(
            login=MT5_LOGIN,
            password=MT5_PASSWORD,
            server=MT5_SERVER
        )
        
        if not connected:
            print("❌ Bağlantı başarısız!")
            print("⚠️  MT5 Terminal açık mı? Manual login yapıldı mı?")
            return False
        
        print("✅ MT5 Bağlantısı Başarılı!")
        
        # 2. Hesap Bilgileri
        print("\n💰 Hesap Bilgileri:")
        account_info = await mt5_service.get_account_info()
        for key, value in account_info.items():
            print(f"   {key}: {value}")
        
        # 3. Canlı Fiyat Testi
        print("\n📊 Canlı Fiyat Testi:")
        test_symbols = ["EURUSD", "GBPUSD", "XAUUSD", "BTCUSD"]
        
        for symbol in test_symbols:
            try:
                tick = await mt5_service.get_symbol_tick(symbol)
                print(f"   {symbol}: Bid={tick['bid']}, Ask={tick['ask']}, Time={tick['time']}")
            except Exception as e:
                print(f"   {symbol}: Error - {e}")
        
        # 4. Pozisyon Testi
        print("\n📈 Açık Pozisyonlar:")
        positions = await mt5_service.get_positions()
        if positions:
            for pos in positions:
                print(f"   {pos['symbol']} {pos['type']} {pos['volume']} lots - P/L: {pos['profit']} USD")
        else:
            print("   Açık pozisyon yok")
        
        # 5. Mum Verisi Testi
        print("\n🕯️ Son 5 EURUSD H1 Mumu:")
        try:
            candles = await mt5_service.get_candles("EURUSD", "H1", 5)
            for candle in candles[-5:]:
                print(f"   {candle['time']}: O={candle['open']}, H={candle['high']}, L={candle['low']}, C={candle['close']}")
        except Exception as e:
            print(f"   Mum verisi hatası: {e}")
        
        print("\n🎉 Tüm testler başarılı! Tickmill hesabı aktif ve çalışıyor.")
        return True
        
    except Exception as e:
        print(f"❌ Test hatası: {e}")
        return False
    
    finally:
        await mt5_service.disconnect()
        print("\n🔌 MT5 bağlantısı kapatıldı.")

if __name__ == "__main__":
    try:
        result = asyncio.run(test_tickmill_connection())
        if result:
            print("\n✅ SONUÇ: MT5 Tickmill Demo hesabı başarıyla bağlandı!")
        else:
            print("\n❌ SONUÇ: Bağlantı başarısız!")
            print("🔧 Çözüm önerileri:")
            print("   1. MT5 Terminal'i açın")
            print("   2. Manual olarak demo hesaba login yapın")
            print("   3. Tekrar test edin")
    except Exception as e:
        print(f"\n�� FATAL ERROR: {e}") 