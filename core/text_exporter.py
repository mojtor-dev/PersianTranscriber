"""
PersianTranscriber Text Exporter
Version: 0.1.0
"""

import os


class TextExporter:

    def __init__(self):

        self.output_dir = "output"

        os.makedirs(
            self.output_dir,
            exist_ok=True
        )

    def save_text(
        self,
        text,
        filename="transcription.txt"
    ):

        output_path = os.path.join(
            self.output_dir,
            filename
        )

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(text)

        return output_path
