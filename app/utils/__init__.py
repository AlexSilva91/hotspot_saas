import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging(app):

    log_dir = os.path.join(os.getcwd(), "logs")

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_format = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
    )

    # Log principal
    app_log = RotatingFileHandler(
        os.path.join(log_dir, "app.log"),
        maxBytes=10 * 1024 * 1024,
        backupCount=5
    )

    app_log.setLevel(logging.INFO)
    app_log.setFormatter(log_format)

    # Log de erros
    error_log = RotatingFileHandler(
        os.path.join(log_dir, "error.log"),
        maxBytes=10 * 1024 * 1024,
        backupCount=5
    )

    error_log.setLevel(logging.ERROR)
    error_log.setFormatter(log_format)

    app.logger.setLevel(logging.INFO)

    app.logger.addHandler(app_log)
    app.logger.addHandler(error_log)