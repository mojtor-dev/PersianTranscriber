"""
PersianTranscriber Audio Splitter
Version: 0.2.0
"""

import json
import shutil
import subprocess
from pathlib import Path


class AudioSplitter:
    """
    تشخیص مدت و تقسیم فایل صوتی با ffmpeg و ffprobe.
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

    def get_duration(self, audio_path):
        """
        مدت فایل صوتی را بر حسب ثانیه برمی‌گرداند.
        """
        source_path = self._validate_audio_path(audio_path)
        self._require_command("ffprobe")

        command = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            str(source_path),
        ]

        completed_process = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )

        probe_data = json.loads(
            completed_process.stdout
        )

        duration_value = (
            probe_data
            .get("format", {})
            .get("duration")
        )

        if duration_value is None:
            raise RuntimeError(
                "ffprobe did not return audio duration"
            )

        try:
            duration_seconds = float(duration_value)
        except (TypeError, ValueError) as error:
            raise RuntimeError(
                "ffprobe returned an invalid audio duration"
            ) from error

        if duration_seconds < 0:
            raise RuntimeError(
                "Audio duration cannot be negative"
            )

        return duration_seconds

    def should_split(self, audio_path):
        """
        مشخص می‌کند آیا فایل از اندازه‌ی یک chunk طولانی‌تر است.
        """
        return (
            self.get_duration(audio_path)
            > self.chunk_duration_seconds
        )

    def split(self, audio_path):
        """
        فایل صوتی را به قطعه‌های WAV مرتب تقسیم می‌کند.
        """
        source_path = self._validate_audio_path(audio_path)
        self._require_command("ffmpeg")

        self._prepare_output_directory()

        output_pattern = (
            self.output_dir
            / "chunk_%04d.wav"
        )

        command = [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(source_path),
            "-map",
            "0:a:0",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-f",
            "segment",
            "-segment_time",
            str(self.chunk_duration_seconds),
            "-reset_timestamps",
            "1",
            "-c:a",
            "pcm_s16le",
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

    @staticmethod
    def _require_command(command_name):
        if shutil.which(command_name) is None:
            raise RuntimeError(
                f"{command_name} is not installed "
                "or is not available in PATH"
            )

    @staticmethod
    def _validate_audio_path(audio_path):
        source_path = Path(audio_path)

        if not source_path.exists():
            raise FileNotFoundError(
                f"Audio file not found: {source_path}"
            )

        if not source_path.is_file():
            raise ValueError(
                f"Audio path is not a file: {source_path}"
            )

        return source_path

    def _prepare_output_directory(self):
        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        for old_chunk in self.output_dir.glob(
            "chunk_*.wav"
        ):
            old_chunk.unlink()
