from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import logging

from .service import PerformanceService, PerformanceMetrics, TradeAnalysis, EquityCurvePoint
from ...core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/performance", tags=["performance"])

# Global performance service instance
performance_service = PerformanceService()

@router.get("/metrics", response_model=Dict[str, Any])
async def get_performance_metrics(
    start_date: Optional[str] = Query(None, description="Start date in ISO format"),
    end_date: Optional[str] = Query(None, description="End date in ISO format"),
    refresh_cache: bool = Query(False, description="Force refresh cache")
):
    """Get comprehensive performance metrics"""
    try:
        # Parse dates if provided
        start_dt = None
        end_dt = None
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        metrics = await performance_service.get_performance_metrics(
            start_date=start_dt,
            end_date=end_dt,
            refresh_cache=refresh_cache
        )
        
        # Convert to dict for JSON response
        return {
            "total_return": metrics.total_return,
            "total_return_pct": metrics.total_return_pct,
            "sharpe_ratio": metrics.sharpe_ratio,
            "max_drawdown": metrics.max_drawdown,
            "max_drawdown_pct": metrics.max_drawdown_pct,
            "win_rate": metrics.win_rate,
            "profit_factor": metrics.profit_factor,
            "average_win": metrics.average_win,
            "average_loss": metrics.average_loss,
            "total_trades": metrics.total_trades,
            "winning_trades": metrics.winning_trades,
            "losing_trades": metrics.losing_trades,
            "largest_win": metrics.largest_win,
            "largest_loss": metrics.largest_loss,
            "consecutive_wins": metrics.consecutive_wins,
            "consecutive_losses": metrics.consecutive_losses,
            "calmar_ratio": metrics.calmar_ratio,
            "sortino_ratio": metrics.sortino_ratio,
            "recovery_factor": metrics.recovery_factor,
            "expectancy": metrics.expectancy,
            "kelly_criterion": metrics.kelly_criterion
        }
        
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/equity-curve")
async def get_equity_curve(
    start_date: Optional[str] = Query(None, description="Start date in ISO format"),
    end_date: Optional[str] = Query(None, description="End date in ISO format"),
    interval_minutes: int = Query(60, description="Data point interval in minutes")
):
    """Get equity curve data"""
    try:
        # Parse dates if provided
        start_dt = None
        end_dt = None
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        equity_curve = await performance_service.get_equity_curve(
            start_date=start_dt,
            end_date=end_dt,
            interval_minutes=interval_minutes
        )
        
        # Convert to list of dicts for JSON response
        return [
            {
                "timestamp": point.timestamp.isoformat(),
                "balance": point.balance,
                "equity": point.equity,
                "drawdown": point.drawdown,
                "drawdown_pct": point.drawdown_pct,
                "trade_count": point.trade_count,
                "cumulative_return": point.cumulative_return
            }
            for point in equity_curve
        ]
        
    except Exception as e:
        logger.error(f"Error getting equity curve: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trades")
async def get_trade_analysis(
    start_date: Optional[str] = Query(None, description="Start date in ISO format"),
    end_date: Optional[str] = Query(None, description="End date in ISO format"),
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    strategy: Optional[str] = Query(None, description="Filter by strategy"),
    limit: int = Query(100, description="Maximum number of trades to return"),
    offset: int = Query(0, description="Number of trades to skip")
):
    """Get detailed trade analysis"""
    try:
        # Parse dates if provided
        start_dt = None
        end_dt = None
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        trades = await performance_service.get_trade_analysis(
            start_date=start_dt,
            end_date=end_dt,
            symbol=symbol,
            strategy=strategy
        )
        
        # Apply pagination
        paginated_trades = trades[offset:offset + limit]
        
        # Convert to list of dicts for JSON response
        return [
            {
                "symbol": trade.symbol,
                "entry_time": trade.entry_time.isoformat(),
                "exit_time": trade.exit_time.isoformat() if trade.exit_time else None,
                "entry_price": trade.entry_price,
                "exit_price": trade.exit_price,
                "volume": trade.volume,
                "trade_type": trade.trade_type,
                "profit": trade.profit,
                "profit_pct": trade.profit_pct,
                "duration_minutes": trade.duration_minutes,
                "max_favorable_excursion": trade.max_favorable_excursion,
                "max_adverse_excursion": trade.max_adverse_excursion,
                "r_multiple": trade.r_multiple,
                "strategy": trade.strategy,
                "comment": trade.comment
            }
            for trade in paginated_trades
        ]
        
    except Exception as e:
        logger.error(f"Error getting trade analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/symbols")
async def get_symbol_performance(
    start_date: Optional[str] = Query(None, description="Start date in ISO format"),
    end_date: Optional[str] = Query(None, description="End date in ISO format")
):
    """Get performance breakdown by symbol"""
    try:
        # Parse dates if provided
        start_dt = None
        end_dt = None
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        symbol_performance = await performance_service.get_symbol_performance(
            start_date=start_dt,
            end_date=end_dt
        )
        
        return symbol_performance
        
    except Exception as e:
        logger.error(f"Error getting symbol performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/strategies")
async def get_strategy_performance(
    start_date: Optional[str] = Query(None, description="Start date in ISO format"),
    end_date: Optional[str] = Query(None, description="End date in ISO format")
):
    """Get performance breakdown by strategy"""
    try:
        # Parse dates if provided
        start_dt = None
        end_dt = None
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        strategy_performance = await performance_service.get_strategy_performance(
            start_date=start_dt,
            end_date=end_dt
        )
        
        return strategy_performance
        
    except Exception as e:
        logger.error(f"Error getting strategy performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monthly")
async def get_monthly_performance(
    year: Optional[int] = Query(None, description="Year for monthly breakdown")
):
    """Get monthly performance breakdown"""
    try:
        monthly_performance = await performance_service.get_monthly_performance(year=year)
        return monthly_performance
        
    except Exception as e:
        logger.error(f"Error getting monthly performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/risk-metrics")
async def get_risk_metrics(
    start_date: Optional[str] = Query(None, description="Start date in ISO format"),
    end_date: Optional[str] = Query(None, description="End date in ISO format")
):
    """Get risk-related metrics"""
    try:
        # Parse dates if provided
        start_dt = None
        end_dt = None
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        risk_metrics = await performance_service.get_risk_metrics(
            start_date=start_dt,
            end_date=end_dt
        )
        
        return risk_metrics
        
    except Exception as e:
        logger.error(f"Error getting risk metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/report")
async def export_performance_report(
    format: str = Query("json", description="Report format (json, detailed)"),
    start_date: Optional[str] = Query(None, description="Start date in ISO format"),
    end_date: Optional[str] = Query(None, description="End date in ISO format")
):
    """Export comprehensive performance report"""
    try:
        # Parse dates if provided
        start_dt = None
        end_dt = None
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        report = await performance_service.export_performance_report(
            format=format,
            start_date=start_dt,
            end_date=end_dt
        )
        
        return report
        
    except Exception as e:
        logger.error(f"Error exporting performance report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary")
async def get_performance_summary():
    """Get quick performance summary"""
    try:
        # Get last 30 days performance
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        metrics = await performance_service.get_performance_metrics(
            start_date=start_date,
            end_date=end_date
        )
        
        # Get recent trades
        recent_trades = await performance_service.get_trade_analysis(
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            "period": "Last 30 Days",
            "total_return": metrics.total_return,
            "total_return_pct": metrics.total_return_pct,
            "total_trades": metrics.total_trades,
            "win_rate": metrics.win_rate,
            "profit_factor": metrics.profit_factor,
            "max_drawdown_pct": metrics.max_drawdown_pct,
            "sharpe_ratio": metrics.sharpe_ratio,
            "recent_trades_count": len(recent_trades),
            "last_trade_time": recent_trades[-1].entry_time.isoformat() if recent_trades else None
        }
        
    except Exception as e:
        logger.error(f"Error getting performance summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def performance_health_check():
    """Health check for performance service"""
    try:
        # Test basic functionality
        metrics = await performance_service.get_performance_metrics()
        
        return {
            "status": "healthy",
            "service": "performance",
            "total_trades": metrics.total_trades,
            "cache_status": "active" if performance_service.performance_cache else "empty",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Performance service health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "performance",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        } 