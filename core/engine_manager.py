"""
PersianTranscriber Engine Manager
Version: 0.1.0
"""

from core.engines.whisper import WhisperEngine
from core.engines.whisper_cpp import WhisperCppEngine
from core.config_loader import ConfigLoader


class EngineManager:

    def __init__(self):

        self.config = ConfigLoader()

        self.engines = {

            "whisper": WhisperEngine(
                model=self.config.get_model(),
                language=self.config.get_language()
            ),

            "whisper_cpp": WhisperCppEngine(
                model=self.config.get_model(),
                language=self.config.get_language()
            )

        }

    def get_engine(self):

        name = self.config.get_engine_name()

        return self.engines.get(
            name,
            self.engines["whisper"]
        )
