import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from core.pipeline import TranscriptionPipeline


class FakeProgress:
    def __init__(self):
        self.updates = []

    def update(self, percent, message):
        self.updates.append(
            (percent, message)
        )


class FakeLogger:
    def __init__(self):
        self.errors = []

    def error(self, message):
        self.errors.append(message)


class FakeTranscriber:
    def __init__(self, results_by_path):
        self.results_by_path = results_by_path
        self.transcribed_paths = []

    def transcribe(self, audio_info):
        audio_path = audio_info.file_path

        self.transcribed_paths.append(
            audio_path
        )

        result = self.results_by_path[
            audio_path
        ]

        if isinstance(result, Exception):
            raise result

        if isinstance(result, dict):
            return result

        return {
            "text": result
        }


class FakeSplitter:
    def __init__(
        self,
        should_split_result,
        chunk_paths=None,
        cleanup_error=None,
    ):
        self.should_split_result = (
            should_split_result
        )

        self.chunk_paths = (
            chunk_paths or []
        )

        self.cleanup_error = cleanup_error
        self.checked_paths = []
        self.split_paths = []
        self.cleanup_calls = 0

    def should_split(self, audio_path):
        self.checked_paths.append(
            audio_path
        )

        return self.should_split_result

    def split(self, audio_path):
        self.split_paths.append(
            audio_path
        )

        return self.chunk_paths

    def cleanup(self):
        self.cleanup_calls += 1

        if self.cleanup_error is not None:
            raise self.cleanup_error

        return len(self.chunk_paths)


class FakeMerger:
    def __init__(self):
        self.received_texts = None

    def merge(self, texts):
        self.received_texts = texts

        return "\n\n".join(texts)


class TestLongAudioPipeline(unittest.TestCase):
    def create_pipeline(
        self,
        transcriber,
        splitter,
        merger=None,
    ):
        pipeline = (
            TranscriptionPipeline.__new__(
                TranscriptionPipeline
            )
        )

        pipeline.transcriber = transcriber
        pipeline.splitter = splitter
        pipeline.merger = (
            merger or FakeMerger()
        )
        pipeline.progress = FakeProgress()
        pipeline.logger = FakeLogger()

        return pipeline

    def create_chunks(self, directory, count):
        directory_path = Path(directory)
        chunk_paths = []

        for index in range(count):
            chunk_path = (
                directory_path
                / f"chunk_{index:04d}.wav"
            )

            chunk_path.write_bytes(
                b"test"
            )

            chunk_paths.append(
                str(chunk_path)
            )

        return chunk_paths

    def test_short_audio_uses_original_file(self):
        audio_info = SimpleNamespace(
            file_path="short.wav"
        )

        transcriber = FakeTranscriber(
            {
                "short.wav": "متن کوتاه",
            }
        )

        splitter = FakeSplitter(
            should_split_result=False
        )

        pipeline = self.create_pipeline(
            transcriber=transcriber,
            splitter=splitter,
        )

        result = pipeline._transcribe_audio(
            audio_info
        )

        self.assertEqual(
            result,
            "متن کوتاه",
        )

        self.assertEqual(
            transcriber.transcribed_paths,
            ["short.wav"],
        )

        self.assertEqual(
            splitter.split_paths,
            [],
        )

        self.assertEqual(
            splitter.cleanup_calls,
            0,
        )

    def test_long_audio_transcribes_chunks_in_order(self):
        with tempfile.TemporaryDirectory() as directory:
            chunk_paths = self.create_chunks(
                directory,
                count=3,
            )

            transcriber = FakeTranscriber(
                {
                    chunk_paths[0]: "بخش اول",
                    chunk_paths[1]: "بخش دوم",
                    chunk_paths[2]: "بخش سوم",
                }
            )

            splitter = FakeSplitter(
                should_split_result=True,
                chunk_paths=chunk_paths,
            )

            merger = FakeMerger()

            pipeline = self.create_pipeline(
                transcriber=transcriber,
                splitter=splitter,
                merger=merger,
            )

            result = pipeline._transcribe_audio(
                SimpleNamespace(
                    file_path="long.mp3"
                )
            )

            self.assertEqual(
                transcriber.transcribed_paths,
                chunk_paths,
            )

            self.assertEqual(
                merger.received_texts,
                [
                    "بخش اول",
                    "بخش دوم",
                    "بخش سوم",
                ],
            )

            self.assertEqual(
                result,
                "بخش اول\n\nبخش دوم\n\nبخش سوم",
            )

            self.assertEqual(
                splitter.cleanup_calls,
                1,
            )

    def test_long_audio_ignores_empty_chunk_text(self):
        with tempfile.TemporaryDirectory() as directory:
            chunk_paths = self.create_chunks(
                directory,
                count=2,
            )

            transcriber = FakeTranscriber(
                {
                    chunk_paths[0]: "متن",
                    chunk_paths[1]: "   ",
                }
            )

            splitter = FakeSplitter(
                should_split_result=True,
                chunk_paths=chunk_paths,
            )

            merger = FakeMerger()

            pipeline = self.create_pipeline(
                transcriber=transcriber,
                splitter=splitter,
                merger=merger,
            )

            result = pipeline._transcribe_audio(
                SimpleNamespace(
                    file_path="long.wav"
                )
            )

            self.assertEqual(
                result,
                "متن",
            )

            self.assertEqual(
                merger.received_texts,
                ["متن"],
            )

            self.assertEqual(
                splitter.cleanup_calls,
                1,
            )

    def test_cleans_chunks_after_transcription_error(self):
        with tempfile.TemporaryDirectory() as directory:
            chunk_paths = self.create_chunks(
                directory,
                count=2,
            )

            transcriber = FakeTranscriber(
                {
                    chunk_paths[0]: "بخش اول",
                    chunk_paths[1]: RuntimeError(
                        "Whisper failed"
                    ),
                }
            )

            splitter = FakeSplitter(
                should_split_result=True,
                chunk_paths=chunk_paths,
            )

            pipeline = self.create_pipeline(
                transcriber=transcriber,
                splitter=splitter,
            )

            with self.assertRaisesRegex(
                RuntimeError,
                "Whisper failed",
            ):
                pipeline._transcribe_audio(
                    SimpleNamespace(
                        file_path="long.wav"
                    )
                )

            self.assertEqual(
                splitter.cleanup_calls,
                1,
            )

    def test_cleanup_error_does_not_hide_success(self):
        with tempfile.TemporaryDirectory() as directory:
            chunk_paths = self.create_chunks(
                directory,
                count=1,
            )

            transcriber = FakeTranscriber(
                {
                    chunk_paths[0]: "متن",
                }
            )

            splitter = FakeSplitter(
                should_split_result=True,
                chunk_paths=chunk_paths,
                cleanup_error=OSError(
                    "cleanup failed"
                ),
            )

            pipeline = self.create_pipeline(
                transcriber=transcriber,
                splitter=splitter,
            )

            result = pipeline._transcribe_audio(
                SimpleNamespace(
                    file_path="long.wav"
                )
            )

            self.assertEqual(
                result,
                "متن",
            )

            self.assertEqual(
                splitter.cleanup_calls,
                1,
            )

            self.assertEqual(
                len(pipeline.logger.errors),
                1,
            )

            self.assertIn(
                "cleanup failed",
                pipeline.logger.errors[0],
            )

    def test_rejects_invalid_transcriber_result(self):
        with self.assertRaises(RuntimeError):
            TranscriptionPipeline._extract_text(
                None
            )

        with self.assertRaises(RuntimeError):
            TranscriptionPipeline._extract_text(
                {}
            )

        with self.assertRaises(RuntimeError):
            TranscriptionPipeline._extract_text(
                {
                    "text": None,
                }
            )

    def test_chunk_progress_stays_in_range(self):
        progress_values = [
            TranscriptionPipeline._chunk_progress(
                index=index,
                total_chunks=4,
            )
            for index in range(1, 5)
        ]

        self.assertEqual(
            progress_values,
            sorted(progress_values),
        )

        self.assertGreaterEqual(
            progress_values[0],
            35,
        )

        self.assertEqual(
            progress_values[-1],
            80,
        )


if __name__ == "__main__":
    unittest.main()
