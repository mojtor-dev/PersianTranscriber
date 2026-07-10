"""
PersianTranscriber Progress Manager
Version: 0.1.0
"""


class ProgressManager:

    def __init__(self):

        self.current = 0


    def update(self, percent, message):

        self.current = percent

        print(
            f"[{percent}%] {message}"
        )


    def start(self):

        self.update(
            0,
            "Starting"
        )


    def finish(self):

        self.update(
            100,
            "Completed"
        )
