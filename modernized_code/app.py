#!/usr/bin/env python3

import logging
import datetime
from typing import Dict, Any, Optional, List

from binance_client import BinanceClient
from websocket_client import WebSocketClient
from data_processor import DataProcessor
from strategy_manager import StrategyManager
from fake_account import FakeAccount
from backtest import Backtest
from utils.logger import get_logger


class TraderBotApp:
    """Main application class for the Trader Bot."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the Trader Bot application.
        
        Args:
            config: Configuration dictionary
        """
        self.logger = get_logger()
        self.config = config or {}
        
        # Initialize components
        self.binance_client = BinanceClient()
        self.websocket_client = WebSocketClient()
        self.data_processor = DataProcessor()
        self.strategy_manager = StrategyManager()
        self.fake_account = FakeAccount(initial_balance=1000)
        self.backtest = Backtest(self.data_processor)
        
        # State variables
        self.selected_coin = None
        self.selected_timeframe = None
        self.selected_strategy = None
        self.strategy_running = False
        self.backtest_running = False
        self.start_date = None
        self.end_date = None
        
        # Connect signals
        self.websocket_client.on_message = self._on_websocket_message
        self.logger.info("TraderBotApp initialized")
    
    def select_coin(self, symbol: str) -> None:
        """Select a cryptocurrency pair.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
        """
        self.selected_coin = symbol
        self.logger.info(f"Selected coin: {symbol}")
    
    def connect_websocket(self) -> None:
        """Connect to Binance WebSocket for real-time data."""
        if not self.selected_coin:
            self.logger.error("No coin selected")
            return
        
        self.websocket_client.connect(self.selected_coin)
        self.logger.info(f"Connected to WebSocket for {self.selected_coin}")
    
    def disconnect_websocket(self) -> None:
        """Disconnect from Binance WebSocket."""
        self.websocket_client.disconnect()
        self.logger.info("Disconnected from WebSocket")
    
    def select_strategy(self, strategy_name: str) -> None:
        """Select a trading strategy.
        
        Args:
            strategy_name: Name of the strategy to select
        """
        self.selected_strategy = strategy_name
        self.logger.info(f"Selected strategy: {strategy_name}")
    
    def configure_strategy(self, params: Dict[str, Any]) -> None:
        """Configure strategy parameters.
        
        Args:
            params: Dictionary of strategy parameters
        """
        if not self.selected_strategy:
            self.logger.error("No strategy selected")
            return
        
        self.strategy_manager.configure_strategy(self.selected_strategy, params)
        self.logger.info(f"Configured strategy {self.selected_strategy} with params: {params}")
    
    def start_strategy(self) -> None:
        """Start the selected strategy."""
        if not self.selected_strategy:
            self.logger.error("No strategy selected")
            return
        
        if not self.selected_coin:
            self.logger.error("No coin selected")
            return
        
        if self.strategy_running:
            self.logger.warning("Strategy already running")
            return
        
        # Initialize strategy
        strategy = self.strategy_manager.create_strategy(self.selected_strategy)
        
        # Start strategy
        self.strategy_running = True
        self.logger.info(f"Started strategy {self.selected_strategy} for {self.selected_coin}")
    
    def stop_strategy(self) -> None:
        """Stop the current strategy."""
        if not self.strategy_running:
            self.logger.warning("No strategy running")
            return
        
        self.strategy_running = False
        self.logger.info("Stopped strategy")
    
    def select_timeframe(self, timeframe: str) -> None:
        """Select a timeframe for historical data.
        
        Args:
            timeframe: Timeframe string (e.g., '1m', '5m', '1h')
        """
        self.selected_timeframe = timeframe
        self.logger.info(f"Selected timeframe: {timeframe}")
    
    def set_date_range(self, start_date: str, end_date: str) -> None:
        """Set date range for historical data.
        
        Args:
            start_date: Start date in format 'YYYY-MM-DDThh:mm:ss'
            end_date: End date in format 'YYYY-MM-DDThh:mm:ss'
        """
        try:
            self.start_date = datetime.datetime.fromisoformat(start_date)
            self.end_date = datetime.datetime.fromisoformat(end_date)
            self.logger.info(f"Set date range: {start_date} to {end_date}")
        except ValueError as e:
            self.logger.error(f"Invalid date format: {e}")
    
    def fetch_historical_data(self) -> None:
        """Fetch historical data for backtesting."""
        if not self.selected_coin:
            self.logger.error("No coin selected")
            return
        
        if not self.selected_timeframe:
            self.logger.error("No timeframe selected")
            return
        
        if not self.start_date or not self.end_date:
            self.logger.error("No date range set")
            return
        
        self.logger.info(f"Fetching historical data for {self.selected_coin} "
                        f"({self.selected_timeframe}) from {self.start_date} to {self.end_date}")
        
        # Fetch data from Binance API
        data = self.binance_client.get_historical_klines(
            self.selected_coin,
            self.selected_timeframe,
            self.start_date,
            self.end_date
        )
        
        # Process data
        self.data_processor.process_historical_data(data)
        self.logger.info(f"Fetched {len(data)} historical data points")
    
    def start_backtest(self) -> None:
        """Start backtesting with historical data."""
        if not self.selected_strategy:
            self.logger.error("No strategy selected")
            return
        
        if not self.data_processor.has_data():
            self.logger.error("No historical data available")
            return
        
        if self.backtest_running:
            self.logger.warning("Backtest already running")
            return
        
        # Initialize strategy
        strategy = self.strategy_manager.create_strategy(self.selected_strategy)
        
        # Start backtest
        self.backtest_running = True
        self.backtest.run(strategy, self.fake_account)
        self.logger.info(f"Started backtest with strategy {self.selected_strategy}")
    
    def stop_backtest(self) -> None:
        """Stop the current backtest."""
        if not self.backtest_running:
            self.logger.warning("No backtest running")
            return
        
        self.backtest_running = False
        self.backtest.stop()
        self.logger.info("Stopped backtest")
    
    def set_api_keys(self, api_key: str, api_secret: str) -> None:
        """Set Binance API keys.
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
        """
        self.binance_client.set_api_keys(api_key, api_secret)
        self.logger.info("Set API keys")
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get account information from Binance.
        
        Returns:
            Dictionary containing account information
        """
        return self.binance_client.get_account_info()
    
    def get_trade_history(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get trade history from Binance.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
        
        Returns:
            List of trades
        """
        return self.binance_client.get_trade_history(symbol or self.selected_coin)
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get open orders from Binance.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
        
        Returns:
            List of open orders
        """
        return self.binance_client.get_open_orders(symbol or self.selected_coin)
    
    def place_order(self, symbol: str, side: str, order_type: str, quantity: float,
                   price: Optional[float] = None) -> Dict[str, Any]:
        """Place an order on Binance.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
            side: Order side ('buy' or 'sell')
            order_type: Order type ('market', 'limit', etc.)
            quantity: Order quantity
            price: Order price (required for limit orders)
        
        Returns:
            Order information
        """
        return self.binance_client.place_order(symbol, side, order_type, quantity, price)
    
    def cancel_order(self, symbol: str, order_id: str) -> Dict[str, Any]:
        """Cancel an order on Binance.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
            order_id: Order ID
        
        Returns:
            Cancellation information
        """
        return self.binance_client.cancel_order(symbol, order_id)
    
    def _on_websocket_message(self, message: Dict[str, Any]) -> None:
        """Handle WebSocket messages.
        
        Args:
            message: WebSocket message
        """
        # Process real-time data
        self.data_processor.process_realtime_data(message)
        
        # Update strategy if running
        if self.strategy_running and self.selected_strategy:
            strategy = self.strategy_manager.get_strategy(self.selected_strategy)
            if strategy:
                # Get latest data
                data = self.data_processor.get_latest_data()
                
                # Execute strategy
                signal = strategy.execute(data)
                
                # Handle signal
                if signal:
                    self._handle_strategy_signal(signal)
    
    def _handle_strategy_signal(self, signal: Dict[str, Any]) -> None:
        """Handle strategy signals.
        
        Args:
            signal: Strategy signal
        """
        action = signal.get('action')
        if not action:
            return
        
        if action == 'buy':
            # Execute buy order
            self.logger.info(f"Buy signal received: {signal}")
            # Implement buy logic here
        
        elif action == 'sell':
            # Execute sell order
            self.logger.info(f"Sell signal received: {signal}")
            # Implement sell logic here
