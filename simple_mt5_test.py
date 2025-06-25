"""
Simple MetaTrader 5 connection test script for Crypto Symbols.
"""

import time
import MetaTrader5 as mt5

# MT5 credentials
MT5_LOGIN = 25201110
MT5_PASSWORD = "e|([rXU1IsiM"
MT5_SERVER = "Tickmill-Demo"

def check_symbol(symbol_name):
    """Checks and prints information for a given symbol."""
    print(f"\n--- Checking symbol: {symbol_name} ---")
    symbol_info = mt5.symbol_info(symbol_name)
    if not symbol_info:
        print(f"✗ Symbol {symbol_name} not found.")
        return

    print(f"✓ Symbol found: {symbol_info.description}")
    print(f"  Tradeable: {'Yes' if symbol_info.visible else 'No'}")
    
    if symbol_info.visible:
        tick = mt5.symbol_info_tick(symbol_name)
        if tick:
            print(f"  Ask: {tick.ask}")
            print(f"  Bid: {tick.bid}")
        else:
            print("  Could not retrieve tick data.")
    else:
        # If not visible, try to select it
        print(f"  Attempting to select {symbol_name}...")
        if mt5.symbol_select(symbol_name, True):
             print(f"  ✓ Successfully selected {symbol_name}. Please re-run the test.")
        else:
             print(f"  ✗ Failed to select {symbol_name}.")


def main():
    """Main function to test MT5 connection."""
    print("ICT Ultra v2: Algo Forge Edition - Crypto Symbol Test")
    print("=====================================================")
    
    # Initialize MT5
    if not mt5.initialize():
        print(f"MT5 initialization failed!")
        return
    
    # Connect to account
    if not mt5.login(login=MT5_LOGIN, password=MT5_PASSWORD, server=MT5_SERVER):
        print(f"MT5 login failed: {mt5.last_error()}")
        mt5.shutdown()
        return
    
    print(f"\n✓ Connected successfully to account {MT5_LOGIN}!")
    
    # Check for crypto symbols
    check_symbol("BTCUSD")
    check_symbol("ETHUSD")
    
    # Disconnect
    print("\nDisconnecting from MT5...")
    mt5.shutdown()
    print("✓ Disconnected!")

if __name__ == "__main__":
    main() 