import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from core.audio_splitter import AudioSplitter


@unittest.skipUnless(
    shutil.which("ffmpeg"),
    "ffmpeg is required for AudioSplitter tests",
)
class TestAudioSplitter(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = (
            tempfile.TemporaryDirectory()
        )

        self.temp_path = Path(
            self.temporary_directory.name
        )

        self.audio_path = (
            self.temp_path
            / "sample.wav"
        )

        self.chunks_path = (
            self.temp_path
            / "chunks"
        )

        self._create_test_audio(
            duration_seconds=3
        )

    def tearDown(self):
        self.temporary_directory.cleanup()

    def _create_test_audio(self, duration_seconds):
        command = [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "lavfi",
            "-i",
            (
                "sine="
                "frequency=440:"
                f"duration={duration_seconds}"
            ),
            "-ac",
            "1",
            "-ar",
            "16000",
            str(self.audio_path),
        ]

        subprocess.run(
            command,
            check=True,
        )

    def test_rejects_invalid_chunk_duration(self):
        invalid_values = [
            0,
            -1,
            1.5,
            True,
            "10",
        ]

        for invalid_value in invalid_values:
            with self.subTest(value=invalid_value):
                with self.assertRaises(ValueError):
                    AudioSplitter(
                        chunk_duration_seconds=invalid_value
                    )

    def test_raises_for_missing_audio_file(self):
        splitter = AudioSplitter(
            output_dir=self.chunks_path,
            chunk_duration_seconds=1,
        )

        missing_path = (
            self.temp_path
            / "missing.wav"
        )

        with self.assertRaises(FileNotFoundError):
            splitter.split(missing_path)

    def test_splits_audio_into_ordered_chunks(self):
        splitter = AudioSplitter(
            output_dir=self.chunks_path,
            chunk_duration_seconds=1,
        )

        chunks = splitter.split(
            self.audio_path
        )

        self.assertGreaterEqual(
            len(chunks),
            3,
        )

        chunk_names = [
            Path(chunk).name
            for chunk in chunks
        ]

        self.assertEqual(
            chunk_names,
            sorted(chunk_names),
        )

        self.assertEqual(
            chunk_names[0],
            "chunk_0000.wav",
        )

        for chunk in chunks:
            chunk_path = Path(chunk)

            self.assertTrue(
                chunk_path.exists()
            )

            self.assertGreater(
                chunk_path.stat().st_size,
                0,
            )

    def test_removes_old_chunks_before_splitting(self):
        self.chunks_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        old_chunk = (
            self.chunks_path
            / "chunk_9999.wav"
        )

        old_chunk.write_bytes(
            b"old test data"
        )

        splitter = AudioSplitter(
            output_dir=self.chunks_path,
            chunk_duration_seconds=1,
        )

        chunks = splitter.split(
            self.audio_path
        )

        self.assertFalse(
            old_chunk.exists()
        )

        self.assertNotIn(
            str(old_chunk),
            chunks,
        )


if __name__ == "__main__":
    unittest.main()
