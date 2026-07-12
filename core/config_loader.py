"""
PersianTranscriber Config Loader
Version: 1.0.0
"""

import configparser
import os


class ConfigLoader:

    def __init__(self, path="config.ini"):
        self.path = path
        self.config = configparser.ConfigParser()
        self.load()

    def load(self):

        if os.path.exists(self.path):
            self.config.read(
                self.path,
                encoding="utf-8"
            )

    def get_engine_name(self):

        return self.config.get(
            "ENGINE",
            "name",
            fallback="whisper"
        )

    def get_model(self):

        return self.config.get(
            "ENGINE",
            "model",
            fallback="base"
        )

    def get_language(self):

        return self.config.get(
            "ENGINE",
            "language",
            fallback="fa"
        )
