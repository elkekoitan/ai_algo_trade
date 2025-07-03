#!/usr/bin/env python3
"""
Quantum Trading System Launcher
24/7 Automated Trading with Performance Monitoring
"""
import asyncio
import sys
import os
import signal
import logging
from datetime import datetime

# Add backend to path
sys.path.append('backend')

from modules.quantum_trading.quantum_engine import QuantumTradingEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'quantum_trading_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('QuantumLauncher')

# Global engine instance for signal handling
engine = None

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    global engine
    logger.info("🛑 Shutdown signal received...")
    if engine:
        engine.running = False
    sys.exit(0)

async def main():
    """Main launcher function"""
    global engine
    
    print("="*60)
    print("🚀 QUANTUM TRADING SYSTEM v1.0")
    print("="*60)
    print("📊 24/7 Automated Trading Engine")
    print("🧠 AI-Powered Multi-Instrument Scanner")
    print("⚡ High-Frequency Execution")
    print("📈 Real-Time Performance Tracking")
    print("="*60)
    
    # Account configurations
    accounts = [
        {
            "login": 25201110,
            "password": "e|([rXU1IsiM",
            "server": "Tickmill-Demo",
            "name": "Master Account"
        },
        {
            "login": 25216036,
            "password": "oB9UY1&,B=^9",
            "server": "Tickmill-Demo",
            "name": "Copy Account 1"
        },
        {
            "login": 25216037,
            "password": "L[.Sdo4QRxx2",
            "server": "Tickmill-Demo",
            "name": "Copy Account 2"
        }
    ]
    
    # Create quantum engine
    engine = QuantumTradingEngine(accounts, risk_per_trade=0.01)
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Initialize engine
        if not engine.initialize():
            logger.error("❌ Failed to initialize Quantum Trading Engine")
            return
            
        logger.info("✅ Quantum Trading Engine initialized successfully")
        logger.info(f"📊 Trading {len(engine.symbols)} instruments")
        logger.info("🔄 Starting 24/7 trading operation...")
        
        # Run the engine
        await engine.run()
        
    except Exception as e:
        logger.error(f"❌ Critical error: {e}")
        
    finally:
        # Export results
        if engine and engine.start_time:
            engine.export_results()
            logger.info("📄 Trading results exported")
            
        logger.info("🛑 Quantum Trading System stopped")

if __name__ == "__main__":
    print("\n⚠️  WARNING: This will start REAL trading on demo accounts!")
    print("Press Ctrl+C at any time to stop the system.\n")
    
    response = input("Start Quantum Trading System? (yes/no): ")
    if response.lower() == 'yes':
        asyncio.run(main())
    else:
        print("❌ Trading cancelled") 