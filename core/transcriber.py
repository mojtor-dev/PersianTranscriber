"""
PersianTranscriber Engine
Version: 0.1.0
"""


class TranscriberEngine:

    def __init__(self):
        self.model = None

    def load_model(self):
        """
        Load transcription model.
        Whisper will be connected here later.
        """

        print("Transcription model initialized")

        return True

    def transcribe(self, audio_info):
        """
        Convert audio to text.
        """

        if not audio_info:
            return None

        return {
            "file": audio_info.file_name,
            "text": "Sample transcription result"
        }
