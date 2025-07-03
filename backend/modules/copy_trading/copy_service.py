"""
Copy Trading Service
Real-time trade copying with advanced risk management
"""
import asyncio
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
from decimal import Decimal

from .models import (
    CopyTraderProfile, CopySettings, CopyTradeResult, 
    FollowerStats, CopySignal, CopyStatus
)
from ..mt5_integration.service import MT5Service
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from core.enhanced_event_bus import enhanced_event_bus

logger = logging.getLogger(__name__)

class CopyTradingService:
    """Advanced copy trading service with real-time execution"""
    
    def __init__(self):
        self.mt5_service = MT5Service()
        self.active_copy_settings: Dict[str, CopySettings] = {}
        self.trader_profiles: Dict[str, CopyTraderProfile] = {}
        self.copy_queue = asyncio.Queue()
        self.is_running = False
        
        # Performance tracking
        self.copy_latency_ms = []
        self.success_rate = 0.0
        
    async def start_service(self):
        """Start the copy trading service"""
        self.is_running = True
        logger.info("🔥 Copy Trading Service started")
        
        # Start background tasks
        asyncio.create_task(self._process_copy_queue())
        asyncio.create_task(self._monitor_trader_performance())
        asyncio.create_task(self._risk_management_monitor())
        
        # Subscribe to trade events
        await enhanced_event_bus.subscribe(
            "mt5:trade_opened", 
            self._handle_new_trade
        )
        await enhanced_event_bus.subscribe(
            "mt5:trade_closed", 
            self._handle_trade_closed
        )
        
    async def stop_service(self):
        """Stop the copy trading service"""
        self.is_running = False
        logger.info("Copy Trading Service stopped")
        
    # Trader Management
    async def register_trader(self, profile: CopyTraderProfile) -> str:
        """Register a new copy trader"""
        try:
            # Validate trader's trading history
            trading_history = await self._get_trader_history(profile.trader_id)
            
            if not self._validate_trader_performance(trading_history):
                raise ValueError("Trader does not meet minimum performance requirements")
            
            # Calculate real performance metrics
            profile = await self._calculate_trader_metrics(profile, trading_history)
            
            self.trader_profiles[profile.trader_id] = profile
            
            # Broadcast new trader availability
            await enhanced_event_bus.publish(
                "copy_trading:trader_registered",
                {"trader_id": profile.trader_id, "profile": profile.dict()}
            )
            
            logger.info(f"✅ Trader {profile.display_name} registered successfully")
            return profile.trader_id
            
        except Exception as e:
            logger.error(f"Failed to register trader: {e}")
            raise
            
    async def get_available_traders(
        self, 
        risk_level: Optional[str] = None,
        min_return: Optional[float] = None,
        max_drawdown: Optional[float] = None
    ) -> List[CopyTraderProfile]:
        """Get list of available traders with optional filters"""
        traders = list(self.trader_profiles.values())
        
        # Apply filters
        if risk_level:
            traders = [t for t in traders if t.risk_level == risk_level]
        if min_return:
            traders = [t for t in traders if t.monthly_return >= min_return]
        if max_drawdown:
            traders = [t for t in traders if t.max_drawdown <= max_drawdown]
            
        # Sort by performance score
        traders.sort(key=lambda t: self._calculate_trader_score(t), reverse=True)
        
        return traders
        
    # Copy Settings Management
    async def start_copying(
        self, 
        follower_id: str, 
        settings: CopySettings
    ) -> str:
        """Start copying a trader"""
        try:
            # Validate settings
            await self._validate_copy_settings(settings)
            
            # Check follower's account balance
            account_info = await self.mt5_service.get_account_info()
            if account_info.balance < settings.copy_amount:
                raise ValueError("Insufficient account balance")
                
            # Store settings
            copy_id = f"copy_{follower_id}_{settings.trader_id}_{datetime.utcnow().isoformat()}"
            settings.status = CopyStatus.ACTIVE
            self.active_copy_settings[copy_id] = settings
            
            # Initialize follower stats
            stats = FollowerStats(
                follower_id=follower_id,
                trader_id=settings.trader_id,
                start_date=datetime.utcnow(),
                current_copy_settings=settings
            )
            
            # Broadcast copy started
            await enhanced_event_bus.publish(
                "copy_trading:copy_started",
                {
                    "copy_id": copy_id,
                    "follower_id": follower_id,
                    "trader_id": settings.trader_id,
                    "settings": settings.dict()
                }
            )
            
            logger.info(f"✅ Copy trading started: {follower_id} -> {settings.trader_id}")
            return copy_id
            
        except Exception as e:
            logger.error(f"Failed to start copying: {e}")
            raise
            
    async def stop_copying(self, copy_id: str) -> bool:
        """Stop copying a trader"""
        try:
            if copy_id not in self.active_copy_settings:
                return False
                
            settings = self.active_copy_settings[copy_id]
            settings.status = CopyStatus.STOPPED
            
            # Close any open copied positions
            await self._close_copied_positions(copy_id)
            
            # Remove from active settings
            del self.active_copy_settings[copy_id]
            
            # Broadcast copy stopped
            await enhanced_event_bus.publish(
                "copy_trading:copy_stopped",
                {"copy_id": copy_id}
            )
            
            logger.info(f"Copy trading stopped: {copy_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop copying: {e}")
            return False
            
    # Trade Copying Logic
    async def _handle_new_trade(self, event_data: Dict[str, Any]):
        """Handle new trade from a copied trader"""
        try:
            trader_id = event_data.get("trader_id")
            trade_data = event_data.get("trade_data")
            
            if not trader_id or not trade_data:
                return
                
            # Find active copy settings for this trader
            relevant_copies = [
                (copy_id, settings) for copy_id, settings in self.active_copy_settings.items()
                if settings.trader_id == trader_id and settings.status == CopyStatus.ACTIVE
            ]
            
            if not relevant_copies:
                return
                
            # Create copy signals for each follower
            for copy_id, settings in relevant_copies:
                if await self._should_copy_trade(settings, trade_data):
                    signal = CopySignal(
                        signal_id=f"signal_{copy_id}_{trade_data['trade_id']}",
                        trader_id=trader_id,
                        symbol=trade_data["symbol"],
                        action=trade_data["type"],
                        volume=self._calculate_copy_volume(settings, trade_data["volume"]),
                        price=trade_data.get("price"),
                        stop_loss=trade_data.get("stop_loss"),
                        take_profit=trade_data.get("take_profit"),
                        signal_strength=0.9
                    )
                    
                    # Add to copy queue
                    await self.copy_queue.put((copy_id, signal, trade_data))
                    
        except Exception as e:
            logger.error(f"Error handling new trade: {e}")
            
    async def _process_copy_queue(self):
        """Process copy trading queue"""
        while self.is_running:
            try:
                # Get next copy signal
                copy_id, signal, original_trade = await asyncio.wait_for(
                    self.copy_queue.get(), timeout=1.0
                )
                
                # Execute copy trade
                start_time = datetime.utcnow()
                result = await self._execute_copy_trade(copy_id, signal, original_trade)
                end_time = datetime.utcnow()
                
                # Track latency
                latency_ms = (end_time - start_time).total_seconds() * 1000
                self.copy_latency_ms.append(latency_ms)
                
                # Keep only last 100 latency measurements
                if len(self.copy_latency_ms) > 100:
                    self.copy_latency_ms = self.copy_latency_ms[-100:]
                    
                # Log result
                if result.copy_status == "copied":
                    logger.info(f"✅ Trade copied successfully: {signal.symbol} ({latency_ms:.1f}ms)")
                else:
                    logger.warning(f"❌ Failed to copy trade: {result.error_message}")
                    
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing copy queue: {e}")
                
    async def _execute_copy_trade(
        self, 
        copy_id: str, 
        signal: CopySignal, 
        original_trade: Dict[str, Any]
    ) -> CopyTradeResult:
        """Execute a copy trade"""
        try:
            settings = self.active_copy_settings[copy_id]
            
            # Prepare trade request
            trade_request = {
                "symbol": signal.symbol,
                "volume": signal.volume,
                "type": signal.action,
                "price": signal.price,
                "sl": signal.stop_loss,
                "tp": signal.take_profit,
                "comment": f"Copy:{copy_id}",
                "magic": int(copy_id.split("_")[-1][-8:], 16) % 2147483647  # Convert to valid magic number
            }
            
            # Execute trade via MT5
            trade_result = await self.mt5_service.place_order(**trade_request)
            
            if trade_result.get("retcode") == 10009:  # Trade successful
                result = CopyTradeResult(
                    trade_id=str(trade_result["order"]),
                    copy_settings_id=copy_id,
                    original_trade_id=original_trade["trade_id"],
                    trader_id=signal.trader_id,
                    follower_id=settings.follower_id,
                    symbol=signal.symbol,
                    trade_type=signal.action,
                    volume=signal.volume,
                    open_price=trade_result.get("price", signal.price),
                    stop_loss=signal.stop_loss,
                    take_profit=signal.take_profit,
                    copy_ratio_used=settings.copy_ratio,
                    original_volume=original_trade["volume"],
                    copy_status="copied",
                    original_open_time=datetime.fromisoformat(original_trade["time"]),
                    copy_open_time=datetime.utcnow()
                )
                
                # Broadcast successful copy
                await enhanced_event_bus.publish(
                    "copy_trading:trade_copied",
                    {"result": result.dict()}
                )
                
            else:
                result = CopyTradeResult(
                    trade_id="",
                    copy_settings_id=copy_id,
                    original_trade_id=original_trade["trade_id"],
                    trader_id=signal.trader_id,
                    follower_id=settings.follower_id,
                    symbol=signal.symbol,
                    trade_type=signal.action,
                    volume=signal.volume,
                    open_price=0,
                    copy_ratio_used=settings.copy_ratio,
                    original_volume=original_trade["volume"],
                    copy_status="failed",
                    error_message=trade_result.get("comment", "Unknown error"),
                    original_open_time=datetime.fromisoformat(original_trade["time"]),
                    copy_open_time=datetime.utcnow(),
                    is_open=False
                )
                
            return result
            
        except Exception as e:
            logger.error(f"Failed to execute copy trade: {e}")
            return CopyTradeResult(
                trade_id="",
                copy_settings_id=copy_id,
                original_trade_id=original_trade.get("trade_id", ""),
                trader_id=signal.trader_id,
                follower_id=settings.follower_id if settings else "",
                symbol=signal.symbol,
                trade_type=signal.action,
                volume=signal.volume,
                open_price=0,
                copy_ratio_used=1.0,
                original_volume=0,
                copy_status="failed",
                error_message=str(e),
                original_open_time=datetime.utcnow(),
                copy_open_time=datetime.utcnow(),
                is_open=False
            )
            
    # Helper Methods
    def _calculate_copy_volume(self, settings: CopySettings, original_volume: float) -> float:
        """Calculate volume for copy trade"""
        copy_volume = original_volume * settings.copy_ratio
        
        # Apply size limits
        copy_volume = max(copy_volume, settings.min_trade_size)
        copy_volume = min(copy_volume, settings.max_trade_size)
        
        # Round to 2 decimal places
        return round(copy_volume, 2)
        
    async def _should_copy_trade(self, settings: CopySettings, trade_data: Dict[str, Any]) -> bool:
        """Determine if a trade should be copied"""
        # Check symbol filters
        symbol = trade_data["symbol"]
        
        if settings.copy_only_pairs and symbol not in settings.copy_only_pairs:
            return False
            
        if symbol in settings.exclude_pairs:
            return False
            
        # Check time filters
        if not self._is_within_copy_hours(settings):
            return False
            
        # Check risk limits
        if not await self._check_risk_limits(settings):
            return False
            
        return True
        
    def _is_within_copy_hours(self, settings: CopySettings) -> bool:
        """Check if current time is within copy hours"""
        if not settings.copy_hours_start or not settings.copy_hours_end:
            return True
            
        now = datetime.utcnow().time()
        start_time = datetime.strptime(settings.copy_hours_start, "%H:%M").time()
        end_time = datetime.strptime(settings.copy_hours_end, "%H:%M").time()
        
        return start_time <= now <= end_time
        
    async def _check_risk_limits(self, settings: CopySettings) -> bool:
        """Check if copying this trade would exceed risk limits"""
        # Get current open positions
        positions = await self.mt5_service.get_positions()
        copy_positions = [p for p in positions if p.comment.startswith(f"Copy:{settings.trader_id}")]
        
        # Check max open positions
        if len(copy_positions) >= settings.max_open_positions:
            return False
            
        # Check daily loss limit
        today_loss = await self._calculate_daily_loss(settings)
        if today_loss >= settings.max_daily_loss:
            return False
            
        return True
        
    async def _calculate_daily_loss(self, settings: CopySettings) -> float:
        """Calculate today's loss for copy trading"""
        # This would query trade history for today's copy trades
        # For now, return 0
        return 0.0
        
    def _calculate_trader_score(self, trader: CopyTraderProfile) -> float:
        """Calculate overall score for a trader"""
        # Weighted scoring algorithm
        return (
            trader.total_return * 0.3 +
            trader.win_rate * 0.2 +
            trader.profit_factor * 0.2 +
            (100 - trader.max_drawdown) * 0.1 +
            trader.sharpe_ratio * 0.1 +
            trader.rating * 0.1
        )
        
    async def get_copy_statistics(self) -> Dict[str, Any]:
        """Get copy trading statistics"""
        return {
            "active_copies": len(self.active_copy_settings),
            "available_traders": len(self.trader_profiles),
            "average_latency_ms": sum(self.copy_latency_ms) / len(self.copy_latency_ms) if self.copy_latency_ms else 0,
            "success_rate": self.success_rate,
            "total_copied_trades_today": 0,  # Would be calculated from database
            "top_traders": await self.get_available_traders()[:5]
        } 