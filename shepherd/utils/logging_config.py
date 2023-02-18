import logging
import traceback

from datetime import datetime, timezone
from logging.config import dictConfig
from pathlib import Path


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


class LoggerMaxInfoFilter(logging.Filter):
    """
    Logger filter, which allows logs only with level INFO or lower.
    """
    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno <= logging.INFO


def setup_logging_dict_config(logging_directory: str):
    logging_config = {
        "version": 1,
        "disable_existing_loggers": True,
        "filters": {
            "max_info_filter": {
                "()": LoggerMaxInfoFilter
            }
        },
        "formatters": {
            "terminal": {
                "()": BaseFormatter
            },
            "file": {
                "()": BaseFormatter
            }
        },
        "handlers": {
            "console_info": {
                "class": "logging.StreamHandler",
                "filters": ["max_info_filter"],
                "level": "NOTSET",
                "formatter": 'terminal',
                "stream": "ext://sys.stdout"
            },
            "console_error": {
                "class": "logging.StreamHandler",
                "level": "WARNING",
                "formatter": 'terminal',
                "stream": "ext://sys.stderr"
            },
            "info_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "file",
                "filename": f"{logging_directory}/info_shepherd.log",
                "maxBytes": 5000000,
                "backupCount": 5,
                "encoding": "utf-8"
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "file",
                "filename": f"{logging_directory}/error_shepherd.log",
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
                    "console_info", "console_error", "info_file", "error_file"
                ],
            },
            "aiohttp.server": {
                "level": "WARNING",
                "handlers": [
                    "console_info", "console_error", "info_file", "error_file"
                ]
            }
        }
    }

    dictConfig(config=logging_config)


def setup_logging(logging_directory: str = '../logs'):
    Path(logging_directory).mkdir(parents=True, exist_ok=True)
    setup_logging_dict_config(logging_directory)
    logging.getLogger("urllib3").setLevel(logging.WARNING)  # switch off unnecessary logs
