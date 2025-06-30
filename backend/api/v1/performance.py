from fastapi import APIRouter, HTTPException, Depends, Request, Query
from typing import List, Dict, Any
import logging
from datetime import datetime
import pandas as pd

from backend.core.unified_trading_engine import UnifiedTradingEngine
from backend.modules.mt5_integration.service import MT5Service
from backend.core.logger import get_logger
from backend.modules.performance.service import PerformanceService

router = APIRouter()
logger = logging.getLogger(__name__)

# This service will be initialized using the engine's instance
performance_service: PerformanceService | None = None

def get_performance_service(request: Request) -> PerformanceService:
    """Dependency to get or create the performance service."""
    global performance_service
    if performance_service is None:
        engine = request.app.state.trading_engine
        if not engine or not engine.connected:
            raise HTTPException(status_code=503, detail="Trading engine not available")
        performance_service = PerformanceService(engine.mt5_service)
        logger.info("PerformanceService initialized and linked with Unified Trading Engine's MT5 connection.")
    return performance_service

@router.get("/equity_curve", summary="Get account equity curve")
async def get_equity_curve(
    service: PerformanceService = Depends(get_performance_service)
):
    """
    Calculates and returns the equity curve based on trade history.
    """
    try:
        # Get current account state
        account_info = await service.get_account_info()
        current_equity = account_info.get("equity")
        
        # Get trade history
        deals = await service.get_trade_history(days=90) # Fetch more days for better curve
        if not deals:
            # If no history, return current equity as a single point
            return [{"time": datetime.now().isoformat(), "equity": current_equity}]

        # Create a DataFrame for easier manipulation
        df = pd.DataFrame(deals)
        df['time'] = pd.to_datetime(df['time'])
        df = df.sort_values('time', ascending=True)

        # Calculate equity at the start of the history period
        total_profit_in_period = df['profit'].sum()
        start_equity = current_equity - total_profit_in_period
        
        # Calculate cumulative profit and equity curve
        df['cumulative_profit'] = df['profit'].cumsum()
        df['equity'] = start_equity + df['cumulative_profit']
        
        # Format for response
        equity_curve = df[['time', 'equity']].to_dict('records')
        
        # Add the starting point
        start_point = {
            "time": df['time'].iloc[0] - pd.Timedelta(seconds=1),
            "equity": start_equity
        }
        
        # Return a list of dictionaries
        return [start_point] + equity_curve

    except Exception as e:
        logger.error(f"Error calculating equity curve: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to calculate equity curve")

@router.get("/performance_summary", response_model=Dict[str, Any])
async def get_performance_summary(
    service: PerformanceService = Depends(get_performance_service),
    refresh: bool = Query(False, description="Force refresh the cache")
):
    """
    Calculates and returns a summary of trading performance metrics.
    """
    try:
        history_deals = await service.get_trade_history()
        if not history_deals:
            return {
                "total_trades": 0,
                "net_profit": 0,
                "win_rate": 0,
                "loss_rate": 0,
                "profit_factor": 0,
                "average_profit": 0,
                "average_loss": 0,
                "risk_reward_ratio": 0,
                "largest_profit": 0,
                "largest_loss": 0,
            }

        df = pd.DataFrame(history_deals)
        
        # Ensure 'profit' is numeric
        df['profit'] = pd.to_numeric(df['profit'])

        total_trades = len(df)
        net_profit = df['profit'].sum()
        
        winning_trades = df[df['profit'] > 0]
        losing_trades = df[df['profit'] < 0]
        
        num_winning_trades = len(winning_trades)
        num_losing_trades = len(losing_trades)
        
        win_rate = (num_winning_trades / total_trades) * 100 if total_trades > 0 else 0
        loss_rate = (num_losing_trades / total_trades) * 100 if total_trades > 0 else 0
        
        gross_profit = winning_trades['profit'].sum()
        gross_loss = abs(losing_trades['profit'].sum())
        
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        average_profit = winning_trades['profit'].mean() if num_winning_trades > 0 else 0
        average_loss = abs(losing_trades['profit'].mean()) if num_losing_trades > 0 else 0
        
        risk_reward_ratio = average_profit / average_loss if average_loss > 0 else float('inf')

        largest_profit = winning_trades['profit'].max() if num_winning_trades > 0 else 0
        largest_loss = losing_trades['profit'].min() if num_losing_trades > 0 else 0

        return {
            "total_trades": total_trades,
            "net_profit": round(net_profit, 2),
            "win_rate": round(win_rate, 2),
            "loss_rate": round(loss_rate, 2),
            "profit_factor": round(profit_factor, 2) if profit_factor != float('inf') else 'inf',
            "average_profit": round(average_profit, 2),
            "average_loss": round(average_loss, 2),
            "risk_reward_ratio": round(risk_reward_ratio, 2) if risk_reward_ratio != float('inf') else 'inf',
            "largest_profit": round(largest_profit, 2),
            "largest_loss": round(largest_loss, 2),
        }
    except Exception as e:
        logger.error(f"Error calculating performance summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate performance metrics") 