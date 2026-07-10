"""
PersianTranscriber Audio Loader
Version: 0.1.0
"""

import os

from core.models import AudioInfo


class AudioLoader:

    SUPPORTED_FORMATS = [
        ".mp3",
        ".wav",
        ".m4a",
        ".flac"
    ]

    def __init__(self, file_path):
        self.file_path = file_path

    def exists(self):
        return os.path.exists(self.file_path)

    def get_extension(self):
        return os.path.splitext(self.file_path)[1].lower()

    def is_supported(self):
        return self.get_extension() in self.SUPPORTED_FORMATS

    def get_size(self):
        if self.exists():
            return os.path.getsize(self.file_path)
        return 0

    def load_info(self):

        if not self.exists():
            return None

        return AudioInfo(
            file_name=os.path.basename(self.file_path),
            file_path=self.file_path,
            extension=self.get_extension(),
            size=self.get_size()
        )
