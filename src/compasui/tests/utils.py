"""
Test utilities for compasui app.
Contains helper functions and decorators for testing.
"""
import functools
import logging


def silence_logging(logger_name="", level=logging.CRITICAL):
    """
    Decorator to silence logging during test execution.

    Args:
        logger_name (str): Name of the logger to silence. If empty, silences root logger.
        level (int): The minimum logging level to set during test execution.
                     Default is CRITICAL which suppresses ERROR, WARNING, INFO, DEBUG.

    Returns:
        function: Decorated test function with logging silenced.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(logger_name)
            original_level = logger.level
            try:
                logger.setLevel(level)
                return func(*args, **kwargs)
            finally:
                logger.setLevel(original_level)

        return wrapper

    return decorator
