import logging


def get_logger() -> logging.Logger:
    logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")
    # Set httpx logger to only show WARN and ERROR
    httpx_logger = logging.getLogger("httpx")
    httpx_logger.setLevel(logging.WARNING)
    logger = logging.getLogger(__name__)
    return logger
