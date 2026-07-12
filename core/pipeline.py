"""
PersianTranscriber Pipeline
Version: 0.3.0
"""

from core.audio_loader import AudioLoader
from core.audio_splitter import AudioSplitter
from core.cleaner import TextCleaner
from core.dictionary_engine import DictionaryEngine
from core.docx_exporter import DocxExporter
from core.logger import AppLogger
from core.persian_normalizer import PersianNormalizer
from core.progress import ProgressManager
from core.text_exporter import TextExporter
from core.text_merger import TextMerger
from core.transcriber import TranscriberEngine


class TranscriptionPipeline:

    def __init__(self):
        self.transcriber = TranscriberEngine()
        self.cleaner = TextCleaner()
        self.normalizer = PersianNormalizer()
        self.dictionary = DictionaryEngine()
        self.splitter = AudioSplitter()
        self.merger = TextMerger()
        self.exporter = DocxExporter()
        self.text_exporter = TextExporter()
        self.logger = AppLogger()
        self.progress = ProgressManager()

    def run(self, audio_path):
        self.progress.start()
        self.logger.start(audio_path)

        try:
            self.progress.update(
                10,
                "Loading audio",
            )

            loader = AudioLoader(audio_path)

            if not loader.exists():
                raise FileNotFoundError(
                    f"File not found: {audio_path}"
                )

            if not loader.is_supported():
                raise ValueError(
                    "Unsupported audio format: "
                    f"{loader.get_extension()}"
                )

            audio_info = loader.load_info()

            self.progress.update(
                20,
                "Loading model",
            )

            self.transcriber.load_model()

            raw_text = self._transcribe_audio(
                audio_info
            )

            self.progress.update(
                85,
                "Cleaning text",
            )

            clean_text = self.cleaner.clean(
                raw_text
            )

            clean_text = self.normalizer.normalize(
                clean_text
            )

            clean_text = self.dictionary.correct(
                clean_text
            )

            self.progress.update(
                95,
                "Saving output",
            )

            self.text_exporter.save_text(
                clean_text
            )

            output = self.exporter.save_docx(
                clean_text
            )

            self.logger.finish(output)
            self.progress.finish()

            return output

        except Exception as error:
            self.logger.error(str(error))
            raise

    def _transcribe_audio(self, audio_info):
        audio_path = audio_info.file_path

        if not self.splitter.should_split(audio_path):
            self.progress.update(
                50,
                "Transcribing audio",
            )

            result = self.transcriber.transcribe(
                audio_info
            )

            return self._extract_text(result)

        self.progress.update(
            30,
            "Splitting long audio",
        )

        try:
            chunk_paths = self.splitter.split(
                audio_path
            )

            chunk_texts = []
            total_chunks = len(chunk_paths)

            for index, chunk_path in enumerate(
                chunk_paths,
                start=1,
            ):
                progress_percent = self._chunk_progress(
                    index=index,
                    total_chunks=total_chunks,
                )

                self.progress.update(
                    progress_percent,
                    (
                        "Transcribing chunk "
                        f"{index}/{total_chunks}"
                    ),
                )

                chunk_loader = AudioLoader(
                    chunk_path
                )

                chunk_info = chunk_loader.load_info()

                if chunk_info is None:
                    raise RuntimeError(
                        f"Cannot load audio chunk: {chunk_path}"
                    )

                result = self.transcriber.transcribe(
                    chunk_info
                )

                chunk_text = self._extract_text(
                    result
                )

                if chunk_text.strip():
                    chunk_texts.append(
                        chunk_text
                    )

            if not chunk_texts:
                raise RuntimeError(
                    "Whisper returned no text for audio chunks"
                )

            return self.merger.merge(
                chunk_texts
            )

        finally:
            self._cleanup_audio_chunks()

    def _cleanup_audio_chunks(self):
        try:
            return self.splitter.cleanup()
        except Exception as cleanup_error:
            logger = getattr(
                self,
                "logger",
                None,
            )

            if logger is not None:
                logger.error(
                    "Cannot clean temporary audio chunks: "
                    f"{cleanup_error}"
                )

            return 0

    @staticmethod
    def _extract_text(result):
        if not isinstance(result, dict):
            raise RuntimeError(
                "Transcriber returned an invalid result"
            )

        text = result.get("text")

        if not isinstance(text, str):
            raise RuntimeError(
                "Transcriber result does not contain valid text"
            )

        return text

    @staticmethod
    def _chunk_progress(index, total_chunks):
        if total_chunks <= 0:
            return 30

        start_percent = 35
        end_percent = 80
        progress_range = (
            end_percent - start_percent
        )

        return start_percent + int(
            progress_range
            * index
            / total_chunks
        )
