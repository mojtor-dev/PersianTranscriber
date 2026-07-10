"""
PersianTranscriber Exporter
Version: 0.1.0
"""

import os

import config


class TextExporter:

    def __init__(self):
        os.makedirs(
            config.DEFAULT_OUTPUT_FOLDER,
            exist_ok=True
        )

    def save_txt(self, text, filename="transcription.txt"):

        path = os.path.join(
            config.DEFAULT_OUTPUT_FOLDER,
            filename
        )

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as file:
            file.write(text)

        return path
