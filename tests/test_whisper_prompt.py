import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import app
from core.engines.whisper_cpp import WhisperCppEngine


class FakePipeline:
    received_options = None

    def __init__(self, **options):
        type(self).received_options = options

    def run(self, audio_path):
        return {
            "txt": "output/transcription.txt",
        }


class TestWhisperPrompt(unittest.TestCase):

    def create_engine(self, initial_prompt=None):
        temporary_directory = (
            tempfile.TemporaryDirectory()
        )

        root = Path(
            temporary_directory.name
        )

        binary = (
            root
            / "tools"
            / "whisper.cpp"
            / "build"
            / "bin"
            / "whisper-cli"
        )

        model = (
            root
            / "tools"
            / "whisper.cpp"
            / "models"
            / "ggml-small.bin"
        )

        binary.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        model.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        binary.write_text(
            "#!/bin/sh\n",
            encoding="utf-8",
        )

        binary.chmod(0o700)
        model.write_bytes(b"model")

        engine = WhisperCppEngine(
            model="small",
            language="fa",
            project_root=root,
            threads=4,
            initial_prompt=initial_prompt,
        )

        return temporary_directory, engine

    def test_command_without_prompt_is_unchanged(self):
        temporary_directory, engine = (
            self.create_engine()
        )

        try:
            command = engine.build_command(
                Path("sample.wav")
            )

            self.assertNotIn(
                "--prompt",
                command,
            )
        finally:
            temporary_directory.cleanup()

    def test_command_uses_long_prompt_option(self):
        temporary_directory, engine = (
            self.create_engine(
                initial_prompt=(
                    "هوش مصنوعی، جی‌پی‌تی و ترمکس."
                )
            )
        )

        try:
            command = engine.build_command(
                Path("sample.wav")
            )

            prompt_index = command.index(
                "--prompt"
            )

            self.assertEqual(
                command[prompt_index + 1],
                "هوش مصنوعی، جی‌پی‌تی و ترمکس.",
            )

            self.assertNotEqual(
                command[prompt_index],
                "-p",
            )
        finally:
            temporary_directory.cleanup()

    def test_rejects_empty_prompt(self):
        with self.assertRaises(ValueError):
            self.create_engine(
                initial_prompt="   "
            )

    def test_reads_prompt_file(self):
        parser = app.build_parser()

        with tempfile.TemporaryDirectory() as directory:
            prompt_path = (
                Path(directory)
                / "prompt.txt"
            )

            prompt_path.write_text(
                "نرم‌افزار و تبدیل گفتار به متن.",
                encoding="utf-8",
            )

            args = parser.parse_args(
                [
                    "audio.wav",
                    "--prompt-file",
                    str(prompt_path),
                ]
            )

            result = app.resolve_initial_prompt(
                args
            )

        self.assertEqual(
            result,
            "نرم‌افزار و تبدیل گفتار به متن.",
        )

    @patch(
        "app.TranscriptionPipeline",
        FakePipeline,
    )
    def test_cli_passes_prompt_to_pipeline(self):
        with tempfile.TemporaryDirectory() as directory:
            audio_path = (
                Path(directory)
                / "audio.wav"
            )

            audio_path.write_bytes(b"audio")

            exit_code = app.main(
                [
                    str(audio_path),
                    "--txt-only",
                    "--prompt",
                    "جی‌پی‌تی و هوش مصنوعی.",
                ]
            )

        self.assertEqual(
            exit_code,
            0,
        )

        self.assertEqual(
            FakePipeline.received_options[
                "initial_prompt"
            ],
            "جی‌پی‌تی و هوش مصنوعی.",
        )


if __name__ == "__main__":
    unittest.main()
