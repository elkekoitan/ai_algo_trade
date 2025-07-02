#!/usr/bin/env python3
"""
Tickmill MT5 Login Test
Test demo hesabı ile MT5 bağlantısını kontrol eder.
"""

import MetaTrader5 as mt5
import time
from datetime import datetime

def test_tickmill_login():
    """Tickmill demo hesabı ile MT5 bağlantısını test eder."""
    
    print("🚀 AI Algo Trade - Tickmill MT5 Login Test")
    print("=" * 50)
    
    # MT5 başlat
    if not mt5.initialize():
        print("❌ MT5 initialize() failed")
        print(f"Error code: {mt5.last_error()}")
        return False
    
    print("✅ MT5 terminal başarıyla başlatıldı")
    
    # Tickmill demo hesap bilgileri
    login = 25201110
    password = "e|([rXU1IsiM"
    server = "Tickmill-Demo"
    
    print(f"\n🔐 Giriş bilgileri:")
    print(f"Login: {login}")
    print(f"Server: {server}")
    print(f"Password: {'*' * len(password)}")
    
    # Login dene
    authorized = mt5.login(login, password=password, server=server)
    
    if authorized:
        print("\n✅ Tickmill MT5 hesabına başarıyla giriş yapıldı!")
        
        # Hesap bilgilerini al
        account_info = mt5.account_info()
        if account_info:
            print(f"\n📊 Hesap Bilgileri:")
            print(f"Login: {account_info.login}")
            print(f"Trade Server: {account_info.server}")
            print(f"Name: {account_info.name}")
            print(f"Company: {account_info.company}")
            print(f"Currency: {account_info.currency}")
            print(f"Balance: {account_info.balance}")
            print(f"Equity: {account_info.equity}")
            print(f"Margin: {account_info.margin}")
            print(f"Free Margin: {account_info.margin_free}")
            print(f"Leverage: 1:{account_info.leverage}")
            
        # Terminal bilgilerini al
        terminal_info = mt5.terminal_info()
        if terminal_info:
            print(f"\n🖥️ Terminal Bilgileri:")
            print(f"Company: {terminal_info.company}")
            print(f"Name: {terminal_info.name}")
            print(f"Path: {terminal_info.path}")
            print(f"Version: {terminal_info.build}")
            print(f"Trade Allowed: {terminal_info.trade_allowed}")
            print(f"Connected: {terminal_info.connected}")
            
        # Sembol listesini al
        symbols = mt5.symbols_get()
        if symbols:
            print(f"\n📈 Mevcut Sembol Sayısı: {len(symbols)}")
            print("İlk 10 sembol:")
            for i, symbol in enumerate(symbols[:10]):
                print(f"  {i+1}. {symbol.name} - {symbol.description}")
        
        # Market verilerini test et
        print(f"\n💹 Market Verileri Test:")
        test_symbols = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD"]
        
        for symbol in test_symbols:
            tick = mt5.symbol_info_tick(symbol)
            if tick:
                print(f"  {symbol}: Bid={tick.bid}, Ask={tick.ask}, Spread={tick.ask-tick.bid:.5f}")
            else:
                print(f"  {symbol}: Veri alınamadı")
        
        print(f"\n🎯 Test Başarılı! Sistem tamamen hazır.")
        print(f"🕒 Test Zamanı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        mt5.shutdown()
        return True
        
    else:
        print(f"\n❌ MT5 hesabına giriş yapılamadı!")
        print(f"Error code: {mt5.last_error()}")
        mt5.shutdown()
        return False

if __name__ == "__main__":
    success = test_tickmill_login()
    if success:
        print("\n🎉 Tebrikler! Tickmill MT5 hesabınız aktif ve sistem hazır!")
        print("🚀 Artık AI Algo Trade platformunu kullanabilirsiniz.")
    else:
        print("\n⚠️ Bağlantı sorunu var. Lütfen:")
        print("1. MT5 terminal'in açık olduğundan emin olun")
        print("2. İnternet bağlantınızı kontrol edin")
        print("3. Hesap bilgilerini doğrulayın") 