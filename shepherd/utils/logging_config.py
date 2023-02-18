import logging
import traceback

from datetime import datetime, timezone
from logging.config import dictConfig

LOGGING_DIRECTORY = '../logs'


class BaseFormatter(logging.Formatter):

    @staticmethod
    def __insert_exception(record):
        if not record.exc_info:
            return ''
        return '\n' + ''.join(traceback.format_exception(record.exc_info[0],
                                                         record.exc_info[1],
                                                         record.exc_info[2]))

    def format(self, record: logging.LogRecord) -> str:
        time = datetime.fromtimestamp(record.created,
                                      timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        return f'{time}-{record.levelname}-{record.name}:: ' \
               f'{record.module}|{record.lineno}:: {record.getMessage()}' + \
                self.__insert_exception(record)


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "terminal": {
            "()": BaseFormatter
        },
        "file": {
            "()": BaseFormatter
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "NOTSET",
            "formatter": 'terminal',
            "stream": "ext://sys.stdout"
        },
        "info_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "file",
            "filename": f"{LOGGING_DIRECTORY}/info_shepherd.log",
            "maxBytes": 5000000,
            "backupCount": 5,
            "encoding": "utf-8"
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "file",
            "filename": f"{LOGGING_DIRECTORY}/error_shepherd.log",
            "maxBytes": 5000000,
            "backupCount": 5,
            "encoding": "utf-8"
        }
    },
    "loggers": {
        "": {
            # root logger
            "level": "NOTSET",
            "handlers": [
                "console", "info_file", "error_file"
            ],
        },
        "aiohttp.server": {
            "level": "WARNING",
            "handlers": [
                "console", "info_file", "error_file"
            ]
        }
    }
}


def setup_logging():
    dictConfig(config=LOGGING_CONFIG)
    logging.getLogger("urllib3").setLevel(logging.WARNING)  # switch off unnecessary logs
