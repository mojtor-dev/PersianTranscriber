"""
PersianTranscriber Audio Splitter
Version: 0.1.0
"""

import shutil
import subprocess
from pathlib import Path


class AudioSplitter:
    """
    تقسیم فایل صوتی آماده‌شده به قطعه‌های مرتب WAV با استفاده از ffmpeg.
    """

    DEFAULT_CHUNK_DURATION_SECONDS = 300

    def __init__(
        self,
        output_dir="temp/chunks",
        chunk_duration_seconds=DEFAULT_CHUNK_DURATION_SECONDS,
    ):
        if (
            not isinstance(chunk_duration_seconds, int)
            or isinstance(chunk_duration_seconds, bool)
            or chunk_duration_seconds <= 0
        ):
            raise ValueError(
                "chunk_duration_seconds must be a positive integer"
            )

        self.output_dir = Path(output_dir)
        self.chunk_duration_seconds = chunk_duration_seconds

    def split(self, audio_path):
        """
        فایل صوتی را تقسیم کرده و مسیر قطعه‌ها را به ترتیب بازمی‌گرداند.
        """
        source_path = Path(audio_path)

        if not source_path.exists():
            raise FileNotFoundError(
                f"Audio file not found: {source_path}"
            )

        if not source_path.is_file():
            raise ValueError(
                f"Audio path is not a file: {source_path}"
            )

        if shutil.which("ffmpeg") is None:
            raise RuntimeError(
                "ffmpeg is not installed or is not available in PATH"
            )

        self._prepare_output_directory()

        output_pattern = self.output_dir / "chunk_%04d.wav"

        command = [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(source_path),
            "-f",
            "segment",
            "-segment_time",
            str(self.chunk_duration_seconds),
            "-reset_timestamps",
            "1",
            "-c",
            "copy",
            str(output_pattern),
        ]

        subprocess.run(
            command,
            check=True,
        )

        chunks = sorted(
            self.output_dir.glob("chunk_*.wav")
        )

        if not chunks:
            raise RuntimeError(
                "ffmpeg completed but no audio chunks were created"
            )

        return [
            str(chunk_path)
            for chunk_path in chunks
        ]

    def _prepare_output_directory(self):
        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        for old_chunk in self.output_dir.glob("chunk_*.wav"):
            old_chunk.unlink()
