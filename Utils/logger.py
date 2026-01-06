import logging
import os
from datetime import datetime
import multiprocessing as mp


class ProcessLogger:
    """
    Logger process-safe:
    - un logger per processo
    - nessun singleton cross-process
    - file separato per processo
    """

    _loggers = {}

    @classmethod
    def get_logger(cls, name="app_logger", role="main", log_level=logging.INFO):
        """
        Restituisce un logger unico per (processo, role).
        """
        pid = os.getpid()
        key = (pid, role)

        if key in cls._loggers:
            return cls._loggers[key]

        logger_name = f"{name}.{role}.pid{pid}"
        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)
        logger.propagate = False

        if not logger.handlers:
            formatter = logging.Formatter(
                fmt="%(asctime)s - PID %(process)d - %(processName)s - %(filename)s - %(levelname)s - %(funcName)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )

            # console
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

            # file
            date = datetime.now().strftime("%Y_%m_%d")
            log_dir = os.path.join("logs", date)
            os.makedirs(log_dir, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")
            filename = f"{role}_pid{pid}_{timestamp}.log"
            filepath = os.path.join(log_dir, filename)

            file_handler = logging.FileHandler(filepath, encoding="utf-8")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

            logger.info(f"Logger inizializzato")
            logger.info(f"Role      : {role}")
            logger.info(f"PID       : {pid}")
            logger.info(f"Log file  : {filepath}")
            logger.info("-" * 50)

        cls._loggers[key] = logger
        return logger
