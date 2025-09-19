#!/usr/bin/env python3

from .simple_ma_crossover import SimpleMovingAverageCrossover
from .rsi_strategy import RSIStrategy
from .macd_strategy import MACDStrategy
from .bollinger_bands_strategy import BollingerBandsStrategy

# List of available strategies
AVAILABLE_STRATEGIES = {
    'SimpleMovingAverageCrossover': SimpleMovingAverageCrossover,
    'RSIStrategy': RSIStrategy,
    'MACDStrategy': MACDStrategy,
    'BollingerBandsStrategy': BollingerBandsStrategy
}
