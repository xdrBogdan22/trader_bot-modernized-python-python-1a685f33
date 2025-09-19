#!/usr/bin/env python3

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

import pandas as pd


class StrategyInterface(ABC):
    """Interface for all trading strategies."""
    
    def __init__(self, params: Dict[str, Any] = None):
        """Initialize the strategy.
        
        Args:
            params: Strategy parameters
        """
        self.params = params or {}
    
    @abstractmethod
    def execute(self, data: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Execute the strategy on the given data.
        
        Args:
            data: DataFrame with price data and indicators
        
        Returns:
            Signal dictionary or None if no signal
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get the name of the strategy.
        
        Returns:
            Strategy name
        """
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Get the description of the strategy.
        
        Returns:
            Strategy description
        """
        pass
    
    @abstractmethod
    def get_default_params(self) -> Dict[str, Any]:
        """Get the default parameters for the strategy.
        
        Returns:
            Dictionary of default parameters
        """
        pass
    
    def set_params(self, params: Dict[str, Any]) -> None:
        """Set strategy parameters.
        
        Args:
            params: Strategy parameters
        """
        self.params.update(params)
    
    def get_params(self) -> Dict[str, Any]:
        """Get current strategy parameters.
        
        Returns:
            Dictionary of current parameters
        """
        return self.params.copy()
