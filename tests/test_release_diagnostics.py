import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core.release import ReleaseDiagnostics


class TestReleaseDiagnostics(unittest.TestCase):

    def test_reports_missing_commands(self):
        with tempfile.TemporaryDirectory() as directory:
            diagnostics = ReleaseDiagnostics(
                project_root=directory
            )

            with patch(
                "core.release.diagnostics.shutil.which",
                return_value=None,
            ):
                results = diagnostics.run()

        python_result = next(
            result
            for result in results
            if result.name == "python"
        )

        self.assertFalse(
            python_result.ok
        )

    def test_detects_whisper_binary_and_model(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

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

            diagnostics = ReleaseDiagnostics(
                project_root=root
            )

            results = diagnostics.run()

        whisper_result = next(
            result
            for result in results
            if result.name == "whisper-cli"
        )

        model_result = next(
            result
            for result in results
            if result.name == "whisper-model"
        )

        self.assertTrue(
            whisper_result.ok
        )
        self.assertTrue(
            model_result.ok
        )


if __name__ == "__main__":
    unittest.main()
