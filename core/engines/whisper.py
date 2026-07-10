"""
PersianTranscriber Whisper Engine
Version: 0.1.0
"""


class WhisperEngine:

    def __init__(self):
        self.model = None

    def load(self):
        print("Whisper engine initialized")
        return True

    def transcribe(self, audio_path):

        return {
            "text": "Whisper transcription result",
            "file": audio_path
        }
