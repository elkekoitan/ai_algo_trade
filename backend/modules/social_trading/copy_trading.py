"""
Copy Trading Engine
Automatically copies trades from successful traders to followers.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import uuid

logger = logging.getLogger(__name__)

class CopyStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"

@dataclass
class CopyRelationship:
    id: str
    follower_id: str
    leader_id: str
    allocation_amount: float
    copy_percentage: float
    max_risk_per_trade: float
    status: CopyStatus
    created_at: datetime
    performance: Dict[str, float]

@dataclass
class TradeExecution:
    id: str
    original_trade_id: str
    leader_id: str
    follower_id: str
    symbol: str
    action: str
    original_size: float
    copied_size: float
    entry_price: float
    exit_price: Optional[float]
    pnl: float
    executed_at: datetime

class CopyTradingEngine:
    """Advanced copy trading engine with intelligent position sizing."""
    
    def __init__(self):
        self.copy_relationships: Dict[str, CopyRelationship] = {}
        self.active_trades: Dict[str, TradeExecution] = {}
        self.performance_tracker: Dict[str, Dict] = {}
        
    async def create_copy_relationship(self, follower_id: str, leader_id: str, 
                                       allocation: float, copy_percentage: float = 100.0,
                                       max_risk: float = 0.02) -> str:
        """Create new copy trading relationship."""
        try:
            relationship_id = str(uuid.uuid4())
            
            relationship = CopyRelationship(
                id=relationship_id,
                follower_id=follower_id,
                leader_id=leader_id,
                allocation_amount=allocation,
                copy_percentage=copy_percentage,
                max_risk_per_trade=max_risk,
                status=CopyStatus.ACTIVE,
                created_at=datetime.now(),
                performance={'total_return': 0.0, 'win_rate': 0.0, 'trades_copied': 0}
            )
            
            self.copy_relationships[relationship_id] = relationship
            logger.info(f"Copy relationship created: {follower_id} -> {leader_id}")
            
            return relationship_id
            
        except Exception as e:
            logger.error(f"Error creating copy relationship: {e}")
            raise

    async def execute_copy_trade(self, leader_trade: Dict[str, Any]) -> List[TradeExecution]:
        """Execute copy trades for all followers of a leader."""
        executions = []
        
        try:
            leader_id = leader_trade['trader_id']
            
            # Find all active copy relationships for this leader
            followers = [rel for rel in self.copy_relationships.values() 
                        if rel.leader_id == leader_id and rel.status == CopyStatus.ACTIVE]
            
            for relationship in followers:
                try:
                    # Calculate position size for follower
                    copied_size = self._calculate_copy_size(leader_trade, relationship)
                    
                    if copied_size > 0:
                        execution = TradeExecution(
                            id=str(uuid.uuid4()),
                            original_trade_id=leader_trade['id'],
                            leader_id=leader_id,
                            follower_id=relationship.follower_id,
                            symbol=leader_trade['symbol'],
                            action=leader_trade['action'],
                            original_size=leader_trade['size'],
                            copied_size=copied_size,
                            entry_price=leader_trade['price'],
                            exit_price=None,
                            pnl=0.0,
                            executed_at=datetime.now()
                        )
                        
                        # Execute the trade (integrate with trading system)
                        await self._execute_trade(execution)
                        
                        executions.append(execution)
                        self.active_trades[execution.id] = execution
                        
                        # Update relationship performance
                        relationship.performance['trades_copied'] += 1
                        
                except Exception as e:
                    logger.error(f"Error copying trade for follower {relationship.follower_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Error executing copy trades: {e}")
            
        return executions
    
    def _calculate_copy_size(self, leader_trade: Dict[str, Any], 
                           relationship: CopyRelationship) -> float:
        """Calculate appropriate position size for copy trade."""
        try:
            # Base calculation using allocation and copy percentage
            base_size = (relationship.allocation_amount / leader_trade['price']) * \
                       (relationship.copy_percentage / 100.0)
            
            # Apply risk management
            max_risk_amount = relationship.allocation_amount * relationship.max_risk_per_trade
            max_size_by_risk = max_risk_amount / leader_trade['price']
            
            # Take the smaller of the two
            final_size = min(base_size, max_size_by_risk)
            
            return max(0, final_size)
            
        except Exception as e:
            logger.error(f"Error calculating copy size: {e}")
            return 0.0
    
    async def _execute_trade(self, execution: TradeExecution):
        """Execute the actual trade (integrate with trading system)."""
        try:
            # This would integrate with the actual trading system
            # For now, simulate execution
            logger.info(f"Executing copy trade: {execution.symbol} {execution.action} {execution.copied_size}")
            
            # Here you would call the actual trading API
            # await trading_service.place_order(...)
            
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            raise
    
    async def get_copy_performance(self, relationship_id: str) -> Dict[str, Any]:
        """Get performance metrics for copy relationship."""
        try:
            relationship = self.copy_relationships.get(relationship_id)
            if not relationship:
                return {}
            
            # Calculate detailed performance metrics
            follower_trades = [trade for trade in self.active_trades.values() 
                             if trade.follower_id == relationship.follower_id]
            
            total_pnl = sum(trade.pnl for trade in follower_trades if trade.exit_price)
            winning_trades = len([t for t in follower_trades if t.pnl > 0])
            total_trades = len([t for t in follower_trades if t.exit_price])
            
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            
            return {
                'relationship_id': relationship_id,
                'total_pnl': total_pnl,
                'total_return_pct': (total_pnl / relationship.allocation_amount * 100) if relationship.allocation_amount > 0 else 0,
                'win_rate': win_rate,
                'total_trades': total_trades,
                'trades_copied': relationship.performance['trades_copied'],
                'created_at': relationship.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting copy performance: {e}")
            return {} 