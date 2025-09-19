#!/usr/bin/env python3

from typing import Dict, Any, Optional

import pandas as pd
import numpy as np

from strategy_interface import StrategyInterface
from utils.logger import get_logger


class SimpleMovingAverageCrossover(StrategyInterface):
    """Simple Moving Average Crossover Strategy.
    
    Generates buy signals when fast MA crosses above slow MA,
    and sell signals when fast MA crosses below slow MA.
    """
    
    def __init__(self, params: Dict[str, Any] = None):
        """Initialize the strategy.
        
        Args:
            params: Strategy parameters
        """
        super().__init__(params)
        self.logger = get_logger()
        
        # Set default parameters if not provided
        default_params = self.get_default_params()
        for key, value in default_params.items():
            if key not in self.params:
                self.params[key] = value
        
        self.logger.info(f"Initialized {self.get_name()} with params: {self.params}")
    
    def execute(self, data: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Execute the strategy on the given data.
        
        Args:
            data: DataFrame with price data and indicators
        
        Returns:
            Signal dictionary or None if no signal
        """
        if len(data) < 2:
            return None
        
        # Get parameters
        fast_ma = f"sma_{self.params['fast_period']}"
        slow_ma = f"sma_{self.params['slow_period']}"
        
        # Check if required indicators are available
        if fast_ma not in data.columns or slow_ma not in data.columns:
            self.logger.warning(f"Required indicators not available: {fast_ma}, {slow_ma}")
            return None
        
        # Get the last two rows for crossover detection
        last_row = data.iloc[-1]
        prev_row = data.iloc[-2]
        
        # Check for crossover
        if prev_row[fast_ma] <= prev_row[slow_ma] and last_row[fast_ma] > last_row[slow_ma]:
            # Fast MA crossed above slow MA -> Buy signal
            return {
                'action': 'buy',
                'price': last_row['close'],
                'timestamp': last_row.name,
                'reason': f"{fast_ma} crossed above {slow_ma}"
            }
        
        elif prev_row[fast_ma] >= prev_row[slow_ma] and last_row[fast_ma] < last_row[slow_ma]:
            # Fast MA crossed below slow MA -> Sell signal
            return {
                'action': 'sell',
                'price': last_row['close'],
                'timestamp': last_row.name,
                'reason': f"{fast_ma} crossed below {slow_ma}"
            }
        
        # No signal
        return None
    
    def get_name(self) -> str:
        """Get the name of the strategy.
        
        Returns:
            Strategy name
        """
        return "Simple Moving Average Crossover"
    
    def get_description(self) -> str:
        """Get the description of the strategy.
        
        Returns:
            Strategy description
        """
        return (
            "Generates buy signals when fast MA crosses above slow MA, "
            "and sell signals when fast MA crosses below slow MA."
        )
    
    def get_default_params(self) -> Dict[str, Any]:
        """Get the default parameters for the strategy.
        
        Returns:
            Dictionary of default parameters
        """
        return {
            'fast_period': 20,
            'slow_period': 50
        }
