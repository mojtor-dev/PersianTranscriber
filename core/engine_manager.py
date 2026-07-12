"""
PersianTranscriber Engine Manager
Version: 0.3.0
"""

from core.config_loader import ConfigLoader
from core.engines.whisper import WhisperEngine
from core.engines.whisper_cpp import WhisperCppEngine


class EngineManager:

    def __init__(
        self,
        engine_name=None,
        model=None,
        language=None,
        threads=None,
        timeout_seconds=None,
        initial_prompt=None,
    ):
        self.config = ConfigLoader()

        self.engine_name = (
            engine_name
            or self.config.get_engine_name()
        )

        self.model = (
            model
            or self.config.get_model()
        )

        self.language = (
            language
            or self.config.get_language()
        )

        whisper_cpp_options = {
            "model": self.model,
            "language": self.language,
            "initial_prompt": initial_prompt,
        }

        if threads is not None:
            whisper_cpp_options["threads"] = threads

        if timeout_seconds is not None:
            whisper_cpp_options[
                "timeout_seconds"
            ] = timeout_seconds

        self.engines = {
            "whisper": WhisperEngine(
                model=self.model,
                language=self.language,
            ),
            "whisper_cpp": WhisperCppEngine(
                **whisper_cpp_options
            ),
        }

    def get_engine(self):
        if self.engine_name not in self.engines:
            available = ", ".join(
                sorted(self.engines)
            )

            raise ValueError(
                f"Unknown engine: {self.engine_name}. "
                f"Available engines: {available}"
            )

        return self.engines[
            self.engine_name
        ]
