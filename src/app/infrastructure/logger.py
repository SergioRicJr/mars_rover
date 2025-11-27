import logging
import sys

from app.config import Config


class Logger:
    def __init__(self, name: str = "mars_rover") -> None:
        self._logger = logging.getLogger(name)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(Config.LOG_LEVEL)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)

    def __getattr__(self, name: str):
        """Automatically delegates to the internal logger."""
        return getattr(self._logger, name)
