"""
Logging configuration for the trading bot.

Sets up a logger that writes structured, timestamped entries to both:
- a rotating log file (trading_bot.log) for persistent audit trail
- the console, for immediate feedback

Every API request, response, and error should be logged through this
logger so the log file can be submitted as evidence of order placement.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
LOG_FILE = os.path.join(LOG_DIR, "trading_bot.log")


def setup_logger(name: str = "trading_bot", level: int = logging.INFO) -> logging.Logger:
    """
    Create and configure the shared application logger.

    Args:
        name: Logger name (usually the module name).
        level: Logging level (default INFO).

    Returns:
        A configured logging.Logger instance.
    """
    os.makedirs(LOG_DIR, exist_ok=True)

    logger = logging.getLogger(name)

    # Avoid attaching duplicate handlers if setup_logger is called more than once
    if logger.handlers:
        return logger

    logger.setLevel(level)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Rotating file handler: keeps log files from growing unbounded
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=2_000_000, backupCount=3, encoding="utf-8"
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    # Console handler for immediate feedback while running the CLI
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
