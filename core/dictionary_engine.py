"""
PersianTranscriber Dictionary Engine
Version: 0.1.0
"""

import json
import os


class DictionaryEngine:


    def __init__(self, dictionary_path="data/persian_dictionary.json"):

        self.dictionary_path = dictionary_path

        self.words = {}

        self.load()


    def load(self):

        if not os.path.exists(self.dictionary_path):

            return

        with open(
            self.dictionary_path,
            "r",
            encoding="utf-8"
        ) as file:

            self.words = json.load(file)



    def correct(self, text):

        if not text:

            return ""


        for wrong, correct in self.words.items():

            text = text.replace(
                wrong,
                correct
            )


        return text
