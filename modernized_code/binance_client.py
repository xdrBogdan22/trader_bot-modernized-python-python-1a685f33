#!/usr/bin/env python3

import time
import hmac
import hashlib
import requests
import datetime
from typing import Dict, Any, List, Optional
from urllib.parse import urlencode

from utils.logger import get_logger


class BinanceClient:
    """Client for interacting with Binance API."""
    
    BASE_URL = "https://api.binance.com"
    API_VERSION = "v3"
    
    def __init__(self, api_key: str = None, api_secret: str = None):
        """Initialize the Binance client.
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
        """
        self.logger = get_logger()
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'ModernizedTraderBot/1.0'
        })
        if api_key:
            self.session.headers.update({
                'X-MBX-APIKEY': api_key
            })
    
    def set_api_keys(self, api_key: str, api_secret: str) -> None:
        """Set Binance API keys.
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.session.headers.update({
            'X-MBX-APIKEY': api_key
        })
        self.logger.info("API keys set")
    
    def _get_signed_params(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get signed parameters for authenticated requests.
        
        Args:
            params: Request parameters
        
        Returns:
            Parameters with signature
        """
        if params is None:
            params = {}
        
        # Add timestamp
        params['timestamp'] = int(time.time() * 1000)
        
        # Create signature
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Add signature to parameters
        params['signature'] = signature
        
        return params
    
    def _request(self, method: str, endpoint: str, signed: bool = False,
                params: Dict[str, Any] = None) -> Any:
        """Make a request to the Binance API.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            signed: Whether the request needs authentication
            params: Request parameters
        
        Returns:
            Response data
        """
        url = f"{self.BASE_URL}/api/{self.API_VERSION}/{endpoint}"
        
        # Prepare parameters
        if params is None:
            params = {}
        
        if signed:
            if not self.api_key or not self.api_secret:
                raise ValueError("API key and secret required for authenticated requests")
            params = self._get_signed_params(params)
        
        # Make request
        try:
            if method == 'GET':
                response = self.session.get(url, params=params)
            elif method == 'POST':
                response = self.session.post(url, params=params)
            elif method == 'DELETE':
                response = self.session.delete(url, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {e}")
            if hasattr(e.response, 'text'):
                self.logger.error(f"Response: {e.response.text}")
            raise
    
    def get_server_time(self) -> int:
        """Get Binance server time.
        
        Returns:
            Server time in milliseconds
        """
        response = self._request('GET', 'time')
        return response['serverTime']
    
    def get_exchange_info(self) -> Dict[str, Any]:
        """Get exchange information.
        
        Returns:
            Exchange information
        """
        return self._request('GET', 'exchangeInfo')
    
    def get_symbol_info(self, symbol: str) -> Dict[str, Any]:
        """Get information for a specific symbol.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
        
        Returns:
            Symbol information
        """
        # Convert from CCXT format if needed
        if '/' in symbol:
            symbol = symbol.replace('/', '')
        
        exchange_info = self.get_exchange_info()
        for sym_info in exchange_info['symbols']:
            if sym_info['symbol'] == symbol:
                return sym_info
        
        raise ValueError(f"Symbol not found: {symbol}")
    
    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get ticker information for a symbol.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
        
        Returns:
            Ticker information
        """
        # Convert from CCXT format if needed
        if '/' in symbol:
            symbol = symbol.replace('/', '')
        
        return self._request('GET', 'ticker/24hr', params={'symbol': symbol})
    
    def get_klines(self, symbol: str, interval: str, limit: int = 500) -> List[List]:
        """Get klines/candlestick data for a symbol.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            interval: Kline interval (e.g., '1m', '5m', '1h')
            limit: Number of klines to get (max 1000)
        
        Returns:
            List of klines
        """
        # Convert from CCXT format if needed
        if '/' in symbol:
            symbol = symbol.replace('/', '')
        
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        
        return self._request('GET', 'klines', params=params)
    
    def get_historical_klines(self, symbol: str, interval: str,
                             start_time: datetime.datetime,
                             end_time: datetime.datetime) -> List[List]:
        """Get historical klines/candlestick data for a symbol.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            interval: Kline interval (e.g., '1m', '5m', '1h')
            start_time: Start time
            end_time: End time
        
        Returns:
            List of klines
        """
        # Convert from CCXT format if needed
        if '/' in symbol:
            symbol = symbol.replace('/', '')
        
        # Convert datetime to milliseconds
        start_ms = int(start_time.timestamp() * 1000)
        end_ms = int(end_time.timestamp() * 1000)
        
        params = {
            'symbol': symbol,
            'interval': interval,
            'startTime': start_ms,
            'endTime': end_ms,
            'limit': 1000
        }
        
        # Fetch data in chunks if needed
        all_klines = []
        current_start = start_ms
        
        while current_start < end_ms:
            params['startTime'] = current_start
            klines = self._request('GET', 'klines', params=params)
            
            if not klines:
                break
            
            all_klines.extend(klines)
            
            # Update start time for next chunk
            current_start = klines[-1][0] + 1
            
            # Avoid rate limiting
            time.sleep(0.1)
        
        return all_klines
    
    def get_depth(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        """Get order book depth for a symbol.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            limit: Depth limit (max 5000)
        
        Returns:
            Order book depth
        """
        # Convert from CCXT format if needed
        if '/' in symbol:
            symbol = symbol.replace('/', '')
        
        params = {
            'symbol': symbol,
            'limit': limit
        }
        
        return self._request('GET', 'depth', params=params)
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get account information.
        
        Returns:
            Account information
        """
        return self._request('GET', 'account', signed=True)
    
    def get_trade_history(self, symbol: str) -> List[Dict[str, Any]]:
        """Get trade history for a symbol.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
        
        Returns:
            List of trades
        """
        # Convert from CCXT format if needed
        if '/' in symbol:
            symbol = symbol.replace('/', '')
        
        params = {'symbol': symbol}
        return self._request('GET', 'myTrades', signed=True, params=params)
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get open orders.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
        
        Returns:
            List of open orders
        """
        params = {}
        if symbol:
            # Convert from CCXT format if needed
            if '/' in symbol:
                symbol = symbol.replace('/', '')
            params['symbol'] = symbol
        
        return self._request('GET', 'openOrders', signed=True, params=params)
    
    def place_order(self, symbol: str, side: str, order_type: str, quantity: float,
                   price: Optional[float] = None) -> Dict[str, Any]:
        """Place an order.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            side: Order side ('BUY' or 'SELL')
            order_type: Order type ('LIMIT', 'MARKET', etc.)
            quantity: Order quantity
            price: Order price (required for limit orders)
        
        Returns:
            Order information
        """
        # Convert from CCXT format if needed
        if '/' in symbol:
            symbol = symbol.replace('/', '')
        
        # Prepare parameters
        params = {
            'symbol': symbol,
            'side': side.upper(),
            'type': order_type.upper(),
            'quantity': quantity,
            'newOrderRespType': 'FULL'
        }
        
        # Add price for limit orders
        if order_type.upper() == 'LIMIT':
            if price is None:
                raise ValueError("Price is required for limit orders")
            params['price'] = price
            params['timeInForce'] = 'GTC'
        
        return self._request('POST', 'order', signed=True, params=params)
    
    def cancel_order(self, symbol: str, order_id: str) -> Dict[str, Any]:
        """Cancel an order.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            order_id: Order ID
        
        Returns:
            Cancellation information
        """
        # Convert from CCXT format if needed
        if '/' in symbol:
            symbol = symbol.replace('/', '')
        
        params = {
            'symbol': symbol,
            'orderId': order_id
        }
        
        return self._request('DELETE', 'order', signed=True, params=params)
