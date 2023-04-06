import logging
import functools


def silence_errors(func):
    @functools.wraps(func)
    def wrapper_silence_errors(*args, **kwargs):
        try:
            logging.disable(logging.ERROR)
            func(*args, **kwargs)
        finally:
            logging.disable(logging.NOTSET)

    return wrapper_silence_errors
