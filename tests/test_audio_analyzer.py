import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core.audio_analysis import AudioAnalyzer


class TestAudioAnalyzer(unittest.TestCase):

    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.audio_path = (
            Path(self.temporary_directory.name)
            / "technical_meeting.wav"
        )
        self.audio_path.write_bytes(b"audio")

    def tearDown(self):
        self.temporary_directory.cleanup()

    @patch("core.audio_analysis.analyzer.subprocess.run")
    def test_analyzes_ffprobe_output(self, mocked_run):
        mocked_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=json.dumps(
                {
                    "format": {
                        "duration": "600.5",
                        "bit_rate": "128000",
                        "format_name": "wav",
                    },
                    "streams": [
                        {
                            "codec_type": "audio",
                            "channels": 2,
                            "sample_rate": "16000",
                        }
                    ],
                }
            ),
            stderr="",
        )

        analysis = AudioAnalyzer().analyze(self.audio_path)

        self.assertEqual(analysis.duration_seconds, 600.5)
        self.assertEqual(analysis.channels, 2)
        self.assertEqual(analysis.sample_rate, 16000)
        self.assertIn("technical", analysis.filename_tokens)

    def test_rejects_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            AudioAnalyzer().analyze(
                self.audio_path.parent / "missing.wav"
            )


if __name__ == "__main__":
    unittest.main()
