"""
Advanced Strategy Framework

AI-powered multi-strategy trading system with real-time adaptation.
Provides base classes, interfaces, and services for all trading strategies.
"""

from .base import IStrategy, StrategyBase, StrategySignal, ExecutionResult
from .factory import StrategyFactory, StrategyRegistry
from .optimizer import StrategyOptimizer, OptimizationGoals, OptimizedParameters
from .adapters import EventBusAdapter, StrategyEventHandler
from .risk import RiskAnalyzer, RiskAnalysis, EmergencyAction
from .market_context import MarketContextService, MarketContext
from .parameters import AdaptiveParameterService, ParameterAdjustment
from .performance import PerformanceTracker, PerformanceReport
from .alerts import AlertSystem, Alert, AlertType, AlertSeverity

__all__ = [
    # Base classes
    "IStrategy",
    "StrategyBase", 
    "StrategySignal",
    "ExecutionResult",
    
    # Factory and Registry
    "StrategyFactory",
    "StrategyRegistry",
    
    # Services
    "StrategyOptimizer",
    "OptimizationGoals",
    "OptimizedParameters",
    "EventBusAdapter",
    "StrategyEventHandler",
    "RiskAnalyzer",
    "RiskAnalysis",
    "EmergencyAction",
    "MarketContextService",
    "MarketContext",
    "AdaptiveParameterService",
    "ParameterAdjustment",
    "PerformanceTracker",
    "PerformanceReport",
    "AlertSystem",
    "Alert",
    "AlertType",
    "AlertSeverity"
] 