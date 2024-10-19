import logging

# from logging.handlers import RotatingFileHandler


# the setup is called once at the start of the app
def setup_logging() -> None:
    # Define log format for both console and file output
    log_format = "%(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(log_format)

    # Create a console handler (for output to console)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    # TODO: Create a file handler (for output to file)
    # file_handler = RotatingFileHandler('logs/app.log', maxBytes=10485760, backupCount=5)
    # file_handler.setFormatter(formatter)
    # file_handler.setLevel(logging.INFO)

    # Get the root logger and configure it
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Set the root logger level
    root_logger.addHandler(console_handler)

    # Set up module-specific loggers if necessary (e.g., with different levels)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    return logger
