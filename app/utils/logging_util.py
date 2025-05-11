from enum import Enum
import traceback

from app.infrastructure.logging_config import logger


class LogLevel(Enum):
    INFO = "info"
    CRITICAL = "critical"
    WARNING = "warning"
    ERROR = "error"
    DEBUG = "debug"


def log_message(
    level: LogLevel,
    event: str,
    **kwargs,
):
    """Custom log function with extra context."""

    extra_info = " ".join([f"{key}={value}" for key, value in kwargs.items()])
    full_message = f"{event} | {extra_info}"

    # If there's an error in kwargs, append the stack trace
    if level == LogLevel.ERROR and "error" in kwargs:
        error_stack = traceback.format_exc()
        if (
            error_stack and error_stack != "NoneType: None\n"
        ):  # Check if there's a valid stack trace
            full_message = f"{full_message}\nStack trace:\n{error_stack}"

    if level == LogLevel.INFO:
        logger.info(full_message)
    elif level == LogLevel.CRITICAL:
        logger.critical(full_message)
    elif level == LogLevel.WARNING:
        logger.warning(full_message)
    elif level == LogLevel.ERROR:
        logger.error(full_message)
    elif level == LogLevel.DEBUG:
        logger.debug(full_message)
