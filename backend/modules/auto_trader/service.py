import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import logging
from dataclasses import asdict

from .models import (
    AutoTradeRequest, AutoTradeResponse, TradingStrategy, 
    AutoTraderStatus, TradeResult, StrategyConfig, SessionStatus
)
from ..mt5_integration.service import MT5Service
from ..signals.ict.scoring import ICTSignalScorer
from ..signals.ict.order_blocks import OrderBlockDetector
from ..signals.ict.fair_value_gaps import FairValueGapDetector
from ..signals.ict.breaker_blocks import BreakerBlockDetector
from ...core.logger import get_logger

logger = get_logger(__name__)

class TradingSession:
    """Represents an active trading session"""
    
    def __init__(self, session_id: str, strategy: TradingStrategy, config: StrategyConfig):
        self.session_id = session_id
        self.strategy = strategy
        self.config = config
        self.status = SessionStatus.STARTING
        self.created_at = datetime.utcnow()
        self.started_at: Optional[datetime] = None
        self.stopped_at: Optional[datetime] = None
        self.paused_at: Optional[datetime] = None
        self.trades: List[TradeResult] = []
        self.signals: List[Dict] = []
        self.total_profit = 0.0
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.is_running = False
        self.is_paused = False
        self.last_signal_time: Optional[datetime] = None
        
    def add_trade(self, trade: TradeResult):
        """Add trade result to session"""
        self.trades.append(trade)
        self.total_trades += 1
        self.total_profit += trade.profit
        
        if trade.profit > 0:
            self.winning_trades += 1
        else:
            self.losing_trades += 1
    
    def add_signal(self, signal: Dict):
        """Add signal to session history"""
        self.signals.append(signal)
        self.last_signal_time = datetime.utcnow()
    
    def get_win_rate(self) -> float:
        """Calculate win rate percentage"""
        if self.total_trades == 0:
            return 0.0
        return (self.winning_trades / self.total_trades) * 100
    
    def get_performance_metrics(self) -> Dict:
        """Get comprehensive performance metrics"""
        return {
            "session_id": self.session_id,
            "strategy_name": self.strategy.name,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "stopped_at": self.stopped_at.isoformat() if self.stopped_at else None,
            "duration_minutes": self._get_duration_minutes(),
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "win_rate": self.get_win_rate(),
            "total_profit": self.total_profit,
            "signals_processed": len(self.signals),
            "last_signal_time": self.last_signal_time.isoformat() if self.last_signal_time else None,
            "is_running": self.is_running,
            "is_paused": self.is_paused
        }
    
    def _get_duration_minutes(self) -> Optional[float]:
        """Get session duration in minutes"""
        if not self.started_at:
            return None
        
        end_time = self.stopped_at or datetime.utcnow()
        duration = end_time - self.started_at
        return duration.total_seconds() / 60

class AutoTraderService:
    """Advanced automated trading service with ICT signal integration"""
    
    def __init__(self):
        self.mt5_service = MT5Service()
        self.signal_scorer = ICTSignalScorer()
        self.order_block_detector = OrderBlockDetector()
        self.fvg_detector = FairValueGapDetector()
        self.breaker_detector = BreakerBlockDetector()
        
        # Session management
        self.active_sessions: Dict[str, TradingSession] = {}
        self.strategies: Dict[str, TradingStrategy] = {}
        self.is_initialized = False
        
        # Default strategies
        self._initialize_default_strategies()
        
        logger.info("AutoTrader service initialized")
    
    def _initialize_default_strategies(self):
        """Initialize default trading strategies"""
        
        # ICT Smart Money Strategy
        ict_strategy = TradingStrategy(
            name="ICT_Smart_Money",
            description="ICT Smart Money Concepts with Order Blocks and FVG",
            signal_types=["order_block", "fair_value_gap", "breaker_block"],
            min_score=85,
            max_risk_per_trade=0.02,  # 2% risk per trade
            max_daily_trades=10,
            trading_hours={"start": "08:00", "end": "17:00"},
            symbols=["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"],
            timeframes=["M15", "H1", "H4"],
            parameters={
                "order_block_strength": 0.7,
                "fvg_min_size": 10,  # pips
                "confluence_required": True,
                "trend_filter": True,
                "volume_confirmation": True
            }
        )
        
        # Scalping Strategy
        scalping_strategy = TradingStrategy(
            name="ICT_Scalping",
            description="High-frequency ICT scalping with quick entries",
            signal_types=["order_block", "fair_value_gap"],
            min_score=75,
            max_risk_per_trade=0.01,  # 1% risk per trade
            max_daily_trades=50,
            trading_hours={"start": "07:00", "end": "18:00"},
            symbols=["EURUSD", "GBPUSD", "USDJPY"],
            timeframes=["M5", "M15"],
            parameters={
                "quick_tp": True,
                "tight_sl": True,
                "scalp_mode": True,
                "min_rr_ratio": 1.5
            }
        )
        
        # Conservative Strategy
        conservative_strategy = TradingStrategy(
            name="ICT_Conservative",
            description="Conservative ICT trading with high-probability setups",
            signal_types=["order_block", "breaker_block"],
            min_score=90,
            max_risk_per_trade=0.015,  # 1.5% risk per trade
            max_daily_trades=5,
            trading_hours={"start": "09:00", "end": "16:00"},
            symbols=["EURUSD", "GBPUSD", "XAUUSD"],
            timeframes=["H1", "H4", "D1"],
            parameters={
                "high_confluence": True,
                "strict_filters": True,
                "min_rr_ratio": 2.0,
                "trend_confirmation": True
            }
        )
        
        self.strategies = {
            "ICT_Smart_Money": ict_strategy,
            "ICT_Scalping": scalping_strategy,
            "ICT_Conservative": conservative_strategy
        }
    
    async def start_trading(
        self, 
        strategy_name: str, 
        symbols: List[str], 
        config: StrategyConfig
    ) -> Dict:
        """Start automated trading session"""
        
        if not await self._ensure_mt5_connection():
            raise Exception("MT5 connection failed")
        
        # Get strategy
        strategy = self.strategies.get(strategy_name)
        if not strategy:
            raise Exception(f"Strategy '{strategy_name}' not found")
        
        # Create session
        session_id = str(uuid.uuid4())
        session = TradingSession(session_id, strategy, config)
        
        # Override symbols if provided
        if symbols:
            strategy.symbols = symbols
        
        # Start session
        session.status = SessionStatus.RUNNING
        session.started_at = datetime.utcnow()
        session.is_running = True
        
        self.active_sessions[session_id] = session
        
        # Start trading loop in background
        asyncio.create_task(self._trading_loop(session))
        
        logger.info(f"Started trading session {session_id} with strategy {strategy_name}")
        
        return {
            "session_id": session_id,
            "strategy": strategy_name,
            "symbols": strategy.symbols,
            "started_at": session.started_at.isoformat()
        }
    
    async def stop_trading(self, session_id: str) -> Dict:
        """Stop trading session"""
        
        session = self.active_sessions.get(session_id)
        if not session:
            raise Exception(f"Session {session_id} not found")
        
        session.status = SessionStatus.STOPPED
        session.stopped_at = datetime.utcnow()
        session.is_running = False
        session.is_paused = False
        
        logger.info(f"Stopped trading session {session_id}")
        
        return session.get_performance_metrics()
    
    async def pause_session(self, session_id: str) -> str:
        """Pause trading session"""
        
        session = self.active_sessions.get(session_id)
        if not session:
            raise Exception(f"Session {session_id} not found")
        
        session.is_paused = True
        session.paused_at = datetime.utcnow()
        
        logger.info(f"Paused trading session {session_id}")
        
        return session.paused_at.isoformat()
    
    async def resume_session(self, session_id: str) -> str:
        """Resume paused trading session"""
        
        session = self.active_sessions.get(session_id)
        if not session:
            raise Exception(f"Session {session_id} not found")
        
        session.is_paused = False
        session.paused_at = None
        resumed_at = datetime.utcnow()
        
        logger.info(f"Resumed trading session {session_id}")
        
        return resumed_at.isoformat()
    
    async def _trading_loop(self, session: TradingSession):
        """Main trading loop for session"""
        
        logger.info(f"Starting trading loop for session {session.session_id}")
        
        while session.is_running:
            try:
                if session.is_paused:
                    await asyncio.sleep(5)
                    continue
                
                # Check trading hours
                if not self._is_trading_time(session.strategy):
                    await asyncio.sleep(60)  # Check every minute
                    continue
                
                # Check daily trade limit
                if self._has_reached_daily_limit(session):
                    logger.info(f"Daily trade limit reached for session {session.session_id}")
                    await asyncio.sleep(300)  # Wait 5 minutes
                    continue
                
                # Get signals for each symbol
                for symbol in session.strategy.symbols:
                    if not session.is_running:
                        break
                    
                    await self._process_symbol_signals(session, symbol)
                
                # Wait before next iteration
                await asyncio.sleep(session.config.signal_check_interval)
                
            except Exception as e:
                logger.error(f"Error in trading loop for session {session.session_id}: {e}")
                await asyncio.sleep(30)  # Wait 30 seconds on error
        
        logger.info(f"Trading loop ended for session {session.session_id}")
    
    async def _process_symbol_signals(self, session: TradingSession, symbol: str):
        """Process signals for a specific symbol"""
        
        try:
            # Get market data for all timeframes
            for timeframe in session.strategy.timeframes:
                if not session.is_running or session.is_paused:
                    break
                
                # Get candlestick data
                rates = await self.mt5_service.get_rates(symbol, timeframe, 100)
                if not rates:
                    continue
                
                # Detect signals
                signals = await self._detect_signals(session.strategy, symbol, timeframe, rates)
                
                # Process each signal
                for signal in signals:
                    if not session.is_running or session.is_paused:
                        break
                    
                    session.add_signal(signal)
                    
                    # Check if signal meets criteria
                    if await self._should_trade_signal(session, signal):
                        await self._execute_trade(session, signal)
                
        except Exception as e:
            logger.error(f"Error processing signals for {symbol}: {e}")
    
    async def _detect_signals(
        self, 
        strategy: TradingStrategy, 
        symbol: str, 
        timeframe: str, 
        rates: List[Dict]
    ) -> List[Dict]:
        """Detect ICT signals based on strategy"""
        
        signals = []
        
        try:
            # Order Block signals
            if "order_block" in strategy.signal_types:
                ob_signals = self.order_block_detector.detect(rates)
                for signal in ob_signals:
                    signal.update({
                        "type": "order_block",
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    signals.append(signal)
            
            # Fair Value Gap signals
            if "fair_value_gap" in strategy.signal_types:
                fvg_signals = self.fvg_detector.detect(rates)
                for signal in fvg_signals:
                    signal.update({
                        "type": "fair_value_gap",
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    signals.append(signal)
            
            # Breaker Block signals
            if "breaker_block" in strategy.signal_types:
                bb_signals = self.breaker_detector.detect(rates)
                for signal in bb_signals:
                    signal.update({
                        "type": "breaker_block",
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    signals.append(signal)
            
            # Score all signals
            for signal in signals:
                score = self.signal_scorer.score_signal(signal, rates)
                signal["score"] = score
            
            # Filter by minimum score
            signals = [s for s in signals if s["score"] >= strategy.min_score]
            
        except Exception as e:
            logger.error(f"Error detecting signals: {e}")
        
        return signals
    
    async def _should_trade_signal(self, session: TradingSession, signal: Dict) -> bool:
        """Determine if signal should be traded"""
        
        try:
            # Check score threshold
            if signal["score"] < session.strategy.min_score:
                return False
            
            # Check if we already have position on this symbol
            positions = await self.mt5_service.get_positions(signal["symbol"])
            if positions:
                return False  # Don't trade if already have position
            
            # Check risk management
            account_info = await self.mt5_service.get_account_info()
            if not account_info:
                return False
            
            # Calculate position size
            risk_amount = account_info["balance"] * session.strategy.max_risk_per_trade
            position_size = self._calculate_position_size(signal, risk_amount)
            
            if position_size <= 0:
                return False
            
            # Check confluence if required
            if session.strategy.parameters.get("confluence_required", False):
                if not self._has_confluence(signal):
                    return False
            
            # Check trend filter if enabled
            if session.strategy.parameters.get("trend_filter", False):
                if not self._trend_aligned(signal):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking signal criteria: {e}")
            return False
    
    async def _execute_trade(self, session: TradingSession, signal: Dict):
        """Execute trade based on signal"""
        
        try:
            # Get account info
            account_info = await self.mt5_service.get_account_info()
            if not account_info:
                logger.error("Cannot get account info for trade execution")
                return
            
            # Calculate trade parameters
            risk_amount = account_info["balance"] * session.strategy.max_risk_per_trade
            position_size = self._calculate_position_size(signal, risk_amount)
            
            # Determine trade direction
            trade_type = "buy" if signal.get("direction") == "bullish" else "sell"
            
            # Get current price
            symbol_info = await self.mt5_service.get_symbol_info(signal["symbol"])
            if not symbol_info:
                logger.error(f"Cannot get symbol info for {signal['symbol']}")
                return
            
            current_price = symbol_info["bid"] if trade_type == "sell" else symbol_info["ask"]
            
            # Calculate SL and TP
            sl_price = self._calculate_stop_loss(signal, current_price, trade_type)
            tp_price = self._calculate_take_profit(signal, current_price, trade_type, session.strategy)
            
            # Execute trade
            trade_request = {
                "symbol": signal["symbol"],
                "volume": position_size,
                "type": trade_type,
                "price": current_price,
                "sl": sl_price,
                "tp": tp_price,
                "comment": f"AutoTrader-{session.strategy.name}-{signal['type']}-Score:{signal['score']}"
            }
            
            result = await self.mt5_service.send_order(trade_request)
            
            if result and result.get("success"):
                # Create trade result
                trade_result = TradeResult(
                    session_id=session.session_id,
                    signal_id=signal.get("id", str(uuid.uuid4())),
                    symbol=signal["symbol"],
                    trade_type=trade_type,
                    volume=position_size,
                    entry_price=current_price,
                    sl_price=sl_price,
                    tp_price=tp_price,
                    signal_score=signal["score"],
                    timestamp=datetime.utcnow(),
                    ticket=result.get("order", 0),
                    profit=0.0,  # Will be updated when closed
                    status="open"
                )
                
                session.add_trade(trade_result)
                
                logger.info(
                    f"Trade executed for session {session.session_id}: "
                    f"{trade_type} {position_size} {signal['symbol']} at {current_price}"
                )
            else:
                logger.error(f"Trade execution failed: {result}")
                
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
    
    def _calculate_position_size(self, signal: Dict, risk_amount: float) -> float:
        """Calculate position size based on risk"""
        
        try:
            # Get signal levels
            entry_price = signal.get("entry_price", 0)
            sl_price = signal.get("sl_price", 0)
            
            if entry_price <= 0 or sl_price <= 0:
                return 0.01  # Default minimum size
            
            # Calculate risk in pips
            risk_pips = abs(entry_price - sl_price) * 10000  # Assuming 4-digit quotes
            
            if risk_pips <= 0:
                return 0.01
            
            # Calculate position size
            # Risk per pip = Risk amount / Risk pips
            # Position size = Risk per pip / Pip value
            pip_value = 1.0  # Simplified, should be calculated based on symbol
            position_size = risk_amount / (risk_pips * pip_value)
            
            # Apply limits
            position_size = max(0.01, min(position_size, 10.0))
            
            return round(position_size, 2)
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return 0.01
    
    def _calculate_stop_loss(self, signal: Dict, current_price: float, trade_type: str) -> float:
        """Calculate stop loss price"""
        
        try:
            # Use signal's suggested SL if available
            if "sl_price" in signal:
                return signal["sl_price"]
            
            # Default SL calculation
            sl_pips = 50  # Default 50 pips SL
            pip_size = 0.0001  # For 4-digit quotes
            
            if trade_type == "buy":
                return current_price - (sl_pips * pip_size)
            else:
                return current_price + (sl_pips * pip_size)
                
        except Exception as e:
            logger.error(f"Error calculating stop loss: {e}")
            return current_price * 0.99 if trade_type == "buy" else current_price * 1.01
    
    def _calculate_take_profit(
        self, 
        signal: Dict, 
        current_price: float, 
        trade_type: str, 
        strategy: TradingStrategy
    ) -> float:
        """Calculate take profit price"""
        
        try:
            # Use signal's suggested TP if available
            if "tp_price" in signal:
                return signal["tp_price"]
            
            # Calculate based on risk-reward ratio
            min_rr = strategy.parameters.get("min_rr_ratio", 2.0)
            sl_distance = abs(current_price - self._calculate_stop_loss(signal, current_price, trade_type))
            tp_distance = sl_distance * min_rr
            
            if trade_type == "buy":
                return current_price + tp_distance
            else:
                return current_price - tp_distance
                
        except Exception as e:
            logger.error(f"Error calculating take profit: {e}")
            return current_price * 1.02 if trade_type == "buy" else current_price * 0.98
    
    def _is_trading_time(self, strategy: TradingStrategy) -> bool:
        """Check if current time is within trading hours"""
        
        try:
            now = datetime.utcnow().time()
            start_time = datetime.strptime(strategy.trading_hours["start"], "%H:%M").time()
            end_time = datetime.strptime(strategy.trading_hours["end"], "%H:%M").time()
            
            return start_time <= now <= end_time
            
        except Exception as e:
            logger.error(f"Error checking trading time: {e}")
            return True  # Default to allow trading
    
    def _has_reached_daily_limit(self, session: TradingSession) -> bool:
        """Check if daily trade limit has been reached"""
        
        try:
            today = datetime.utcnow().date()
            today_trades = [
                t for t in session.trades 
                if t.timestamp.date() == today
            ]
            
            return len(today_trades) >= session.strategy.max_daily_trades
            
        except Exception as e:
            logger.error(f"Error checking daily limit: {e}")
            return False
    
    def _has_confluence(self, signal: Dict) -> bool:
        """Check if signal has confluence factors"""
        
        # Simplified confluence check
        confluence_factors = 0
        
        if signal.get("trend_aligned"):
            confluence_factors += 1
        
        if signal.get("volume_confirmation"):
            confluence_factors += 1
        
        if signal.get("structure_break"):
            confluence_factors += 1
        
        if signal.get("fibonacci_level"):
            confluence_factors += 1
        
        return confluence_factors >= 2
    
    def _trend_aligned(self, signal: Dict) -> bool:
        """Check if signal is aligned with trend"""
        
        # Simplified trend check
        return signal.get("trend_aligned", True)
    
    async def _ensure_mt5_connection(self) -> bool:
        """Ensure MT5 connection is active"""
        
        try:
            if not self.mt5_service.is_connected():
                return await self.mt5_service.connect()
            return True
            
        except Exception as e:
            logger.error(f"MT5 connection error: {e}")
            return False
    
    # Public interface methods
    
    def strategy_exists(self, strategy_name: str) -> bool:
        """Check if strategy exists"""
        return strategy_name in self.strategies
    
    async def get_status(self) -> AutoTraderStatus:
        """Get current auto trader status"""
        
        active_sessions = [
            session.get_performance_metrics() 
            for session in self.active_sessions.values()
            if session.is_running
        ]
        
        total_profit = sum(session.total_profit for session in self.active_sessions.values())
        total_trades = sum(session.total_trades for session in self.active_sessions.values())
        
        return AutoTraderStatus(
            is_running=len(active_sessions) > 0,
            active_sessions=len(active_sessions),
            total_sessions=len(self.active_sessions),
            total_profit=total_profit,
            total_trades=total_trades,
            mt5_connected=await self._ensure_mt5_connection(),
            sessions=active_sessions
        )
    
    async def get_session_status(self, session_id: str) -> Optional[Dict]:
        """Get specific session status"""
        
        session = self.active_sessions.get(session_id)
        if not session:
            return None
        
        return session.get_performance_metrics()
    
    def get_available_strategies(self) -> List[TradingStrategy]:
        """Get list of available strategies"""
        return list(self.strategies.values())
    
    async def create_strategy(self, strategy: TradingStrategy) -> str:
        """Create new trading strategy"""
        
        self.strategies[strategy.name] = strategy
        logger.info(f"Created new strategy: {strategy.name}")
        return strategy.name
    
    async def update_strategy(self, strategy_name: str, strategy: TradingStrategy) -> bool:
        """Update existing strategy"""
        
        if strategy_name not in self.strategies:
            return False
        
        self.strategies[strategy_name] = strategy
        logger.info(f"Updated strategy: {strategy_name}")
        return True
    
    async def delete_strategy(self, strategy_name: str) -> bool:
        """Delete strategy"""
        
        if strategy_name not in self.strategies:
            return False
        
        # Check if strategy is in use
        active_sessions = [
            s for s in self.active_sessions.values() 
            if s.strategy.name == strategy_name and s.is_running
        ]
        
        if active_sessions:
            raise Exception(f"Cannot delete strategy '{strategy_name}' - it's currently in use")
        
        del self.strategies[strategy_name]
        logger.info(f"Deleted strategy: {strategy_name}")
        return True
    
    async def get_session_trades(
        self, 
        session_id: str, 
        limit: int = 100, 
        offset: int = 0
    ) -> List[TradeResult]:
        """Get trades for session"""
        
        session = self.active_sessions.get(session_id)
        if not session:
            return []
        
        trades = session.trades[offset:offset + limit]
        return trades
    
    async def get_session_performance(self, session_id: str) -> Optional[Dict]:
        """Get session performance metrics"""
        
        session = self.active_sessions.get(session_id)
        if not session:
            return None
        
        return session.get_performance_metrics()
    
    async def emergency_stop_all(self) -> List[str]:
        """Emergency stop all active sessions"""
        
        stopped_sessions = []
        
        for session_id, session in self.active_sessions.items():
            if session.is_running:
                session.is_running = False
                session.status = SessionStatus.STOPPED
                session.stopped_at = datetime.utcnow()
                stopped_sessions.append(session_id)
        
        logger.warning(f"Emergency stop executed for {len(stopped_sessions)} sessions")
        return stopped_sessions
    
    async def get_session_signals(self, session_id: str, limit: int = 50) -> List[Dict]:
        """Get recent signals for session"""
        
        session = self.active_sessions.get(session_id)
        if not session:
            return []
        
        # Return most recent signals
        return session.signals[-limit:]
    
    async def update_session_config(self, session_id: str, config: StrategyConfig) -> str:
        """Update session configuration"""
        
        session = self.active_sessions.get(session_id)
        if not session:
            raise Exception(f"Session {session_id} not found")
        
        session.config = config
        updated_at = datetime.utcnow()
        
        logger.info(f"Updated configuration for session {session_id}")
        return updated_at.isoformat()
    
    async def monitor_trading_session(self, session_id: str):
        """Background task to monitor trading session"""
        
        session = self.active_sessions.get(session_id)
        if not session:
            return
        
        logger.info(f"Starting monitoring for session {session_id}")
        
        while session.is_running:
            try:
                # Update open positions
                await self._update_open_positions(session)
                
                # Check for session health
                await self._check_session_health(session)
                
                # Wait before next check
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error monitoring session {session_id}: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _update_open_positions(self, session: TradingSession):
        """Update open positions for session"""
        
        try:
            for trade in session.trades:
                if trade.status == "open":
                    # Get current position info
                    positions = await self.mt5_service.get_positions(trade.symbol)
                    
                    # Find matching position
                    for pos in positions:
                        if pos.get("ticket") == trade.ticket:
                            # Update profit
                            trade.profit = pos.get("profit", 0)
                            break
                    
        except Exception as e:
            logger.error(f"Error updating positions: {e}")
    
    async def _check_session_health(self, session: TradingSession):
        """Check session health and performance"""
        
        try:
            # Check if session has been running too long without trades
            if session.total_trades == 0 and session.started_at:
                runtime = datetime.utcnow() - session.started_at
                if runtime.total_seconds() > 3600:  # 1 hour
                    logger.warning(f"Session {session.session_id} has no trades after 1 hour")
            
            # Check for excessive losses
            if session.total_profit < -1000:  # $1000 loss threshold
                logger.warning(f"Session {session.session_id} has significant losses: ${session.total_profit}")
            
        except Exception as e:
            logger.error(f"Error checking session health: {e}")
    
    async def health_check(self) -> Dict:
        """Health check for auto trader service"""
        
        try:
            mt5_connected = await self._ensure_mt5_connection()
            
            return {
                "status": "healthy",
                "mt5_connected": mt5_connected,
                "active_sessions": len([s for s in self.active_sessions.values() if s.is_running]),
                "total_sessions": len(self.active_sessions),
                "available_strategies": len(self.strategies),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            } 