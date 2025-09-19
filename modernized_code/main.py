#!/usr/bin/env python3

import sys
import argparse
from PyQt5.QtWidgets import QApplication

from ui.main_window import MainWindow
from utils.config import load_config
from utils.logger import setup_logger


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Modernized Trader Bot')
    parser.add_argument('--config', type=str, default='config.yaml',
                        help='Path to configuration file')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug logging')
    parser.add_argument('--no-ui', action='store_true',
                        help='Run without UI (for backtesting only)')
    return parser.parse_args()


def main():
    """Main entry point for the application."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Setup logging
    logger = setup_logger(debug=args.debug)
    logger.info("Starting Modernized Trader Bot")
    
    # Load configuration
    config = load_config(args.config)
    logger.info(f"Loaded configuration from {args.config}")
    
    if args.no_ui:
        # Run in headless mode (for backtesting only)
        from app import TraderBotApp
        app = TraderBotApp(config)
        # Example: Run a backtest
        app.select_coin(config.get('default_coin', 'BTC/USDT'))
        app.select_timeframe(config.get('default_timeframe', '5m'))
        app.set_date_range(
            config.get('backtest_start_date', '2023-01-01T00:00:00'),
            config.get('backtest_end_date', '2023-01-31T23:59:59')
        )
        app.fetch_historical_data()
        app.select_strategy(config.get('default_strategy', 'SimpleMovingAverageCrossover'))
        app.start_backtest()
        app.stop_backtest()
        logger.info("Backtest completed")
    else:
        # Run with UI
        qt_app = QApplication(sys.argv)
        window = MainWindow(config)
        window.show()
        sys.exit(qt_app.exec_())


if __name__ == "__main__":
    main()
