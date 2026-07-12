import json
import tempfile
import unittest
from pathlib import Path

from core.exporters import ExportManager


class TestExportSuite(unittest.TestCase):

    def test_exports_text_formats(self):
        with tempfile.TemporaryDirectory() as directory:
            manager = ExportManager(
                output_dir=directory,
                subtitle_seconds=3,
            )

            outputs = manager.export(
                "سلام دنیا. حال شما چطور است؟",
                formats=[
                    "txt",
                    "md",
                    "json",
                    "srt",
                    "vtt",
                ],
            )

            self.assertEqual(
                set(outputs),
                {
                    "txt",
                    "md",
                    "json",
                    "srt",
                    "vtt",
                },
            )

            for output_path in outputs.values():
                self.assertTrue(
                    Path(output_path).is_file()
                )

            payload = json.loads(
                Path(
                    outputs["json"]
                ).read_text(
                    encoding="utf-8"
                )
            )

            self.assertIn(
                "سلام دنیا",
                payload["text"],
            )

            self.assertIn(
                "00:00:00,000 --> 00:00:03,000",
                Path(
                    outputs["srt"]
                ).read_text(
                    encoding="utf-8"
                ),
            )

            self.assertTrue(
                Path(
                    outputs["vtt"]
                ).read_text(
                    encoding="utf-8"
                ).startswith("WEBVTT")
            )

    def test_both_alias(self):
        with tempfile.TemporaryDirectory() as directory:
            manager = ExportManager(
                output_dir=directory
            )

            self.assertEqual(
                manager.normalize_formats(
                    "both"
                ),
                [
                    "txt",
                    "docx",
                ],
            )

    def test_rejects_unknown_format(self):
        with tempfile.TemporaryDirectory() as directory:
            manager = ExportManager(
                output_dir=directory
            )

            with self.assertRaisesRegex(
                ValueError,
                "Unknown output format",
            ):
                manager.normalize_formats(
                    ["unknown"]
                )


if __name__ == "__main__":
    unittest.main()
