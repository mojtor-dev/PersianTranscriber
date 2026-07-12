"""
PersianTranscriber DOCX Exporter
Version: 0.2.0
"""

from pathlib import Path

from docx import Document


class DocxExporter:

    def __init__(self, output_dir="output"):
        self.output_dir = Path(
            output_dir
        )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def save_docx(
        self,
        text,
        filename="transcription.docx",
    ):
        output_path = (
            self.output_dir
            / filename
        )

        document = Document()
        document.add_paragraph(text)
        document.save(output_path)

        return str(output_path)
