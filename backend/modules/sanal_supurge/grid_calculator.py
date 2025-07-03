"""
Grid Calculator Service

High-performance grid calculation engine based on pro-grid-süpürge.html
Provides risk analysis, P&L calculation, and grid optimization.
"""

import math
from typing import List, Dict, Any, Tuple, Optional
from .models import (
    GridConfig, GridLevel, GridCalculationResult, 
    InstrumentSettings, RiskSettings, LotProgressionModel
)


class GridCalculator:
    """Advanced grid trading calculator with risk analysis"""
    
    def __init__(self):
        self.fibonacci_ratios = [0, 0.236, 0.382, 0.500, 0.618, 0.786, 1.0]
    
    def calculate_grid(self, config: GridConfig, current_price: float) -> GridCalculationResult:
        """Calculate complete grid analysis"""
        # Generate optimized grid levels
        optimized_levels = self._optimize_grid_levels(config)
        
        # Calculate buy and sell scenarios
        buy_scenarios = self._calculate_buy_scenarios(optimized_levels, config, current_price)
        sell_scenarios = self._calculate_sell_scenarios(optimized_levels, config, current_price)
        
        # Risk analysis
        risk_analysis = self._calculate_risk_analysis(buy_scenarios, sell_scenarios, config)
        
        return GridCalculationResult(
            buy_scenarios=buy_scenarios,
            sell_scenarios=sell_scenarios,
            **risk_analysis
        )
    
    def _optimize_grid_levels(self, config: GridConfig) -> List[GridLevel]:
        """Optimize grid levels based on progression model"""
        levels = []
        current_lot = config.grid_levels[0].lot_size if config.grid_levels else 0.01
        
        for i in range(len(config.grid_levels)):
            level_config = config.grid_levels[i]
            
            # Calculate optimized lot size
            if i == 0:
                lot_size = current_lot
            else:
                lot_size = self._calculate_progressive_lot(
                    current_lot, i, config.lot_progression, 
                    config.custom_multiplier, config.fibonacci_strength
                )
            
            # Apply lot size limits
            if config.risk_settings.max_lot_per_order > 0:
                lot_size = min(lot_size, config.risk_settings.max_lot_per_order)
            
            # Calculate distance for this level
            if i == 0:
                distance = 0
            else:
                distance = level_config.distance_points or config.default_grid_distance
            
            levels.append(GridLevel(
                level=i + 1,
                send_order=level_config.send_order,
                lot_size=round(lot_size, 2),
                distance_points=distance,
                tp_points=level_config.tp_points or config.default_tp,
                sl_points=level_config.sl_points or config.default_sl
            ))
            
            current_lot = lot_size
        
        return levels
    
    def _calculate_progressive_lot(
        self, 
        current_lot: float, 
        level: int, 
        progression: LotProgressionModel,
        custom_multiplier: float,
        fibonacci_strength: float
    ) -> float:
        """Calculate lot size based on progression model"""
        
        if progression == LotProgressionModel.LINEAR:
            return current_lot
        
        elif progression == LotProgressionModel.MARTINGALE:
            return current_lot * 2
        
        elif progression == LotProgressionModel.CUSTOM_MULTIPLIER:
            return current_lot * custom_multiplier
        
        elif progression == LotProgressionModel.FIBONACCI_WEIGHTED:
            return current_lot * (1 + fibonacci_strength)
        
        else:  # CUSTOM_SEQUENCE
            return current_lot
    
    def _calculate_buy_scenarios(
        self, 
        levels: List[GridLevel], 
        config: GridConfig, 
        current_price: float
    ) -> List[Dict[str, Any]]:
        """Calculate buy grid scenarios"""
        scenarios = []
        
        if not config.buy_enabled:
            return scenarios
        
        cumulative_distance = 0
        cumulative_lot = 0
        weighted_price_sum = 0
        
        for level in levels:
            if not level.send_order:
                continue
            
            # Calculate entry price
            if level.level == 1:
                entry_price = current_price
            else:
                cumulative_distance += level.distance_points
                entry_price = current_price - (cumulative_distance * config.instrument.tick_size)
            
            # Update cumulative values
            cumulative_lot += level.lot_size
            weighted_price_sum += entry_price * level.lot_size
            avg_entry = weighted_price_sum / cumulative_lot if cumulative_lot > 0 else 0
            
            # Calculate group TP price (using this level's TP)
            group_tp_price = entry_price + (level.tp_points * config.instrument.tick_size)
            
            # Calculate P&L at group TP
            if cumulative_lot > 0:
                price_diff_points = (group_tp_price - avg_entry) / config.instrument.tick_size
                pnl_at_tp = price_diff_points * cumulative_lot * config.instrument.value_per_point
            else:
                pnl_at_tp = 0
            
            # Calculate potential drawdown (before next level opens)
            next_level_price = entry_price - (level.distance_points * config.instrument.tick_size)
            dd_price_diff = (avg_entry - next_level_price) / config.instrument.tick_size
            potential_drawdown = dd_price_diff * cumulative_lot * config.instrument.value_per_point
            
            # Calculate margin requirement
            margin = self._calculate_margin(
                level.lot_size, entry_price, config.instrument, config.risk_settings
            )
            
            scenarios.append({
                "level": level.level,
                "lot": level.lot_size,
                "entry": entry_price,
                "cumulative_lot": cumulative_lot,
                "avg_entry": avg_entry,
                "group_tp_price": group_tp_price,
                "pnl_at_tp": pnl_at_tp,
                "potential_drawdown": potential_drawdown,
                "margin": margin,
                "distance_cumulative": cumulative_distance
            })
        
        return scenarios
    
    def _calculate_sell_scenarios(
        self, 
        levels: List[GridLevel], 
        config: GridConfig, 
        current_price: float
    ) -> List[Dict[str, Any]]:
        """Calculate sell grid scenarios"""
        scenarios = []
        
        if not config.sell_enabled:
            return scenarios
        
        cumulative_distance = 0
        cumulative_lot = 0
        weighted_price_sum = 0
        
        for level in levels:
            if not level.send_order:
                continue
            
            # Calculate entry price
            if level.level == 1:
                entry_price = current_price
            else:
                cumulative_distance += level.distance_points
                entry_price = current_price + (cumulative_distance * config.instrument.tick_size)
            
            # Update cumulative values
            cumulative_lot += level.lot_size
            weighted_price_sum += entry_price * level.lot_size
            avg_entry = weighted_price_sum / cumulative_lot if cumulative_lot > 0 else 0
            
            # Calculate group TP price (using this level's TP)
            group_tp_price = entry_price - (level.tp_points * config.instrument.tick_size)
            
            # Calculate P&L at group TP
            if cumulative_lot > 0:
                price_diff_points = (avg_entry - group_tp_price) / config.instrument.tick_size
                pnl_at_tp = price_diff_points * cumulative_lot * config.instrument.value_per_point
            else:
                pnl_at_tp = 0
            
            # Calculate potential drawdown (before next level opens)
            next_level_price = entry_price + (level.distance_points * config.instrument.tick_size)
            dd_price_diff = (next_level_price - avg_entry) / config.instrument.tick_size
            potential_drawdown = dd_price_diff * cumulative_lot * config.instrument.value_per_point
            
            # Calculate margin requirement
            margin = self._calculate_margin(
                level.lot_size, entry_price, config.instrument, config.risk_settings
            )
            
            scenarios.append({
                "level": level.level,
                "lot": level.lot_size,
                "entry": entry_price,
                "cumulative_lot": cumulative_lot,
                "avg_entry": avg_entry,
                "group_tp_price": group_tp_price,
                "pnl_at_tp": pnl_at_tp,
                "potential_drawdown": potential_drawdown,
                "margin": margin,
                "distance_cumulative": cumulative_distance
            })
        
        return scenarios
    
    def _calculate_margin(
        self, 
        lot_size: float, 
        price: float, 
        instrument: InstrumentSettings, 
        risk_settings: RiskSettings
    ) -> float:
        """Calculate margin requirement for a position"""
        return (lot_size * instrument.contract_size * price) / risk_settings.leverage
    
    def _calculate_risk_analysis(
        self, 
        buy_scenarios: List[Dict[str, Any]], 
        sell_scenarios: List[Dict[str, Any]], 
        config: GridConfig
    ) -> Dict[str, Any]:
        """Calculate comprehensive risk analysis"""
        
        # Calculate maximum drawdowns
        max_buy_dd = max([s["potential_drawdown"] for s in buy_scenarios], default=0)
        max_sell_dd = max([s["potential_drawdown"] for s in sell_scenarios], default=0)
        
        # Calculate total margin requirements
        buy_margin = sum([s["margin"] for s in buy_scenarios])
        sell_margin = sum([s["margin"] for s in sell_scenarios])
        
        # Calculate margin percentages
        balance = config.risk_settings.balance
        buy_margin_percent = (buy_margin / balance * 100) if balance > 0 else 0
        sell_margin_percent = (sell_margin / balance * 100) if balance > 0 else 0
        
        # Calculate total lots
        total_buy_lots = sum([s["lot"] for s in buy_scenarios])
        total_sell_lots = sum([s["lot"] for s in sell_scenarios])
        
        # Estimate maximum profits
        max_buy_profit = max([s["pnl_at_tp"] for s in buy_scenarios], default=0)
        max_sell_profit = max([s["pnl_at_tp"] for s in sell_scenarios], default=0)
        
        return {
            "max_buy_drawdown": abs(max_buy_dd),
            "max_sell_drawdown": abs(max_sell_dd),
            "buy_margin_percent": buy_margin_percent,
            "sell_margin_percent": sell_margin_percent,
            "total_buy_lots": total_buy_lots,
            "total_sell_lots": total_sell_lots,
            "estimated_max_profit_buy": max_buy_profit,
            "estimated_max_profit_sell": max_sell_profit
        }
    
    def calculate_smart_distance(
        self, 
        atr_value: float, 
        volatility_factor: float = 0.15
    ) -> int:
        """Calculate smart grid distance based on ATR"""
        smart_distance = round(atr_value * volatility_factor / 100) * 100
        return max(100, smart_distance)  # Minimum 100 points
    
    def generate_fibonacci_levels(
        self, 
        high_price: float, 
        low_price: float, 
        decimals: int = 5
    ) -> Dict[str, Dict[str, float]]:
        """Generate Fibonacci retracement levels"""
        price_range = high_price - low_price
        
        if price_range <= 0:
            return {}
        
        levels = {}
        for ratio in self.fibonacci_ratios:
            retracement_up = low_price + (price_range * ratio)
            retracement_down = high_price - (price_range * ratio)
            
            levels[f"{ratio*100:.1f}%"] = {
                "uptrend": round(retracement_up, decimals),
                "downtrend": round(retracement_down, decimals)
            }
        
        return levels
    
    def export_mt5_set_file(self, config: GridConfig) -> str:
        """Export configuration as MT5 .set file content"""
        lines = []
        
        # Basic EA parameters
        lines.append(f"BuyIslemiAc={str(config.buy_enabled).lower()}")
        lines.append(f"SellIslemiAc={str(config.sell_enabled).lower()}")
        lines.append(f"PositionComment={config.position_comment}")
        lines.append(f"PivotUst={config.pivot_upper:.1f}")
        lines.append(f"PivotAlt={config.pivot_lower:.2f}")
        
        # Alert settings
        lines.append(f"Alert3={str(config.alert_level_3).lower()}")
        lines.append(f"Alert4={str(config.alert_level_4).lower()}")
        lines.append(f"Alert5={str(config.alert_level_5).lower()}")
        
        # Time filter settings
        lines.append(f"UseTimeLimit={str(config.use_time_filter).lower()}")
        lines.append(f"DoNotOpenBeforeHour={config.trading_start_hour}")
        lines.append(f"DoNotOpenBeforeMinutes={config.trading_start_minute}")
        lines.append(f"DoNotOpenAfterHour={config.trading_end_hour}")
        lines.append(f"DoNotOpenAfterMinutes={config.trading_end_minute}")
        
        lines.append(f"UseTimeLimitBreak={str(config.use_break_filter).lower()}")
        lines.append(f"DoNotOpenAfterHourBreak={config.break_start_hour}")
        lines.append(f"DoNotOpenAfterMinutesBreak={config.break_start_minute}")
        lines.append(f"DoNotOpenBeforeHourBreak={config.break_end_hour}")
        lines.append(f"DoNotOpenBeforeMinutesBreak={config.break_end_minute}")
        
        lines.append("")
        
        # Grid level parameters (up to 14 levels)
        for i in range(14):
            level_num = i + 1
            
            if i < len(config.grid_levels):
                level = config.grid_levels[i]
                lines.append(f"SendOrder{level_num}={str(level.send_order).lower()}")
                lines.append(f"LotSize{level_num}={level.lot_size:.2f}")
                if level_num > 1:  # No distance for first level
                    lines.append(f"NewPositionAddLevel{level_num}={level.distance_points}")
                lines.append(f"tp{level_num}={level.tp_points}")
                lines.append(f"sl{level_num}={level.sl_points}")
            else:
                # Default values for unused levels
                lines.append(f"SendOrder{level_num}=false")
                lines.append(f"LotSize{level_num}=0.01")
                if level_num > 1:
                    lines.append(f"NewPositionAddLevel{level_num}=100")
                lines.append(f"tp{level_num}=1000")
                lines.append(f"sl{level_num}=100")
        
        return "\n".join(lines) 