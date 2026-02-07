import logging
import sys
from pythonjsonlogger import jsonlogger
import os

def setup_logging(service_name: str):
    """Set up structured logging for the service."""

    # Create logger
    logger = logging.getLogger(service_name)
    logger.setLevel(logging.INFO)

    # Prevent adding handlers multiple times
    if logger.handlers:
        return logger

    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)

    # Create formatter
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%SZ'
    )
    handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(handler)

    return logger

def get_logger(service_name: str):
    """Get a configured logger instance."""
    return setup_logging(service_name)