"""
Position Monitor for Adaptive Trade Manager

Continuously tracks open positions from the MT5 terminal.
"""
import asyncio
from typing import Dict, List, Optional
from datetime import datetime
import MetaTrader5 as mt5

from backend.core.logger import get_logger
from backend.modules.mt5_integration.service import MT5Service
from .models import ManagedPosition

logger = get_logger(__name__)

class PositionMonitor:
    def __init__(self, mt5_service: MT5Service):
        self.mt5 = mt5_service
        self.managed_positions: Dict[int, ManagedPosition] = {}
        self.lock = asyncio.Lock()

    async def get_all_positions(self) -> List[ManagedPosition]:
        """Returns a list of all currently managed positions."""
        async with self.lock:
            return list(self.managed_positions.values())

    async def get_position(self, ticket: int) -> Optional[ManagedPosition]:
        """Returns a specific managed position by its ticket."""
        async with self.lock:
            return self.managed_positions.get(ticket)

    async def run(self):
        """Starts the continuous monitoring loop."""
        logger.info("Starting Position Monitor...")
        while True:
            try:
                await self.update_positions()
            except Exception as e:
                logger.error(f"Error in Position Monitor loop: {e}")
            await asyncio.sleep(2) # Update every 2 seconds

    async def update_positions(self):
        """Fetches and updates the state of all open positions."""
        if not self.mt5.connected:
            logger.warning("Position Monitor: MT5 not connected. Skipping update.")
            async with self.lock:
                self.managed_positions.clear()
            return

        positions = self.mt5.get_open_positions()
        if positions is None:
            logger.warning("Position Monitor: Failed to fetch open positions.")
            async with self.lock:
                self.managed_positions.clear()
            return
        
        current_tickets = {p.ticket for p in positions}
        
        async with self.lock:
            # Remove closed positions
            closed_tickets = [t for t in self.managed_positions if t not in current_tickets]
            for ticket in closed_tickets:
                logger.info(f"Position {ticket} closed. Removing from monitor.")
                del self.managed_positions[ticket]

            # Update existing and add new positions
            for pos in positions:
                is_new = pos.ticket not in self.managed_positions
                pips = self._calculate_pips(pos)
                
                managed_pos = ManagedPosition(
                    ticket=pos.ticket,
                    symbol=pos.symbol,
                    open_time=datetime.fromtimestamp(pos.time),
                    position_type='buy' if pos.type == mt5.ORDER_TYPE_BUY else 'sell',
                    volume=pos.volume,
                    open_price=pos.price_open,
                    current_price=pos.price_current,
                    stop_loss=pos.sl,
                    take_profit=pos.tp,
                    pnl=pos.profit,
                    pips=pips,
                    is_new=is_new
                )
                self.managed_positions[pos.ticket] = managed_pos
                if is_new:
                    logger.info(f"New position added to monitor: Ticket {pos.ticket} on {pos.symbol}")
    
    def _calculate_pips(self, position) -> float:
        """Calculates the pips for a given position."""
        if not position:
            return 0.0

        point = self.mt5.get_symbol_info(position.symbol).point
        if point == 0:
            return 0.0
            
        pips = (position.price_current - position.price_open) / point
        
        # Adjust for JPY pairs (and others) that have different pip decimal places
        if "JPY" in position.symbol:
            pips /= 100
        
        if position.type == mt5.ORDER_TYPE_SELL:
            pips = -pips
            
        return round(pips, 2) 