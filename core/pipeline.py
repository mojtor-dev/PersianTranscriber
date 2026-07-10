"""
PersianTranscriber Pipeline
Version: 0.1.0
"""

from core.audio_loader import AudioLoader
from core.transcriber import TranscriberEngine
from core.cleaner import TextCleaner
from core.docx_exporter import DocxExporter


class TranscriptionPipeline:

    def __init__(self):
        self.transcriber = TranscriberEngine()
        self.cleaner = TextCleaner()
        self.exporter = DocxExporter()

    def run(self, audio_path):

        loader = AudioLoader(audio_path)

        if not loader.exists():
            return None

        audio_info = loader.load_info()

        self.transcriber.load_model()

        result = self.transcriber.transcribe(audio_info)

        clean_text = self.cleaner.clean(
            result["text"]
        )

        output = self.exporter.save_docx(
            clean_text
        )

        return output
