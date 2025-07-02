"""
Advanced Copy Trading Service
Based on MT5 best practices and competitor analysis
"""
import MetaTrader5 as mt5
import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
import threading
from collections import deque

logger = logging.getLogger(__name__)

class CopyMode(Enum):
    PROPORTIONAL = "proportional"  # Default - copies based on balance ratio
    FIXED_LOT = "fixed_lot"        # Fixed lot size
    FIXED_RATIO = "fixed_ratio"    # Fixed multiplier ratio
    PERCENTAGE_EQUITY = "percentage_equity"  # % of equity per trade

class CopyStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"

@dataclass
class MasterAccount:
    login: int
    password: str
    server: str
    name: str
    account_type: str = "Classic"
    currency: str = "USD"

@dataclass
class SlaveAccount:
    login: int
    password: str
    server: str
    name: str
    copy_mode: CopyMode = CopyMode.PROPORTIONAL
    copy_ratio: float = 1.0
    max_lot_size: float = 100.0
    min_lot_size: float = 0.01
    max_slippage: int = 10
    copy_sl: bool = True
    copy_tp: bool = True
    reverse_trades: bool = False
    max_spread: float = 0.0
    allowed_symbols: List[str] = None
    blocked_symbols: List[str] = None
    copy_pending_orders: bool = True
    status: CopyStatus = CopyStatus.ACTIVE

@dataclass
class CopyTradeInfo:
    master_ticket: int
    slave_ticket: int
    master_account: int
    slave_account: int
    symbol: str
    trade_type: str
    master_volume: float
    slave_volume: float
    master_price: float
    slave_price: float
    copy_time: datetime
    sl: float = 0.0
    tp: float = 0.0
    commission: float = 0.0
    swap: float = 0.0
    profit: float = 0.0

class AdvancedCopyService:
    """Advanced MT5 Copy Trading Service with Best Practices"""
    
    def __init__(self):
        self.master_account: Optional[MasterAccount] = None
        self.slave_accounts: Dict[int, SlaveAccount] = {}
        self.active_copies: Dict[int, List[CopyTradeInfo]] = {}  # master_ticket -> slave_copies
        self.copy_history: deque = deque(maxlen=10000)
        self.running = False
        self.copy_thread = None
        self.performance_stats = {}
        self.last_sync_time = {}
        
        # Performance tracking
        self.execution_times = deque(maxlen=1000)
        self.slippage_data = deque(maxlen=1000)
        self.copy_success_rate = 0.0
        
        # Risk management
        self.daily_loss_limit = 0.05  # 5% max daily loss
        self.max_concurrent_trades = 50
        self.emergency_stop_triggered = False
        
    def set_master_account(self, account: MasterAccount) -> bool:
        """Set master account for signal providing"""
        try:
            if not mt5.initialize():
                logger.error("Failed to initialize MT5")
                return False
                
            if not mt5.login(account.login, account.password, account.server):
                logger.error(f"Failed to login to master account {account.login}")
                return False
                
            # Verify account
            account_info = mt5.account_info()
            if account_info is None:
                logger.error("Failed to get master account info")
                return False
                
            self.master_account = account
            logger.info(f"Master account set: {account.name} - {account.login}")
            logger.info(f"Balance: ${account_info.balance:,.2f} {account_info.currency}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting master account: {e}")
            return False
            
    def add_slave_account(self, account: SlaveAccount) -> bool:
        """Add slave account for copying"""
        try:
            # Test connection
            if not mt5.login(account.login, account.password, account.server):
                logger.error(f"Failed to login to slave account {account.login}")
                return False
                
            account_info = mt5.account_info()
            if account_info is None:
                logger.error("Failed to get slave account info")
                return False
                
            self.slave_accounts[account.login] = account
            self.active_copies[account.login] = []
            self.last_sync_time[account.login] = datetime.now()
            
            logger.info(f"Slave account added: {account.name} - {account.login}")
            logger.info(f"Balance: ${account_info.balance:,.2f} {account_info.currency}")
            logger.info(f"Copy mode: {account.copy_mode.value}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding slave account: {e}")
            return False
            
    def calculate_copy_volume(self, master_volume: float, slave_account: SlaveAccount, 
                            master_balance: float, slave_balance: float) -> float:
        """Calculate volume for slave account based on copy mode"""
        try:
            if slave_account.copy_mode == CopyMode.PROPORTIONAL:
                # Balance-based proportional copying
                if master_balance <= 0:
                    return slave_account.min_lot_size
                ratio = slave_balance / master_balance
                volume = master_volume * ratio
                
            elif slave_account.copy_mode == CopyMode.FIXED_LOT:
                # Fixed lot size
                volume = slave_account.copy_ratio
                
            elif slave_account.copy_mode == CopyMode.FIXED_RATIO:
                # Fixed multiplier
                volume = master_volume * slave_account.copy_ratio
                
            elif slave_account.copy_mode == CopyMode.PERCENTAGE_EQUITY:
                # Percentage of equity per trade
                volume = (slave_balance * slave_account.copy_ratio / 100) / 1000  # Simplified
                
            else:
                volume = master_volume
                
            # Apply limits
            volume = max(slave_account.min_lot_size, volume)
            volume = min(slave_account.max_lot_size, volume)
            
            # Round to broker's lot step (simplified to 0.01)
            volume = round(volume, 2)
            
            return volume
            
        except Exception as e:
            logger.error(f"Error calculating copy volume: {e}")
            return slave_account.min_lot_size
            
    def copy_trade(self, master_trade: dict, slave_account: SlaveAccount) -> Optional[CopyTradeInfo]:
        """Copy individual trade to slave account"""
        start_time = time.time()
        
        try:
            # Login to slave account
            if not mt5.login(slave_account.login, slave_account.password, slave_account.server):
                logger.error(f"Failed to login to slave account {slave_account.login}")
                return None
                
            # Get account info
            slave_info = mt5.account_info()
            if slave_info is None:
                return None
                
            # Check symbol filters
            symbol = master_trade['symbol']
            if slave_account.allowed_symbols and symbol not in slave_account.allowed_symbols:
                logger.debug(f"Symbol {symbol} not in allowed list for {slave_account.login}")
                return None
                
            if slave_account.blocked_symbols and symbol in slave_account.blocked_symbols:
                logger.debug(f"Symbol {symbol} is blocked for {slave_account.login}")
                return None
                
            # Get symbol info
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                logger.warning(f"Symbol {symbol} not available on slave account {slave_account.login}")
                return None
                
            # Check spread limit
            if slave_account.max_spread > 0:
                spread = (symbol_info.ask - symbol_info.bid) / symbol_info.point
                if spread > slave_account.max_spread:
                    logger.debug(f"Spread too high for {symbol}: {spread} points")
                    return None
                    
            # Login to master account to get balance
            if not mt5.login(self.master_account.login, self.master_account.password, self.master_account.server):
                return None
            master_info = mt5.account_info()
            
            # Calculate copy volume
            copy_volume = self.calculate_copy_volume(
                master_trade['volume'],
                slave_account,
                master_info.balance,
                slave_info.balance
            )
            
            # Login back to slave account
            if not mt5.login(slave_account.login, slave_account.password, slave_account.server):
                return None
                
            # Prepare trade request
            trade_type = master_trade['type']
            if slave_account.reverse_trades:
                trade_type = mt5.ORDER_TYPE_SELL if trade_type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
                
            price = symbol_info.ask if trade_type == mt5.ORDER_TYPE_BUY else symbol_info.bid
            
            # Calculate SL/TP
            sl = 0.0
            tp = 0.0
            
            if slave_account.copy_sl and master_trade.get('sl', 0) > 0:
                sl = master_trade['sl']
                
            if slave_account.copy_tp and master_trade.get('tp', 0) > 0:
                tp = master_trade['tp']
                
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": copy_volume,
                "type": trade_type,
                "price": price,
                "sl": sl,
                "tp": tp,
                "deviation": slave_account.max_slippage,
                "magic": 234000,
                "comment": f"Copy from {self.master_account.login}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Execute trade
            result = mt5.order_send(request)
            execution_time = time.time() - start_time
            self.execution_times.append(execution_time)
            
            if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
                logger.error(f"Failed to copy trade to {slave_account.login}: {result.comment if result else 'Unknown error'}")
                return None
                
            # Calculate slippage
            slippage = abs(result.price - price) / symbol_info.point if symbol_info.point > 0 else 0
            self.slippage_data.append(slippage)
            
            # Create copy info
            copy_info = CopyTradeInfo(
                master_ticket=master_trade['ticket'],
                slave_ticket=result.order,
                master_account=self.master_account.login,
                slave_account=slave_account.login,
                symbol=symbol,
                trade_type="BUY" if trade_type == mt5.ORDER_TYPE_BUY else "SELL",
                master_volume=master_trade['volume'],
                slave_volume=copy_volume,
                master_price=master_trade['price'],
                slave_price=result.price,
                copy_time=datetime.now(),
                sl=sl,
                tp=tp
            )
            
            # Store copy info
            self.active_copies[slave_account.login].append(copy_info)
            self.copy_history.append(copy_info)
            
            logger.info(f"✅ Trade copied to {slave_account.name}")
            logger.info(f"   Symbol: {symbol} | Type: {copy_info.trade_type}")
            logger.info(f"   Master: {master_trade['volume']} lot @ {master_trade['price']}")
            logger.info(f"   Slave: {copy_volume} lot @ {result.price}")
            logger.info(f"   Execution time: {execution_time*1000:.1f}ms | Slippage: {slippage:.1f} points")
            
            return copy_info
            
        except Exception as e:
            logger.error(f"Error copying trade: {e}")
            return None
            
    def close_copied_trade(self, master_ticket: int, slave_account: SlaveAccount) -> bool:
        """Close copied trade when master closes"""
        try:
            # Find copied trade
            copied_trade = None
            for copy_info in self.active_copies.get(slave_account.login, []):
                if copy_info.master_ticket == master_ticket:
                    copied_trade = copy_info
                    break
                    
            if not copied_trade:
                return False
                
            # Login to slave account
            if not mt5.login(slave_account.login, slave_account.password, slave_account.server):
                return False
                
            # Get position
            positions = mt5.positions_get(ticket=copied_trade.slave_ticket)
            if not positions:
                # Position already closed
                self.active_copies[slave_account.login].remove(copied_trade)
                return True
                
            position = positions[0]
            symbol_info = mt5.symbol_info(position.symbol)
            
            # Close position
            close_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": position.symbol,
                "volume": position.volume,
                "type": mt5.ORDER_TYPE_SELL if position.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY,
                "position": copied_trade.slave_ticket,
                "price": symbol_info.bid if position.type == mt5.POSITION_TYPE_BUY else symbol_info.ask,
                "deviation": slave_account.max_slippage,
                "magic": 234000,
                "comment": "Close copied trade",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            result = mt5.order_send(close_request)
            
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                # Update copy info with profit
                copied_trade.profit = position.profit
                copied_trade.commission = position.commission
                copied_trade.swap = position.swap
                
                # Remove from active copies
                self.active_copies[slave_account.login].remove(copied_trade)
                
                logger.info(f"✅ Copied trade closed on {slave_account.name}")
                logger.info(f"   Ticket: {copied_trade.slave_ticket} | P&L: ${position.profit:.2f}")
                
                return True
            else:
                logger.error(f"Failed to close copied trade: {result.comment if result else 'Unknown error'}")
                return False
                
        except Exception as e:
            logger.error(f"Error closing copied trade: {e}")
            return False
            
    def sync_trades(self):
        """Synchronize trades between master and slave accounts"""
        try:
            # Login to master account
            if not mt5.login(self.master_account.login, self.master_account.password, self.master_account.server):
                logger.error("Failed to login to master account for sync")
                return
                
            # Get master positions
            master_positions = mt5.positions_get()
            if master_positions is None:
                master_positions = []
                
            # Get master deals (recent trades)
            deals = mt5.history_deals_get(datetime.now() - timedelta(minutes=5), datetime.now())
            if deals is None:
                deals = []
                
            # Track new trades
            for deal in deals:
                if deal.entry == mt5.DEAL_ENTRY_IN:  # Opening trade
                    master_trade = {
                        'ticket': deal.position_id,
                        'symbol': deal.symbol,
                        'type': mt5.ORDER_TYPE_BUY if deal.type == mt5.DEAL_TYPE_BUY else mt5.ORDER_TYPE_SELL,
                        'volume': deal.volume,
                        'price': deal.price,
                        'sl': 0,  # Will be updated if available
                        'tp': 0,  # Will be updated if available
                        'time': datetime.fromtimestamp(deal.time),
                        'comment': deal.comment
                    }
                    
                    # Get SL/TP from position
                    position = next((p for p in master_positions if p.ticket == deal.position_id), None)
                    if position:
                        master_trade['sl'] = position.sl
                        master_trade['tp'] = position.tp
                        
                    # Copy to all active slave accounts
                    for slave_account in self.slave_accounts.values():
                        if slave_account.status == CopyStatus.ACTIVE:
                            # Check if already copied
                            already_copied = any(
                                copy_info.master_ticket == deal.position_id 
                                for copy_info in self.active_copies.get(slave_account.login, [])
                            )
                            
                            if not already_copied:
                                self.copy_trade(master_trade, slave_account)
                                
                elif deal.entry == mt5.DEAL_ENTRY_OUT:  # Closing trade
                    # Close corresponding copied trades
                    for slave_account in self.slave_accounts.values():
                        if slave_account.status == CopyStatus.ACTIVE:
                            self.close_copied_trade(deal.position_id, slave_account)
                            
        except Exception as e:
            logger.error(f"Error in sync_trades: {e}")
            
    def calculate_performance_stats(self) -> Dict:
        """Calculate comprehensive performance statistics"""
        try:
            stats = {
                'total_copies': len(self.copy_history),
                'active_copies': sum(len(copies) for copies in self.active_copies.values()),
                'avg_execution_time_ms': np.mean(self.execution_times) * 1000 if self.execution_times else 0,
                'avg_slippage_points': np.mean(self.slippage_data) if self.slippage_data else 0,
                'slave_accounts': len(self.slave_accounts),
                'copy_success_rate': self.copy_success_rate * 100,
                'daily_trades': 0,
                'total_profit': 0.0,
                'win_rate': 0.0
            }
            
            # Calculate P&L statistics
            closed_trades = [trade for trade in self.copy_history if hasattr(trade, 'profit') and trade.profit != 0]
            if closed_trades:
                total_profit = sum(trade.profit for trade in closed_trades)
                winning_trades = [trade for trade in closed_trades if trade.profit > 0]
                win_rate = len(winning_trades) / len(closed_trades) * 100
                
                stats['total_profit'] = total_profit
                stats['win_rate'] = win_rate
                stats['closed_trades'] = len(closed_trades)
                
            # Daily trades
            today = datetime.now().date()
            daily_trades = [trade for trade in self.copy_history if trade.copy_time.date() == today]
            stats['daily_trades'] = len(daily_trades)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating performance stats: {e}")
            return {}
            
    async def run_copy_service(self):
        """Main copy trading service loop"""
        logger.info("🚀 Starting Advanced Copy Trading Service")
        self.running = True
        
        while self.running:
            try:
                if self.master_account and self.slave_accounts:
                    # Sync trades
                    self.sync_trades()
                    
                    # Update performance stats
                    self.performance_stats = self.calculate_performance_stats()
                    
                    # Log performance every 5 minutes
                    if int(time.time()) % 300 == 0:
                        self.log_performance_summary()
                        
                # Risk management checks
                self.check_risk_limits()
                
                # Wait before next sync
                await asyncio.sleep(1)  # High frequency monitoring
                
            except Exception as e:
                logger.error(f"Error in copy service loop: {e}")
                await asyncio.sleep(5)
                
    def check_risk_limits(self):
        """Check and enforce risk management limits"""
        try:
            # Check daily loss limits for each slave account
            for slave_account in self.slave_accounts.values():
                if slave_account.status != CopyStatus.ACTIVE:
                    continue
                    
                # Get today's trades
                today = datetime.now().date()
                today_trades = [
                    trade for trade in self.copy_history 
                    if (trade.slave_account == slave_account.login and 
                        trade.copy_time.date() == today and 
                        hasattr(trade, 'profit'))
                ]
                
                if today_trades:
                    daily_pnl = sum(trade.profit for trade in today_trades)
                    
                    # Check if daily loss limit exceeded
                    if not mt5.login(slave_account.login, slave_account.password, slave_account.server):
                        continue
                        
                    account_info = mt5.account_info()
                    if account_info:
                        loss_percentage = abs(daily_pnl) / account_info.balance
                        
                        if daily_pnl < 0 and loss_percentage > self.daily_loss_limit:
                            logger.warning(f"Daily loss limit exceeded for {slave_account.name}")
                            slave_account.status = CopyStatus.PAUSED
                            
            # Check max concurrent trades
            total_active = sum(len(copies) for copies in self.active_copies.values())
            if total_active > self.max_concurrent_trades:
                logger.warning(f"Max concurrent trades limit reached: {total_active}")
                
        except Exception as e:
            logger.error(f"Error in risk limit check: {e}")
            
    def log_performance_summary(self):
        """Log comprehensive performance summary"""
        stats = self.performance_stats
        
        logger.info("="*60)
        logger.info("📊 COPY TRADING PERFORMANCE SUMMARY")
        logger.info("="*60)
        logger.info(f"📈 Total Copies: {stats.get('total_copies', 0)}")
        logger.info(f"🔄 Active Copies: {stats.get('active_copies', 0)}")
        logger.info(f"👥 Slave Accounts: {stats.get('slave_accounts', 0)}")
        logger.info(f"⚡ Avg Execution: {stats.get('avg_execution_time_ms', 0):.1f}ms")
        logger.info(f"📊 Avg Slippage: {stats.get('avg_slippage_points', 0):.1f} points")
        logger.info(f"✅ Success Rate: {stats.get('copy_success_rate', 0):.1f}%")
        logger.info(f"💰 Total Profit: ${stats.get('total_profit', 0):.2f}")
        logger.info(f"🎯 Win Rate: {stats.get('win_rate', 0):.1f}%")
        logger.info(f"📅 Daily Trades: {stats.get('daily_trades', 0)}")
        logger.info("="*60)
        
    def get_status(self) -> Dict:
        """Get current copy trading status"""
        return {
            'service_running': self.running,
            'master_account': self.master_account.name if self.master_account else None,
            'slave_accounts': [
                {
                    'name': account.name,
                    'login': account.login,
                    'copy_mode': account.copy_mode.value,
                    'status': account.status.value,
                    'active_copies': len(self.active_copies.get(account.login, []))
                }
                for account in self.slave_accounts.values()
            ],
            'performance': self.performance_stats,
            'risk_status': {
                'emergency_stop': self.emergency_stop_triggered,
                'daily_loss_limit': self.daily_loss_limit * 100,
                'max_concurrent_trades': self.max_concurrent_trades
            }
        }
        
    def pause_account(self, account_login: int):
        """Pause copying for specific account"""
        if account_login in self.slave_accounts:
            self.slave_accounts[account_login].status = CopyStatus.PAUSED
            logger.info(f"Account {account_login} paused")
            
    def resume_account(self, account_login: int):
        """Resume copying for specific account"""
        if account_login in self.slave_accounts:
            self.slave_accounts[account_login].status = CopyStatus.ACTIVE
            logger.info(f"Account {account_login} resumed")
            
    def stop_service(self):
        """Stop copy trading service"""
        logger.info("🛑 Stopping Copy Trading Service")
        self.running = False
        
        # Close all copied positions
        for slave_account in self.slave_accounts.values():
            for copy_info in self.active_copies.get(slave_account.login, []):
                self.close_copied_trade(copy_info.master_ticket, slave_account)
                
        logger.info("✅ Copy Trading Service stopped")

# Export for API integration
def create_copy_service() -> AdvancedCopyService:
    """Factory function to create copy service instance"""
    return AdvancedCopyService() 