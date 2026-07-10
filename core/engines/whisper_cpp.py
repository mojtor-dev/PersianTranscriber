"""
PersianTranscriber Whisper.cpp Engine
Version: 0.1.0
"""


class WhisperCppEngine:

    def __init__(
        self,
        model="base",
        language="fa"
    ):
        self.model = model
        self.language = language

    def load(self):

        print(
            f"Whisper.cpp initialized "
            f"(model={self.model}, language={self.language})"
        )

        return True

    def transcribe(self, audio_path):

        return {
            "text": "Whisper.cpp transcription result",
            "file": audio_path,
            "model": self.model,
            "language": self.language
        }
