import logging
from pathlib import Path

class Logger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance.logger = cls._instance.setup_logging()
        return cls._instance

    def setup_logging(self):
        PROJECT_ROOT = Path(__file__).parent.parent
        LOG_DIR = PROJECT_ROOT / 'logs'
        LOG_FILE = LOG_DIR / 'bot.log'

        try:
            LOG_DIR.mkdir(parents=True, exist_ok=True)

            logging.basicConfig(
                filename=LOG_FILE,
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

            logger = logging.getLogger(__name__)
            logger.info("Logging is set up.")
            return logger
        except Exception as exc:
            print(f"Error setting logging up: {exc}")

    def get_logger(self):
        return self.logger
