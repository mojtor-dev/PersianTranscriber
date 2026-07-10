"""
PersianTranscriber Data Models
Version: 0.1.0
"""


class AudioInfo:

    def __init__(
        self,
        file_name,
        file_path,
        extension,
        size
    ):
        self.file_name = file_name
        self.file_path = file_path
        self.extension = extension
        self.size = size

    def to_dict(self):
        return {
            "file_name": self.file_name,
            "file_path": self.file_path,
            "extension": self.extension,
            "size": self.size
        }
