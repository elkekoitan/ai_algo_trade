#!/usr/bin/env python3
"""
ICT Ultra Platform - Advanced MT5 Playwright Automation
Using modern async/await patterns and best practices from Playwright documentation
"""

import asyncio
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
import requests
import MetaTrader5 as mt5

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mt5_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ICTUltraMT5Automation:
    def __init__(self, api_url: str = "http://localhost:8080"):
        self.api_url = api_url
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.is_connected = False
        self.mt5_connected = False
        
    async def initialize_browser(self) -> None:
        """Initialize Playwright browser with modern async patterns"""
        async with async_playwright() as p:
            # Launch browser with optimized settings
            self.browser = await p.chromium.launch(
                headless=False,  # Visible for MT5 interaction
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-extensions',
                    '--disable-plugins',
                    '--disable-images'  # Faster loading
                ]
            )
            
            # Create browser context with proper settings
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            
            # Create new page
            self.page = await self.context.new_page()
            
            # Set up page event listeners
            self.page.on("console", lambda msg: logger.info(f"Browser Console: {msg.text}"))
            self.page.on("pageerror", lambda error: logger.error(f"Page Error: {error}"))
            
            logger.info("✅ Browser initialized successfully")
            
    async def connect_to_mt5_terminal(self) -> bool:
        """Connect to MT5 terminal using both direct API and browser automation"""
        try:
            # First try direct MT5 connection
            if not mt5.initialize():
                logger.warning("Direct MT5 connection failed, using browser automation")
                return await self.browser_mt5_connection()
            
            # Get account info
            account_info = mt5.account_info()
            if account_info is None:
                logger.error("Failed to get MT5 account info")
                return False
                
            logger.info(f"✅ Connected to MT5 Account: {account_info.login}")
            logger.info(f"🏦 Server: {account_info.server}")
            logger.info(f"💰 Balance: ${account_info.balance:,.2f}")
            
            self.mt5_connected = True
            return True
            
        except Exception as e:
            logger.error(f"MT5 connection error: {e}")
            return await self.browser_mt5_connection()
    
    async def execute_real_trade(self, symbol: str, trade_type: str, volume: float) -> Dict[str, Any]:
        """Execute real trade on MT5"""
        if not self.mt5_connected:
            logger.error("MT5 not connected for trade execution")
            return {'success': False, 'error': 'MT5 not connected'}
        
        try:
            # Get current price
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                return {'success': False, 'error': 'Could not get current price'}
            
            price = tick.ask if trade_type.upper() == 'BUY' else tick.bid
            
            # Create trade request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": mt5.ORDER_TYPE_BUY if trade_type.upper() == 'BUY' else mt5.ORDER_TYPE_SELL,
                "price": price,
                "deviation": 20,
                "magic": 777888,
                "comment": "ICT Ultra Platform",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Send trade request
            result = mt5.order_send(request)
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logger.error(f"Trade failed: {result.retcode} - {result.comment}")
                return {
                    'success': False,
                    'error': f'Trade failed: {result.comment}',
                    'retcode': result.retcode
                }
            
            logger.info(f"✅ Trade executed successfully!")
            logger.info(f"Order: {result.order} | Deal: {result.deal}")
            logger.info(f"Symbol: {symbol} | Type: {trade_type} | Volume: {volume}")
            
            return {
                'success': True,
                'order_id': result.order,
                'deal_id': result.deal,
                'symbol': symbol,
                'type': trade_type,
                'volume': volume,
                'price': result.price,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Trade execution error: {e}")
            return {'success': False, 'error': str(e)}

# Main execution
async def main():
    """Main execution function"""
    automation = ICTUltraMT5Automation()
    
    try:
        logger.info("🚀 Starting ICT Ultra MT5 Automation")
        
        # Connect to MT5
        if await automation.connect_to_mt5_terminal():
            logger.info("✅ MT5 connection established")
            
            # Execute sample trade
            result = await automation.execute_real_trade('EURUSD', 'SELL', 0.01)
            if result['success']:
                logger.info(f"✅ Sample trade executed: {result}")
            else:
                logger.error(f"❌ Trade failed: {result}")
        else:
            logger.error("❌ Failed to connect to MT5")
            
    except Exception as e:
        logger.error(f"Fatal error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 