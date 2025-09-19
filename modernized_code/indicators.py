#!/usr/bin/env python3

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional


def calculate_sma(data: pd.DataFrame, column: str = 'close', periods: List[int] = [20, 50, 200]) -> pd.DataFrame:
    """Calculate Simple Moving Average for given periods.
    
    Args:
        data: DataFrame with price data
        column: Column to calculate SMA for
        periods: List of periods to calculate SMA for
    
    Returns:
        DataFrame with SMA columns added
    """
    df = data.copy()
    
    for period in periods:
        df[f'sma_{period}'] = df[column].rolling(window=period).mean()
    
    return df


def calculate_ema(data: pd.DataFrame, column: str = 'close', periods: List[int] = [12, 26]) -> pd.DataFrame:
    """Calculate Exponential Moving Average for given periods.
    
    Args:
        data: DataFrame with price data
        column: Column to calculate EMA for
        periods: List of periods to calculate EMA for
    
    Returns:
        DataFrame with EMA columns added
    """
    df = data.copy()
    
    for period in periods:
        df[f'ema_{period}'] = df[column].ewm(span=period, adjust=False).mean()
    
    return df


def calculate_rsi(data: pd.DataFrame, column: str = 'close', period: int = 14) -> pd.DataFrame:
    """Calculate Relative Strength Index.
    
    Args:
        data: DataFrame with price data
        column: Column to calculate RSI for
        period: RSI period
    
    Returns:
        DataFrame with RSI column added
    """
    df = data.copy()
    
    # Calculate price changes
    delta = df[column].diff()
    
    # Separate gains and losses
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    # Calculate average gain and loss
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    
    # Calculate RS and RSI
    rs = avg_gain / avg_loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    return df


def calculate_macd(data: pd.DataFrame, column: str = 'close', fast_period: int = 12,
                  slow_period: int = 26, signal_period: int = 9) -> pd.DataFrame:
    """Calculate Moving Average Convergence Divergence.
    
    Args:
        data: DataFrame with price data
        column: Column to calculate MACD for
        fast_period: Fast EMA period
        slow_period: Slow EMA period
        signal_period: Signal EMA period
    
    Returns:
        DataFrame with MACD columns added
    """
    df = data.copy()
    
    # Calculate fast and slow EMAs
    fast_ema = df[column].ewm(span=fast_period, adjust=False).mean()
    slow_ema = df[column].ewm(span=slow_period, adjust=False).mean()
    
    # Calculate MACD line and signal line
    df['macd'] = fast_ema - slow_ema
    df['macd_signal'] = df['macd'].ewm(span=signal_period, adjust=False).mean()
    df['macd_histogram'] = df['macd'] - df['macd_signal']
    
    return df


def calculate_bollinger_bands(data: pd.DataFrame, column: str = 'close', period: int = 20,
                             std_dev: float = 2.0) -> pd.DataFrame:
    """Calculate Bollinger Bands.
    
    Args:
        data: DataFrame with price data
        column: Column to calculate Bollinger Bands for
        period: SMA period
        std_dev: Standard deviation multiplier
    
    Returns:
        DataFrame with Bollinger Bands columns added
    """
    df = data.copy()
    
    # Calculate SMA and standard deviation
    df['bb_middle'] = df[column].rolling(window=period).mean()
    df['bb_std'] = df[column].rolling(window=period).std()
    
    # Calculate upper and lower bands
    df['bb_upper'] = df['bb_middle'] + (df['bb_std'] * std_dev)
    df['bb_lower'] = df['bb_middle'] - (df['bb_std'] * std_dev)
    
    return df


def calculate_atr(data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """Calculate Average True Range.
    
    Args:
        data: DataFrame with price data
        period: ATR period
    
    Returns:
        DataFrame with ATR column added
    """
    df = data.copy()
    
    # Calculate True Range
    df['tr1'] = abs(df['high'] - df['low'])
    df['tr2'] = abs(df['high'] - df['close'].shift())
    df['tr3'] = abs(df['low'] - df['close'].shift())
    df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
    
    # Calculate ATR
    df['atr'] = df['tr'].rolling(window=period).mean()
    
    # Drop temporary columns
    df.drop(['tr1', 'tr2', 'tr3', 'tr'], axis=1, inplace=True)
    
    return df


def calculate_stochastic(data: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> pd.DataFrame:
    """Calculate Stochastic Oscillator.
    
    Args:
        data: DataFrame with price data
        k_period: %K period
        d_period: %D period
    
    Returns:
        DataFrame with Stochastic Oscillator columns added
    """
    df = data.copy()
    
    # Calculate %K
    df['stoch_lowest_low'] = df['low'].rolling(window=k_period).min()
    df['stoch_highest_high'] = df['high'].rolling(window=k_period).max()
    df['stoch_k'] = 100 * ((df['close'] - df['stoch_lowest_low']) / 
                          (df['stoch_highest_high'] - df['stoch_lowest_low']))
    
    # Calculate %D
    df['stoch_d'] = df['stoch_k'].rolling(window=d_period).mean()
    
    # Drop temporary columns
    df.drop(['stoch_lowest_low', 'stoch_highest_high'], axis=1, inplace=True)
    
    return df


def calculate_indicators(data: pd.DataFrame) -> pd.DataFrame:
    """Calculate all technical indicators.
    
    Args:
        data: DataFrame with price data
    
    Returns:
        DataFrame with all indicators added
    """
    if len(data) == 0:
        return data
    
    df = data.copy()
    
    # Calculate indicators
    df = calculate_sma(df, periods=[20, 50, 200])
    df = calculate_ema(df, periods=[12, 26])
    df = calculate_rsi(df)
    df = calculate_macd(df)
    df = calculate_bollinger_bands(df)
    df = calculate_atr(df)
    df = calculate_stochastic(df)
    
    return df
