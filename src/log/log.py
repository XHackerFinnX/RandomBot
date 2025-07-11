from zoneinfo import ZoneInfo
import logging
from datetime import datetime

def setup_logger(name):
    MOSCOW_TZ = ZoneInfo("Europe/Moscow")

    class PiterTimezoneFormatter(logging.Formatter):
        def formatTime(self, record, datefmt=None):
            dt = datetime.fromtimestamp(record.created, tz=MOSCOW_TZ)
            if datefmt:
                return dt.strftime(datefmt)
            return dt.isoformat()

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    formatter = PiterTimezoneFormatter(
        '%(asctime)s - %(name)s %(levelname)s: %(message)s',
        datefmt='%d.%m.%Y %H:%M:%S'
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger