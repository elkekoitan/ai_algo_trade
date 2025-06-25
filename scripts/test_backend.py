"""
Test script for ICT Ultra v2 backend functionality.
"""

import asyncio
import aiohttp
import json
from datetime import datetime


async def test_api():
    """Test various API endpoints."""
    base_url = "http://localhost:8001"
    
    async with aiohttp.ClientSession() as session:
        print("=" * 50)
        print("ICT Ultra v2 - Backend API Test")
        print("=" * 50)
        
        # Test 1: Health check
        print("\n1. Testing health endpoint...")
        try:
            async with session.get(f"{base_url}/health") as resp:
                data = await resp.json()
                print(f"✓ Health Status: {data['status']}")
                print(f"  MT5 Connected: {data['mt5_connected']}")
                print(f"  Version: {data['version']}")
        except Exception as e:
            print(f"✗ Health check failed: {e}")
        
        # Test 2: Account info
        print("\n2. Testing account info...")
        try:
            async with session.get(f"{base_url}/api/v1/trading/account_info") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✓ Account Info Retrieved:")
                    print(f"  Login: {data['login']}")
                    print(f"  Balance: ${data['balance']:,.2f}")
                    print(f"  Equity: ${data['equity']:,.2f}")
                    print(f"  Server: {data['server']}")
                else:
                    print(f"✗ Failed to get account info: {resp.status}")
        except Exception as e:
            print(f"✗ Account info failed: {e}")
        
        # Test 3: Get symbols
        print("\n3. Testing market symbols...")
        try:
            async with session.get(f"{base_url}/api/v1/market/symbols") as resp:
                if resp.status == 200:
                    symbols = await resp.json()
                    print(f"✓ Found {len(symbols)} symbols")
                    print(f"  First 5: {symbols[:5]}")
                else:
                    print(f"✗ Failed to get symbols: {resp.status}")
        except Exception as e:
            print(f"✗ Symbols fetch failed: {e}")
        
        # Test 4: Get ICT signals
        print("\n4. Testing ICT signals...")
        try:
            async with session.get(f"{base_url}/api/v1/signals/ict?min_score=70") as resp:
                if resp.status == 200:
                    signals = await resp.json()
                    print(f"✓ Found {len(signals)} ICT signals")
                    if signals:
                        signal = signals[0]
                        print(f"  Top Signal: {signal['symbol']} {signal['signal_type']}")
                        print(f"  Pattern: {signal['pattern_type']}")
                        print(f"  Score: {signal['score']}")
                else:
                    print(f"✗ Failed to get signals: {resp.status}")
        except Exception as e:
            print(f"✗ Signals fetch failed: {e}")
        
        # Test 5: Get candlestick data
        print("\n5. Testing candlestick data...")
        try:
            async with session.get(f"{base_url}/api/v1/market/candles/EURUSD?timeframe=H1&count=10") as resp:
                if resp.status == 200:
                    candles = await resp.json()
                    print(f"✓ Retrieved {len(candles)} candles")
                    if candles:
                        latest = candles[-1]
                        print(f"  Latest: {latest['time']}")
                        print(f"  OHLC: {latest['open']:.5f} / {latest['high']:.5f} / {latest['low']:.5f} / {latest['close']:.5f}")
                else:
                    print(f"✗ Failed to get candles: {resp.status}")
        except Exception as e:
            print(f"✗ Candles fetch failed: {e}")
        
        print("\n" + "=" * 50)
        print("Test completed!")
        print("=" * 50)


if __name__ == "__main__":
    asyncio.run(test_api()) 