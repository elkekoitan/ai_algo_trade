"""
Basit Backend Testi
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.logger import setup_logger
from core.unified_trading_engine import UnifiedTradingEngine
from modules.mt5_integration.service import MT5Service

logger = setup_logger(__name__)

async def test_backend():
    """Backend'i test et"""
    
    logger.info("=" * 50)
    logger.info("🚀 BACKEND TESTİ BAŞLIYOR")
    logger.info("=" * 50)
    
    # MT5 servisi oluştur
    mt5_service = MT5Service(
        login=25201110,
        password="e|([rXU1IsiM", 
        server="Tickmill-Demo"
    )
    
    # Bağlan
    logger.info("📡 MT5'e bağlanılıyor...")
    connected = await mt5_service.connect()
    
    if not connected:
        logger.error("❌ MT5 bağlantısı başarısız!")
        return
        
    logger.info("✅ MT5 bağlantısı başarılı!")
    
    # Hesap bilgilerini al
    account_info = await mt5_service.get_account_info()
    logger.info(f"💰 Hesap: {account_info['login']} - Balance: ${account_info['balance']:,.2f}")
    
    # Unified Trading Engine'i oluştur
    logger.info("\n🔧 Unified Trading Engine oluşturuluyor...")
    engine = UnifiedTradingEngine(mt5_service)
    
    # Engine'i başlat
    logger.info("🚀 Engine başlatılıyor...")
    await engine.start()
    
    logger.info("✅ Engine başarıyla başlatıldı!")
    
    # Modül durumlarını kontrol et
    logger.info("\n📊 MODÜL DURUMLARI:")
    logger.info(f"  ATM: {await engine.adaptive_manager.get_status()}")
    logger.info(f"  God Mode: {await engine.god_mode.get_status()}")
    logger.info(f"  Market Narrator: {await engine.market_narrator.get_status()}")
    logger.info(f"  Shadow Mode: {await engine.shadow_mode.get_status()}")
    
    # 10 saniye çalıştır
    logger.info("\n⏰ 10 saniye çalışıyor...")
    await asyncio.sleep(10)
    
    # Engine'i durdur
    logger.info("\n🛑 Engine durduruluyor...")
    await engine.stop()
    
    # MT5 bağlantısını kapat
    await mt5_service.disconnect()
    
    logger.info("\n✅ TEST TAMAMLANDI!")

if __name__ == "__main__":
    asyncio.run(test_backend()) 