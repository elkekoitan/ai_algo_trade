import MetaTrader5 as mt5
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_mt5_connection():
    """Test MT5 connection with detailed error reporting"""
    print("=== MT5 Connection Test ===")
    print(f"MT5 Package Version: {mt5.__version__}")
    print(f"Python Version: {sys.version}")
    print(f"Current Directory: {os.getcwd()}")
    
    # Demo account credentials
    login = 25201110
    password = "e|([rXU1IsiM"
    server = "Tickmill-Demo"
    
    print(f"\nTrying to connect:")
    print(f"Login: {login}")
    print(f"Server: {server}")
    print(f"Password: {'*' * len(password)}")
    
    # Initialize MT5
    if not mt5.initialize():
        print(f"\nERROR: MT5 initialization failed!")
        print(f"Error code: {mt5.last_error()}")
        return False
    
    print("\n✓ MT5 initialized successfully")
    
    # Login to account
    authorized = mt5.login(login, password, server)
    if not authorized:
        print(f"\nERROR: Login failed!")
        print(f"Error code: {mt5.last_error()}")
        mt5.shutdown()
        return False
    
    print("✓ Login successful!")
    
    # Get account info
    account_info = mt5.account_info()
    if account_info is None:
        print("\nERROR: Failed to get account info")
        print(f"Error code: {mt5.last_error()}")
    else:
        print(f"\n✓ Account Info:")
        print(f"  - Name: {account_info.name}")
        print(f"  - Server: {account_info.server}")
        print(f"  - Balance: ${account_info.balance:.2f}")
        print(f"  - Currency: {account_info.currency}")
        print(f"  - Leverage: 1:{account_info.leverage}")
    
    # Check weekend crypto symbols
    print("\n✓ Checking Weekend Crypto Symbols:")
    crypto_symbols = [
        "BTCUSD", "ETHUSD", "LTCUSD", "XRPUSD", "BCHUSD",
        "ADAUSD", "DOGUSD", "DOTUSD", "LNKUSD", "UNIUSD", "XLMUSD"
    ]
    
    active_symbols = []
    for symbol in crypto_symbols:
        tick = mt5.symbol_info_tick(symbol)
        if tick and tick.time > 0:
            active_symbols.append(symbol)
            print(f"  - {symbol}: Active (Bid: {tick.bid}, Ask: {tick.ask})")
    
    print(f"\nTotal active symbols: {len(active_symbols)}")
    
    # Shutdown
    mt5.shutdown()
    print("\n✓ MT5 connection closed")
    return True

if __name__ == "__main__":
    success = test_mt5_connection()
    if not success:
        print("\n❌ MT5 connection test FAILED!")
        sys.exit(1)
    else:
        print("\n✅ MT5 connection test PASSED!")
        sys.exit(0) 