"""
Basit MT5 Import ve Initialize Test
"""

import asyncio
import logging
from modules.mt5_integration.service import MT5Service

# Uygulamanın kendi logger'ı yerine standart logger kullanıyoruz
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def main():
    """Sadece MT5 bağlantısını test eden fonksiyon."""
    logging.info("--- STANDALONE MT5 Connection Check ---")
    
    # Memory'deki demo hesap bilgileri
    login = 25201110
    password = "e|([rXU1IsiM"
    server = "Tickmill-Demo"
    
    # MT5 servisini başlat
    mt5 = MT5Service(login=login, password=password, server=server)
    
    logging.info(f"Attempting to connect to {server} with login {login}...")
    
    try:
        # Bağlantı kurmayı dene
        connected = await mt5.connect()
        
        if connected:
            logging.info("✅✅✅ STANDALONE CONNECTION SUCCESSFUL ✅✅✅")
            
            # Hesap bilgilerini al ve yazdır
            account_info = await mt5.get_account_info()
            logging.info(f"Account Info: {account_info}")
            
            # Bağlantıyı kapat
            await mt5.disconnect()
            logging.info("Disconnected successfully.")
        else:
            logging.error("❌❌❌ STANDALONE CONNECTION FAILED ❌❌❌")
            
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main()) 