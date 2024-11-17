import logging
import shutil
from logging.handlers import RotatingFileHandler

# from logging.handlers import RotatingFileHandler


# the setup is called once at the start of the app
def setup_logging(
    include_file_handler: bool = False,
    file_path: str | None = None,
    level: int = logging.INFO,
) -> None:

    # Define log format for both console and file output
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(log_format)

    # Create a console handler (for output to console)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    if include_file_handler:
        if file_path is None:
            raise ValueError("file_path must be provided if include_file_handler is True")
        file_handler = RotatingFileHandler(file_path, maxBytes=10485760, backupCount=10)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)

    # Get the root logger and configure it
    root_logger = logging.getLogger()
    root_logger.setLevel(level)  # Set the root logger level
    root_logger.addHandler(console_handler)
    if include_file_handler:
        root_logger.addHandler(file_handler)

    # Set up module-specific loggers if necessary (e.g., with different levels)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    return logger


def create_headline(title: str, fill_char: str = "=") -> str:
    """Create a header that fills the terminal width with the given title centered.

    Args:
        title: The text to center in the header
        fill_char: The character to use for filling (default: "=")

    Returns:
        A string containing the formatted header
    """
    terminal_width = shutil.get_terminal_size().columns or 80
    padded_title = f" {title} "  # Add spaces around the title
    padding = fill_char * ((terminal_width - len(padded_title)) // 2)
    header = f"{padding}{padded_title}{padding}\n"

    # Add extra fill_char if the total length is off by one due to integer division
    if len(header) < terminal_width:
        header += fill_char

    return header
