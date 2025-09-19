#!/usr/bin/env python3

from typing import Dict, Any, Optional, Type, List

from strategy_interface import StrategyInterface
from strategies import AVAILABLE_STRATEGIES
from utils.logger import get_logger


class StrategyManager:
    """Manager for trading strategies."""
    
    def __init__(self):
        """Initialize the strategy manager."""
        self.logger = get_logger()
        self.strategies = {}
        self.strategy_params = {}
    
    def create_strategy(self, strategy_name: str) -> Optional[StrategyInterface]:
        """Create a strategy instance.
        
        Args:
            strategy_name: Name of the strategy to create
        
        Returns:
            Strategy instance or None if strategy not found
        """
        if strategy_name not in AVAILABLE_STRATEGIES:
            self.logger.error(f"Strategy not found: {strategy_name}")
            return None
        
        # Get strategy class
        strategy_class = AVAILABLE_STRATEGIES[strategy_name]
        
        # Get parameters for this strategy
        params = self.strategy_params.get(strategy_name, {})
        
        # Create strategy instance
        strategy = strategy_class(params)
        
        # Store strategy instance
        self.strategies[strategy_name] = strategy
        
        self.logger.info(f"Created strategy: {strategy_name}")
        return strategy
    
    def get_strategy(self, strategy_name: str) -> Optional[StrategyInterface]:
        """Get a strategy instance.
        
        Args:
            strategy_name: Name of the strategy to get
        
        Returns:
            Strategy instance or None if strategy not found
        """
        if strategy_name not in self.strategies:
            return self.create_strategy(strategy_name)
        
        return self.strategies[strategy_name]
    
    def configure_strategy(self, strategy_name: str, params: Dict[str, Any]) -> None:
        """Configure strategy parameters.
        
        Args:
            strategy_name: Name of the strategy to configure
            params: Strategy parameters
        """
        # Store parameters
        if strategy_name not in self.strategy_params:
            self.strategy_params[strategy_name] = {}
        
        self.strategy_params[strategy_name].update(params)
        
        # Update existing strategy instance if it exists
        if strategy_name in self.strategies:
            self.strategies[strategy_name].set_params(params)
        
        self.logger.info(f"Configured strategy {strategy_name} with params: {params}")
    
    def get_available_strategies(self) -> List[str]:
        """Get list of available strategies.
        
        Returns:
            List of strategy names
        """
        return list(AVAILABLE_STRATEGIES.keys())
    
    def get_strategy_info(self, strategy_name: str) -> Dict[str, Any]:
        """Get information about a strategy.
        
        Args:
            strategy_name: Name of the strategy
        
        Returns:
            Dictionary with strategy information
        """
        if strategy_name not in AVAILABLE_STRATEGIES:
            self.logger.error(f"Strategy not found: {strategy_name}")
            return {}
        
        # Create temporary instance to get info
        temp_strategy = AVAILABLE_STRATEGIES[strategy_name]()
        
        return {
            'name': temp_strategy.get_name(),
            'description': temp_strategy.get_description(),
            'default_params': temp_strategy.get_default_params(),
            'current_params': self.strategy_params.get(strategy_name, {})
        }
