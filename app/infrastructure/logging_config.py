import logging
import sys

def configure_logging():
    """Configure root logger with standard settings"""
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(threadName)s - %(message)s",
        handlers=[
            logging.StreamHandler(stream=sys.stdout),
        ],
        force=True
    )

    # Get and return root logger
    return logging.getLogger()

# Configure and get the root logger
logger = configure_logging()
