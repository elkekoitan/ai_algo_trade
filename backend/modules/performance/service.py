"""
Performance tracking and analysis service for the trading platform.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
from dataclasses import dataclass, asdict
import json
from pathlib import Path

from backend.core.logger import setup_logger
from backend.modules.mt5_integration.service import MT5Service

logger = setup_logger("performance_service")

@dataclass
class PerformanceMetrics:
    """Performance metrics data class"""
    total_return: float
    total_return_pct: float
    sharpe_ratio: float
    max_drawdown: float
    max_drawdown_pct: float
    win_rate: float
    profit_factor: float
    average_win: float
    average_loss: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    largest_win: float
    largest_loss: float
    consecutive_wins: int
    consecutive_losses: int
    calmar_ratio: float
    sortino_ratio: float
    recovery_factor: float
    expectancy: float
    kelly_criterion: float

@dataclass
class TradeAnalysis:
    """Individual trade analysis"""
    symbol: str
    entry_time: datetime
    exit_time: Optional[datetime]
    entry_price: float
    exit_price: Optional[float]
    volume: float
    trade_type: str  # 'buy' or 'sell'
    profit: float
    profit_pct: float
    duration_minutes: Optional[float]
    max_favorable_excursion: float
    max_adverse_excursion: float
    r_multiple: float
    strategy: str
    comment: str

@dataclass
class EquityCurvePoint:
    """Equity curve data point"""
    timestamp: datetime
    balance: float
    equity: float
    drawdown: float
    drawdown_pct: float
    trade_count: int
    cumulative_return: float

class PerformanceService:
    """Advanced performance monitoring and analytics service"""
    
    def __init__(self, mt5_service: MT5Service):
        self.mt5_service = mt5_service
        self.trades_cache: List[TradeAnalysis] = []
        self.equity_curve: List[EquityCurvePoint] = []
        self.performance_cache: Optional[PerformanceMetrics] = None
        self.cache_timestamp: Optional[datetime] = None
        self.cache_duration = timedelta(minutes=5)  # Cache for 5 minutes
        
        logger.info("Performance service initialized")
    
    async def get_performance_metrics(
        self, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        refresh_cache: bool = False
    ) -> PerformanceMetrics:
        """Get comprehensive performance metrics"""
        
        # Check cache
        if (not refresh_cache and 
            self.performance_cache and 
            self.cache_timestamp and 
            datetime.utcnow() - self.cache_timestamp < self.cache_duration):
            return self.performance_cache
        
        try:
            # Get trading history
            trades = await self._get_trading_history(start_date, end_date)
            
            if not trades:
                return self._get_empty_metrics()
            
            # Calculate metrics
            metrics = await self._calculate_performance_metrics(trades)
            
            # Update cache
            self.performance_cache = metrics
            self.cache_timestamp = datetime.utcnow()
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
            return self._get_empty_metrics()
    
    async def get_equity_curve(
        self, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        interval_minutes: int = 60
    ) -> List[EquityCurvePoint]:
        """Get equity curve data"""
        
        try:
            # Get account history
            history = await self.mt5_service.get_account_history(start_date, end_date)
            if not history:
                return []
            
            # Get trading history
            trades = await self._get_trading_history(start_date, end_date)
            
            # Build equity curve
            equity_curve = await self._build_equity_curve(history, trades, interval_minutes)
            
            return equity_curve
            
        except Exception as e:
            logger.error(f"Error building equity curve: {e}")
            return []
    
    async def get_trade_analysis(
        self, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        symbol: Optional[str] = None,
        strategy: Optional[str] = None
    ) -> List[TradeAnalysis]:
        """Get detailed trade analysis"""
        
        try:
            trades = await self._get_trading_history(start_date, end_date)
            
            # Filter by symbol if specified
            if symbol:
                trades = [t for t in trades if t.symbol == symbol]
            
            # Filter by strategy if specified
            if strategy:
                trades = [t for t in trades if strategy.lower() in t.strategy.lower()]
            
            return trades
            
        except Exception as e:
            logger.error(f"Error getting trade analysis: {e}")
            return []
    
    async def get_symbol_performance(
        self, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Dict]:
        """Get performance breakdown by symbol"""
        
        try:
            trades = await self._get_trading_history(start_date, end_date)
            
            symbol_stats = {}
            
            for trade in trades:
                if trade.symbol not in symbol_stats:
                    symbol_stats[trade.symbol] = {
                        'trades': [],
                        'total_profit': 0,
                        'total_trades': 0,
                        'winning_trades': 0,
                        'losing_trades': 0
                    }
                
                symbol_stats[trade.symbol]['trades'].append(trade)
                symbol_stats[trade.symbol]['total_profit'] += trade.profit
                symbol_stats[trade.symbol]['total_trades'] += 1
                
                if trade.profit > 0:
                    symbol_stats[trade.symbol]['winning_trades'] += 1
                else:
                    symbol_stats[trade.symbol]['losing_trades'] += 1
            
            # Calculate metrics for each symbol
            result = {}
            for symbol, stats in symbol_stats.items():
                trades_list = stats['trades']
                
                result[symbol] = {
                    'total_profit': stats['total_profit'],
                    'total_trades': stats['total_trades'],
                    'winning_trades': stats['winning_trades'],
                    'losing_trades': stats['losing_trades'],
                    'win_rate': (stats['winning_trades'] / stats['total_trades'] * 100) if stats['total_trades'] > 0 else 0,
                    'average_profit': stats['total_profit'] / stats['total_trades'] if stats['total_trades'] > 0 else 0,
                    'largest_win': max([t.profit for t in trades_list if t.profit > 0], default=0),
                    'largest_loss': min([t.profit for t in trades_list if t.profit < 0], default=0),
                    'profit_factor': self._calculate_profit_factor([t.profit for t in trades_list])
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating symbol performance: {e}")
            return {}
    
    async def get_strategy_performance(
        self, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Dict]:
        """Get performance breakdown by strategy"""
        
        try:
            trades = await self._get_trading_history(start_date, end_date)
            
            strategy_stats = {}
            
            for trade in trades:
                strategy = trade.strategy or "Unknown"
                
                if strategy not in strategy_stats:
                    strategy_stats[strategy] = {
                        'trades': [],
                        'total_profit': 0,
                        'total_trades': 0,
                        'winning_trades': 0,
                        'losing_trades': 0
                    }
                
                strategy_stats[strategy]['trades'].append(trade)
                strategy_stats[strategy]['total_profit'] += trade.profit
                strategy_stats[strategy]['total_trades'] += 1
                
                if trade.profit > 0:
                    strategy_stats[strategy]['winning_trades'] += 1
                else:
                    strategy_stats[strategy]['losing_trades'] += 1
            
            # Calculate metrics for each strategy
            result = {}
            for strategy, stats in strategy_stats.items():
                trades_list = stats['trades']
                
                result[strategy] = {
                    'total_profit': stats['total_profit'],
                    'total_trades': stats['total_trades'],
                    'winning_trades': stats['winning_trades'],
                    'losing_trades': stats['losing_trades'],
                    'win_rate': (stats['winning_trades'] / stats['total_trades'] * 100) if stats['total_trades'] > 0 else 0,
                    'average_profit': stats['total_profit'] / stats['total_trades'] if stats['total_trades'] > 0 else 0,
                    'largest_win': max([t.profit for t in trades_list if t.profit > 0], default=0),
                    'largest_loss': min([t.profit for t in trades_list if t.profit < 0], default=0),
                    'profit_factor': self._calculate_profit_factor([t.profit for t in trades_list]),
                    'average_duration': np.mean([t.duration_minutes for t in trades_list if t.duration_minutes]) if trades_list else 0
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating strategy performance: {e}")
            return {}
    
    async def get_monthly_performance(
        self, 
        year: Optional[int] = None
    ) -> Dict[str, Dict]:
        """Get monthly performance breakdown"""
        
        try:
            if not year:
                year = datetime.utcnow().year
            
            start_date = datetime(year, 1, 1)
            end_date = datetime(year, 12, 31)
            
            trades = await self._get_trading_history(start_date, end_date)
            
            monthly_stats = {}
            
            for month in range(1, 13):
                month_name = datetime(year, month, 1).strftime('%B')
                monthly_stats[month_name] = {
                    'trades': [],
                    'total_profit': 0,
                    'total_trades': 0,
                    'winning_trades': 0,
                    'losing_trades': 0
                }
            
            for trade in trades:
                month_name = trade.entry_time.strftime('%B')
                
                monthly_stats[month_name]['trades'].append(trade)
                monthly_stats[month_name]['total_profit'] += trade.profit
                monthly_stats[month_name]['total_trades'] += 1
                
                if trade.profit > 0:
                    monthly_stats[month_name]['winning_trades'] += 1
                else:
                    monthly_stats[month_name]['losing_trades'] += 1
            
            # Calculate metrics for each month
            result = {}
            for month, stats in monthly_stats.items():
                result[month] = {
                    'total_profit': stats['total_profit'],
                    'total_trades': stats['total_trades'],
                    'winning_trades': stats['winning_trades'],
                    'losing_trades': stats['losing_trades'],
                    'win_rate': (stats['winning_trades'] / stats['total_trades'] * 100) if stats['total_trades'] > 0 else 0,
                    'average_profit': stats['total_profit'] / stats['total_trades'] if stats['total_trades'] > 0 else 0
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating monthly performance: {e}")
            return {}
    
    async def get_risk_metrics(
        self, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get risk-related metrics"""
        
        try:
            trades = await self._get_trading_history(start_date, end_date)
            equity_curve = await self.get_equity_curve(start_date, end_date)
            
            if not trades or not equity_curve:
                return {}
            
            # Calculate various risk metrics
            profits = [t.profit for t in trades]
            returns = [point.cumulative_return for point in equity_curve]
            drawdowns = [point.drawdown_pct for point in equity_curve]
            
            risk_metrics = {
                'value_at_risk_95': np.percentile(profits, 5) if profits else 0,
                'value_at_risk_99': np.percentile(profits, 1) if profits else 0,
                'conditional_var_95': np.mean([p for p in profits if p <= np.percentile(profits, 5)]) if profits else 0,
                'volatility': np.std(returns) if returns else 0,
                'downside_deviation': self._calculate_downside_deviation(returns),
                'max_consecutive_losses': self._calculate_max_consecutive_losses(profits),
                'average_drawdown': np.mean(drawdowns) if drawdowns else 0,
                'max_drawdown_duration': self._calculate_max_drawdown_duration(equity_curve),
                'recovery_time': self._calculate_recovery_time(equity_curve),
                'tail_ratio': self._calculate_tail_ratio(profits),
                'gain_to_pain_ratio': self._calculate_gain_to_pain_ratio(returns)
            }
            
            return risk_metrics
            
        except Exception as e:
            logger.error(f"Error calculating risk metrics: {e}")
            return {}
    
    async def _get_trading_history(
        self, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[TradeAnalysis]:
        """Get trading history and convert to TradeAnalysis objects"""
        
        try:
            # Get deals from MT5
            deals = await self.mt5_service.get_deals_history(start_date, end_date)
            if not deals:
                return []
            
            # Group deals by position ticket to create complete trades
            positions = {}
            
            for deal in deals:
                ticket = deal.get('position', deal.get('ticket'))
                
                if ticket not in positions:
                    positions[ticket] = {
                        'entry_deal': None,
                        'exit_deal': None,
                        'symbol': deal.get('symbol'),
                        'volume': deal.get('volume', 0)
                    }
                
                deal_type = deal.get('type')
                if deal_type in [0, 1]:  # Buy or Sell entry
                    positions[ticket]['entry_deal'] = deal
                elif deal_type in [2, 3]:  # Buy or Sell exit
                    positions[ticket]['exit_deal'] = deal
            
            # Convert to TradeAnalysis objects
            trades = []
            
            for ticket, position in positions.items():
                entry_deal = position['entry_deal']
                exit_deal = position['exit_deal']
                
                if not entry_deal:
                    continue
                
                # Extract strategy from comment
                comment = entry_deal.get('comment', '')
                strategy = self._extract_strategy_from_comment(comment)
                
                # Calculate trade metrics
                entry_time = datetime.fromtimestamp(entry_deal.get('time', 0))
                exit_time = datetime.fromtimestamp(exit_deal.get('time', 0)) if exit_deal else None
                
                entry_price = entry_deal.get('price', 0)
                exit_price = exit_deal.get('price', 0) if exit_deal else None
                
                profit = exit_deal.get('profit', 0) if exit_deal else 0
                
                # Calculate duration
                duration_minutes = None
                if exit_time:
                    duration = exit_time - entry_time
                    duration_minutes = duration.total_seconds() / 60
                
                # Calculate profit percentage (simplified)
                profit_pct = (profit / (entry_price * position['volume'] * 100000)) * 100 if entry_price > 0 else 0
                
                # Calculate R-multiple (simplified)
                r_multiple = profit / 100 if profit != 0 else 0  # Simplified calculation
                
                trade = TradeAnalysis(
                    symbol=position['symbol'],
                    entry_time=entry_time,
                    exit_time=exit_time,
                    entry_price=entry_price,
                    exit_price=exit_price,
                    volume=position['volume'],
                    trade_type='buy' if entry_deal.get('type') == 0 else 'sell',
                    profit=profit,
                    profit_pct=profit_pct,
                    duration_minutes=duration_minutes,
                    max_favorable_excursion=0,  # Would need tick data to calculate
                    max_adverse_excursion=0,    # Would need tick data to calculate
                    r_multiple=r_multiple,
                    strategy=strategy,
                    comment=comment
                )
                
                trades.append(trade)
            
            # Sort by entry time
            trades.sort(key=lambda x: x.entry_time)
            
            return trades
            
        except Exception as e:
            logger.error(f"Error getting trading history: {e}")
            return []
    
    async def _calculate_performance_metrics(self, trades: List[TradeAnalysis]) -> PerformanceMetrics:
        """Calculate comprehensive performance metrics"""
        
        try:
            if not trades:
                return self._get_empty_metrics()
            
            # Basic calculations
            profits = [t.profit for t in trades]
            total_return = sum(profits)
            
            winning_trades = [t for t in trades if t.profit > 0]
            losing_trades = [t for t in trades if t.profit < 0]
            
            win_rate = (len(winning_trades) / len(trades)) * 100
            
            # Calculate returns for ratio calculations
            returns = []
            cumulative_balance = 10000  # Starting balance assumption
            
            for trade in trades:
                old_balance = cumulative_balance
                cumulative_balance += trade.profit
                if old_balance > 0:
                    returns.append(trade.profit / old_balance)
            
            total_return_pct = ((cumulative_balance - 10000) / 10000) * 100
            
            # Advanced metrics
            sharpe_ratio = self._calculate_sharpe_ratio(returns)
            max_drawdown, max_drawdown_pct = self._calculate_max_drawdown(trades)
            
            profit_factor = self._calculate_profit_factor(profits)
            
            average_win = np.mean([t.profit for t in winning_trades]) if winning_trades else 0
            average_loss = np.mean([t.profit for t in losing_trades]) if losing_trades else 0
            
            largest_win = max(profits) if profits else 0
            largest_loss = min(profits) if profits else 0
            
            consecutive_wins = self._calculate_max_consecutive_wins(profits)
            consecutive_losses = self._calculate_max_consecutive_losses(profits)
            
            calmar_ratio = self._calculate_calmar_ratio(total_return_pct, max_drawdown_pct)
            sortino_ratio = self._calculate_sortino_ratio(returns)
            recovery_factor = total_return / abs(max_drawdown) if max_drawdown != 0 else 0
            
            expectancy = self._calculate_expectancy(winning_trades, losing_trades)
            kelly_criterion = self._calculate_kelly_criterion(winning_trades, losing_trades)
            
            return PerformanceMetrics(
                total_return=total_return,
                total_return_pct=total_return_pct,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                max_drawdown_pct=max_drawdown_pct,
                win_rate=win_rate,
                profit_factor=profit_factor,
                average_win=average_win,
                average_loss=average_loss,
                total_trades=len(trades),
                winning_trades=len(winning_trades),
                losing_trades=len(losing_trades),
                largest_win=largest_win,
                largest_loss=largest_loss,
                consecutive_wins=consecutive_wins,
                consecutive_losses=consecutive_losses,
                calmar_ratio=calmar_ratio,
                sortino_ratio=sortino_ratio,
                recovery_factor=recovery_factor,
                expectancy=expectancy,
                kelly_criterion=kelly_criterion
            )
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
            return self._get_empty_metrics()
    
    async def _build_equity_curve(
        self, 
        history: List[Dict], 
        trades: List[TradeAnalysis], 
        interval_minutes: int
    ) -> List[EquityCurvePoint]:
        """Build equity curve from account history and trades"""
        
        try:
            equity_points = []
            
            if not history:
                return equity_points
            
            # Sort history by time
            history.sort(key=lambda x: x.get('time', 0))
            
            # Calculate equity curve points
            peak_equity = 0
            trade_count = 0
            
            for record in history:
                timestamp = datetime.fromtimestamp(record.get('time', 0))
                balance = record.get('balance', 0)
                equity = record.get('equity', balance)
                
                # Update peak
                if equity > peak_equity:
                    peak_equity = equity
                
                # Calculate drawdown
                drawdown = peak_equity - equity
                drawdown_pct = (drawdown / peak_equity * 100) if peak_equity > 0 else 0
                
                # Count trades up to this point
                trade_count = len([t for t in trades if t.entry_time <= timestamp])
                
                # Calculate cumulative return
                initial_balance = history[0].get('balance', 10000) if history else 10000
                cumulative_return = ((equity - initial_balance) / initial_balance * 100) if initial_balance > 0 else 0
                
                point = EquityCurvePoint(
                    timestamp=timestamp,
                    balance=balance,
                    equity=equity,
                    drawdown=drawdown,
                    drawdown_pct=drawdown_pct,
                    trade_count=trade_count,
                    cumulative_return=cumulative_return
                )
                
                equity_points.append(point)
            
            return equity_points
            
        except Exception as e:
            logger.error(f"Error building equity curve: {e}")
            return []
    
    # Helper calculation methods
    
    def _calculate_sharpe_ratio(self, returns: List[float], risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio"""
        if not returns or len(returns) < 2:
            return 0
        
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        
        if std_return == 0:
            return 0
        
        # Annualize the ratio (assuming daily returns)
        sharpe = (mean_return - risk_free_rate / 252) / std_return * np.sqrt(252)
        return sharpe
    
    def _calculate_max_drawdown(self, trades: List[TradeAnalysis]) -> Tuple[float, float]:
        """Calculate maximum drawdown"""
        if not trades:
            return 0, 0
        
        cumulative_balance = 10000  # Starting balance
        peak_balance = cumulative_balance
        max_dd = 0
        max_dd_pct = 0
        
        for trade in trades:
            cumulative_balance += trade.profit
            
            if cumulative_balance > peak_balance:
                peak_balance = cumulative_balance
            
            drawdown = peak_balance - cumulative_balance
            drawdown_pct = (drawdown / peak_balance * 100) if peak_balance > 0 else 0
            
            if drawdown > max_dd:
                max_dd = drawdown
                max_dd_pct = drawdown_pct
        
        return max_dd, max_dd_pct
    
    def _calculate_profit_factor(self, profits: List[float]) -> float:
        """Calculate profit factor"""
        if not profits:
            return 0
        
        gross_profit = sum([p for p in profits if p > 0])
        gross_loss = abs(sum([p for p in profits if p < 0]))
        
        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0
        
        return gross_profit / gross_loss
    
    def _calculate_max_consecutive_wins(self, profits: List[float]) -> int:
        """Calculate maximum consecutive wins"""
        if not profits:
            return 0
        
        max_consecutive = 0
        current_consecutive = 0
        
        for profit in profits:
            if profit > 0:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
        
        return max_consecutive
    
    def _calculate_max_consecutive_losses(self, profits: List[float]) -> int:
        """Calculate maximum consecutive losses"""
        if not profits:
            return 0
        
        max_consecutive = 0
        current_consecutive = 0
        
        for profit in profits:
            if profit < 0:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
        
        return max_consecutive
    
    def _calculate_calmar_ratio(self, annual_return: float, max_drawdown_pct: float) -> float:
        """Calculate Calmar ratio"""
        if max_drawdown_pct == 0:
            return 0
        return annual_return / max_drawdown_pct
    
    def _calculate_sortino_ratio(self, returns: List[float], target_return: float = 0) -> float:
        """Calculate Sortino ratio"""
        if not returns:
            return 0
        
        mean_return = np.mean(returns)
        downside_returns = [r for r in returns if r < target_return]
        
        if not downside_returns:
            return float('inf') if mean_return > target_return else 0
        
        downside_deviation = np.std(downside_returns)
        
        if downside_deviation == 0:
            return 0
        
        return (mean_return - target_return) / downside_deviation
    
    def _calculate_expectancy(self, winning_trades: List[TradeAnalysis], losing_trades: List[TradeAnalysis]) -> float:
        """Calculate expectancy"""
        total_trades = len(winning_trades) + len(losing_trades)
        
        if total_trades == 0:
            return 0
        
        win_rate = len(winning_trades) / total_trades
        loss_rate = len(losing_trades) / total_trades
        
        avg_win = np.mean([t.profit for t in winning_trades]) if winning_trades else 0
        avg_loss = abs(np.mean([t.profit for t in losing_trades])) if losing_trades else 0
        
        expectancy = (win_rate * avg_win) - (loss_rate * avg_loss)
        return expectancy
    
    def _calculate_kelly_criterion(self, winning_trades: List[TradeAnalysis], losing_trades: List[TradeAnalysis]) -> float:
        """Calculate Kelly criterion for optimal position sizing"""
        total_trades = len(winning_trades) + len(losing_trades)
        
        if total_trades == 0 or not losing_trades:
            return 0
        
        win_rate = len(winning_trades) / total_trades
        avg_win = np.mean([t.profit for t in winning_trades]) if winning_trades else 0
        avg_loss = abs(np.mean([t.profit for t in losing_trades])) if losing_trades else 1
        
        if avg_loss == 0:
            return 0
        
        win_loss_ratio = avg_win / avg_loss
        kelly = win_rate - ((1 - win_rate) / win_loss_ratio)
        
        return max(0, min(kelly, 0.25))  # Cap at 25% for safety
    
    def _calculate_downside_deviation(self, returns: List[float]) -> float:
        """Calculate downside deviation"""
        if not returns:
            return 0
        
        negative_returns = [r for r in returns if r < 0]
        return np.std(negative_returns) if negative_returns else 0
    
    def _calculate_max_drawdown_duration(self, equity_curve: List[EquityCurvePoint]) -> int:
        """Calculate maximum drawdown duration in periods"""
        if not equity_curve:
            return 0
        
        max_duration = 0
        current_duration = 0
        in_drawdown = False
        
        for point in equity_curve:
            if point.drawdown > 0:
                if not in_drawdown:
                    in_drawdown = True
                    current_duration = 1
                else:
                    current_duration += 1
                max_duration = max(max_duration, current_duration)
            else:
                in_drawdown = False
                current_duration = 0
        
        return max_duration
    
    def _calculate_recovery_time(self, equity_curve: List[EquityCurvePoint]) -> int:
        """Calculate average recovery time from drawdowns"""
        if not equity_curve:
            return 0
        
        recovery_times = []
        drawdown_start = None
        
        for i, point in enumerate(equity_curve):
            if point.drawdown > 0 and drawdown_start is None:
                drawdown_start = i
            elif point.drawdown == 0 and drawdown_start is not None:
                recovery_time = i - drawdown_start
                recovery_times.append(recovery_time)
                drawdown_start = None
        
        return int(np.mean(recovery_times)) if recovery_times else 0
    
    def _calculate_tail_ratio(self, profits: List[float]) -> float:
        """Calculate tail ratio (95th percentile / 5th percentile)"""
        if not profits:
            return 0
        
        p95 = np.percentile(profits, 95)
        p5 = np.percentile(profits, 5)
        
        if p5 == 0:
            return 0
        
        return abs(p95 / p5)
    
    def _calculate_gain_to_pain_ratio(self, returns: List[float]) -> float:
        """Calculate gain to pain ratio"""
        if not returns:
            return 0
        
        total_return = sum(returns)
        pain = sum([abs(r) for r in returns if r < 0])
        
        if pain == 0:
            return float('inf') if total_return > 0 else 0
        
        return total_return / pain
    
    def _extract_strategy_from_comment(self, comment: str) -> str:
        """Extract strategy name from trade comment"""
        if not comment:
            return "Unknown"
        
        # Look for common strategy patterns
        if "ICT" in comment.upper():
            return "ICT Strategy"
        elif "AUTO" in comment.upper():
            return "Auto Trader"
        elif "SCALP" in comment.upper():
            return "Scalping"
        elif "SWING" in comment.upper():
            return "Swing Trading"
        else:
            return "Manual"
    
    def _get_empty_metrics(self) -> PerformanceMetrics:
        """Return empty performance metrics"""
        return PerformanceMetrics(
            total_return=0,
            total_return_pct=0,
            sharpe_ratio=0,
            max_drawdown=0,
            max_drawdown_pct=0,
            win_rate=0,
            profit_factor=0,
            average_win=0,
            average_loss=0,
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            largest_win=0,
            largest_loss=0,
            consecutive_wins=0,
            consecutive_losses=0,
            calmar_ratio=0,
            sortino_ratio=0,
            recovery_factor=0,
            expectancy=0,
            kelly_criterion=0
        )
    
    async def export_performance_report(
        self, 
        format: str = "json",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Export comprehensive performance report"""
        
        try:
            # Get all performance data
            metrics = await self.get_performance_metrics(start_date, end_date)
            trades = await self.get_trade_analysis(start_date, end_date)
            equity_curve = await self.get_equity_curve(start_date, end_date)
            symbol_performance = await self.get_symbol_performance(start_date, end_date)
            strategy_performance = await self.get_strategy_performance(start_date, end_date)
            risk_metrics = await self.get_risk_metrics(start_date, end_date)
            
            report = {
                "report_generated": datetime.utcnow().isoformat(),
                "period": {
                    "start_date": start_date.isoformat() if start_date else None,
                    "end_date": end_date.isoformat() if end_date else None
                },
                "performance_metrics": asdict(metrics),
                "symbol_performance": symbol_performance,
                "strategy_performance": strategy_performance,
                "risk_metrics": risk_metrics,
                "trade_count": len(trades),
                "equity_curve_points": len(equity_curve)
            }
            
            if format.lower() == "detailed":
                report["trades"] = [asdict(trade) for trade in trades]
                report["equity_curve"] = [asdict(point) for point in equity_curve]
            
            return report
            
        except Exception as e:
            logger.error(f"Error exporting performance report: {e}")
            return {"error": str(e)} 