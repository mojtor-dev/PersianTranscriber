# Safe audio metadata analysis using ffprobe.

import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class AudioAnalysis:
    file_path: str
    duration_seconds: float
    channels: int
    sample_rate: int
    bit_rate: int | None
    format_name: str
    file_size_bytes: int
    filename_tokens: tuple[str, ...]

    def to_dict(self):
        payload = asdict(self)
        payload["filename_tokens"] = list(self.filename_tokens)
        return payload


class AudioAnalyzer:

    def __init__(self, ffprobe_binary="ffprobe", timeout_seconds=30):
        if (
            not isinstance(timeout_seconds, int)
            or isinstance(timeout_seconds, bool)
            or timeout_seconds <= 0
        ):
            raise ValueError(
                "timeout_seconds must be a positive integer"
            )

        self.ffprobe_binary = ffprobe_binary
        self.timeout_seconds = timeout_seconds

    def analyze(self, audio_path):
        source_path = Path(audio_path).expanduser().resolve()

        if not source_path.is_file():
            raise FileNotFoundError(
                f"Audio file not found: {source_path}"
            )

        command = [
            self.ffprobe_binary,
            "-v",
            "error",
            "-show_entries",
            (
                "format=duration,bit_rate,format_name:"
                "stream=codec_type,channels,sample_rate"
            ),
            "-of",
            "json",
            str(source_path),
        ]

        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
                timeout=self.timeout_seconds,
            )
        except subprocess.TimeoutExpired as error:
            raise RuntimeError(
                "ffprobe analysis timed out"
            ) from error
        except OSError as error:
            raise RuntimeError(
                f"Failed to start ffprobe: {error}"
            ) from error

        if completed.returncode != 0:
            message = (
                completed.stderr.strip()
                or completed.stdout.strip()
                or "unknown ffprobe error"
            )
            raise RuntimeError(
                f"ffprobe failed: {message}"
            )

        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError as error:
            raise RuntimeError(
                "ffprobe returned invalid JSON"
            ) from error

        format_data = payload.get("format", {})
        streams = payload.get("streams", [])
        audio_stream = next(
            (
                stream
                for stream in streams
                if stream.get("codec_type") == "audio"
            ),
            {},
        )

        duration_seconds = self._parse_float(
            format_data.get("duration"),
            default=0.0,
        )
        channels = self._parse_int(
            audio_stream.get("channels"),
            default=1,
        )
        sample_rate = self._parse_int(
            audio_stream.get("sample_rate"),
            default=0,
        )
        bit_rate = self._parse_optional_int(
            format_data.get("bit_rate")
        )
        format_name = str(
            format_data.get(
                "format_name",
                source_path.suffix.lstrip("."),
            )
        )

        return AudioAnalysis(
            file_path=str(source_path),
            duration_seconds=duration_seconds,
            channels=max(1, channels),
            sample_rate=max(0, sample_rate),
            bit_rate=bit_rate,
            format_name=format_name,
            file_size_bytes=source_path.stat().st_size,
            filename_tokens=self._tokenize_filename(
                source_path.stem
            ),
        )

    @staticmethod
    def _tokenize_filename(filename):
        normalized = (
            filename.lower()
            .replace("-", " ")
            .replace("_", " ")
            .replace(".", " ")
        )
        return tuple(
            token
            for token in normalized.split()
            if token
        )

    @staticmethod
    def _parse_float(value, default):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _parse_int(value, default):
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _parse_optional_int(value):
        try:
            return int(value)
        except (TypeError, ValueError):
            return None
