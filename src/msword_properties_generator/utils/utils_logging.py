from datetime import datetime, timezone
import logging
import pytz
import os


class LocalTimezoneFormatter(logging.Formatter):
    default_time_format = "%Y-%m-%d %H:%M:%S %Z%z"
    local_timezone = pytz.timezone('Europe/Amsterdam')

    def formatTime(self, record, datefmt=None):
        utc_dt = datetime.fromtimestamp(record.created, timezone.utc)
        local_dt = utc_dt.astimezone(self.local_timezone)
        return local_dt.strftime(datefmt or self.default_time_format)

def setup_logging():
    LEVEL = os.environ.get("LOG_LEVEL", "INFO")

    handler = logging.StreamHandler()
    formatter = LocalTimezoneFormatter(fmt="%(asctime)s [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, LEVEL.upper(), "INFO"))

    # Important: clear existing handlers to avoid duplication
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    root_logger.addHandler(handler)