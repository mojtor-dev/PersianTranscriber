"""
PersianTranscriber Pipeline
Version: 0.5.0
"""

from core.audio_loader import AudioLoader
from core.audio_splitter import AudioSplitter
from core.cleaner import TextCleaner
from core.dictionary_engine import DictionaryEngine
from core.docx_exporter import DocxExporter
from core.exporters import ExportManager
from core.logger import AppLogger
from core.persian_normalizer import PersianNormalizer
from core.progress import ProgressManager
from core.post_processing import PersianPostProcessor
from core.text_exporter import TextExporter
from core.text_merger import TextMerger
from core.transcriber import TranscriberEngine


class TranscriptionPipeline:

    VALID_OUTPUT_FORMATS = {
        "both",
        "txt",
        "docx",
        "md",
        "json",
        "srt",
        "vtt",
        "pdf",
    }

    def __init__(
        self,
        engine_name=None,
        model=None,
        language=None,
        threads=None,
        timeout_seconds=None,
        chunk_duration_seconds=300,
        output_dir="output",
        output_format="both",
        output_formats=None,
        subtitle_seconds=5,
        initial_prompt=None,
    ):
        if (
            output_format
            not in self.VALID_OUTPUT_FORMATS
        ):
            raise ValueError(
                "output_format must be one of: "
                "both, txt, docx"
            )

        self.output_format = output_format
        self.output_formats = (
            output_formats
            if output_formats is not None
            else output_format
        )

        self.transcriber = TranscriberEngine(
            engine_name=engine_name,
            model=model,
            language=language,
            threads=threads,
            timeout_seconds=timeout_seconds,
            initial_prompt=initial_prompt,
        )

        self.cleaner = TextCleaner()
        self.normalizer = PersianNormalizer()
        self.dictionary = DictionaryEngine()
        self.post_processor = PersianPostProcessor(
            cleaner=self.cleaner,
            normalizer=self.normalizer,
            dictionary=self.dictionary,
        )

        self.splitter = AudioSplitter(
            chunk_duration_seconds=(
                chunk_duration_seconds
            )
        )

        self.merger = TextMerger()

        self.exporter = DocxExporter(
            output_dir=output_dir
        )

        self.text_exporter = TextExporter(
            output_dir=output_dir
        )

        self.export_manager = ExportManager(
            output_dir=output_dir,
            subtitle_seconds=subtitle_seconds,
        )

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

            clean_text = self._post_process_text(
                raw_text
            )

            self.progress.update(
                95,
                "Saving output",
            )

            outputs = self._save_outputs(
                clean_text
            )

            primary_output = (
                outputs.get("docx")
                or outputs.get("txt")
            )

            self.logger.finish(
                primary_output
            )

            self.progress.finish()

            return outputs

        except Exception as error:
            self.logger.error(str(error))
            raise

    def _post_process_text(self, raw_text):
        post_processor = getattr(
            self,
            "post_processor",
            None,
        )

        if post_processor is not None:
            clean_text, report = (
                post_processor.process(
                    raw_text
                )
            )

            if report.dictionary_replacements > 0:
                self.logger.write(
                    "DICTIONARY "
                    f"replacements={report.dictionary_replacements} "
                    f"rules={report.dictionary_rules}"
                )

            if report.rule_replacements > 0:
                self.logger.write(
                    "POST_PROCESSOR "
                    f"replacements={report.rule_replacements} "
                    f"rules={report.rule_matches}"
                )

            return clean_text

        clean_text = self.cleaner.clean(
            raw_text
        )

        clean_text = self.normalizer.normalize(
            clean_text
        )

        clean_text, dictionary_report = (
            self.dictionary.correct_with_report(
                clean_text
            )
        )

        if dictionary_report["replacement_count"] > 0:
            self.logger.write(
                "DICTIONARY "
                f"replacements={dictionary_report['replacement_count']} "
                f"rules={dictionary_report['matched_rules']}"
            )

        return clean_text

    def _save_outputs(self, text):
        export_manager = getattr(
            self,
            "export_manager",
            None,
        )

        if export_manager is not None:
            return export_manager.export(
                text,
                formats=self.output_formats,
            )

        outputs = {}

        if self.output_format in {
            "both",
            "txt",
        }:
            outputs["txt"] = (
                self.text_exporter.save_text(
                    text
                )
            )

        if self.output_format in {
            "both",
            "docx",
        }:
            outputs["docx"] = (
                self.exporter.save_docx(
                    text
                )
            )

        return outputs

    def _transcribe_audio(self, audio_info):
        audio_path = audio_info.file_path

        if not self.splitter.should_split(
            audio_path
        ):
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
                progress_percent = (
                    self._chunk_progress(
                        index=index,
                        total_chunks=total_chunks,
                    )
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

                chunk_info = (
                    chunk_loader.load_info()
                )

                if chunk_info is None:
                    raise RuntimeError(
                        "Cannot load audio chunk: "
                        f"{chunk_path}"
                    )

                result = (
                    self.transcriber.transcribe(
                        chunk_info
                    )
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
                    "Whisper returned no text "
                    "for audio chunks"
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
                    "Cannot clean temporary "
                    "audio chunks: "
                    f"{cleanup_error}"
                )

            return 0

    @staticmethod
    def _extract_text(result):
        if not isinstance(result, dict):
            raise RuntimeError(
                "Transcriber returned "
                "an invalid result"
            )

        text = result.get("text")

        if not isinstance(text, str):
            raise RuntimeError(
                "Transcriber result does not "
                "contain valid text"
            )

        return text

    @staticmethod
    def _chunk_progress(
        index,
        total_chunks,
    ):
        if total_chunks <= 0:
            return 30

        start_percent = 35
        end_percent = 80

        return start_percent + int(
            (end_percent - start_percent)
            * index
            / total_chunks
        )
