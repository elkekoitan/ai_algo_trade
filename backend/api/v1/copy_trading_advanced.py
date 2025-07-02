"""
Advanced Copy Trading API
REST endpoints for professional copy trading management
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Optional
import asyncio
from datetime import datetime

from modules.copy_trading.advanced_copy_service import (
    AdvancedCopyService, 
    MasterAccount, 
    SlaveAccount, 
    CopyMode, 
    CopyStatus
)

router = APIRouter(prefix="/copy-trading", tags=["Advanced Copy Trading"])

# Global copy service instance
copy_service = AdvancedCopyService()

# Pydantic models for API
class MasterAccountModel(BaseModel):
    login: int
    password: str
    server: str
    name: str
    account_type: str = "Classic"
    currency: str = "USD"

class SlaveAccountModel(BaseModel):
    login: int
    password: str
    server: str
    name: str
    copy_mode: str = "proportional"  # proportional, fixed_lot, fixed_ratio, percentage_equity
    copy_ratio: float = 1.0
    max_lot_size: float = 100.0
    min_lot_size: float = 0.01
    max_slippage: int = 10
    copy_sl: bool = True
    copy_tp: bool = True
    reverse_trades: bool = False
    max_spread: float = 0.0
    allowed_symbols: Optional[List[str]] = None
    blocked_symbols: Optional[List[str]] = None
    copy_pending_orders: bool = True

class CopyConfigModel(BaseModel):
    master_account: MasterAccountModel
    slave_accounts: List[SlaveAccountModel]

@router.post("/setup")
async def setup_copy_trading(config: CopyConfigModel, background_tasks: BackgroundTasks):
    """
    Setup copy trading with master and slave accounts
    Supports multiple copy modes: proportional, fixed_lot, fixed_ratio, percentage_equity
    """
    try:
        # Setup master account
        master = MasterAccount(
            login=config.master_account.login,
            password=config.master_account.password,
            server=config.master_account.server,
            name=config.master_account.name,
            account_type=config.master_account.account_type,
            currency=config.master_account.currency
        )
        
        if not copy_service.set_master_account(master):
            raise HTTPException(status_code=400, detail="Failed to setup master account")
        
        # Setup slave accounts
        slave_count = 0
        for slave_config in config.slave_accounts:
            # Convert copy mode string to enum
            try:
                copy_mode = CopyMode(slave_config.copy_mode.lower())
            except ValueError:
                copy_mode = CopyMode.PROPORTIONAL
                
            slave = SlaveAccount(
                login=slave_config.login,
                password=slave_config.password,
                server=slave_config.server,
                name=slave_config.name,
                copy_mode=copy_mode,
                copy_ratio=slave_config.copy_ratio,
                max_lot_size=slave_config.max_lot_size,
                min_lot_size=slave_config.min_lot_size,
                max_slippage=slave_config.max_slippage,
                copy_sl=slave_config.copy_sl,
                copy_tp=slave_config.copy_tp,
                reverse_trades=slave_config.reverse_trades,
                max_spread=slave_config.max_spread,
                allowed_symbols=slave_config.allowed_symbols,
                blocked_symbols=slave_config.blocked_symbols,
                copy_pending_orders=slave_config.copy_pending_orders,
                status=CopyStatus.ACTIVE
            )
            
            if copy_service.add_slave_account(slave):
                slave_count += 1
        
        # Start copy service in background
        if not copy_service.running:
            background_tasks.add_task(start_copy_service_background)
        
        return {
            "status": "success",
            "message": f"Copy trading setup complete",
            "master_account": config.master_account.name,
            "slave_accounts_added": slave_count,
            "total_slave_accounts": len(config.slave_accounts)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Setup failed: {str(e)}")

async def start_copy_service_background():
    """Background task to start copy service"""
    await copy_service.run_copy_service()

@router.get("/status")
async def get_copy_status():
    """Get current copy trading status and performance metrics"""
    return copy_service.get_status()

@router.post("/accounts/{account_login}/pause")
async def pause_account(account_login: int):
    """Pause copying for specific slave account"""
    if account_login not in copy_service.slave_accounts:
        raise HTTPException(status_code=404, detail="Account not found")
    
    copy_service.pause_account(account_login)
    return {"status": "success", "message": f"Account {account_login} paused"}

@router.post("/accounts/{account_login}/resume")
async def resume_account(account_login: int):
    """Resume copying for specific slave account"""
    if account_login not in copy_service.slave_accounts:
        raise HTTPException(status_code=404, detail="Account not found")
    
    copy_service.resume_account(account_login)
    return {"status": "success", "message": f"Account {account_login} resumed"}

@router.get("/performance")
async def get_performance_metrics():
    """Get detailed performance metrics and statistics"""
    stats = copy_service.calculate_performance_stats()
    
    return {
        "performance_metrics": stats,
        "execution_stats": {
            "avg_execution_time_ms": stats.get('avg_execution_time_ms', 0),
            "min_execution_time_ms": min(copy_service.execution_times) * 1000 if copy_service.execution_times else 0,
            "max_execution_time_ms": max(copy_service.execution_times) * 1000 if copy_service.execution_times else 0,
            "avg_slippage_points": stats.get('avg_slippage_points', 0),
            "success_rate": stats.get('copy_success_rate', 0)
        },
        "financial_metrics": {
            "total_profit": stats.get('total_profit', 0),
            "win_rate": stats.get('win_rate', 0),
            "total_trades": stats.get('total_copies', 0),
            "active_trades": stats.get('active_copies', 0)
        },
        "risk_metrics": {
            "daily_loss_limit": copy_service.daily_loss_limit * 100,
            "max_concurrent_trades": copy_service.max_concurrent_trades,
            "emergency_stop": copy_service.emergency_stop_triggered
        }
    }

@router.get("/history")
async def get_copy_history(limit: int = 100):
    """Get copy trading history"""
    history = list(copy_service.copy_history)[-limit:]
    
    return {
        "history": [
            {
                "master_ticket": trade.master_ticket,
                "slave_ticket": trade.slave_ticket,
                "master_account": trade.master_account,
                "slave_account": trade.slave_account,
                "symbol": trade.symbol,
                "trade_type": trade.trade_type,
                "master_volume": trade.master_volume,
                "slave_volume": trade.slave_volume,
                "master_price": trade.master_price,
                "slave_price": trade.slave_price,
                "copy_time": trade.copy_time.isoformat(),
                "profit": getattr(trade, 'profit', 0),
                "commission": getattr(trade, 'commission', 0),
                "swap": getattr(trade, 'swap', 0)
            }
            for trade in history
        ],
        "total_records": len(copy_service.copy_history),
        "showing": len(history)
    }

@router.get("/accounts")
async def get_accounts_info():
    """Get information about all configured accounts"""
    accounts_info = []
    
    # Master account info
    if copy_service.master_account:
        accounts_info.append({
            "type": "master",
            "login": copy_service.master_account.login,
            "name": copy_service.master_account.name,
            "server": copy_service.master_account.server,
            "currency": copy_service.master_account.currency
        })
    
    # Slave accounts info
    for slave in copy_service.slave_accounts.values():
        accounts_info.append({
            "type": "slave",
            "login": slave.login,
            "name": slave.name,
            "server": slave.server,
            "copy_mode": slave.copy_mode.value,
            "copy_ratio": slave.copy_ratio,
            "status": slave.status.value,
            "active_copies": len(copy_service.active_copies.get(slave.login, [])),
            "settings": {
                "max_lot_size": slave.max_lot_size,
                "min_lot_size": slave.min_lot_size,
                "max_slippage": slave.max_slippage,
                "copy_sl": slave.copy_sl,
                "copy_tp": slave.copy_tp,
                "reverse_trades": slave.reverse_trades,
                "max_spread": slave.max_spread
            }
        })
    
    return {
        "accounts": accounts_info,
        "total_accounts": len(accounts_info),
        "master_accounts": 1 if copy_service.master_account else 0,
        "slave_accounts": len(copy_service.slave_accounts)
    }

@router.post("/stop")
async def stop_copy_service():
    """Stop copy trading service and close all positions"""
    copy_service.stop_service()
    return {"status": "success", "message": "Copy trading service stopped"}

@router.post("/emergency-stop")
async def emergency_stop():
    """Emergency stop - immediately halt all copying and close positions"""
    copy_service.emergency_stop_triggered = True
    copy_service.stop_service()
    
    return {
        "status": "emergency_stop_activated",
        "message": "Emergency stop activated - all copying halted",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/real-time-monitor")
async def real_time_monitor():
    """Real-time monitoring endpoint for live statistics"""
    current_stats = copy_service.calculate_performance_stats()
    
    # Get recent execution times (last 10)
    recent_executions = list(copy_service.execution_times)[-10:] if copy_service.execution_times else []
    recent_slippage = list(copy_service.slippage_data)[-10:] if copy_service.slippage_data else []
    
    return {
        "timestamp": datetime.now().isoformat(),
        "service_status": "running" if copy_service.running else "stopped",
        "live_stats": current_stats,
        "recent_performance": {
            "last_10_executions_ms": [t * 1000 for t in recent_executions],
            "last_10_slippage_points": recent_slippage,
            "current_active_copies": sum(len(copies) for copies in copy_service.active_copies.values())
        },
        "account_status": [
            {
                "login": account.login,
                "name": account.name,
                "status": account.status.value,
                "active_copies": len(copy_service.active_copies.get(account.login, []))
            }
            for account in copy_service.slave_accounts.values()
        ]
    }

@router.post("/test-connection")
async def test_connection(account: MasterAccountModel):
    """Test MT5 connection for given account credentials"""
    import MetaTrader5 as mt5
    
    try:
        if not mt5.initialize():
            return {"status": "error", "message": "MT5 initialization failed"}
        
        if not mt5.login(account.login, account.password, account.server):
            error = mt5.last_error()
            return {"status": "error", "message": f"Login failed: {error}"}
        
        account_info = mt5.account_info()
        if account_info is None:
            return {"status": "error", "message": "Failed to get account info"}
        
        mt5.shutdown()
        
        return {
            "status": "success",
            "message": "Connection successful",
            "account_info": {
                "login": account_info.login,
                "server": account_info.server,
                "name": account_info.name,
                "balance": account_info.balance,
                "equity": account_info.equity,
                "currency": account_info.currency,
                "company": account_info.company
            }
        }
        
    except Exception as e:
        return {"status": "error", "message": f"Connection test failed: {str(e)}"} 