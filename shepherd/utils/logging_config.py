import logging

from logging.config import dictConfig

LOGGING_DIRECTORY = '../logs'


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "terminal": {
            "level": "NOTSET",
            "format": "%(asctime)s-%(levelname)s-%(name)s::%(module)s|%(lineno)s:: %(message)s"
        },
        "file": {
            "level": "NOTSET",
            "format": "%(asctime)s-%(levelname)s-%(name)s::%(module)s|%(lineno)s:: %(message)s"
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
        "aiohttp.server": {}
    }
}


def setup_logging():
    dictConfig(config=LOGGING_CONFIG)
    logging.getLogger("urllib3").setLevel(logging.WARNING)  # switch off unnecessary logs
