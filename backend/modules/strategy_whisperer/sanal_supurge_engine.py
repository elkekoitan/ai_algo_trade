"""
Sanal Süpürge (Virtual Sweeper) Grid Trading Engine
Advanced grid trading with automatic Fibonacci level calculation
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
from ..mt5_integration.models import MT5Account, OrderType
from ..signals.ict.support_resistance import ICTSupportResistance
import logging

logger = logging.getLogger(__name__)

class SanalSupurgeEngine:
    """Advanced grid trading engine with Fibonacci-based level calculation"""
    
    def __init__(self):
        self.fib_ratios = [0, 0.236, 0.382, 0.500, 0.618, 0.786, 1.0]
        self.sr_analyzer = ICTSupportResistance()
        
    def calculate_fibonacci_levels(
        self, 
        symbol: str, 
        timeframe: str = "H1",
        lookback_days: int = 30
    ) -> Dict[str, float]:
        """Calculate Fibonacci retracement levels for the given symbol"""
        try:
            # Get historical data for swing point calculation
            bars = self.sr_analyzer.get_historical_data(symbol, timeframe, lookback_days)
            if not bars or len(bars) < 20:
                raise ValueError(f"Insufficient data for {symbol}")
            
            # Find swing high and low
            highs = [bar['high'] for bar in bars]
            lows = [bar['low'] for bar in bars]
            
            swing_high = max(highs)
            swing_low = min(lows)
            range_size = swing_high - swing_low
            
            if range_size <= 0:
                raise ValueError("Invalid price range")
            
            # Calculate Fibonacci levels
            fib_levels = {}
            for ratio in self.fib_ratios:
                level_up = swing_low + (range_size * ratio)
                level_down = swing_high - (range_size * ratio)
                fib_levels[f"{int(ratio*100)}%_up"] = level_up
                fib_levels[f"{int(ratio*100)}%_down"] = level_down
            
            fib_levels['swing_high'] = swing_high
            fib_levels['swing_low'] = swing_low
            fib_levels['range'] = range_size
            
            return fib_levels
            
        except Exception as e:
            logger.error(f"Error calculating Fibonacci levels: {e}")
            return {}
    
    def calculate_grid_levels(
        self,
        symbol: str,
        settings: Dict
    ) -> List[Dict]:
        """Calculate grid levels based on Fibonacci and user settings"""
        
        # Get Fibonacci levels
        fib_levels = self.calculate_fibonacci_levels(
            symbol, 
            settings.get('timeframe', 'H1'),
            settings.get('lookback_days', 30)
        )
        
        if not fib_levels:
            return []
        
        # Grid configuration
        grid_count = settings.get('grid_levels', 14)
        initial_lot = settings.get('initial_lot', 0.01)
        lot_multiplier = settings.get('lot_multiplier', 2.0)
        tp_points = settings.get('tp_points', 1000)
        sl_points = settings.get('sl_points', 10000)
        
        # Calculate grid spacing based on Fibonacci range
        price_range = fib_levels['range']
        grid_distance = price_range / (grid_count + 1)
        
        # Get current price
        current_price = settings.get('current_price', (fib_levels['swing_high'] + fib_levels['swing_low']) / 2)
        
        grid_levels = []
        current_lot = initial_lot
        
        for i in range(grid_count):
            level = {
                'index': i + 1,
                'active': True,
                'lot_size': round(current_lot, 2),
                'buy_price': current_price - (grid_distance * (i + 1)),
                'sell_price': current_price + (grid_distance * (i + 1)),
                'tp_points': tp_points,
                'sl_points': sl_points,
                'margin_required': 0  # To be calculated based on leverage
            }
            
            # Calculate next lot size
            if settings.get('lot_progression', 'martingale') == 'martingale':
                current_lot *= lot_multiplier
            elif settings.get('lot_progression') == 'fibonacci':
                current_lot = initial_lot * self._fibonacci(i + 2)
            
            # Apply max lot limit
            max_lot = settings.get('max_lot_per_order', 10.0)
            level['lot_size'] = min(level['lot_size'], max_lot)
            
            grid_levels.append(level)
        
        return grid_levels
    
    def _fibonacci(self, n: int) -> int:
        """Calculate Fibonacci number"""
        if n <= 1:
            return n
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b
    
    def analyze_risk(
        self,
        grid_levels: List[Dict],
        account_balance: float,
        leverage: int,
        symbol_info: Dict
    ) -> Dict:
        """Analyze risk for the grid configuration"""
        
        total_lots = sum(level['lot_size'] for level in grid_levels if level['active'])
        
        # Calculate required margin
        contract_size = symbol_info.get('contract_size', 100000)
        avg_price = sum(level['buy_price'] + level['sell_price'] for level in grid_levels) / (len(grid_levels) * 2)
        total_margin = (total_lots * contract_size * avg_price) / leverage
        
        # Calculate maximum drawdown
        max_dd = self._calculate_max_drawdown(grid_levels, symbol_info)
        
        # Risk metrics
        margin_usage_percent = (total_margin / account_balance) * 100
        dd_percent = (max_dd / account_balance) * 100
        risk_reward_ratio = self._calculate_risk_reward(grid_levels, symbol_info)
        
        risk_level = 'Low'
        if margin_usage_percent > 50 or dd_percent > 30:
            risk_level = 'High'
        elif margin_usage_percent > 30 or dd_percent > 15:
            risk_level = 'Medium'
        
        return {
            'total_lots': total_lots,
            'total_margin_required': total_margin,
            'margin_usage_percent': margin_usage_percent,
            'max_drawdown': max_dd,
            'max_drawdown_percent': dd_percent,
            'risk_reward_ratio': risk_reward_ratio,
            'risk_level': risk_level,
            'active_levels': sum(1 for level in grid_levels if level['active'])
        }
    
    def _calculate_max_drawdown(self, grid_levels: List[Dict], symbol_info: Dict) -> float:
        """Calculate maximum potential drawdown"""
        max_dd = 0
        point_value = symbol_info.get('point_value', 1.0)
        
        for i, level in enumerate(grid_levels):
            if not level['active']:
                continue
            
            # Calculate cumulative loss if all levels up to this one are triggered
            cumulative_lots = sum(grid_levels[j]['lot_size'] for j in range(i + 1) if grid_levels[j]['active'])
            
            # Worst case: price moves to trigger next level
            if i < len(grid_levels) - 1:
                next_level_distance = abs(grid_levels[i + 1]['buy_price'] - grid_levels[i]['buy_price'])
                potential_loss = cumulative_lots * next_level_distance * point_value
                max_dd = max(max_dd, potential_loss)
        
        return max_dd
    
    def _calculate_risk_reward(self, grid_levels: List[Dict], symbol_info: Dict) -> float:
        """Calculate risk/reward ratio for the grid"""
        if not grid_levels:
            return 0
        
        point_value = symbol_info.get('point_value', 1.0)
        tick_size = symbol_info.get('tick_size', 0.00001)
        
        # Calculate average potential profit
        total_profit = 0
        for level in grid_levels:
            if level['active']:
                profit = level['lot_size'] * level['tp_points'] * tick_size * point_value
                total_profit += profit
        
        avg_profit = total_profit / len([l for l in grid_levels if l['active']])
        
        # Calculate max drawdown
        max_dd = self._calculate_max_drawdown(grid_levels, symbol_info)
        
        if max_dd > 0:
            return avg_profit / max_dd
        return 0
    
    def generate_ea_settings(self, grid_levels: List[Dict], settings: Dict) -> str:
        """Generate MT5 EA settings file content"""
        
        ea_content = f"""
; Sanal Süpürge Grid EA Settings
; Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

; General Settings
BuyIslemiAc={str(settings.get('allow_buy', True)).lower()}
SellIslemiAc={str(settings.get('allow_sell', True)).lower()}
PositionComment=SanalSupurge_{settings.get('symbol', 'XAUUSD')}

; Pivot Settings
PivotUst={settings.get('pivot_upper', 999999.0)}
PivotAlt={settings.get('pivot_lower', 0.0)}

; Alert Settings
Alert3={str(settings.get('alert_level_3', True)).lower()}
Alert4={str(settings.get('alert_level_4', True)).lower()}
Alert5={str(settings.get('alert_level_5', True)).lower()}

; Time Filter
UseTimeLimit={str(settings.get('use_time_filter', False)).lower()}
DoNotOpenAfterHour={settings.get('no_trade_after_hour', 20)}
DoNotOpenAfterMinutes={settings.get('no_trade_after_min', 30)}
DoNotOpenBeforeHour={settings.get('no_trade_before_hour', 2)}
DoNotOpenBeforeMinutes={settings.get('no_trade_before_min', 30)}

"""
        
        # Add grid levels
        for i, level in enumerate(grid_levels[:14]):  # MT5 EA supports max 14 levels
            level_num = i + 1
            ea_content += f"""
; Level {level_num}
SendOrder{level_num}={str(level['active']).lower()}
LotSize{level_num}={level['lot_size']:.2f}"""
            
            if i > 0:
                distance = abs(grid_levels[i]['buy_price'] - grid_levels[i-1]['buy_price'])
                distance_points = int(distance / settings.get('tick_size', 0.00001))
                ea_content += f"\nNewPositionAddLevel{level_num}={distance_points}"
            
            ea_content += f"""
tp{level_num}={level['tp_points']}
sl{level_num}={level['sl_points']}
"""
        
        return ea_content
    
    def optimize_grid_for_volatility(
        self,
        symbol: str,
        volatility_atr: float,
        settings: Dict
    ) -> Dict:
        """Optimize grid settings based on current market volatility"""
        
        # Base settings
        optimized = settings.copy()
        
        # Adjust grid distance based on ATR
        base_distance = volatility_atr * 0.15  # 15% of ATR as base distance
        
        # Adjust lot progression based on volatility
        if volatility_atr > settings.get('high_volatility_threshold', 1000):
            # High volatility: more conservative
            optimized['lot_multiplier'] = 1.5
            optimized['grid_distance_multiplier'] = 1.5
            optimized['grid_levels'] = min(settings.get('grid_levels', 14), 10)
        elif volatility_atr < settings.get('low_volatility_threshold', 500):
            # Low volatility: can be more aggressive
            optimized['lot_multiplier'] = 2.5
            optimized['grid_distance_multiplier'] = 0.8
            optimized['grid_levels'] = settings.get('grid_levels', 14)
        else:
            # Normal volatility
            optimized['lot_multiplier'] = 2.0
            optimized['grid_distance_multiplier'] = 1.0
        
        optimized['base_grid_distance'] = base_distance
        
        return optimized 