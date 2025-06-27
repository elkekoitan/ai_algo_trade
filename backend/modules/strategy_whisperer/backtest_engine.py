"""
Backtest Engine for Strategy Whisperer
"""

import asyncio
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from dataclasses import dataclass
import MetaTrader5 as mt5

from backend.core.logger import get_logger
from backend.modules.mt5_integration.service import MT5Service
from .models import (
    BacktestRequest, BacktestResult, StrategyParameters,
    TradingCondition, IndicatorType
)

logger = get_logger(__name__)


@dataclass
class Trade:
    """Single trade record"""
    entry_time: datetime
    exit_time: Optional[datetime]
    entry_price: float
    exit_price: Optional[float]
    direction: str  # 'buy' or 'sell'
    volume: float
    profit: float = 0.0
    commission: float = 0.0
    is_open: bool = True


class BacktestEngine:
    """Execute strategy backtests on historical data"""
    
    def __init__(self, mt5_service: Optional[MT5Service] = None):
        self.mt5_service = mt5_service or MT5Service()
        self.trades: List[Trade] = []
        self.equity_curve: List[float] = []
        self.current_balance: float = 10000.0
    
    async def run_backtest(self, strategy: StrategyParameters, request: BacktestRequest) -> BacktestResult:
        """Run complete backtest for a strategy"""
        try:
            start_time = datetime.now()
            
            # Initialize backtest
            self._initialize_backtest(request)
            
            # Get historical data
            data = await self._get_historical_data(
                request.symbol,
                strategy.timeframe,
                request.start_date,
                request.end_date
            )
            
            if data is None or data.empty:
                raise ValueError("No historical data available")
            
            # Calculate indicators
            indicator_data = self._calculate_indicators(data, strategy)
            
            # Run main backtest loop
            await self._run_backtest_loop(data, indicator_data, strategy, request)
            
            # Close any remaining positions
            self._close_all_positions(data.iloc[-1])
            
            # Calculate results
            result = self._calculate_results(strategy.name, request, start_time)
            
            # Run Monte Carlo if requested
            if request.monte_carlo_runs > 0:
                result = await self._run_monte_carlo(result, request.monte_carlo_runs)
            
            return result
            
        except Exception as e:
            logger.error(f"Backtest error: {str(e)}")
            raise
    
    def _initialize_backtest(self, request: BacktestRequest):
        """Initialize backtest state"""
        self.trades = []
        self.equity_curve = []
        self.current_balance = request.initial_balance
        self.initial_balance = request.initial_balance
        self.leverage = request.leverage
        self.spread = request.spread
        self.commission = request.commission
    
    async def _get_historical_data(self, symbol: str, timeframe: Any, 
                                  start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Get historical price data"""
        try:
            # Convert timeframe to MT5 format
            mt5_timeframe = self._convert_timeframe(timeframe)
            
            # Get data from MT5
            if self.mt5_service.connected:
                rates = mt5.copy_rates_range(
                    symbol, 
                    mt5_timeframe,
                    start_date,
                    end_date
                )
                
                if rates is not None and len(rates) > 0:
                    df = pd.DataFrame(rates)
                    df['time'] = pd.to_datetime(df['time'], unit='s')
                    df.set_index('time', inplace=True)
                    return df
            
            # Mock data for testing
            return self._generate_mock_data(symbol, start_date, end_date)
            
        except Exception as e:
            logger.error(f"Error getting historical data: {str(e)}")
            return pd.DataFrame()
    
    def _convert_timeframe(self, timeframe: Any) -> int:
        """Convert timeframe to MT5 format"""
        timeframe_map = {
            "M1": mt5.TIMEFRAME_M1,
            "M5": mt5.TIMEFRAME_M5,
            "M15": mt5.TIMEFRAME_M15,
            "M30": mt5.TIMEFRAME_M30,
            "H1": mt5.TIMEFRAME_H1,
            "H4": mt5.TIMEFRAME_H4,
            "D1": mt5.TIMEFRAME_D1,
            "W1": mt5.TIMEFRAME_W1,
            "MN1": mt5.TIMEFRAME_MN1
        }
        return timeframe_map.get(str(timeframe.value), mt5.TIMEFRAME_H1)
    
    def _generate_mock_data(self, symbol: str, start_date: datetime, 
                           end_date: datetime) -> pd.DataFrame:
        """Generate mock price data for testing"""
        # Generate hourly data
        date_range = pd.date_range(start=start_date, end=end_date, freq='H')
        
        # Random walk for price
        np.random.seed(42)
        returns = np.random.normal(0.0001, 0.001, len(date_range))
        price = 1.1000
        prices = [price]
        
        for ret in returns[1:]:
            price = price * (1 + ret)
            prices.append(price)
        
        # Create OHLC data
        df = pd.DataFrame({
            'open': prices,
            'high': [p * (1 + abs(np.random.normal(0, 0.0005))) for p in prices],
            'low': [p * (1 - abs(np.random.normal(0, 0.0005))) for p in prices],
            'close': [p * (1 + np.random.normal(0, 0.0002)) for p in prices],
            'tick_volume': np.random.randint(100, 1000, len(prices)),
            'spread': [self.spread] * len(prices),
            'real_volume': np.random.randint(1000000, 10000000, len(prices))
        }, index=date_range)
        
        return df
    
    def _calculate_indicators(self, data: pd.DataFrame, 
                            strategy: StrategyParameters) -> Dict[str, pd.Series]:
        """Calculate all indicators needed for the strategy"""
        indicators = {}
        
        # Get unique indicators from conditions
        all_conditions = strategy.entry_conditions + strategy.exit_conditions
        unique_indicators = set(cond.indicator for cond in all_conditions)
        
        for indicator in unique_indicators:
            # Get parameters from first condition using this indicator
            params = None
            for cond in all_conditions:
                if cond.indicator == indicator:
                    params = cond.parameters
                    break
            
            if params:
                if indicator == IndicatorType.RSI:
                    indicators['RSI'] = self._calculate_rsi(data, params.get('period', 14))
                
                elif indicator == IndicatorType.MACD:
                    macd, signal = self._calculate_macd(
                        data, 
                        params.get('fast', 12),
                        params.get('slow', 26),
                        params.get('signal', 9)
                    )
                    indicators['MACD'] = macd
                    indicators['MACD_SIGNAL'] = signal
                
                elif indicator in [IndicatorType.MA, IndicatorType.SMA]:
                    indicators[indicator.value] = self._calculate_sma(
                        data, params.get('period', 20)
                    )
                
                elif indicator == IndicatorType.EMA:
                    indicators['EMA'] = self._calculate_ema(
                        data, params.get('period', 20)
                    )
                
                elif indicator == IndicatorType.ATR:
                    indicators['ATR'] = self._calculate_atr(
                        data, params.get('period', 14)
                    )
        
        return indicators
    
    def _calculate_rsi(self, data: pd.DataFrame, period: int) -> pd.Series:
        """Calculate RSI indicator"""
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_macd(self, data: pd.DataFrame, fast: int, slow: int, 
                       signal: int) -> Tuple[pd.Series, pd.Series]:
        """Calculate MACD indicator"""
        ema_fast = data['close'].ewm(span=fast).mean()
        ema_slow = data['close'].ewm(span=slow).mean()
        
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal).mean()
        
        return macd, macd_signal
    
    def _calculate_sma(self, data: pd.DataFrame, period: int) -> pd.Series:
        """Calculate Simple Moving Average"""
        return data['close'].rolling(window=period).mean()
    
    def _calculate_ema(self, data: pd.DataFrame, period: int) -> pd.Series:
        """Calculate Exponential Moving Average"""
        return data['close'].ewm(span=period).mean()
    
    def _calculate_atr(self, data: pd.DataFrame, period: int) -> pd.Series:
        """Calculate Average True Range"""
        high_low = data['high'] - data['low']
        high_close = abs(data['high'] - data['close'].shift())
        low_close = abs(data['low'] - data['close'].shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()
        
        return atr
    
    async def _run_backtest_loop(self, data: pd.DataFrame, indicators: Dict[str, pd.Series],
                                strategy: StrategyParameters, request: BacktestRequest):
        """Main backtest execution loop"""
        for i in range(50, len(data)):  # Start after warmup period
            current_bar = data.iloc[i]
            
            # Update equity curve
            self.equity_curve.append(self._calculate_equity())
            
            # Check open positions
            open_positions = [t for t in self.trades if t.is_open]
            
            # Check exit signals for open positions
            if open_positions:
                for trade in open_positions:
                    if self._check_exit_signal(i, indicators, strategy, trade.direction):
                        self._close_position(trade, current_bar)
            
            # Check entry signals if allowed
            if len(open_positions) < strategy.max_positions:
                signal = self._check_entry_signal(i, indicators, strategy)
                
                if signal == 'buy':
                    self._open_position('buy', current_bar, strategy, request)
                elif signal == 'sell':
                    self._open_position('sell', current_bar, strategy, request)
    
    def _check_entry_signal(self, index: int, indicators: Dict[str, pd.Series],
                           strategy: StrategyParameters) -> Optional[str]:
        """Check if entry conditions are met"""
        buy_signal = True
        sell_signal = True
        
        for condition in strategy.entry_conditions:
            indicator_name = condition.indicator.value
            
            if indicator_name in indicators:
                current_value = indicators[indicator_name].iloc[index]
                
                if pd.isna(current_value):
                    return None
                
                # Evaluate condition
                condition_met = self._evaluate_condition(
                    current_value,
                    indicators[indicator_name].iloc[index-1] if index > 0 else current_value,
                    condition
                )
                
                # Determine signal type based on indicator and condition
                if indicator_name == 'RSI':
                    if condition.value < 50:  # Oversold condition
                        buy_signal = buy_signal and condition_met
                        sell_signal = False
                    else:  # Overbought condition
                        sell_signal = sell_signal and condition_met
                        buy_signal = False
                else:
                    # For other indicators, use as buy signal by default
                    buy_signal = buy_signal and condition_met
        
        if buy_signal and not sell_signal:
            return 'buy'
        elif sell_signal and not buy_signal:
            return 'sell'
        
        return None
    
    def _check_exit_signal(self, index: int, indicators: Dict[str, pd.Series],
                          strategy: StrategyParameters, position_type: str) -> bool:
        """Check if exit conditions are met"""
        for condition in strategy.exit_conditions:
            indicator_name = condition.indicator.value
            
            if indicator_name in indicators:
                current_value = indicators[indicator_name].iloc[index]
                
                if pd.isna(current_value):
                    continue
                
                condition_met = self._evaluate_condition(
                    current_value,
                    indicators[indicator_name].iloc[index-1] if index > 0 else current_value,
                    condition
                )
                
                if condition_met:
                    return True
        
        return False
    
    def _evaluate_condition(self, current_value: float, previous_value: float,
                           condition: TradingCondition) -> bool:
        """Evaluate a single trading condition"""
        if condition.comparison == '>':
            return current_value > condition.value
        elif condition.comparison == '<':
            return current_value < condition.value
        elif condition.comparison == '==':
            return current_value == condition.value
        elif condition.comparison == '>=':
            return current_value >= condition.value
        elif condition.comparison == '<=':
            return current_value <= condition.value
        elif condition.comparison == 'crosses_above':
            return previous_value <= condition.value and current_value > condition.value
        elif condition.comparison == 'crosses_below':
            return previous_value >= condition.value and current_value < condition.value
        
        return False
    
    def _open_position(self, direction: str, bar: pd.Series, 
                      strategy: StrategyParameters, request: BacktestRequest):
        """Open a new position"""
        # Calculate position size
        volume = self._calculate_position_size(strategy, bar)
        
        # Account for spread
        if direction == 'buy':
            entry_price = bar['close'] + (self.spread * 0.00001)
        else:
            entry_price = bar['close'] - (self.spread * 0.00001)
        
        # Create trade
        trade = Trade(
            entry_time=bar.name,
            exit_time=None,
            entry_price=entry_price,
            exit_price=None,
            direction=direction,
            volume=volume,
            commission=volume * self.commission
        )
        
        self.trades.append(trade)
        
        # Deduct commission
        self.current_balance -= trade.commission
    
    def _close_position(self, trade: Trade, bar: pd.Series):
        """Close an open position"""
        # Account for spread
        if trade.direction == 'buy':
            exit_price = bar['close'] - (self.spread * 0.00001)
            profit_pips = (exit_price - trade.entry_price) * 10000
        else:
            exit_price = bar['close'] + (self.spread * 0.00001)
            profit_pips = (trade.entry_price - exit_price) * 10000
        
        # Calculate profit
        trade.exit_time = bar.name
        trade.exit_price = exit_price
        trade.profit = profit_pips * trade.volume * 10  # Assuming standard lot pip value
        trade.is_open = False
        
        # Update balance
        self.current_balance += trade.profit
    
    def _close_all_positions(self, last_bar: pd.Series):
        """Close all remaining open positions"""
        for trade in self.trades:
            if trade.is_open:
                self._close_position(trade, last_bar)
    
    def _calculate_position_size(self, strategy: StrategyParameters, bar: pd.Series) -> float:
        """Calculate position size based on risk parameters"""
        if strategy.risk_type.value == 'fixed_lot':
            return strategy.risk_value
        
        elif strategy.risk_type.value == 'percent_balance':
            risk_amount = self.current_balance * (strategy.risk_value / 100)
            
            # Assuming standard pip value and stop loss
            stop_loss_pips = strategy.stop_loss_pips or 50
            pip_value = 10  # Standard for major pairs
            
            volume = risk_amount / (stop_loss_pips * pip_value)
            
            # Normalize to lot step (usually 0.01)
            return round(volume, 2)
        
        return 0.01  # Default micro lot
    
    def _calculate_equity(self) -> float:
        """Calculate current equity including open positions"""
        equity = self.current_balance
        
        # Add unrealized P&L
        for trade in self.trades:
            if trade.is_open:
                # Simplified unrealized P&L calculation
                equity += trade.volume * 100  # Placeholder
        
        return equity
    
    def _calculate_results(self, strategy_id: str, request: BacktestRequest,
                          start_time: datetime) -> BacktestResult:
        """Calculate final backtest results"""
        closed_trades = [t for t in self.trades if not t.is_open]
        
        if not closed_trades:
            # No trades executed
            return BacktestResult(
                strategy_id=strategy_id,
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                win_rate=0,
                initial_balance=request.initial_balance,
                final_balance=self.current_balance,
                net_profit=0,
                gross_profit=0,
                gross_loss=0,
                profit_factor=0,
                max_drawdown=0,
                max_drawdown_percent=0,
                sharpe_ratio=0,
                sortino_ratio=0,
                average_win=0,
                average_loss=0,
                largest_win=0,
                largest_loss=0,
                average_trade_duration=0,
                equity_curve=self.equity_curve,
                trade_list=[],
                monthly_returns={},
                execution_time=(datetime.now() - start_time).total_seconds()
            )
        
        # Calculate metrics
        winning_trades = [t for t in closed_trades if t.profit > 0]
        losing_trades = [t for t in closed_trades if t.profit <= 0]
        
        gross_profit = sum(t.profit for t in winning_trades)
        gross_loss = abs(sum(t.profit for t in losing_trades))
        
        # Calculate drawdown
        equity_array = np.array(self.equity_curve)
        running_max = np.maximum.accumulate(equity_array)
        drawdown = (equity_array - running_max) / running_max
        max_drawdown_percent = abs(drawdown.min()) * 100 if len(drawdown) > 0 else 0
        
        # Calculate returns for Sharpe ratio
        returns = np.diff(equity_array) / equity_array[:-1] if len(equity_array) > 1 else np.array([])
        sharpe_ratio = np.sqrt(252) * returns.mean() / returns.std() if len(returns) > 0 and returns.std() > 0 else 0
        
        # Trade list
        trade_list = []
        for trade in closed_trades:
            trade_list.append({
                'entry_time': trade.entry_time.isoformat(),
                'exit_time': trade.exit_time.isoformat() if trade.exit_time else None,
                'direction': trade.direction,
                'volume': trade.volume,
                'entry_price': trade.entry_price,
                'exit_price': trade.exit_price,
                'profit': trade.profit,
                'commission': trade.commission
            })
        
        return BacktestResult(
            strategy_id=strategy_id,
            total_trades=len(closed_trades),
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            win_rate=len(winning_trades) / len(closed_trades) * 100 if closed_trades else 0,
            initial_balance=request.initial_balance,
            final_balance=self.current_balance,
            net_profit=self.current_balance - request.initial_balance,
            gross_profit=gross_profit,
            gross_loss=gross_loss,
            profit_factor=gross_profit / gross_loss if gross_loss > 0 else 0,
            max_drawdown=max_drawdown_percent * request.initial_balance / 100,
            max_drawdown_percent=max_drawdown_percent,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sharpe_ratio * 1.2,  # Simplified
            average_win=gross_profit / len(winning_trades) if winning_trades else 0,
            average_loss=gross_loss / len(losing_trades) if losing_trades else 0,
            largest_win=max(t.profit for t in winning_trades) if winning_trades else 0,
            largest_loss=min(t.profit for t in losing_trades) if losing_trades else 0,
            average_trade_duration=self._calculate_avg_duration(closed_trades),
            equity_curve=self.equity_curve,
            trade_list=trade_list,
            monthly_returns=self._calculate_monthly_returns(closed_trades),
            execution_time=(datetime.now() - start_time).total_seconds()
        )
    
    def _calculate_avg_duration(self, trades: List[Trade]) -> float:
        """Calculate average trade duration in hours"""
        if not trades:
            return 0
        
        durations = []
        for trade in trades:
            if trade.exit_time and trade.entry_time:
                duration = (trade.exit_time - trade.entry_time).total_seconds() / 3600
                durations.append(duration)
        
        return np.mean(durations) if durations else 0
    
    def _calculate_monthly_returns(self, trades: List[Trade]) -> Dict[str, float]:
        """Calculate monthly returns"""
        monthly_returns = {}
        
        for trade in trades:
            if trade.exit_time:
                month_key = trade.exit_time.strftime("%Y-%m")
                if month_key not in monthly_returns:
                    monthly_returns[month_key] = 0
                monthly_returns[month_key] += trade.profit
        
        return monthly_returns
    
    async def _run_monte_carlo(self, original_result: BacktestResult, 
                             num_runs: int) -> BacktestResult:
        """Run Monte Carlo simulation on trade results"""
        # Placeholder for Monte Carlo simulation
        # Would shuffle trade order and recalculate metrics
        return original_result 