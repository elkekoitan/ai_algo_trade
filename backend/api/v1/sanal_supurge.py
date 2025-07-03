"""
Sanal Süpürge (Virtual Sweeper) API endpoints
Grid trading strategy with automatic Fibonacci calculations
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from ...modules.strategy_whisperer.sanal_supurge_engine import SanalSupurgeEngine
from ...modules.mt5_integration.service import MT5Service
from ...core.event_bus import event_bus
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sanal-supurge", tags=["sanal-supurge"])

# Request/Response Models
class GridSettings(BaseModel):
    symbol: str = Field(..., description="Trading symbol (e.g., XAUUSD)")
    timeframe: str = Field(default="H1", description="Timeframe for Fibonacci calculation")
    lookback_days: int = Field(default=30, description="Days to look back for swing points")
    grid_levels: int = Field(default=14, description="Number of grid levels")
    initial_lot: float = Field(default=0.01, description="Initial lot size")
    lot_progression: str = Field(default="martingale", description="Lot progression model")
    lot_multiplier: float = Field(default=2.0, description="Lot size multiplier")
    tp_points: int = Field(default=1000, description="Take profit in points")
    sl_points: int = Field(default=10000, description="Stop loss in points")
    max_lot_per_order: float = Field(default=10.0, description="Maximum lot per order")
    allow_buy: bool = Field(default=True, description="Allow buy orders")
    allow_sell: bool = Field(default=True, description="Allow sell orders")
    use_time_filter: bool = Field(default=False, description="Use time filter")
    risk_percent: float = Field(default=5.0, description="Risk percentage of balance")

class GridAnalysis(BaseModel):
    fib_levels: Dict[str, float]
    grid_levels: List[Dict]
    risk_analysis: Dict
    optimized_settings: Dict
    ea_settings: Optional[str] = None

# Singleton engine instance
sanal_supurge_engine = SanalSupurgeEngine()
mt5_service = MT5Service()

@router.post("/calculate-fibonacci", response_model=Dict[str, float])
async def calculate_fibonacci_levels(
    symbol: str,
    timeframe: str = "H1",
    lookback_days: int = 30
):
    """Calculate Fibonacci retracement levels for the symbol"""
    try:
        levels = sanal_supurge_engine.calculate_fibonacci_levels(
            symbol, timeframe, lookback_days
        )
        
        if not levels:
            raise HTTPException(status_code=400, detail="Could not calculate Fibonacci levels")
        
        # Emit event
        await event_bus.emit("sanal_supurge_fib_calculated", {
            "symbol": symbol,
            "timeframe": timeframe,
            "levels": levels,
            "timestamp": datetime.now()
        })
        
        return levels
        
    except Exception as e:
        logger.error(f"Error calculating Fibonacci: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-grid", response_model=GridAnalysis)
async def analyze_grid_configuration(settings: GridSettings):
    """Analyze grid configuration with risk assessment"""
    try:
        # Get current account info
        account_info = mt5_service.get_account_info()
        if not account_info:
            raise HTTPException(status_code=400, detail="Could not get account info")
        
        # Get symbol info
        symbol_info = mt5_service.get_symbol_info(settings.symbol)
        if not symbol_info:
            raise HTTPException(status_code=400, detail=f"Invalid symbol: {settings.symbol}")
        
        # Get current price
        current_price = mt5_service.get_current_price(settings.symbol)
        settings_dict = settings.dict()
        settings_dict['current_price'] = current_price
        settings_dict['tick_size'] = symbol_info['tick_size']
        
        # Calculate Fibonacci levels
        fib_levels = sanal_supurge_engine.calculate_fibonacci_levels(
            settings.symbol, settings.timeframe, settings.lookback_days
        )
        
        # Calculate grid levels
        grid_levels = sanal_supurge_engine.calculate_grid_levels(
            settings.symbol, settings_dict
        )
        
        # Analyze risk
        risk_analysis = sanal_supurge_engine.analyze_risk(
            grid_levels,
            account_info['balance'],
            account_info['leverage'],
            symbol_info
        )
        
        # Get volatility for optimization
        volatility = mt5_service.calculate_atr(settings.symbol, settings.timeframe, 14)
        
        # Optimize settings
        optimized = sanal_supurge_engine.optimize_grid_for_volatility(
            settings.symbol, volatility, settings_dict
        )
        
        # Generate EA settings if requested
        ea_settings = sanal_supurge_engine.generate_ea_settings(grid_levels, settings_dict)
        
        return GridAnalysis(
            fib_levels=fib_levels,
            grid_levels=grid_levels,
            risk_analysis=risk_analysis,
            optimized_settings=optimized,
            ea_settings=ea_settings
        )
        
    except Exception as e:
        logger.error(f"Error analyzing grid: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimize-for-volatility")
async def optimize_grid_for_volatility(
    symbol: str,
    base_settings: GridSettings
):
    """Optimize grid settings based on current volatility"""
    try:
        # Calculate current ATR
        atr = mt5_service.calculate_atr(symbol, base_settings.timeframe, 14)
        
        # Optimize settings
        optimized = sanal_supurge_engine.optimize_grid_for_volatility(
            symbol, atr, base_settings.dict()
        )
        
        # Emit event
        await event_bus.emit("sanal_supurge_optimized", {
            "symbol": symbol,
            "atr": atr,
            "original_settings": base_settings.dict(),
            "optimized_settings": optimized,
            "timestamp": datetime.now()
        })
        
        return {
            "atr": atr,
            "optimized_settings": optimized,
            "changes": {
                "lot_multiplier": optimized.get('lot_multiplier', base_settings.lot_multiplier),
                "grid_levels": optimized.get('grid_levels', base_settings.grid_levels),
                "base_distance": optimized.get('base_grid_distance', 0)
            }
        }
        
    except Exception as e:
        logger.error(f"Error optimizing grid: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/active-grids")
async def get_active_grid_strategies():
    """Get all active grid trading strategies"""
    try:
        # This would typically query a database
        # For now, return positions with grid comments
        positions = mt5_service.get_positions()
        
        grid_positions = []
        for pos in positions:
            if pos.get('comment', '').startswith('SanalSupurge_'):
                grid_positions.append({
                    'ticket': pos['ticket'],
                    'symbol': pos['symbol'],
                    'volume': pos['volume'],
                    'profit': pos['profit'],
                    'comment': pos['comment'],
                    'open_time': pos['time']
                })
        
        return {
            "active_grids": len(set(p['symbol'] for p in grid_positions)),
            "total_positions": len(grid_positions),
            "positions": grid_positions
        }
        
    except Exception as e:
        logger.error(f"Error getting active grids: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/deploy-to-mt5")
async def deploy_grid_to_mt5(
    settings: GridSettings,
    dry_run: bool = True
):
    """Deploy grid strategy to MT5 (create EA settings file)"""
    try:
        # Analyze grid first
        analysis = await analyze_grid_configuration(settings)
        
        if analysis.risk_analysis['risk_level'] == 'High' and not dry_run:
            return {
                "status": "warning",
                "message": "High risk detected. Please review settings.",
                "risk_analysis": analysis.risk_analysis
            }
        
        # Generate filename
        filename = f"SanalSupurge_{settings.symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.set"
        
        # In production, this would save the file to MT5 Experts/Files directory
        # For now, return the content
        result = {
            "status": "success" if dry_run else "deployed",
            "filename": filename,
            "risk_level": analysis.risk_analysis['risk_level'],
            "grid_levels": len(analysis.grid_levels),
            "total_lots": analysis.risk_analysis['total_lots'],
            "margin_usage": f"{analysis.risk_analysis['margin_usage_percent']:.1f}%",
            "max_drawdown": f"{analysis.risk_analysis['max_drawdown_percent']:.1f}%",
            "ea_settings": analysis.ea_settings if dry_run else None
        }
        
        # Emit deployment event
        await event_bus.emit("sanal_supurge_deployed", {
            "symbol": settings.symbol,
            "settings": settings.dict(),
            "risk_analysis": analysis.risk_analysis,
            "dry_run": dry_run,
            "timestamp": datetime.now()
        })
        
        return result
        
    except Exception as e:
        logger.error(f"Error deploying grid: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance-stats/{symbol}")
async def get_grid_performance_stats(symbol: str):
    """Get performance statistics for a grid strategy"""
    try:
        # Get historical trades for the symbol
        history = mt5_service.get_deals_history(days=30)
        
        grid_trades = []
        for deal in history:
            if (deal.get('symbol') == symbol and 
                deal.get('comment', '').startswith('SanalSupurge_')):
                grid_trades.append(deal)
        
        if not grid_trades:
            return {
                "symbol": symbol,
                "total_trades": 0,
                "message": "No grid trades found for this symbol"
            }
        
        # Calculate statistics
        total_profit = sum(t.get('profit', 0) for t in grid_trades)
        winning_trades = [t for t in grid_trades if t.get('profit', 0) > 0]
        losing_trades = [t for t in grid_trades if t.get('profit', 0) < 0]
        
        stats = {
            "symbol": symbol,
            "total_trades": len(grid_trades),
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate": (len(winning_trades) / len(grid_trades) * 100) if grid_trades else 0,
            "total_profit": total_profit,
            "average_profit": total_profit / len(grid_trades) if grid_trades else 0,
            "largest_win": max([t['profit'] for t in winning_trades]) if winning_trades else 0,
            "largest_loss": min([t['profit'] for t in losing_trades]) if losing_trades else 0,
            "profit_factor": abs(sum(t['profit'] for t in winning_trades) / sum(t['profit'] for t in losing_trades)) if losing_trades and sum(t['profit'] for t in losing_trades) != 0 else 0
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting performance stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/stop-grid/{symbol}")
async def stop_grid_strategy(symbol: str):
    """Stop grid strategy for a symbol (close all related positions)"""
    try:
        positions = mt5_service.get_positions()
        closed_count = 0
        total_profit = 0
        
        for pos in positions:
            if (pos.get('symbol') == symbol and 
                pos.get('comment', '').startswith('SanalSupurge_')):
                # Close position
                result = mt5_service.close_position(pos['ticket'])
                if result:
                    closed_count += 1
                    total_profit += pos.get('profit', 0)
        
        # Emit stop event
        await event_bus.emit("sanal_supurge_stopped", {
            "symbol": symbol,
            "positions_closed": closed_count,
            "total_profit": total_profit,
            "timestamp": datetime.now()
        })
        
        return {
            "status": "success",
            "symbol": symbol,
            "positions_closed": closed_count,
            "total_profit": total_profit
        }
        
    except Exception as e:
        logger.error(f"Error stopping grid: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 