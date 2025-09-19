#!/usr/bin/env python3

from typing import Dict, Any, Optional

import pandas as pd
import numpy as np

from strategy_interface import StrategyInterface
from utils.logger import get_logger


class MACDStrategy(StrategyInterface):
    """MACD Strategy.
    
    Generates buy signals when MACD line crosses above signal line,
    and sell signals when MACD line crosses below signal line.
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
        
        # Check if required indicators are available
        if 'macd' not in data.columns or 'macd_signal' not in data.columns:
            self.logger.warning("MACD indicators not available")
            return None
        
        # Get the last two rows for crossover detection
        last_row = data.iloc[-1]
        prev_row = data.iloc[-2]
        
        # Check for crossover
        if prev_row['macd'] <= prev_row['macd_signal'] and last_row['macd'] > last_row['macd_signal']:
            # MACD crossed above signal line -> Buy signal
            return {
                'action': 'buy',
                'price': last_row['close'],
                'timestamp': last_row.name,
                'reason': "MACD crossed above signal line"
            }
        
        elif prev_row['macd'] >= prev_row['macd_signal'] and last_row['macd'] < last_row['macd_signal']:
            # MACD crossed below signal line -> Sell signal
            return {
                'action': 'sell',
                'price': last_row['close'],
                'timestamp': last_row.name,
                'reason': "MACD crossed below signal line"
            }
        
        # No signal
        return None
    
    def get_name(self) -> str:
        """Get the name of the strategy.
        
        Returns:
            Strategy name
        """
        return "MACD Strategy"
    
    def get_description(self) -> str:
        """Get the description of the strategy.
        
        Returns:
            Strategy description
        """
        return (
            "Generates buy signals when MACD line crosses above signal line, "
            "and sell signals when MACD line crosses below signal line."
        )
    
    def get_default_params(self) -> Dict[str, Any]:
        """Get the default parameters for the strategy.
        
        Returns:
            Dictionary of default parameters
        """
        return {
            'fast_period': 12,
            'slow_period': 26,
            'signal_period': 9
        }
