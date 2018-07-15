import logging
from   logging.handlers import RotatingFileHandler


def rotation_logger(
        filename,
        level='INFO',
        format="%(message)s",
        **file_handler_kwargs):
    """
    Set and return the root handler to have a sole handler of `RotatingFileHandler`.
    """
    handler = RotatingFileHandler(filename, **file_handler_kwargs)
    handler.setFormatter(logging.Formatter(format))
    handler.setLevel(level)
    logger = logging.getLogger(filename)
    logger.handlers[:] = [handler]
    logger.propagate = False
    return logger
