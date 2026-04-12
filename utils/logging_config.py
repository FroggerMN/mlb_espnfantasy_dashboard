"""
utils/logging_config.py

Central logging configuration for the MLB Fantasy Dashboard.
Call configure_logging() once at application startup (in app.py main()).
All child loggers (using getLogger(__name__)) will inherit these settings.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "dashboard.log")
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def configure_logging(log_level: int = logging.DEBUG) -> None:
    """
    Configures the root logger with a console handler and a rotating file handler.

    - Console: WARNING and above (keeps Streamlit's terminal clean).
    - File: DEBUG and above, rotating at 2 MB with 3 backups.

    Args:
        log_level: The minimum level for the file handler. Defaults to DEBUG.
    """
    # Avoid reconfiguring if handlers are already attached
    root_logger = logging.getLogger()
    if root_logger.handlers:
        return

    root_logger.setLevel(log_level)

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # --- Console handler (WARNING+) ---
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # --- Rotating file handler (DEBUG+) ---
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        file_handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=2 * 1024 * 1024,  # 2 MB
            backupCount=3,
            encoding="utf-8",
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    except OSError as e:
        # If we can't write logs (e.g., read-only filesystem), warn on console only
        root_logger.warning(f"Could not create log file at {LOG_FILE}: {e}")

    root_logger.info("Logging configured. File: %s", LOG_FILE)
