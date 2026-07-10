"""
PersianTranscriber Logger
Version: 0.1.0
"""

import os
from datetime import datetime


class AppLogger:

    def __init__(self):

        self.log_dir = "logs"

        os.makedirs(
            self.log_dir,
            exist_ok=True
        )

        self.file = os.path.join(
            self.log_dir,
            "session.log"
        )

    def write(self, message):

        time = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        with open(
            self.file,
            "a",
            encoding="utf-8"
        ) as f:

            f.write(
                f"[{time}] {message}\n"
            )

    def start(self, file):

        self.write(
            f"START file={file}"
        )

    def finish(self, output):

        self.write(
            f"COMPLETE output={output}"
        )

    def error(self, error):

        self.write(
            f"ERROR {error}"
        )
