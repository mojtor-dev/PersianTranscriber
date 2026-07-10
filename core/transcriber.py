"""
PersianTranscriber Engine
Version: 0.1.0
"""

from core.engine_manager import EngineManager


class TranscriberEngine:

    def __init__(self):
        self.manager = EngineManager()
        self.engine = self.manager.get_engine()

    def load_model(self):

        return self.engine.load()

    def transcribe(self, audio_info):

        if not audio_info:
            return None

        return self.engine.transcribe(
            audio_info.file_path
        )
