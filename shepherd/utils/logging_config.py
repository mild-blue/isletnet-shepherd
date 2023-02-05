from logging.config import dictConfig


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "terminal": {
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
        }
    },
    "loggers": {
        "": {
            # root logger
            "level": "NOTSET",
            "handlers": [
                "console"
            ],
        }
    }
}


def setup_logging():
    dictConfig(config=LOGGING_CONFIG)
    logging.getLogger("urllib3").setLevel(logging.WARNING)  # switch off unnecessary logs
