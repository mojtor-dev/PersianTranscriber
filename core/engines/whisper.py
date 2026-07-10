"""
PersianTranscriber Whisper Engine
Version: 0.1.0
"""


class WhisperEngine:

    def __init__(
        self,
        model="base",
        language="fa"
    ):
        self.model = model
        self.language = language

    def load(self):

        print(
            f"Whisper engine initialized "
            f"(model={self.model}, language={self.language})"
        )

        return True

    def transcribe(self, audio_path):

        return {
            "text": "Whisper transcription result",
            "file": audio_path,
            "model": self.model,
            "language": self.language
        }
