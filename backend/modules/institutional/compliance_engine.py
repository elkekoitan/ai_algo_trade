"""
Compliance Engine for Institutional Trading
Handles regulatory reporting, AML, trade surveillance, and audit trails.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import uuid

logger = logging.getLogger(__name__)

class ComplianceStatus(Enum):
    COMPLIANT = "compliant"
    FLAGGED = "flagged"
    VIOLATION = "violation"
    UNDER_REVIEW = "under_review"

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ComplianceAlert:
    id: str
    alert_type: str
    severity: RiskLevel
    trader_id: str
    description: str
    detected_at: datetime
    status: ComplianceStatus
    metadata: Dict[str, Any]

@dataclass
class AMLCheck:
    check_id: str
    entity_id: str
    entity_type: str
    risk_score: float
    sanctions_check: bool
    pep_check: bool
    adverse_media: bool
    result: ComplianceStatus
    checked_at: datetime

class ComplianceEngine:
    """Advanced compliance engine for institutional trading."""
    
    def __init__(self):
        self.compliance_rules: Dict[str, Any] = {}
        self.alerts: List[ComplianceAlert] = []
        self.aml_checks: List[AMLCheck] = []
        self.audit_trail: List[Dict[str, Any]] = []
        self.initialize_rules()
        
    def initialize_rules(self):
        """Initialize compliance rules."""
        self.compliance_rules = {
            'max_position_size': 1000000,  # $1M max position
            'max_daily_volume': 10000000,  # $10M daily volume
            'max_concentration': 0.10,     # 10% max concentration
            'suspicious_pattern_threshold': 5,  # 5 similar trades trigger review
            'large_trade_threshold': 100000,   # $100K triggers reporting
            'wash_trade_window': 300,      # 5 minutes wash trade detection
            'pnl_monitoring_threshold': 50000,  # $50K P&L monitoring
        }
    
    async def monitor_trade(self, trade_data: Dict[str, Any]) -> List[ComplianceAlert]:
        """Monitor trade for compliance violations."""
        alerts = []
        
        try:
            # Position size monitoring
            if trade_data.get('notional_value', 0) > self.compliance_rules['max_position_size']:
                alert = ComplianceAlert(
                    id=str(uuid.uuid4()),
                    alert_type="position_size_limit",
                    severity=RiskLevel.HIGH,
                    trader_id=trade_data.get('trader_id', ''),
                    description=f"Trade exceeds maximum position size limit",
                    detected_at=datetime.now(),
                    status=ComplianceStatus.FLAGGED,
                    metadata={'trade_id': trade_data.get('id'), 'value': trade_data.get('notional_value')}
                )
                alerts.append(alert)
            
            # Large trade reporting
            if trade_data.get('notional_value', 0) > self.compliance_rules['large_trade_threshold']:
                await self._generate_large_trade_report(trade_data)
            
            # Wash trade detection
            wash_trade_alert = await self._detect_wash_trading(trade_data)
            if wash_trade_alert:
                alerts.extend(wash_trade_alert)
            
            # Market manipulation detection
            manipulation_alert = await self._detect_market_manipulation(trade_data)
            if manipulation_alert:
                alerts.extend(manipulation_alert)
            
            # Store alerts
            self.alerts.extend(alerts)
            
            # Log to audit trail
            await self._log_audit_trail("trade_monitoring", trade_data, alerts)
            
        except Exception as e:
            logger.error(f"Error monitoring trade compliance: {e}")
            
        return alerts
    
    async def perform_aml_check(self, entity_id: str, entity_type: str = "trader") -> AMLCheck:
        """Perform Anti-Money Laundering check."""
        try:
            check_id = str(uuid.uuid4())
            
            # Simulate AML checks
            risk_score = await self._calculate_aml_risk_score(entity_id, entity_type)
            sanctions_check = await self._check_sanctions_list(entity_id)
            pep_check = await self._check_pep_list(entity_id)
            adverse_media = await self._check_adverse_media(entity_id)
            
            # Determine result
            if risk_score > 80 or not sanctions_check or pep_check:
                result = ComplianceStatus.VIOLATION
            elif risk_score > 60 or adverse_media:
                result = ComplianceStatus.FLAGGED
            else:
                result = ComplianceStatus.COMPLIANT
            
            aml_check = AMLCheck(
                check_id=check_id,
                entity_id=entity_id,
                entity_type=entity_type,
                risk_score=risk_score,
                sanctions_check=sanctions_check,
                pep_check=pep_check,
                adverse_media=adverse_media,
                result=result,
                checked_at=datetime.now()
            )
            
            self.aml_checks.append(aml_check)
            
            # Log to audit trail
            await self._log_audit_trail("aml_check", {'entity_id': entity_id}, [])
            
            return aml_check
            
        except Exception as e:
            logger.error(f"Error performing AML check: {e}")
            raise
    
    async def generate_regulatory_report(self, report_type: str, 
                                       start_date: datetime, 
                                       end_date: datetime) -> Dict[str, Any]:
        """Generate regulatory compliance report."""
        try:
            if report_type == "mifid_ii":
                return await self._generate_mifid_ii_report(start_date, end_date)
            elif report_type == "dodd_frank":
                return await self._generate_dodd_frank_report(start_date, end_date)
            elif report_type == "trade_surveillance":
                return await self._generate_surveillance_report(start_date, end_date)
            else:
                raise ValueError(f"Unknown report type: {report_type}")
                
        except Exception as e:
            logger.error(f"Error generating regulatory report: {e}")
            raise
    
    async def _detect_wash_trading(self, trade_data: Dict[str, Any]) -> List[ComplianceAlert]:
        """Detect potential wash trading patterns."""
        alerts = []
        
        try:
            trader_id = trade_data.get('trader_id')
            symbol = trade_data.get('symbol')
            timestamp = trade_data.get('timestamp', datetime.now())
            
            # Look for opposite trades within time window
            window_start = timestamp - timedelta(seconds=self.compliance_rules['wash_trade_window'])
            
            # This would query actual trade database
            # For simulation, create alert if random condition
            import random
            if random.random() < 0.05:  # 5% chance of wash trade detection
                alert = ComplianceAlert(
                    id=str(uuid.uuid4()),
                    alert_type="wash_trading",
                    severity=RiskLevel.CRITICAL,
                    trader_id=trader_id,
                    description=f"Potential wash trading detected for {symbol}",
                    detected_at=datetime.now(),
                    status=ComplianceStatus.VIOLATION,
                    metadata={'symbol': symbol, 'time_window': self.compliance_rules['wash_trade_window']}
                )
                alerts.append(alert)
                
        except Exception as e:
            logger.error(f"Error detecting wash trading: {e}")
            
        return alerts
    
    async def _detect_market_manipulation(self, trade_data: Dict[str, Any]) -> List[ComplianceAlert]:
        """Detect potential market manipulation."""
        alerts = []
        
        try:
            # Spoofing detection
            if await self._detect_spoofing(trade_data):
                alert = ComplianceAlert(
                    id=str(uuid.uuid4()),
                    alert_type="spoofing",
                    severity=RiskLevel.CRITICAL,
                    trader_id=trade_data.get('trader_id'),
                    description="Potential spoofing pattern detected",
                    detected_at=datetime.now(),
                    status=ComplianceStatus.VIOLATION,
                    metadata={'trade_id': trade_data.get('id')}
                )
                alerts.append(alert)
            
            # Layering detection
            if await self._detect_layering(trade_data):
                alert = ComplianceAlert(
                    id=str(uuid.uuid4()),
                    alert_type="layering",
                    severity=RiskLevel.HIGH,
                    trader_id=trade_data.get('trader_id'),
                    description="Potential layering pattern detected",
                    detected_at=datetime.now(),
                    status=ComplianceStatus.FLAGGED,
                    metadata={'trade_id': trade_data.get('id')}
                )
                alerts.append(alert)
                
        except Exception as e:
            logger.error(f"Error detecting market manipulation: {e}")
            
        return alerts
    
    async def _calculate_aml_risk_score(self, entity_id: str, entity_type: str) -> float:
        """Calculate AML risk score."""
        # Simulate risk calculation
        import random
        base_score = random.uniform(10, 90)
        
        # Add risk factors
        if entity_type == "high_risk_jurisdiction":
            base_score += 20
        
        return min(100, base_score)
    
    async def _check_sanctions_list(self, entity_id: str) -> bool:
        """Check entity against sanctions lists."""
        # Simulate sanctions check
        import random
        return random.random() > 0.02  # 2% chance of sanctions match
    
    async def _check_pep_list(self, entity_id: str) -> bool:
        """Check if entity is Politically Exposed Person."""
        # Simulate PEP check
        import random
        return random.random() < 0.01  # 1% chance of PEP match
    
    async def _check_adverse_media(self, entity_id: str) -> bool:
        """Check for adverse media coverage."""
        # Simulate adverse media check
        import random
        return random.random() < 0.05  # 5% chance of adverse media
    
    async def _detect_spoofing(self, trade_data: Dict[str, Any]) -> bool:
        """Detect spoofing patterns."""
        # Simulate spoofing detection
        import random
        return random.random() < 0.01  # 1% chance of spoofing detection
    
    async def _detect_layering(self, trade_data: Dict[str, Any]) -> bool:
        """Detect layering patterns."""
        # Simulate layering detection
        import random
        return random.random() < 0.02  # 2% chance of layering detection
    
    async def _generate_large_trade_report(self, trade_data: Dict[str, Any]):
        """Generate large trade report."""
        report = {
            'report_id': str(uuid.uuid4()),
            'trade_id': trade_data.get('id'),
            'trader_id': trade_data.get('trader_id'),
            'symbol': trade_data.get('symbol'),
            'notional_value': trade_data.get('notional_value'),
            'reported_at': datetime.now().isoformat()
        }
        
        # Store report (would send to regulatory authority)
        await self._log_audit_trail("large_trade_report", report, [])
    
    async def _generate_mifid_ii_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate MiFID II compliance report."""
        return {
            'report_type': 'mifid_ii',
            'period': {'start': start_date.isoformat(), 'end': end_date.isoformat()},
            'trade_count': len(self.audit_trail),
            'compliance_violations': len([a for a in self.alerts if a.status == ComplianceStatus.VIOLATION]),
            'generated_at': datetime.now().isoformat()
        }
    
    async def _generate_dodd_frank_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate Dodd-Frank compliance report."""
        return {
            'report_type': 'dodd_frank',
            'period': {'start': start_date.isoformat(), 'end': end_date.isoformat()},
            'swap_transactions': 0,  # Would count actual swap transactions
            'compliance_status': 'compliant',
            'generated_at': datetime.now().isoformat()
        }
    
    async def _generate_surveillance_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate trade surveillance report."""
        period_alerts = [a for a in self.alerts if start_date <= a.detected_at <= end_date]
        
        return {
            'report_type': 'trade_surveillance',
            'period': {'start': start_date.isoformat(), 'end': end_date.isoformat()},
            'total_alerts': len(period_alerts),
            'violations': len([a for a in period_alerts if a.status == ComplianceStatus.VIOLATION]),
            'alerts_by_type': self._group_alerts_by_type(period_alerts),
            'generated_at': datetime.now().isoformat()
        }
    
    def _group_alerts_by_type(self, alerts: List[ComplianceAlert]) -> Dict[str, int]:
        """Group alerts by type."""
        grouped = {}
        for alert in alerts:
            grouped[alert.alert_type] = grouped.get(alert.alert_type, 0) + 1
        return grouped
    
    async def _log_audit_trail(self, action: str, data: Dict[str, Any], alerts: List[ComplianceAlert]):
        """Log action to audit trail."""
        try:
            audit_entry = {
                'id': str(uuid.uuid4()),
                'timestamp': datetime.now().isoformat(),
                'action': action,
                'data': data,
                'alerts_generated': len(alerts),
                'user_id': data.get('trader_id', 'system')
            }
            
            self.audit_trail.append(audit_entry)
            
        except Exception as e:
            logger.error(f"Error logging audit trail: {e}")
    
    def get_compliance_summary(self) -> Dict[str, Any]:
        """Get compliance summary metrics."""
        return {
            'total_alerts': len(self.alerts),
            'violations': len([a for a in self.alerts if a.status == ComplianceStatus.VIOLATION]),
            'flagged_items': len([a for a in self.alerts if a.status == ComplianceStatus.FLAGGED]),
            'aml_checks_performed': len(self.aml_checks),
            'audit_trail_entries': len(self.audit_trail),
            'last_updated': datetime.now().isoformat()
        } 