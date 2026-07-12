"""
PersianTranscriber Whisper.cpp Engine
Version: 0.6.0
"""

import os
import subprocess
from pathlib import Path

from core.config_loader import ConfigLoader


class WhisperCppEngine:
    """
    اجرای محلی whisper.cpp و تبدیل فایل صوتی به متن.
    """

    DEFAULT_TIMEOUT_SECONDS = 60 * 60

    def __init__(
        self,
        model=None,
        language=None,
        project_root=None,
        whisper_bin=None,
        model_path=None,
        threads=None,
        timeout_seconds=DEFAULT_TIMEOUT_SECONDS,
        initial_prompt=None,
    ):
        config = ConfigLoader()

        self.model = model or config.get_model()
        self.language = language or config.get_language()

        self.project_root = self._resolve_project_root(
            project_root
        )

        self.whisper_bin = self._resolve_whisper_binary(
            whisper_bin
        )

        self.model_path = self._resolve_model_path(
            model_path
        )

        self.threads = self._resolve_threads(
            threads
        )

        self.timeout_seconds = self._validate_timeout(
            timeout_seconds
        )

        self.initial_prompt = self._validate_prompt(
            initial_prompt
        )

        self.loaded = False

    def load(self):
        if not self.whisper_bin.exists():
            raise FileNotFoundError(
                "whisper-cli not found: "
                f"{self.whisper_bin}"
            )

        if not self.whisper_bin.is_file():
            raise RuntimeError(
                "whisper-cli path is not a file: "
                f"{self.whisper_bin}"
            )

        if not os.access(self.whisper_bin, os.X_OK):
            raise PermissionError(
                "whisper-cli is not executable: "
                f"{self.whisper_bin}"
            )

        if not self.model_path.exists():
            raise FileNotFoundError(
                "Whisper model not found: "
                f"{self.model_path}"
            )

        if not self.model_path.is_file():
            raise RuntimeError(
                "Whisper model path is not a file: "
                f"{self.model_path}"
            )

        self.loaded = True

        prompt_status = (
            "enabled"
            if self.initial_prompt
            else "disabled"
        )

        print(
            "Whisper.cpp ready "
            f"(model={self.model}, "
            f"language={self.language}, "
            f"threads={self.threads}, "
            f"prompt={prompt_status})"
        )

        return True

    def transcribe(self, audio_path):
        source_path = Path(
            audio_path
        ).expanduser()

        if not source_path.exists():
            raise FileNotFoundError(
                f"Audio file not found: {source_path}"
            )

        if not source_path.is_file():
            raise ValueError(
                f"Audio path is not a file: {source_path}"
            )

        if not self.loaded:
            self.load()

        command = self.build_command(
            source_path
        )

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
                timeout=self.timeout_seconds,
            )
        except subprocess.TimeoutExpired as error:
            raise RuntimeError(
                "Whisper.cpp transcription timed out "
                f"after {self.timeout_seconds} seconds"
            ) from error
        except OSError as error:
            raise RuntimeError(
                "Failed to start whisper-cli: "
                f"{error}"
            ) from error

        if result.returncode != 0:
            error_message = (
                result.stderr.strip()
                or result.stdout.strip()
                or "Unknown whisper-cli error"
            )

            raise RuntimeError(
                "Whisper.cpp failed "
                f"(exit code {result.returncode}): "
                f"{error_message}"
            )

        return {
            "text": result.stdout.strip(),
            "file": str(source_path),
            "model": self.model,
            "language": self.language,
        }

    def build_command(self, audio_path):
        command = [
            str(self.whisper_bin),
            "-m",
            str(self.model_path),
            "-f",
            str(audio_path),
            "-l",
            self.language,
            "-t",
            str(self.threads),
            "-nt",
        ]

        if self.initial_prompt:
            command.extend(
                [
                    "--prompt",
                    self.initial_prompt,
                ]
            )

        return command

    def _resolve_project_root(self, project_root):
        if project_root is not None:
            return (
                Path(project_root)
                .expanduser()
                .resolve()
            )

        return Path(__file__).resolve().parents[2]

    def _resolve_whisper_binary(self, whisper_bin):
        if whisper_bin is not None:
            return (
                Path(whisper_bin)
                .expanduser()
                .resolve()
            )

        candidates = [
            (
                self.project_root
                / "tools"
                / "whisper.cpp"
                / "build"
                / "bin"
                / "whisper-cli"
            ),
            (
                self.project_root
                / "tools"
                / "whisper.cpp"
                / "main"
            ),
        ]

        for candidate in candidates:
            if candidate.exists():
                return candidate

        return candidates[0]

    def _resolve_model_path(self, model_path):
        if model_path is not None:
            return (
                Path(model_path)
                .expanduser()
                .resolve()
            )

        configured_model = Path(
            str(self.model)
        ).expanduser()

        if configured_model.suffix == ".bin":
            if configured_model.is_absolute():
                return configured_model.resolve()

            explicit_candidate = (
                self.project_root
                / configured_model
            )

            if explicit_candidate.exists():
                return explicit_candidate.resolve()

        return (
            self.project_root
            / "tools"
            / "whisper.cpp"
            / "models"
            / f"ggml-{self.model}.bin"
        )

    @staticmethod
    def _resolve_threads(threads):
        if threads is None:
            available_cpus = os.cpu_count() or 1

            return max(
                1,
                min(available_cpus, 6),
            )

        if (
            not isinstance(threads, int)
            or isinstance(threads, bool)
            or threads <= 0
        ):
            raise ValueError(
                "threads must be a positive integer"
            )

        return threads

    @staticmethod
    def _validate_timeout(timeout_seconds):
        if (
            not isinstance(timeout_seconds, int)
            or isinstance(timeout_seconds, bool)
            or timeout_seconds <= 0
        ):
            raise ValueError(
                "timeout_seconds must be a positive integer"
            )

        return timeout_seconds

    @staticmethod
    def _validate_prompt(initial_prompt):
        if initial_prompt is None:
            return None

        if not isinstance(initial_prompt, str):
            raise ValueError(
                "initial_prompt must be a string"
            )

        normalized_prompt = initial_prompt.strip()

        if not normalized_prompt:
            raise ValueError(
                "initial_prompt cannot be empty"
            )

        return normalized_prompt
