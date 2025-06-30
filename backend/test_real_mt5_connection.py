"""
Gerçek MT5 Bağlantı Testi
Demo hesap bilgileri ile gerçek bağlantı kurulacak
"""

import asyncio
import sys
import os

# Proje kök dizinini Python path'ine ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.mt5_integration.service import MT5Service
from core.logger import setup_logger

logger = setup_logger(__name__)

async def test_real_mt5():
    """Gerçek MT5 bağlantısını test et"""
    
    # Demo hesap bilgileri (memory'den)
    login = 25201110
    password = "e|([rXU1IsiM"
    server = "Tickmill-Demo"
    
    logger.info("=" * 50)
    logger.info("🚀 GERÇEK MT5 BAĞLANTI TESTİ BAŞLIYOR")
    logger.info("=" * 50)
    
    # MT5 servisi oluştur
    mt5 = MT5Service(login=login, password=password, server=server)
    
    try:
        # Bağlan
        logger.info(f"📡 MT5'e bağlanılıyor... Server: {server}")
        connected = await mt5.connect()
        
        if not connected:
            logger.error("❌ MT5 bağlantısı başarısız!")
            return
            
        logger.info("✅ MT5 bağlantısı başarılı!")
        
        # Hesap bilgilerini al
        logger.info("\n📊 HESAP BİLGİLERİ:")
        account_info = await mt5.get_account_info()
        for key, value in account_info.items():
            logger.info(f"  {key}: {value}")
        
        # Açık pozisyonları kontrol et
        logger.info("\n📈 AÇIK POZİSYONLAR:")
        positions = await mt5.get_positions()
        if positions:
            for pos in positions:
                logger.info(f"  Ticket: {pos['ticket']}, Symbol: {pos['symbol']}, Type: {pos['type']}, Volume: {pos['volume']}, Profit: {pos['profit']}")
        else:
            logger.info("  Açık pozisyon yok")
        
        # Popüler sembollerin fiyatlarını al
        logger.info("\n💹 CANLI FİYATLAR:")
        symbols = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "BTCUSD", "ETHUSD"]
        for symbol in symbols:
            try:
                tick = await mt5.get_symbol_tick(symbol)
                logger.info(f"  {symbol}: Bid={tick['bid']}, Ask={tick['ask']}, Spread={(tick['ask']-tick['bid'])*10000:.1f} pips")
            except Exception as e:
                logger.warning(f"  {symbol}: Veri alınamadı - {str(e)}")
        
        # Sinyal üret
        logger.info("\n🎯 EURUSD İÇİN SİNYAL ÜRETİLİYOR:")
        signals = await mt5.generate_signals("EURUSD", "H1", 100)
        if signals:
            for signal in signals[:3]:  # İlk 3 sinyali göster
                logger.info(f"  Pattern: {signal['pattern']}, Direction: {signal['direction']}, Confidence: {signal['confidence']}%")
                logger.info(f"  Entry: {signal['entry_price']}, SL: {signal['stop_loss']}, TP: {signal['take_profit']}")
                logger.info(f"  AI Analysis: {signal['ai_analysis']}")
                logger.info("  " + "-" * 40)
        else:
            logger.info("  Şu anda aktif sinyal yok")
        
        logger.info("\n✅ TÜM TESTLER BAŞARILI!")
        logger.info("🎉 GERÇEK MT5 BAĞLANTISI ÇALIŞIYOR!")
        
    except Exception as e:
        logger.error(f"❌ Test sırasında hata: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Bağlantıyı kapat
        await mt5.disconnect()
        logger.info("\n🔌 MT5 bağlantısı kapatıldı")

if __name__ == "__main__":
    asyncio.run(test_real_mt5()) 