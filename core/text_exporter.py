"""
PersianTranscriber Text Exporter
Version: 0.2.0
"""

from pathlib import Path


class TextExporter:

    def __init__(self, output_dir="output"):
        self.output_dir = Path(
            output_dir
        )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def save_text(
        self,
        text,
        filename="transcription.txt",
    ):
        output_path = (
            self.output_dir
            / filename
        )

        output_path.write_text(
            text,
            encoding="utf-8",
        )

        return str(output_path)
