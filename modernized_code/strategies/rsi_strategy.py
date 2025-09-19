#!/usr/bin/env python3

from typing import Dict, Any, Optional

import pandas as pd
import numpy as np

from strategy_interface import StrategyInterface
from utils.logger import get_logger


class RSIStrategy(StrategyInterface):
    """RSI Strategy.
    
    Generates buy signals when RSI crosses below oversold level,
    and sell signals when RSI crosses above overbought level.
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
        if 'rsi' not in data.columns:
            self.logger.warning("RSI indicator not available")
            return None
        
        # Get the last two rows for crossover detection
        last_row = data.iloc[-1]
        prev_row = data.iloc[-2]
        
        # Get parameters
        oversold = self.params['oversold']
        overbought = self.params['overbought']
        
        # Check for oversold condition (buy signal)
        if prev_row['rsi'] < oversold and last_row['rsi'] >= oversold:
            return {
                'action': 'buy',
                'price': last_row['close'],
                'timestamp': last_row.name,
                'reason': f"RSI crossed above oversold level ({oversold})"
            }
        
        # Check for overbought condition (sell signal)
        elif prev_row['rsi'] > overbought and last_row['rsi'] <= overbought:
            return {
                'action': 'sell',
                'price': last_row['close'],
                'timestamp': last_row.name,
                'reason': f"RSI crossed below overbought level ({overbought})"
            }
        
        # No signal
        return None
    
    def get_name(self) -> str:
        """Get the name of the strategy.
        
        Returns:
            Strategy name
        """
        return "RSI Strategy"
    
    def get_description(self) -> str:
        """Get the description of the strategy.
        
        Returns:
            Strategy description
        """
        return (
            "Generates buy signals when RSI crosses above oversold level, "
            "and sell signals when RSI crosses below overbought level."
        )
    
    def get_default_params(self) -> Dict[str, Any]:
        """Get the default parameters for the strategy.
        
        Returns:
            Dictionary of default parameters
        """
        return {
            'rsi_period': 14,
            'oversold': 30,
            'overbought': 70
        }
