"""
PersianTranscriber Pipeline
Version: 0.1.0
"""

from core.audio_loader import AudioLoader
from core.transcriber import TranscriberEngine
from core.cleaner import TextCleaner
from core.docx_exporter import DocxExporter
from core.text_exporter import TextExporter
from core.logger import AppLogger


class TranscriptionPipeline:

    def __init__(self):

        self.transcriber = TranscriberEngine()
        self.cleaner = TextCleaner()
        self.exporter = DocxExporter()
        self.text_exporter = TextExporter()
        self.logger = AppLogger()


    def run(self, audio_path):

        self.logger.start(audio_path)

        loader = AudioLoader(audio_path)

        if not loader.exists():
            self.logger.error(
                f"File not found: {audio_path}"
            )
            return None

        audio_info = loader.load_info()

        self.transcriber.load_model()

        result = self.transcriber.transcribe(
            audio_info
        )

        clean_text = self.cleaner.clean(
            result["text"]
        )

        self.text_exporter.save_text(
            clean_text
        )

        output = self.exporter.save_docx(
            clean_text
        )

        self.logger.finish(
            output
        )

        return output
