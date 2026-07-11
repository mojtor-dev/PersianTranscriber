"""
PersianTranscriber Dictionary Engine
Version: 0.1.0
"""

import json
import os
import re


class DictionaryEngine:

    PERSIAN_WORD_CHARACTER_PATTERN = (
        r"آ-ی"
        r"\u200c"
    )

    def __init__(
        self,
        dictionary_path="data/persian_dictionary.json",
    ):
        self.dictionary_path = dictionary_path
        self.words = {}

        self.load()

    def load(self):
        if not os.path.exists(self.dictionary_path):
            return

        with open(
            self.dictionary_path,
            "r",
            encoding="utf-8",
        ) as file:
            self.words = json.load(file)

    def correct(self, text):
        if not text:
            return ""

        for wrong, correct in self.words.items():
            pattern = self._build_phrase_pattern(wrong)

            text = re.sub(
                pattern,
                lambda match, replacement=correct: replacement,
                text,
            )

        return text

    def _build_phrase_pattern(self, phrase):
        escaped_phrase = re.escape(phrase)

        return (
            rf"(?<![{self.PERSIAN_WORD_CHARACTER_PATTERN}])"
            rf"{escaped_phrase}"
            rf"(?![{self.PERSIAN_WORD_CHARACTER_PATTERN}])"
        )
