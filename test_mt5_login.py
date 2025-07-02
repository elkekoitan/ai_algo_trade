#!/usr/bin/env python3
"""
Test MT5 Login with Tickmill Demo Account
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8001"
MT5_CREDENTIALS = {
    "mt5_login": "25201110",
    "mt5_password": "e|([rXU1IsiM",
    "mt5_server": "Tickmill-Demo"
}

async def test_health():
    """Test if backend is running"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/health") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print("✅ Backend is running")
                    print(f"   Status: {data.get('status')}")
                    print(f"   MT5 Connected: {data.get('mt5_connected')}")
                    print(f"   Version: {data.get('version')}")
                    return True
                else:
                    print(f"❌ Backend health check failed: {resp.status}")
                    return False
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        print("   Make sure backend is running on http://localhost:8001")
        return False

async def test_mt5_login():
    """Test MT5 login with Tickmill demo account"""
    print("\n🔐 Testing MT5 Login...")
    print(f"   Login: {MT5_CREDENTIALS['mt5_login']}")
    print(f"   Server: {MT5_CREDENTIALS['mt5_server']}")
    print(f"   Password: {'*' * 10}")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Login with MT5
            async with session.post(
                f"{BASE_URL}/api/v1/auth/login/mt5",
                json=MT5_CREDENTIALS
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print("\n✅ MT5 Login Successful!")
                    print(f"   Access Token: {data.get('access_token')[:20]}...")
                    print(f"   User ID: {data['user']['id']}")
                    print(f"   Role: {data['user']['role']}")
                    return data.get('access_token')
                else:
                    error = await resp.text()
                    print(f"❌ MT5 login failed: {resp.status}")
                    print(f"   Error: {error}")
                    return None
    except Exception as e:
        print(f"❌ MT5 login error: {e}")
        return None

async def test_account_info(token):
    """Test getting MT5 account info"""
    print("\n💰 Getting Account Info...")
    
    try:
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {token}"}
            
            # Get account info
            async with session.get(
                f"{BASE_URL}/api/v1/trading/account_info",
                headers=headers
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print("✅ Account Info Retrieved:")
                    print(f"   Balance: ${data.get('balance', 0):,.2f}")
                    print(f"   Equity: ${data.get('equity', 0):,.2f}")
                    print(f"   Currency: {data.get('currency')}")
                    print(f"   Leverage: 1:{data.get('leverage', 0)}")
                    return True
                else:
                    print(f"❌ Failed to get account info: {resp.status}")
                    return False
    except Exception as e:
        print(f"❌ Account info error: {e}")
        return False

async def test_market_data(token):
    """Test getting market data"""
    print("\n📊 Getting Market Data...")
    
    try:
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {token}"}
            
            # Get symbols
            async with session.get(
                f"{BASE_URL}/api/v1/market/symbols",
                headers=headers
            ) as resp:
                if resp.status == 200:
                    symbols = await resp.json()
                    print(f"✅ Found {len(symbols)} trading symbols")
                    print(f"   Popular: {symbols[:5]}")
                    
                    # Get price for EURUSD
                    async with session.get(
                        f"{BASE_URL}/api/v1/market/price/EURUSD",
                        headers=headers
                    ) as price_resp:
                        if price_resp.status == 200:
                            price_data = await price_resp.json()
                            print(f"\n💱 EURUSD Price:")
                            print(f"   Bid: {price_data.get('bid')}")
                            print(f"   Ask: {price_data.get('ask')}")
                            print(f"   Spread: {price_data.get('spread')} pips")
                    
                    return True
                else:
                    print(f"❌ Failed to get symbols: {resp.status}")
                    return False
    except Exception as e:
        print(f"❌ Market data error: {e}")
        return False

async def test_ai_signals(token):
    """Test getting AI signals"""
    print("\n🤖 Getting AI Signals...")
    
    try:
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {token}"}
            
            # Get ICT signals
            async with session.get(
                f"{BASE_URL}/api/v1/signals/ict",
                headers=headers
            ) as resp:
                if resp.status == 200:
                    signals = await resp.json()
                    print(f"✅ Found {len(signals)} ICT signals")
                    
                    if signals:
                        signal = signals[0]
                        print(f"\n📈 Latest Signal:")
                        print(f"   Symbol: {signal.get('symbol')}")
                        print(f"   Type: {signal.get('signal_type')}")
                        print(f"   Direction: {signal.get('direction')}")
                        print(f"   Confidence: {signal.get('score', 0):.1f}%")
                    
                    return True
                else:
                    print(f"❌ Failed to get signals: {resp.status}")
                    return False
    except Exception as e:
        print(f"❌ AI signals error: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 AI ALGO TRADE - MT5 LOGIN TEST")
    print("=" * 50)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Test backend health
    if not await test_health():
        print("\n⚠️  Please start the backend first:")
        print("   cd backend && python main.py")
        return
    
    # Test MT5 login
    token = await test_mt5_login()
    if not token:
        print("\n⚠️  MT5 login failed. Check credentials.")
        return
    
    # Test authenticated endpoints
    await test_account_info(token)
    await test_market_data(token)
    await test_ai_signals(token)
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")
    print("\n📌 Next Steps:")
    print("1. Open http://localhost:3000 in your browser")
    print("2. Click 'Login with MT5'")
    print("3. Use these credentials:")
    print(f"   - Login: {MT5_CREDENTIALS['mt5_login']}")
    print(f"   - Password: {MT5_CREDENTIALS['mt5_password']}")
    print(f"   - Server: {MT5_CREDENTIALS['mt5_server']}")
    print("\n🎯 Happy Trading!")

if __name__ == "__main__":
    asyncio.run(main()) 