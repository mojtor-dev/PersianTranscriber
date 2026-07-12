import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core.engines.whisper_cpp import WhisperCppEngine


class TestWhisperCppEngine(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = (
            tempfile.TemporaryDirectory()
        )

        self.project_root = Path(
            self.temporary_directory.name
        )

        self.binary_path = (
            self.project_root
            / "tools"
            / "whisper.cpp"
            / "build"
            / "bin"
            / "whisper-cli"
        )

        self.model_path = (
            self.project_root
            / "tools"
            / "whisper.cpp"
            / "models"
            / "ggml-small.bin"
        )

        self.audio_path = (
            self.project_root
            / "sample.wav"
        )

        self.binary_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.model_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.binary_path.write_text(
            "#!/bin/sh\nexit 0\n",
            encoding="utf-8",
        )

        self.binary_path.chmod(0o700)

        self.model_path.write_bytes(
            b"fake model"
        )

        self.audio_path.write_bytes(
            b"fake audio"
        )

    def tearDown(self):
        self.temporary_directory.cleanup()

    def create_engine(self, **overrides):
        arguments = {
            "model": "small",
            "language": "fa",
            "project_root": self.project_root,
            "threads": 4,
            "timeout_seconds": 60,
        }

        arguments.update(overrides)

        return WhisperCppEngine(
            **arguments
        )

    def test_load_validates_binary_and_model(self):
        engine = self.create_engine()

        self.assertTrue(
            engine.load()
        )

        self.assertTrue(
            engine.loaded
        )

    def test_load_raises_when_binary_is_missing(self):
        self.binary_path.unlink()

        engine = self.create_engine()

        with self.assertRaises(FileNotFoundError):
            engine.load()

    def test_load_raises_when_model_is_missing(self):
        self.model_path.unlink()

        engine = self.create_engine()

        with self.assertRaises(FileNotFoundError):
            engine.load()

    def test_build_command_contains_required_options(self):
        engine = self.create_engine()

        command = engine.build_command(
            self.audio_path
        )

        self.assertEqual(
            command,
            [
                str(self.binary_path),
                "-m",
                str(self.model_path),
                "-f",
                str(self.audio_path),
                "-l",
                "fa",
                "-t",
                "4",
                "-nt",
            ],
        )

    @patch(
        "core.engines.whisper_cpp.subprocess.run"
    )
    def test_transcribe_returns_clean_result(
        self,
        mocked_run,
    ):
        mocked_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="  سلام دنیا  \n",
            stderr="",
        )

        engine = self.create_engine()

        result = engine.transcribe(
            self.audio_path
        )

        self.assertEqual(
            result["text"],
            "سلام دنیا",
        )

        self.assertEqual(
            result["file"],
            str(self.audio_path),
        )

        self.assertEqual(
            result["model"],
            "small",
        )

        self.assertEqual(
            result["language"],
            "fa",
        )

        mocked_run.assert_called_once()

    @patch(
        "core.engines.whisper_cpp.subprocess.run"
    )
    def test_transcribe_raises_for_cli_failure(
        self,
        mocked_run,
    ):
        mocked_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=1,
            stdout="",
            stderr="model loading failed",
        )

        engine = self.create_engine()

        with self.assertRaisesRegex(
            RuntimeError,
            "model loading failed",
        ):
            engine.transcribe(
                self.audio_path
            )

    @patch(
        "core.engines.whisper_cpp.subprocess.run"
    )
    def test_transcribe_raises_for_timeout(
        self,
        mocked_run,
    ):
        mocked_run.side_effect = subprocess.TimeoutExpired(
            cmd=["whisper-cli"],
            timeout=60,
        )

        engine = self.create_engine()

        with self.assertRaisesRegex(
            RuntimeError,
            "timed out",
        ):
            engine.transcribe(
                self.audio_path
            )

    def test_transcribe_rejects_missing_audio(self):
        engine = self.create_engine()

        with self.assertRaises(FileNotFoundError):
            engine.transcribe(
                self.project_root
                / "missing.wav"
            )

    def test_rejects_invalid_threads(self):
        invalid_values = [
            0,
            -1,
            1.5,
            True,
            "4",
        ]

        for invalid_value in invalid_values:
            with self.subTest(value=invalid_value):
                with self.assertRaises(ValueError):
                    self.create_engine(
                        threads=invalid_value
                    )

    def test_rejects_invalid_timeout(self):
        invalid_values = [
            0,
            -1,
            1.5,
            True,
            "60",
        ]

        for invalid_value in invalid_values:
            with self.subTest(value=invalid_value):
                with self.assertRaises(ValueError):
                    self.create_engine(
                        timeout_seconds=invalid_value
                    )


if __name__ == "__main__":
    unittest.main()
