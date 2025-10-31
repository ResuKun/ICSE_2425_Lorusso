import logging
import os
from datetime import datetime
from threading import Lock


class SingletonLogger:
    _instance = None
    _lock = Lock()

    def __new__(cls, name="app_logger", log_level=logging.INFO):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialize(name, log_level)
        return cls._instance

    def _initialize(self, name, log_level):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)

        if not self.logger.handlers:
            # === Creazione del formatter ===
            formatter = logging.Formatter(
                fmt="%(asctime)s - %(filename)s - %(levelname)s - %(funcName)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )

            # === Handler per console ===
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

            # === Handler per file ===
            log_dir = "logs"
            os.makedirs(log_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")
            log_filename = os.path.join(log_dir, f"partita_{timestamp}.log")

            file_handler = logging.FileHandler(log_filename, encoding="utf-8")
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

            self.logger.info(f"Logger inizializzato. File di log: {log_filename}")

    def get_logger(self):
        return self.logger
