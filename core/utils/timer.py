"""
PersianTranscriber Timer
Version: 0.1.0
"""

import time


class Timer:

    def __init__(self):
        self.start_time = None

    def start(self):
        self.start_time = time.time()

    def elapsed(self):

        if self.start_time is None:
            return 0

        return round(
            time.time() - self.start_time,
            2
        )
