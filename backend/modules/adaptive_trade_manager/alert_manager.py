"""
Alert Manager for Adaptive Trade Manager

Generates and manages real-time alerts for the frontend.
"""
import asyncio
from typing import List, Dict
from datetime import datetime
import uuid

from backend.core.logger import get_logger
from .models import ManagedPosition, RiskMetrics, AdaptiveAction, AdaptiveAlert, RiskLevel

logger = get_logger(__name__)

class AlertManager:
    def __init__(self):
        self.active_alerts: List[AdaptiveAlert] = []
        self.alert_queue = asyncio.Queue()
        self.lock = asyncio.Lock()
        # Track sent alerts to avoid duplicates for a short period
        self.sent_alert_cache: Dict[str, datetime] = {}

    async def get_active_alerts(self) -> List[AdaptiveAlert]:
        """Returns a list of all currently active alerts."""
        async with self.lock:
            # Prune old alerts if necessary
            self.active_alerts = [a for a in self.active_alerts if (datetime.now() - a.timestamp).total_seconds() < 300]
            return self.active_alerts

    async def create_alert(self, position: ManagedPosition, risk: RiskMetrics, action: AdaptiveAction):
        """Creates a new alert and adds it to the queue."""
        
        # Debounce alerts: don't send the same type of alert for the same position within 60s
        cache_key = f"{position.ticket}:{action.action_type.value}"
        if cache_key in self.sent_alert_cache:
            if (datetime.now() - self.sent_alert_cache[cache_key]).total_seconds() < 60:
                return # Still within debounce period
        
        title = self._generate_alert_title(risk.risk_level, position.symbol)
        
        alert = AdaptiveAlert(
            alert_id=str(uuid.uuid4()),
            position_ticket=position.ticket,
            title=title,
            description=action.reasoning,
            risk_metrics=risk,
            recommended_action=action,
            urgency=self._calculate_urgency(risk)
        )
        
        await self.alert_queue.put(alert)
        async with self.lock:
            self.active_alerts.append(alert)
        
        self.sent_alert_cache[cache_key] = datetime.now()
        logger.info(f"New alert created for ticket {position.ticket}: {title}")

    def _generate_alert_title(self, risk_level: RiskLevel, symbol: str) -> str:
        """Generates a catchy title for the alert."""
        titles = {
            RiskLevel.CRITICAL: f"🚨 CRITICAL RISK on {symbol}!",
            RiskLevel.HIGH: f"⚠️ High Risk Warning on {symbol}",
            RiskLevel.MEDIUM: f"🔎 Opportunity/Risk on {symbol}",
            RiskLevel.LOW: f"🚀 Momentum Opportunity on {symbol}",
        }
        return titles.get(risk_level, f"Update for {symbol}")

    def _calculate_urgency(self, risk: RiskMetrics) -> int:
        """Determines the urgency of the alert."""
        if risk.risk_level == RiskLevel.CRITICAL:
            return 5
        if risk.risk_level == RiskLevel.HIGH:
            return 4
        if risk.news_impact_level > 1:
            return 4
        if risk.risk_level == RiskLevel.MEDIUM:
            return 3
        return 2 # Low risk opportunities are less "urgent"

    async def clear_alert(self, alert_id: str):
        """Removes an alert after it has been actioned or dismissed."""
        async with self.lock:
            self.active_alerts = [a for a in self.active_alerts if a.alert_id != alert_id]
            logger.info(f"Alert {alert_id} cleared.")

    async def get_next_alert_for_websocket(self) -> AdaptiveAlert:
        """Blocking call to get the next alert for a WebSocket consumer."""
        return await self.alert_queue.get() 