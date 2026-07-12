import io
import tempfile
import unittest
from contextlib import redirect_stderr
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import app


class FakePipeline:
    received_options = None
    received_audio = None

    def __init__(self, **options):
        type(self).received_options = options

    def run(self, audio_path):
        type(self).received_audio = audio_path

        return {
            "txt": "output/transcription.txt",
            "docx": "output/transcription.docx",
        }


class TestCommandLineInterface(unittest.TestCase):

    def test_positive_integer(self):
        self.assertEqual(
            app.positive_integer("6"),
            6,
        )

        invalid_values = [
            "0",
            "-1",
            "abc",
        ]

        for value in invalid_values:
            with self.subTest(value=value):
                with self.assertRaises(
                    Exception
                ):
                    app.positive_integer(
                        value
                    )

    def test_no_audio_prints_help(self):
        output = io.StringIO()

        with redirect_stdout(output):
            exit_code = app.main([])

        self.assertEqual(
            exit_code,
            0,
        )

        self.assertIn(
            "usage:",
            output.getvalue(),
        )

    def test_missing_audio_returns_code_two(self):
        error_output = io.StringIO()

        with redirect_stderr(error_output):
            exit_code = app.main(
                ["missing-file.mp3"]
            )

        self.assertEqual(
            exit_code,
            2,
        )

        self.assertIn(
            "Audio file not found",
            error_output.getvalue(),
        )

    @patch(
        "app.TranscriptionPipeline",
        FakePipeline,
    )
    def test_cli_passes_options_to_pipeline(self):
        with tempfile.TemporaryDirectory() as directory:
            audio_path = (
                Path(directory)
                / "sample.wav"
            )

            audio_path.write_bytes(
                b"audio"
            )

            output = io.StringIO()

            with redirect_stdout(output):
                exit_code = app.main(
                    [
                        str(audio_path),
                        "--engine",
                        "whisper_cpp",
                        "--model",
                        "medium",
                        "--language",
                        "fa",
                        "--threads",
                        "4",
                        "--timeout",
                        "900",
                        "--chunk-duration",
                        "240",
                        "--output-dir",
                        "results",
                        "--txt-only",
                    ]
                )

        self.assertEqual(
            exit_code,
            0,
        )

        self.assertEqual(
            FakePipeline.received_audio,
            str(audio_path),
        )

        self.assertEqual(
            FakePipeline.received_options,
            {
                "engine_name": "whisper_cpp",
                "model": "medium",
                "language": "fa",
                "threads": 4,
                "timeout_seconds": 900,
                "chunk_duration_seconds": 240,
                "output_dir": "results",
                "output_format": "txt",
                "output_formats": ["txt"],
                "subtitle_seconds": 5,
            },
        )

        self.assertIn(
            "Completed successfully",
            output.getvalue(),
        )

    @patch(
        "app.TranscriptionPipeline"
    )
    def test_runtime_error_returns_code_one(
        self,
        mocked_pipeline,
    ):
        with tempfile.TemporaryDirectory() as directory:
            audio_path = (
                Path(directory)
                / "sample.wav"
            )

            audio_path.write_bytes(
                b"audio"
            )

            mocked_pipeline.return_value.run.side_effect = (
                RuntimeError("Whisper failed")
            )

            error_output = io.StringIO()

            with redirect_stderr(error_output):
                exit_code = app.main(
                    [str(audio_path)]
                )

        self.assertEqual(
            exit_code,
            1,
        )

        self.assertIn(
            "Whisper failed",
            error_output.getvalue(),
        )

    def test_output_format_resolution(self):
        parser = app.build_parser()

        both_args = parser.parse_args(
            ["audio.wav"]
        )

        txt_args = parser.parse_args(
            [
                "audio.wav",
                "--txt-only",
            ]
        )

        docx_args = parser.parse_args(
            [
                "audio.wav",
                "--docx-only",
            ]
        )

        self.assertEqual(
            app.resolve_output_format(
                both_args
            ),
            "both",
        )

        self.assertEqual(
            app.resolve_output_format(
                txt_args
            ),
            "txt",
        )

        self.assertEqual(
            app.resolve_output_format(
                docx_args
            ),
            "docx",
        )


if __name__ == "__main__":
    unittest.main()
