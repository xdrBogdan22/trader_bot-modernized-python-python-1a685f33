#!/usr/bin/env python3

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional

from utils.logger import get_logger
from indicators import calculate_indicators


class DataProcessor:
    """Process market data into OHLC format and calculate indicators."""
    
    def __init__(self, max_data_points: int = 500):
        """Initialize the data processor.
        
        Args:
            max_data_points: Maximum number of data points to keep
        """
        self.logger = get_logger()
        self.max_data_points = max_data_points
        self.data = pd.DataFrame()
        self.realtime_data = pd.DataFrame()
    
    def process_historical_data(self, klines: List[List]) -> pd.DataFrame:
        """Process historical klines data.
        
        Args:
            klines: List of klines from Binance API
        
        Returns:
            Processed DataFrame with indicators
        """
        # Create DataFrame from klines
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ])
        
        # Convert types
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
        for col in ['open', 'high', 'low', 'close', 'volume', 'quote_asset_volume',
                   'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume']:
            df[col] = df[col].astype(float)
        
        # Set timestamp as index
        df.set_index('timestamp', inplace=True)
        
        # Calculate indicators
        df = calculate_indicators(df)
        
        # Store data
        self.data = df
        
        self.logger.info(f"Processed {len(df)} historical data points")
        return df
    
    def process_realtime_data(self, message: Dict[str, Any]) -> Optional[pd.DataFrame]:
        """Process real-time data from WebSocket.
        
        Args:
            message: WebSocket message
        
        Returns:
            Updated DataFrame with indicators or None if data is incomplete
        """
        # Check if message contains kline data
        if 'k' not in message:
            return None
        
        kline = message['k']
        
        # Extract data
        timestamp = pd.to_datetime(kline['t'], unit='ms')
        open_price = float(kline['o'])
        high_price = float(kline['h'])
        low_price = float(kline['l'])
        close_price = float(kline['c'])
        volume = float(kline['v'])
        is_closed = kline['x']
        
        # Update realtime data
        if is_closed:
            # If candle is closed, add to historical data
            new_row = pd.DataFrame({
                'open': [open_price],
                'high': [high_price],
                'low': [low_price],
                'close': [close_price],
                'volume': [volume]
            }, index=[timestamp])
            
            # Append to data
            self.data = pd.concat([self.data, new_row])
            
            # Keep only max_data_points
            if len(self.data) > self.max_data_points:
                self.data = self.data.iloc[-self.max_data_points:]
            
            # Recalculate indicators
            self.data = calculate_indicators(self.data)
            
            self.logger.debug(f"Added closed candle at {timestamp}")
        else:
            # If candle is still open, update realtime data
            self.realtime_data = pd.DataFrame({
                'open': [open_price],
                'high': [high_price],
                'low': [low_price],
                'close': [close_price],
                'volume': [volume]
            }, index=[timestamp])
            
            self.logger.debug(f"Updated realtime candle at {timestamp}")
        
        return self.get_latest_data()
    
    def get_latest_data(self, lookback: int = 100) -> pd.DataFrame:
        """Get latest data including current realtime candle.
        
        Args:
            lookback: Number of historical candles to include
        
        Returns:
            DataFrame with historical and realtime data
        """
        # Get historical data
        if len(self.data) == 0:
            return pd.DataFrame()
        
        # Get last lookback candles
        hist_data = self.data.iloc[-lookback:].copy()
        
        # Add realtime data if available
        if not self.realtime_data.empty:
            # Check if realtime candle already exists in historical data
            if self.realtime_data.index[0] in hist_data.index:
                # Replace existing candle
                hist_data.loc[self.realtime_data.index[0]] = self.realtime_data.iloc[0]
            else:
                # Append realtime candle
                hist_data = pd.concat([hist_data, self.realtime_data])
        
        return hist_data
    
    def has_data(self) -> bool:
        """Check if data is available.
        
        Returns:
            True if data is available, False otherwise
        """
        return not self.data.empty
    
    def get_data(self) -> pd.DataFrame:
        """Get all historical data.
        
        Returns:
            DataFrame with historical data
        """
        return self.data.copy()
    
    def clear_data(self) -> None:
        """Clear all data."""
        self.data = pd.DataFrame()
        self.realtime_data = pd.DataFrame()
        self.logger.info("Cleared all data")
