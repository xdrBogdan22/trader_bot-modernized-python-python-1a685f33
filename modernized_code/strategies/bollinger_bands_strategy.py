#!/usr/bin/env python3

from typing import Dict, Any, Optional

import pandas as pd
import numpy as np

from strategy_interface import StrategyInterface
from utils.logger import get_logger


class BollingerBandsStrategy(StrategyInterface):
    """Bollinger Bands Strategy.
    
    Generates buy signals when price touches the lower band,
    and sell signals when price touches the upper band.
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
        if 'bb_upper' not in data.columns or 'bb_lower' not in data.columns:
            self.logger.warning("Bollinger Bands indicators not available")
            return None
        
        # Get the last row
        last_row = data.iloc[-1]
        
        # Get parameters
        band_touch_pct = self.params['band_touch_pct']
        
        # Calculate distance to bands as percentage
        lower_band_dist = (last_row['close'] - last_row['bb_lower']) / last_row['close'] * 100
        upper_band_dist = (last_row['bb_upper'] - last_row['close']) / last_row['close'] * 100
        
        # Check for lower band touch (buy signal)
        if lower_band_dist <= band_touch_pct:
            return {
                'action': 'buy',
                'price': last_row['close'],
                'timestamp': last_row.name,
                'reason': f"Price touched lower Bollinger Band (distance: {lower_band_dist:.2f}%)"
            }
        
        # Check for upper band touch (sell signal)
        elif upper_band_dist <= band_touch_pct:
            return {
                'action': 'sell',
                'price': last_row['close'],
                'timestamp': last_row.name,
                'reason': f"Price touched upper Bollinger Band (distance: {upper_band_dist:.2f}%)"
            }
        
        # No signal
        return None
    
    def get_name(self) -> str:
        """Get the name of the strategy.
        
        Returns:
            Strategy name
        """
        return "Bollinger Bands Strategy"
    
    def get_description(self) -> str:
        """Get the description of the strategy.
        
        Returns:
            Strategy description
        """
        return (
            "Generates buy signals when price touches the lower Bollinger Band, "
            "and sell signals when price touches the upper Bollinger Band."
        )
    
    def get_default_params(self) -> Dict[str, Any]:
        """Get the default parameters for the strategy.
        
        Returns:
            Dictionary of default parameters
        """
        return {
            'period': 20,
            'std_dev': 2.0,
            'band_touch_pct': 0.5  # Percentage distance to consider as 'touching' the band
        }
