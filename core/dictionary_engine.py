"""
PersianTranscriber Dictionary Engine
Version: 0.3.0
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
        self._compiled_entries = []

        self.load()

    def load(self):
        if not os.path.exists(self.dictionary_path):
            self.words = {}
            self._compiled_entries = []
            return

        with open(
            self.dictionary_path,
            "r",
            encoding="utf-8",
        ) as file:
            loaded_words = json.load(file)

        if not isinstance(loaded_words, dict):
            raise ValueError(
                "Dictionary JSON must contain an object"
            )

        for wrong, correct in loaded_words.items():
            if not isinstance(wrong, str):
                raise ValueError(
                    "Dictionary keys must be strings"
                )

            if not isinstance(correct, str):
                raise ValueError(
                    "Dictionary values must be strings"
                )

            if not wrong:
                raise ValueError(
                    "Dictionary keys cannot be empty"
                )

        self.words = loaded_words
        self._compile_entries()

    def correct(self, text):
        corrected_text, _ = self.correct_with_report(
            text
        )

        return corrected_text

    def correct_with_report(self, text):
        if not text:
            return "", {
                "replacement_count": 0,
                "matched_rules": 0,
                "details": [],
            }

        corrected_text = text
        replacement_count = 0
        details = []

        for entry in self._compiled_entries:
            corrected_text, count = (
                entry["pattern"].subn(
                    lambda match, replacement=entry[
                        "correct"
                    ]: replacement,
                    corrected_text,
                )
            )

            if count == 0:
                continue

            replacement_count += count

            details.append(
                {
                    "wrong": entry["wrong"],
                    "correct": entry["correct"],
                    "count": count,
                }
            )

        report = {
            "replacement_count": replacement_count,
            "matched_rules": len(details),
            "details": details,
        }

        return corrected_text, report

    def _compile_entries(self):
        ordered_entries = sorted(
            self.words.items(),
            key=lambda item: len(item[0]),
            reverse=True,
        )

        self._compiled_entries = [
            {
                "wrong": wrong,
                "correct": correct,
                "pattern": re.compile(
                    self._build_phrase_pattern(
                        wrong
                    )
                ),
            }
            for wrong, correct in ordered_entries
        ]

    def _build_phrase_pattern(self, phrase):
        escaped_phrase = re.escape(phrase)

        return (
            rf"(?<![{self.PERSIAN_WORD_CHARACTER_PATTERN}])"
            rf"{escaped_phrase}"
            rf"(?![{self.PERSIAN_WORD_CHARACTER_PATTERN}])"
        )
