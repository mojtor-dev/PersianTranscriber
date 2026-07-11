"""
PersianTranscriber Pipeline

Version: 0.1.0
"""

from core.audio_loader import AudioLoader
from core.transcriber import TranscriberEngine
from core.cleaner import TextCleaner
from core.persian_normalizer import PersianNormalizer
from core.docx_exporter import DocxExporter
from core.text_exporter import TextExporter
from core.logger import AppLogger
from core.progress import ProgressManager
from core.dictionary_engine import DictionaryEngine


class TranscriptionPipeline:

    def __init__(self):
        self.transcriber = TranscriberEngine()
        self.cleaner = TextCleaner()
        self.normalizer = PersianNormalizer()
        self.exporter = DocxExporter()
        self.text_exporter = TextExporter()
        self.dictionary = DictionaryEngine()
        self.logger = AppLogger()
        self.progress = ProgressManager()

    def run(self, audio_path):

        self.progress.start()

        self.logger.start(audio_path)

        self.progress.update(
            20,
            "Loading audio"
        )

        loader = AudioLoader(audio_path)

        if not loader.exists():

            self.logger.error(
                f"File not found: {audio_path}"
            )

            return None

        audio_info = loader.load_info()

        self.progress.update(
            40,
            "Loading model"
        )

        self.transcriber.load_model()

        self.progress.update(
            70,
            "Transcribing"
        )

        result = self.transcriber.transcribe(
            audio_info
        )

        self.progress.update(
            85,
            "Cleaning text"
        )

        clean_text = self.cleaner.clean(
            result["text"]
        )

        clean_text = self.normalizer.normalize(
            clean_text
        )

        clean_text = self.dictionary.correct(
            clean_text
        )

        self.progress.update(
            95,
            "Saving output"
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

        self.progress.finish()

        return output
