"""
PersianTranscriber Audio Preprocessor
Version: 0.1.0
"""

import os
import subprocess


class AudioPreprocessor:

    def __init__(self):

        self.temp_dir = "temp"

        os.makedirs(self.temp_dir, exist_ok=True)


    def prepare(self, audio_path):

        output = os.path.join(
            self.temp_dir,
            "prepared.wav"
        )

        command = [

            "ffmpeg",

            "-y",

            "-i",
            audio_path,

            "-ac",
            "1",

            "-ar",
            "16000",

            output

        ]

        subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )

        return output
