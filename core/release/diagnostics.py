import os
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class DiagnosticResult:
    name: str
    ok: bool
    message: str
    required: bool = True

    def to_dict(self):
        return asdict(self)


class ReleaseDiagnostics:

    def __init__(self, project_root=None):
        self.project_root = (
            Path(project_root).expanduser().resolve()
            if project_root is not None
            else Path(__file__).resolve().parents[2]
        )

    def run(self):
        return [
            self._check_command("python"),
            self._check_command("ffmpeg"),
            self._check_command("ffprobe"),
            self._check_whisper_binary(),
            self._check_model(),
            self._check_output_directory(),
            self._check_temp_directory(),
        ]

    def failed_required(self):
        return [
            result
            for result in self.run()
            if result.required and not result.ok
        ]

    def _check_command(self, command):
        path = shutil.which(command)

        if path:
            return DiagnosticResult(
                name=command,
                ok=True,
                message=f"available: {path}",
            )

        return DiagnosticResult(
            name=command,
            ok=False,
            message=f"not found in PATH: {command}",
        )

    def _check_whisper_binary(self):
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
            if (
                candidate.is_file()
                and os.access(candidate, os.X_OK)
            ):
                return DiagnosticResult(
                    name="whisper-cli",
                    ok=True,
                    message=f"available: {candidate}",
                )

        return DiagnosticResult(
            name="whisper-cli",
            ok=False,
            message=(
                "whisper.cpp executable not found or "
                "not executable"
            ),
        )

    def _check_model(self):
        models_dir = (
            self.project_root
            / "tools"
            / "whisper.cpp"
            / "models"
        )

        models = (
            sorted(models_dir.glob("ggml-*.bin"))
            if models_dir.is_dir()
            else []
        )

        if models:
            return DiagnosticResult(
                name="whisper-model",
                ok=True,
                message=(
                    f"{len(models)} model(s): "
                    + ", ".join(
                        model.name
                        for model in models
                    )
                ),
            )

        return DiagnosticResult(
            name="whisper-model",
            ok=False,
            message="no ggml-*.bin model found",
        )

    def _check_output_directory(self):
        output_dir = self.project_root / "output"

        try:
            output_dir.mkdir(
                parents=True,
                exist_ok=True,
            )
            probe = output_dir / ".write_test"
            probe.write_text(
                "ok",
                encoding="utf-8",
            )
            probe.unlink()
        except OSError as error:
            return DiagnosticResult(
                name="output-directory",
                ok=False,
                message=str(error),
            )

        return DiagnosticResult(
            name="output-directory",
            ok=True,
            message=f"writable: {output_dir}",
        )

    def _check_temp_directory(self):
        temp_dir = self.project_root / "temp"

        try:
            temp_dir.mkdir(
                parents=True,
                exist_ok=True,
            )
            probe = temp_dir / ".write_test"
            probe.write_text(
                "ok",
                encoding="utf-8",
            )
            probe.unlink()
        except OSError as error:
            return DiagnosticResult(
                name="temp-directory",
                ok=False,
                message=str(error),
            )

        return DiagnosticResult(
            name="temp-directory",
            ok=True,
            message=f"writable: {temp_dir}",
        )
