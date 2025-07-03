"""
Strategy Factory and Registry

Factory pattern implementation for creating and managing trading strategies.
"""

from typing import Type, Dict, List, Optional, Any
from dataclasses import dataclass
import inspect
import importlib
import logging
from datetime import datetime

from .base import IStrategy, StrategyBase

logger = logging.getLogger(__name__)


@dataclass
class StrategyInfo:
    """Information about a registered strategy"""
    strategy_id: str
    class_name: str
    module_path: str
    display_name: str
    description: str
    version: str
    author: str
    tags: List[str]
    parameters_schema: Dict[str, Any]
    created_at: datetime
    is_active: bool = True


class StrategyRegistry:
    """
    Central registry for all available trading strategies.
    Manages strategy metadata and provides discovery functionality.
    """
    
    def __init__(self):
        self._strategies: Dict[str, StrategyInfo] = {}
        self._strategy_classes: Dict[str, Type[IStrategy]] = {}
        
    def register(
        self,
        strategy_id: str,
        strategy_class: Type[IStrategy],
        display_name: str,
        description: str,
        version: str = "1.0.0",
        author: str = "AI Algo Trade",
        tags: List[str] = None
    ) -> None:
        """
        Register a new strategy type.
        
        Args:
            strategy_id: Unique identifier for the strategy
            strategy_class: Strategy class (must inherit from IStrategy)
            display_name: Human-readable name
            description: Strategy description
            version: Strategy version
            author: Strategy author
            tags: List of tags for categorization
        """
        # Validate strategy class
        if not issubclass(strategy_class, IStrategy):
            raise ValueError(f"{strategy_class} must inherit from IStrategy")
        
        # Extract parameters schema from class
        parameters_schema = self._extract_parameters_schema(strategy_class)
        
        # Create strategy info
        strategy_info = StrategyInfo(
            strategy_id=strategy_id,
            class_name=strategy_class.__name__,
            module_path=strategy_class.__module__,
            display_name=display_name,
            description=description,
            version=version,
            author=author,
            tags=tags or [],
            parameters_schema=parameters_schema,
            created_at=datetime.now()
        )
        
        # Store in registry
        self._strategies[strategy_id] = strategy_info
        self._strategy_classes[strategy_id] = strategy_class
        
        logger.info(f"Registered strategy: {strategy_id} ({display_name})")
    
    def unregister(self, strategy_id: str) -> None:
        """Remove a strategy from the registry"""
        if strategy_id in self._strategies:
            del self._strategies[strategy_id]
            del self._strategy_classes[strategy_id]
            logger.info(f"Unregistered strategy: {strategy_id}")
    
    def get_strategy_info(self, strategy_id: str) -> Optional[StrategyInfo]:
        """Get information about a specific strategy"""
        return self._strategies.get(strategy_id)
    
    def get_strategy_class(self, strategy_id: str) -> Optional[Type[IStrategy]]:
        """Get strategy class by ID"""
        return self._strategy_classes.get(strategy_id)
    
    def list_strategies(
        self,
        tags: List[str] = None,
        active_only: bool = True
    ) -> List[StrategyInfo]:
        """
        List all registered strategies.
        
        Args:
            tags: Filter by tags (strategies must have all specified tags)
            active_only: Only return active strategies
            
        Returns:
            List of strategy information
        """
        strategies = list(self._strategies.values())
        
        # Filter by active status
        if active_only:
            strategies = [s for s in strategies if s.is_active]
        
        # Filter by tags
        if tags:
            strategies = [
                s for s in strategies
                if all(tag in s.tags for tag in tags)
            ]
        
        return strategies
    
    def search_strategies(self, query: str) -> List[StrategyInfo]:
        """
        Search strategies by name or description.
        
        Args:
            query: Search query
            
        Returns:
            List of matching strategies
        """
        query_lower = query.lower()
        results = []
        
        for strategy in self._strategies.values():
            if (query_lower in strategy.display_name.lower() or
                query_lower in strategy.description.lower() or
                any(query_lower in tag.lower() for tag in strategy.tags)):
                results.append(strategy)
        
        return results
    
    def _extract_parameters_schema(self, strategy_class: Type[IStrategy]) -> Dict[str, Any]:
        """Extract parameter schema from strategy class"""
        # Try to get from class attribute
        if hasattr(strategy_class, "PARAMETERS_SCHEMA"):
            return strategy_class.PARAMETERS_SCHEMA
        
        # Try to extract from docstring or annotations
        schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        # Basic schema - can be enhanced
        return schema
    
    def load_from_module(self, module_path: str) -> int:
        """
        Load strategies from a Python module.
        
        Args:
            module_path: Path to module (e.g., 'strategies.momentum')
            
        Returns:
            Number of strategies loaded
        """
        try:
            module = importlib.import_module(module_path)
            loaded_count = 0
            
            # Find all strategy classes in module
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, IStrategy) and obj != IStrategy and obj != StrategyBase:
                    # Auto-register found strategies
                    strategy_id = getattr(obj, "STRATEGY_ID", name.lower())
                    display_name = getattr(obj, "DISPLAY_NAME", name)
                    description = getattr(obj, "DESCRIPTION", obj.__doc__ or "")
                    version = getattr(obj, "VERSION", "1.0.0")
                    author = getattr(obj, "AUTHOR", "AI Algo Trade")
                    tags = getattr(obj, "TAGS", [])
                    
                    self.register(
                        strategy_id=strategy_id,
                        strategy_class=obj,
                        display_name=display_name,
                        description=description,
                        version=version,
                        author=author,
                        tags=tags
                    )
                    loaded_count += 1
            
            logger.info(f"Loaded {loaded_count} strategies from {module_path}")
            return loaded_count
            
        except ImportError as e:
            logger.error(f"Failed to load module {module_path}: {e}")
            return 0


class StrategyFactory:
    """
    Factory for creating strategy instances.
    Uses the registry to create strategies by ID.
    """
    
    def __init__(self, registry: StrategyRegistry, event_bus=None):
        self.registry = registry
        self.event_bus = event_bus
        self._instances: Dict[str, IStrategy] = {}
    
    def create_strategy(
        self,
        strategy_id: str,
        instance_id: str,
        config: Dict[str, Any] = None
    ) -> IStrategy:
        """
        Create a new strategy instance.
        
        Args:
            strategy_id: ID of the strategy type to create
            instance_id: Unique ID for this instance
            config: Strategy configuration
            
        Returns:
            Strategy instance
            
        Raises:
            ValueError: If strategy_id is not registered
        """
        # Get strategy class from registry
        strategy_class = self.registry.get_strategy_class(strategy_id)
        if not strategy_class:
            raise ValueError(f"Strategy '{strategy_id}' not found in registry")
        
        # Create instance
        try:
            # Check if strategy accepts event_bus in constructor
            sig = inspect.signature(strategy_class.__init__)
            if "event_bus" in sig.parameters:
                strategy = strategy_class(
                    strategy_id=instance_id,
                    event_bus=self.event_bus
                )
            else:
                strategy = strategy_class(strategy_id=instance_id)
                # Set event_bus manually if base class
                if hasattr(strategy, "event_bus"):
                    strategy.event_bus = self.event_bus
            
            # Initialize with config
            if config:
                import asyncio
                if asyncio.iscoroutinefunction(strategy.initialize):
                    # Handle async initialization
                    loop = asyncio.get_event_loop()
                    loop.create_task(strategy.initialize(config))
                else:
                    strategy.initialize(config)
            
            # Store instance
            self._instances[instance_id] = strategy
            
            # Emit creation event
            if self.event_bus:
                self.event_bus.emit(
                    "strategy.created",
                    {
                        "strategy_id": strategy_id,
                        "instance_id": instance_id,
                        "config": config
                    }
                )
            
            logger.info(f"Created strategy instance: {instance_id} (type: {strategy_id})")
            return strategy
            
        except Exception as e:
            logger.error(f"Failed to create strategy {strategy_id}: {e}")
            raise
    
    def get_instance(self, instance_id: str) -> Optional[IStrategy]:
        """Get a strategy instance by ID"""
        return self._instances.get(instance_id)
    
    def list_instances(self) -> Dict[str, IStrategy]:
        """List all active strategy instances"""
        return self._instances.copy()
    
    def destroy_instance(self, instance_id: str) -> bool:
        """
        Destroy a strategy instance.
        
        Args:
            instance_id: ID of instance to destroy
            
        Returns:
            True if destroyed, False if not found
        """
        if instance_id in self._instances:
            strategy = self._instances[instance_id]
            
            # Call cleanup
            import asyncio
            if asyncio.iscoroutinefunction(strategy.cleanup):
                loop = asyncio.get_event_loop()
                loop.create_task(strategy.cleanup())
            else:
                strategy.cleanup()
            
            # Remove from instances
            del self._instances[instance_id]
            
            # Emit destruction event
            if self.event_bus:
                self.event_bus.emit(
                    "strategy.destroyed",
                    {"instance_id": instance_id}
                )
            
            logger.info(f"Destroyed strategy instance: {instance_id}")
            return True
        
        return False
    
    def create_from_config(self, config: Dict[str, Any]) -> IStrategy:
        """
        Create a strategy from a configuration dictionary.
        
        Config format:
        {
            "strategy_id": "momentum_scalper",
            "instance_id": "momentum_scalper_001",
            "parameters": {...},
            "risk_settings": {...}
        }
        """
        strategy_id = config.get("strategy_id")
        instance_id = config.get("instance_id", f"{strategy_id}_{datetime.now().timestamp()}")
        
        return self.create_strategy(
            strategy_id=strategy_id,
            instance_id=instance_id,
            config=config
        )


# Global registry instance
global_registry = StrategyRegistry()


def register_strategy(
    strategy_id: str,
    display_name: str,
    description: str,
    version: str = "1.0.0",
    author: str = "AI Algo Trade",
    tags: List[str] = None
):
    """
    Decorator for registering strategies.
    
    Usage:
        @register_strategy(
            strategy_id="momentum_scalper",
            display_name="Momentum Scalper",
            description="High-frequency momentum trading strategy",
            tags=["scalping", "momentum", "high-frequency"]
        )
        class MomentumScalper(StrategyBase):
            ...
    """
    def decorator(cls):
        global_registry.register(
            strategy_id=strategy_id,
            strategy_class=cls,
            display_name=display_name,
            description=description,
            version=version,
            author=author,
            tags=tags
        )
        
        # Add metadata to class
        cls.STRATEGY_ID = strategy_id
        cls.DISPLAY_NAME = display_name
        cls.DESCRIPTION = description
        cls.VERSION = version
        cls.AUTHOR = author
        cls.TAGS = tags
        
        return cls
    
    return decorator 