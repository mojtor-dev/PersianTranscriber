"""
PersianTranscriber Whisper.cpp Engine
Version: 0.3.0
"""

import subprocess
import os
from core.config_loader import ConfigLoader


class WhisperCppEngine:

    def __init__(self, model=None, language=None):

        config = ConfigLoader()

        self.model = model or config.get_model()
        self.language = language or config.get_language()

        self.project_root = os.path.expanduser(
            "~/PersianTranscriber"
        )

        self.whisper_bin = os.path.join(
            self.project_root,
            "tools/whisper.cpp/build/bin/whisper-cli"
        )

        self.model_path = os.path.join(
            self.project_root,
            f"tools/whisper.cpp/models/ggml-{self.model}.bin"
        )


    def load(self):

        if not os.path.exists(self.whisper_bin):
            raise FileNotFoundError(
                "whisper-cli not found"
            )

        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                "Whisper model not found"
            )

        print(
            f"Whisper.cpp ready "
            f"(model={self.model}, language={self.language})"
        )

        return True


    def transcribe(self, audio_path):

        command = [
            self.whisper_bin,
            "-m",
            self.model_path,
            "-f",
            audio_path,
            "-l",
            self.language
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )

        return {
            "text": result.stdout,
            "file": audio_path,
            "model": self.model,
            "language": self.language
        }
