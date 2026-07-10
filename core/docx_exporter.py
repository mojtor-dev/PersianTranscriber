"""
PersianTranscriber DOCX Exporter
Version: 0.1.0
"""

import os
from docx import Document

import config


class DocxExporter:

    def __init__(self):
        os.makedirs(
            config.DEFAULT_OUTPUT_FOLDER,
            exist_ok=True
        )

    def save_docx(
        self,
        text,
        filename="transcription.docx"
    ):

        path = os.path.join(
            config.DEFAULT_OUTPUT_FOLDER,
            filename
        )

        doc = Document()

        doc.add_paragraph(text)

        doc.save(path)

        return path
