import time
from typing import Dict

from pythonjsonlogger.jsonlogger import JsonFormatter

from logging import LogRecord


class CustomJsonFormatter(JsonFormatter):
    converter = time.gmtime

    def add_fields(self, log_record: Dict, record: LogRecord, message_dict: Dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record["ts"] = log_record.pop("asctime")
        log_record["level"] = log_record.pop("levelname")
