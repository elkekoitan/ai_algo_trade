#!/usr/bin/env python3
"""
AI Algo Trade - Advanced Copy Trading System
Integrated with project architecture and user preferences
"""
import asyncio
import sys
import os
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import MetaTrader5 as mt5

# Add backend to path
sys.path.append('backend')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'copy_trading_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('CopyTrading')

class CopyTradingConfig:
    """Configuration for copy trading system"""
    
    # Master account (signal provider)
    MASTER_ACCOUNT = {
        "login": 25201110,
        "password": "e|([rXU1IsiM",
        "server": "Tickmill-Demo",
        "name": "Master Account"
    }
    
    # Slave accounts (followers)
    SLAVE_ACCOUNTS = [
        {
            "login": 25216036,
            "password": "oB9UY1&,B=^9",
            "server": "Tickmill-Demo",
            "name": "Copy Account 1",
            "copy_mode": "proportional",  # User can change: proportional, fixed_ratio, fixed_lot
            "copy_ratio": 1.0,
            "max_lot": 10.0,
            "min_lot": 0.01,
            "risk_percent": 2.0,  # 2% risk per trade
            "copy_sl": True,
            "copy_tp": True,
            "reverse_trades": False,
            "max_slippage": 10,
            "allowed_symbols": ["EURUSD", "GBPUSD", "XAUUSD", "USDJPY", "US30"],
            "blocked_symbols": []
        },
        {
            "login": 25216037,
            "password": "L[.Sdo4QRxx2",
            "server": "Tickmill-Demo", 
            "name": "Copy Account 2",
            "copy_mode": "fixed_ratio",  # Different copy mode for this account
            "copy_ratio": 2.0,  # 2x multiplier
            "max_lot": 20.0,
            "min_lot": 0.01,
            "risk_percent": 3.0,  # 3% risk per trade
            "copy_sl": True,
            "copy_tp": True,
            "reverse_trades": False,
            "max_slippage": 15,
            "allowed_symbols": [],  # Empty = all symbols allowed
            "blocked_symbols": ["XAUUSD"]  # Block gold trading on this account
        }
    ]

class CopyTradeInfo:
    """Information about a copied trade"""
    def __init__(self, master_ticket, slave_ticket, slave_account, symbol, volume, price):
        self.master_ticket = master_ticket
        self.slave_ticket = slave_ticket
        self.slave_account = slave_account
        self.symbol = symbol
        self.volume = volume
        self.price = price
        self.open_time = datetime.now()
        self.profit = 0.0
        self.closed = False

class AdvancedCopyTradingSystem:
    """Advanced MT5 Copy Trading System"""
    
    def __init__(self):
        self.master_account = CopyTradingConfig.MASTER_ACCOUNT
        self.slave_accounts = CopyTradingConfig.SLAVE_ACCOUNTS
        self.active_copies = {}  # master_ticket -> [CopyTradeInfo]
        self.copy_history = []
        self.running = False
        self.last_sync = datetime.now()
        
        # Performance tracking
        self.total_copies = 0
        self.successful_copies = 0
        self.execution_times = []
        self.slippage_data = []
        
        # Risk management
        self.daily_loss_limit = 0.05  # 5% daily loss limit
        self.max_daily_trades = 100
        self.emergency_stop = False
        
    def calculate_lot_size(self, master_volume: float, slave_config: dict, 
                          master_balance: float, slave_balance: float) -> float:
        """Calculate appropriate lot size based on copy mode"""
        try:
            copy_mode = slave_config.get("copy_mode", "proportional")
            copy_ratio = slave_config.get("copy_ratio", 1.0)
            min_lot = slave_config.get("min_lot", 0.01)
            max_lot = slave_config.get("max_lot", 10.0)
            
            if copy_mode == "proportional":
                # Balance-based proportional copying (default)
                if master_balance <= 0:
                    volume = min_lot
                else:
                    ratio = slave_balance / master_balance
                    volume = master_volume * ratio
                    
            elif copy_mode == "fixed_ratio":
                # Fixed multiplier ratio
                volume = master_volume * copy_ratio
                
            elif copy_mode == "fixed_lot":
                # Always use fixed lot size
                volume = copy_ratio
                
            elif copy_mode == "risk_based":
                # Risk percentage based
                risk_percent = slave_config.get("risk_percent", 2.0) / 100
                # Simplified risk calculation
                volume = (slave_balance * risk_percent) / 100
                
            else:
                volume = master_volume
                
            # Apply limits
            volume = max(min_lot, min(volume, max_lot))
            
            # Round to 0.01 (broker standard)
            volume = round(volume, 2)
            
            return volume
            
        except Exception as e:
            logger.error(f"Error calculating lot size: {e}")
            return slave_config.get("min_lot", 0.01)
            
    def is_symbol_allowed(self, symbol: str, slave_config: dict) -> bool:
        """Check if symbol is allowed for copying"""
        allowed = slave_config.get("allowed_symbols", [])
        blocked = slave_config.get("blocked_symbols", [])
        
        # If blocked list contains symbol, reject
        if blocked and symbol in blocked:
            return False
            
        # If allowed list exists and symbol not in it, reject
        if allowed and symbol not in allowed:
            return False
            
        return True
        
    def login_to_account(self, account: dict) -> bool:
        """Login to MT5 account"""
        try:
            if not mt5.initialize():
                logger.error("MT5 initialization failed")
                return False
                
            success = mt5.login(account["login"], account["password"], account["server"])
            if not success:
                error = mt5.last_error()
                logger.error(f"Login failed for {account['name']}: {error}")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Login error for {account['name']}: {e}")
            return False
            
    def copy_trade_to_slave(self, master_trade: dict, slave_config: dict) -> Optional[CopyTradeInfo]:
        """Copy a single trade to slave account"""
        start_time = time.time()
        
        try:
            # Check if symbol is allowed
            if not self.is_symbol_allowed(master_trade["symbol"], slave_config):
                logger.debug(f"Symbol {master_trade['symbol']} not allowed for {slave_config['name']}")
                return None
                
            # Login to slave account
            if not self.login_to_account(slave_config):
                return None
                
            # Get account info
            slave_info = mt5.account_info()
            if slave_info is None:
                logger.error(f"Failed to get account info for {slave_config['name']}")
                return None
                
            # Login to master to get balance
            if not self.login_to_account(self.master_account):
                return None
            master_info = mt5.account_info()
            
            # Calculate copy volume
            copy_volume = self.calculate_lot_size(
                master_trade["volume"],
                slave_config,
                master_info.balance,
                slave_info.balance
            )
            
            # Login back to slave
            if not self.login_to_account(slave_config):
                return None
                
            # Get symbol info
            symbol = master_trade["symbol"]
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                logger.warning(f"Symbol {symbol} not available on {slave_config['name']}")
                return None
                
            # Determine trade type
            trade_type = master_trade["type"]
            if slave_config.get("reverse_trades", False):
                trade_type = mt5.ORDER_TYPE_SELL if trade_type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
                
            # Get price
            price = symbol_info.ask if trade_type == mt5.ORDER_TYPE_BUY else symbol_info.bid
            
            # Prepare request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": copy_volume,
                "type": trade_type,
                "price": price,
                "deviation": slave_config.get("max_slippage", 10),
                "magic": 234000,
                "comment": f"Copy from {self.master_account['login']}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Add SL/TP if enabled
            if slave_config.get("copy_sl", True) and master_trade.get("sl", 0) > 0:
                request["sl"] = master_trade["sl"]
            if slave_config.get("copy_tp", True) and master_trade.get("tp", 0) > 0:
                request["tp"] = master_trade["tp"]
                
            # Execute trade
            result = mt5.order_send(request)
            execution_time = time.time() - start_time
            self.execution_times.append(execution_time)
            
            if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
                logger.error(f"Copy trade failed for {slave_config['name']}: {result.comment if result else 'Unknown error'}")
                return None
                
            # Calculate slippage
            slippage = abs(result.price - price) / symbol_info.point if symbol_info.point > 0 else 0
            self.slippage_data.append(slippage)
            
            # Create copy info
            copy_info = CopyTradeInfo(
                master_ticket=master_trade["ticket"],
                slave_ticket=result.order,
                slave_account=slave_config["login"],
                symbol=symbol,
                volume=copy_volume,
                price=result.price
            )
            
            # Track the copy
            if master_trade["ticket"] not in self.active_copies:
                self.active_copies[master_trade["ticket"]] = []
            self.active_copies[master_trade["ticket"]].append(copy_info)
            
            self.total_copies += 1
            self.successful_copies += 1
            
            logger.info(f"✅ Trade copied to {slave_config['name']}")
            logger.info(f"   {symbol} {master_trade['volume']} -> {copy_volume} lot")
            logger.info(f"   Price: {result.price} | Slippage: {slippage:.1f} points")
            logger.info(f"   Execution: {execution_time*1000:.1f}ms")
            
            return copy_info
            
        except Exception as e:
            logger.error(f"Error copying trade to {slave_config['name']}: {e}")
            return None
            
    def close_copied_trades(self, master_ticket: int):
        """Close all copied trades when master closes"""
        if master_ticket not in self.active_copies:
            return
            
        for copy_info in self.active_copies[master_ticket]:
            try:
                # Find slave account config
                slave_config = next(
                    (acc for acc in self.slave_accounts if acc["login"] == copy_info.slave_account),
                    None
                )
                
                if not slave_config:
                    continue
                    
                # Login to slave account
                if not self.login_to_account(slave_config):
                    continue
                    
                # Get position
                positions = mt5.positions_get(ticket=copy_info.slave_ticket)
                if not positions:
                    copy_info.closed = True
                    continue
                    
                position = positions[0]
                symbol_info = mt5.symbol_info(position.symbol)
                
                # Close position
                close_request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": position.symbol,
                    "volume": position.volume,
                    "type": mt5.ORDER_TYPE_SELL if position.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY,
                    "position": copy_info.slave_ticket,
                    "price": symbol_info.bid if position.type == mt5.POSITION_TYPE_BUY else symbol_info.ask,
                    "deviation": slave_config.get("max_slippage", 10),
                    "magic": 234000,
                    "comment": "Close copied trade",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC,
                }
                
                result = mt5.order_send(close_request)
                
                if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                    copy_info.profit = position.profit
                    copy_info.closed = True
                    logger.info(f"✅ Copied trade closed on {slave_config['name']} | P&L: ${position.profit:.2f}")
                else:
                    logger.error(f"Failed to close copied trade on {slave_config['name']}")
                    
            except Exception as e:
                logger.error(f"Error closing copied trade: {e}")
                
        # Move to history
        self.copy_history.extend(self.active_copies[master_ticket])
        del self.active_copies[master_ticket]
        
    def sync_trades(self):
        """Synchronize trades between master and slaves"""
        try:
            # Login to master account
            if not self.login_to_account(self.master_account):
                logger.error("Failed to login to master account")
                return
                
            # Get recent deals (last 2 minutes)
            end_time = datetime.now()
            start_time = end_time - timedelta(minutes=2)
            
            deals = mt5.history_deals_get(start_time, end_time)
            if deals is None:
                return
                
            for deal in deals:
                try:
                    # Only process entry deals (new trades)
                    if deal.entry == mt5.DEAL_ENTRY_IN:
                        master_trade = {
                            "ticket": deal.position_id,
                            "symbol": deal.symbol,
                            "type": mt5.ORDER_TYPE_BUY if deal.type == mt5.DEAL_TYPE_BUY else mt5.ORDER_TYPE_SELL,
                            "volume": deal.volume,
                            "price": deal.price,
                            "time": datetime.fromtimestamp(deal.time),
                            "sl": 0,
                            "tp": 0
                        }
                        
                        # Get SL/TP from position
                        positions = mt5.positions_get(ticket=deal.position_id)
                        if positions:
                            master_trade["sl"] = positions[0].sl
                            master_trade["tp"] = positions[0].tp
                            
                        # Check if already copied
                        if deal.position_id in self.active_copies:
                            continue
                            
                        # Copy to all slave accounts
                        logger.info(f"🎯 New master trade detected: {deal.symbol} {deal.volume} lot")
                        
                        for slave_config in self.slave_accounts:
                            self.copy_trade_to_slave(master_trade, slave_config)
                            
                    # Process exit deals (closing trades)
                    elif deal.entry == mt5.DEAL_ENTRY_OUT:
                        logger.info(f"🔄 Master position closed: {deal.position_id}")
                        self.close_copied_trades(deal.position_id)
                        
                except Exception as e:
                    logger.error(f"Error processing deal: {e}")
                    
        except Exception as e:
            logger.error(f"Error in sync_trades: {e}")
            
    def get_performance_stats(self) -> dict:
        """Get performance statistics"""
        success_rate = (self.successful_copies / self.total_copies * 100) if self.total_copies > 0 else 0
        avg_execution = sum(self.execution_times) / len(self.execution_times) if self.execution_times else 0
        avg_slippage = sum(self.slippage_data) / len(self.slippage_data) if self.slippage_data else 0
        
        return {
            "total_copies": self.total_copies,
            "successful_copies": self.successful_copies,
            "success_rate": round(success_rate, 1),
            "avg_execution_ms": round(avg_execution * 1000, 1),
            "avg_slippage_points": round(avg_slippage, 1),
            "active_copies": sum(len(copies) for copies in self.active_copies.values()),
            "total_history": len(self.copy_history),
            "running_time": (datetime.now() - self.last_sync).total_seconds() / 3600
        }
        
    def log_status(self):
        """Log current status"""
        stats = self.get_performance_stats()
        
        logger.info("="*60)
        logger.info("📊 COPY TRADING STATUS REPORT")
        logger.info("="*60)
        logger.info(f"📈 Total Copies: {stats['total_copies']}")
        logger.info(f"✅ Success Rate: {stats['success_rate']}%")
        logger.info(f"🔄 Active Copies: {stats['active_copies']}")
        logger.info(f"⚡ Avg Execution: {stats['avg_execution_ms']}ms")
        logger.info(f"📊 Avg Slippage: {stats['avg_slippage_points']} points")
        logger.info(f"⏱️ Running Time: {stats['running_time']:.1f} hours")
        logger.info("="*60)
        
        # Account status
        for i, account in enumerate(self.slave_accounts, 1):
            active_count = sum(
                1 for copies in self.active_copies.values() 
                for copy in copies if copy.slave_account == account["login"]
            )
            logger.info(f"Account {i} ({account['name']}): {active_count} active copies")
            
    async def run(self):
        """Main copy trading loop"""
        logger.info("🚀 Starting Advanced Copy Trading System")
        logger.info(f"📡 Master Account: {self.master_account['name']} ({self.master_account['login']})")
        logger.info(f"👥 Slave Accounts: {len(self.slave_accounts)}")
        
        # Show copy modes
        for account in self.slave_accounts:
            logger.info(f"   {account['name']}: {account['copy_mode']} mode (ratio: {account['copy_ratio']})")
            
        self.running = True
        self.last_sync = datetime.now()
        
        try:
            while self.running:
                # Sync trades
                self.sync_trades()
                
                # Log status every 5 minutes
                if int(time.time()) % 300 == 0:
                    self.log_status()
                    
                # Emergency stop check
                if self.emergency_stop:
                    logger.warning("🛑 Emergency stop activated!")
                    break
                    
                # Sleep for 2 seconds
                await asyncio.sleep(2)
                
        except KeyboardInterrupt:
            logger.info("⏹️ Copy trading stopped by user")
            
        finally:
            # Close all positions
            logger.info("🔄 Closing all copied positions...")
            for master_ticket in list(self.active_copies.keys()):
                self.close_copied_trades(master_ticket)
                
            # Final stats
            self.log_status()
            
            # Save results
            self.save_results()
            
            mt5.shutdown()
            logger.info("✅ Copy trading system stopped")
            
    def save_results(self):
        """Save copy trading results"""
        try:
            results = {
                "session_summary": self.get_performance_stats(),
                "master_account": self.master_account["name"],
                "slave_accounts": [acc["name"] for acc in self.slave_accounts],
                "copy_history": [
                    {
                        "master_ticket": copy.master_ticket,
                        "slave_ticket": copy.slave_ticket,
                        "slave_account": copy.slave_account,
                        "symbol": copy.symbol,
                        "volume": copy.volume,
                        "price": copy.price,
                        "profit": copy.profit,
                        "open_time": copy.open_time.isoformat(),
                        "closed": copy.closed
                    }
                    for copy in self.copy_history
                ],
                "session_end": datetime.now().isoformat()
            }
            
            filename = f"copy_trading_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
                
            logger.info(f"📄 Results saved to {filename}")
            
        except Exception as e:
            logger.error(f"Error saving results: {e}")

def show_configuration():
    """Show current copy trading configuration"""
    print("="*80)
    print("🔧 COPY TRADING CONFIGURATION")
    print("="*80)
    
    master = CopyTradingConfig.MASTER_ACCOUNT
    print(f"\n📡 MASTER ACCOUNT (Signal Provider)")
    print(f"   Name: {master['name']}")
    print(f"   Login: {master['login']}")
    print(f"   Server: {master['server']}")
    
    print(f"\n👥 SLAVE ACCOUNTS (Followers): {len(CopyTradingConfig.SLAVE_ACCOUNTS)}")
    for i, slave in enumerate(CopyTradingConfig.SLAVE_ACCOUNTS, 1):
        print(f"\n   Account {i}: {slave['name']}")
        print(f"   Login: {slave['login']}")
        print(f"   Copy Mode: {slave['copy_mode']}")
        print(f"   Copy Ratio: {slave['copy_ratio']}")
        print(f"   Risk: {slave['risk_percent']}%")
        print(f"   Max Lot: {slave['max_lot']}")
        if slave['allowed_symbols']:
            print(f"   Allowed: {', '.join(slave['allowed_symbols'])}")
        if slave['blocked_symbols']:
            print(f"   Blocked: {', '.join(slave['blocked_symbols'])}")
            
    print(f"\n🎛️ COPY MODES AVAILABLE:")
    print(f"   proportional  - Copy based on balance ratio (default)")
    print(f"   fixed_ratio   - Fixed multiplier (e.g. 2x)")
    print(f"   fixed_lot     - Always use same lot size")
    print(f"   risk_based    - Risk percentage per trade")
    
    print("\n" + "="*80)

async def main():
    """Main entry point"""
    show_configuration()
    
    print("\n⚠️  WARNING: This will start REAL copy trading!")
    print("All trades from master account will be copied to slave accounts.")
    print("Press Ctrl+C at any time to stop.\n")
    
    response = input("Start Copy Trading System? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Copy trading cancelled")
        return
        
    # Test connections first
    print("\n🔍 Testing account connections...")
    copy_system = AdvancedCopyTradingSystem()
    
    # Test master account
    if copy_system.login_to_account(copy_system.master_account):
        account_info = mt5.account_info()
        print(f"✅ Master: {account_info.name} - ${account_info.balance:,.2f}")
    else:
        print("❌ Master account connection failed!")
        return
        
    # Test slave accounts
    slave_ok = 0
    for slave in copy_system.slave_accounts:
        if copy_system.login_to_account(slave):
            account_info = mt5.account_info()
            print(f"✅ Slave: {account_info.name} - ${account_info.balance:,.2f}")
            slave_ok += 1
        else:
            print(f"❌ {slave['name']} connection failed!")
            
    if slave_ok == 0:
        print("❌ No slave accounts connected!")
        return
        
    print(f"\n🎉 {slave_ok + 1} accounts connected successfully!")
    print("🚀 Starting copy trading system...\n")
    
    # Run copy trading
    await copy_system.run()

if __name__ == "__main__":
    asyncio.run(main()) 