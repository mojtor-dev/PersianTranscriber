import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import app
from core.audio_analysis import AudioAnalysis
from core.prompt_profiles.selector import PromptSelection


class FakePipeline:
    received_options = None

    def __init__(self, **options):
        type(self).received_options = options

    def run(self, audio_path):
        return {
            "txt": "output/transcription.txt",
        }


class FakeAnalyzer:
    def analyze(self, audio_path):
        return AudioAnalysis(
            file_path=str(audio_path),
            duration_seconds=600,
            channels=1,
            sample_rate=16000,
            bit_rate=128000,
            format_name="wav",
            file_size_bytes=1000,
            filename_tokens=(),
        )


class FakeSelector:
    def select(
        self,
        analysis,
        content_hint=None,
    ):
        return PromptSelection(
            profile_name="technical",
            confidence=0.9,
            reason="test",
        )


class TestCliAutoPrompt(unittest.TestCase):

    @patch(
        "app.TranscriptionPipeline",
        FakePipeline,
    )
    @patch(
        "app.AudioAnalyzer",
        return_value=FakeAnalyzer(),
    )
    @patch(
        "app.PromptProfileSelector",
        return_value=FakeSelector(),
    )
    def test_auto_profile_passes_prompt(
        self,
        mocked_selector,
        mocked_analyzer,
    ):
        with tempfile.TemporaryDirectory() as directory:
            audio_path = Path(directory) / "audio.wav"
            audio_path.write_bytes(b"audio")

            exit_code = app.main(
                [
                    str(audio_path),
                    "--txt-only",
                    "--auto-prompt-profile",
                ]
            )

        self.assertEqual(exit_code, 0)
        self.assertIn(
            "initial_prompt",
            FakePipeline.received_options,
        )
        self.assertIn(
            "جی‌پی‌تی",
            FakePipeline.received_options[
                "initial_prompt"
            ],
        )

    def test_content_hint_requires_auto_mode(self):
        with tempfile.TemporaryDirectory() as directory:
            audio_path = Path(directory) / "audio.wav"
            audio_path.write_bytes(b"audio")

            exit_code = app.main(
                [
                    str(audio_path),
                    "--content-hint",
                    "technical",
                ]
            )

        self.assertEqual(exit_code, 1)


if __name__ == "__main__":
    unittest.main()
