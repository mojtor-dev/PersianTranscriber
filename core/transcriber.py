"""
PersianTranscriber Transcriber Engine
Version: 0.3.0
"""

from core.engine_manager import EngineManager


class TranscriberEngine:

    def __init__(
        self,
        engine_name=None,
        model=None,
        language=None,
        threads=None,
        timeout_seconds=None,
        initial_prompt=None,
    ):
        self.manager = EngineManager(
            engine_name=engine_name,
            model=model,
            language=language,
            threads=threads,
            timeout_seconds=timeout_seconds,
            initial_prompt=initial_prompt,
        )

        self.engine = self.manager.get_engine()

    def load_model(self):
        return self.engine.load()

    def transcribe(self, audio_info):
        if not audio_info:
            return None

        return self.engine.transcribe(
            audio_info.file_path
        )
