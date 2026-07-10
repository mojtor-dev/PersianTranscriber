"""
PersianTranscriber Engine Manager
Version: 0.1.0
"""

from core.engines.whisper import WhisperEngine
from core.config_loader import ConfigLoader


class EngineManager:

    def __init__(self):

        self.config = ConfigLoader()

        self.engines = {
            "whisper": WhisperEngine()
        }

    def get_engine(self):

        name = self.config.get_engine_name()

        return self.engines.get(
            name,
            self.engines["whisper"]
        )
