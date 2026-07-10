"""
PersianTranscriber Engine Manager
Version: 0.1.0
"""

from core.engines.whisper import WhisperEngine


class EngineManager:

    def __init__(self):
        self.engines = {
            "whisper": WhisperEngine()
        }

    def get_engine(self, name="whisper"):

        return self.engines.get(name)
