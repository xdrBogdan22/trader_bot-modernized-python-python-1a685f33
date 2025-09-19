#!/usr/bin/env python3

import json
import threading
import time
from typing import Dict, Any, Callable, Optional

import websocket

from utils.logger import get_logger


class WebSocketClient:
    """Client for handling WebSocket connections to Binance."""
    
    def __init__(self):
        """Initialize the WebSocket client."""
        self.logger = get_logger()
        self.ws = None
        self.thread = None
        self.running = False
        self.on_message: Optional[Callable[[Dict[str, Any]], None]] = None
        self.on_error: Optional[Callable[[Exception], None]] = None
        self.on_close: Optional[Callable[[], None]] = None
        self.on_open: Optional[Callable[[], None]] = None
    
    def connect(self, symbol: str) -> None:
        """Connect to Binance WebSocket for a symbol.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
        """
        # Convert from CCXT format if needed
        if '/' in symbol:
            symbol = symbol.replace('/', '').lower()
        
        # Disconnect if already connected
        if self.ws:
            self.disconnect()
        
        # Create WebSocket connection
        url = f"wss://stream.binance.com:9443/ws/{symbol}@kline_1m"
        self.ws = websocket.WebSocketApp(
            url,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
            on_open=self._on_open
        )
        
        # Start WebSocket in a separate thread
        self.running = True
        self.thread = threading.Thread(target=self._run_forever)
        self.thread.daemon = True
        self.thread.start()
        
        self.logger.info(f"Connected to WebSocket for {symbol}")
    
    def disconnect(self) -> None:
        """Disconnect from WebSocket."""
        self.running = False
        if self.ws:
            self.ws.close()
            self.ws = None
        
        if self.thread:
            self.thread.join(timeout=1.0)
            self.thread = None
        
        self.logger.info("Disconnected from WebSocket")
    
    def _run_forever(self) -> None:
        """Run WebSocket connection in a loop."""
        retry_count = 0
        max_retries = 5
        
        while self.running and retry_count < max_retries:
            try:
                self.ws.run_forever()
                
                # If we get here, the connection was closed
                if self.running:
                    self.logger.warning("WebSocket connection closed, reconnecting...")
                    time.sleep(1)  # Wait before reconnecting
                    retry_count += 1
                else:
                    break
            
            except Exception as e:
                self.logger.error(f"WebSocket error: {e}")
                time.sleep(1)  # Wait before reconnecting
                retry_count += 1
        
        if retry_count >= max_retries:
            self.logger.error("Max WebSocket reconnection attempts reached")
    
    def _on_message(self, ws, message) -> None:
        """Handle WebSocket messages.
        
        Args:
            ws: WebSocket instance
            message: Message received
        """
        try:
            data = json.loads(message)
            
            # Call user-defined callback if set
            if self.on_message:
                self.on_message(data)
        
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse WebSocket message: {e}")
        except Exception as e:
            self.logger.error(f"Error handling WebSocket message: {e}")
    
    def _on_error(self, ws, error) -> None:
        """Handle WebSocket errors.
        
        Args:
            ws: WebSocket instance
            error: Error received
        """
        self.logger.error(f"WebSocket error: {error}")
        
        # Call user-defined callback if set
        if self.on_error:
            self.on_error(error)
    
    def _on_close(self, ws, close_status_code, close_msg) -> None:
        """Handle WebSocket connection close.
        
        Args:
            ws: WebSocket instance
            close_status_code: Close status code
            close_msg: Close message
        """
        self.logger.info(f"WebSocket closed: {close_status_code} {close_msg}")
        
        # Call user-defined callback if set
        if self.on_close:
            self.on_close()
    
    def _on_open(self, ws) -> None:
        """Handle WebSocket connection open.
        
        Args:
            ws: WebSocket instance
        """
        self.logger.info("WebSocket connection opened")
        
        # Call user-defined callback if set
        if self.on_open:
            self.on_open()
    
    def send(self, data: Dict[str, Any]) -> None:
        """Send data through WebSocket.
        
        Args:
            data: Data to send
        """
        if not self.ws:
            self.logger.error("WebSocket not connected")
            return
        
        try:
            self.ws.send(json.dumps(data))
        except Exception as e:
            self.logger.error(f"Failed to send WebSocket message: {e}")
