import logging
import os
import string
from datetime import date

from app.core.request_context import request_id_context

BASE62_CHARS = string.ascii_letters + string.digits
BASE = len(BASE62_CHARS)


class CorrelationIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_context.get()
        return True


class AppLogger:
    """
    Centralized logger for the application. Logs to both file and console.
    """

    def __init__(self, name="log") -> None:
        self.file_name = name

        self.today = date.today()
        self.formatted_date = self.today.strftime("%d_%m_%Y")
        self.LOG_DIR = os.path.join(
            os.path.dirname(__file__), "..", "..", "logs"
        )

        self.LOG_FILE = os.path.join(
            self.LOG_DIR, f"{self.file_name}_{self.formatted_date}.log"
        )

    def get_logger(self, name: str = "url_shortener"):
        """Return a named logger configured with file and console handlers."""
        if not os.path.exists(self.LOG_DIR):
            os.makedirs(self.LOG_DIR, exist_ok=True)
            if not os.path.exists(self.LOG_FILE):
                open(self.LOG_FILE, "w")
        logger = logging.getLogger(name)
        if not logger.handlers:
            correlation_filter = CorrelationIdFilter()

            file_handler = logging.FileHandler(self.LOG_FILE)
            stream_handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)s | %(request_id)s | %(name)s | %(message)s"
            )
            file_handler.addFilter(correlation_filter)
            file_handler.setFormatter(formatter)
            stream_handler.setFormatter(formatter)
            stream_handler.addFilter(correlation_filter)
            logger.addHandler(file_handler)
            logger.addHandler(stream_handler)
            logger.setLevel(logging.INFO)
        return logger
