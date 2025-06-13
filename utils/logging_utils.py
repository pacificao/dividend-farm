# utils/logging_utils.py

import logging
import os
from pathlib import Path

def setup_logger(name: str, log_file: str = "logs/app.log", level: int = logging.INFO) -> logging.Logger:
    """
    Set up and return a logger instance with a file and console handler.

    :param name: Name of the logger.
    :param log_file: Path to the log file.
    :param level: Logging level.
    :return: Configured logger.
    """
    Path(os.path.dirname(log_file)).mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.hasHandlers():
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger