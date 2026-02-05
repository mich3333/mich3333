#!/usr/bin/env python3
"""
Centralized logging configuration for Autonomous Claude.
"""
import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler


def setup_logging(name: str = 'autonomous-claude', level: str = None) -> logging.Logger:
    """
    Set up logging with console and file handlers.

    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
              If None, uses LOG_LEVEL env var or defaults to INFO

    Returns:
        Configured logger instance
    """
    # Determine log level
    if level is None:
        level = os.getenv('LOG_LEVEL', 'INFO').upper()

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level))

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    simple_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )

    # Console handler (INFO and above)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)

    # File handler (DEBUG and above) - only if not in-memory
    log_dir = os.getenv('LOG_DIR', 'logs')
    if log_dir != ':memory:':
        try:
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, f'autonomous-claude-{datetime.now().strftime("%Y%m%d")}.log')

            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(detailed_formatter)
            logger.addHandler(file_handler)
        except (OSError, PermissionError) as e:
            logger.warning(f"Could not create log file: {e}")

    return logger


# Create default logger instance
logger = setup_logging()


if __name__ == '__main__':
    # Test logging
    test_logger = setup_logging('test', 'DEBUG')

    test_logger.debug('This is a debug message')
    test_logger.info('This is an info message')
    test_logger.warning('This is a warning message')
    test_logger.error('This is an error message')
    test_logger.critical('This is a critical message')
