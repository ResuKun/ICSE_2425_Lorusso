import logging
import os
from datetime import datetime
from threading import Lock


class SingletonLogger:
    _instance = None
    _lock = Lock()


    def __new__(cls, name="app_logger", partita = "", log_level=logging.INFO):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialize(name, partita, log_level)
        return cls._instance

    @classmethod
    def init(cls, name="app_logger", partita = "", log_level=logging.INFO):
        """Inizializza il logger solo la prima volta."""
        if cls._instance is None:
            cls(name, partita, log_level)
        return cls._instance

    def _initialize(self, name, partita, log_level):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)

        if not self.logger.handlers:
            formatter = logging.Formatter(
                fmt="%(asctime)s - %(filename)s - %(levelname)s - %(funcName)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )

            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

            date = datetime.now().strftime("%Y_%m_%d")
            log_dir = f"logs/{date}"
            os.makedirs(log_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")
            log_filename = os.path.join(log_dir, f"partita_{timestamp}.log")

            file_handler = logging.FileHandler(log_filename, encoding="utf-8")
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

            self.logger.info(f"Logger inizializzato. File di log: {log_filename}")
            self.logger.info(f"---------------------------------------------------")
            self.logger.info(f"PARTITA ::  {partita}")
            self.logger.info(f"---------------------------------------------------")

    def get_logger(self):
        return self.logger
