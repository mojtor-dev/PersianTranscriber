import json
import tempfile
import unittest
from pathlib import Path

from core.dictionary_engine import DictionaryEngine


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "whisper_fa_samples.json"
)

PROJECT_DICTIONARY_PATH = (
    Path(__file__).parent.parent
    / "data"
    / "persian_dictionary.json"
)


class TestDictionaryEngine(unittest.TestCase):
    def create_dictionary(self, entries):
        temporary_directory = tempfile.TemporaryDirectory()
        dictionary_path = (
            Path(temporary_directory.name)
            / "dictionary.json"
        )

        with dictionary_path.open(
            "w",
            encoding="utf-8",
        ) as dictionary_file:
            json.dump(
                entries,
                dictionary_file,
                ensure_ascii=False,
            )

        return temporary_directory, dictionary_path

    def test_returns_empty_string_for_empty_input(self):
        temporary_directory, dictionary_path = (
            self.create_dictionary({})
        )

        try:
            engine = DictionaryEngine(
                dictionary_path=str(dictionary_path)
            )

            self.assertEqual(engine.correct(""), "")
        finally:
            temporary_directory.cleanup()

    def test_loads_dictionary_from_json(self):
        temporary_directory, dictionary_path = (
            self.create_dictionary(
                {
                    "مطن": "متن",
                }
            )
        )

        try:
            engine = DictionaryEngine(
                dictionary_path=str(dictionary_path)
            )

            self.assertEqual(
                engine.words,
                {
                    "مطن": "متن",
                },
            )
        finally:
            temporary_directory.cleanup()

    def test_corrects_exact_word(self):
        temporary_directory, dictionary_path = (
            self.create_dictionary(
                {
                    "مطن": "متن",
                }
            )
        )

        try:
            engine = DictionaryEngine(
                dictionary_path=str(dictionary_path)
            )

            result = engine.correct(
                "این یک مطن آزمایشی است."
            )

            self.assertEqual(
                result,
                "این یک متن آزمایشی است.",
            )
        finally:
            temporary_directory.cleanup()

    def test_corrects_multiword_phrase(self):
        temporary_directory, dictionary_path = (
            self.create_dictionary(
                {
                    "نرم افسار": "نرم‌افزار",
                }
            )
        )

        try:
            engine = DictionaryEngine(
                dictionary_path=str(dictionary_path)
            )

            result = engine.correct(
                "این نرم افسار مفید است."
            )

            self.assertEqual(
                result,
                "این نرم‌افزار مفید است.",
            )
        finally:
            temporary_directory.cleanup()

    def test_does_not_replace_inside_larger_word(self):
        temporary_directory, dictionary_path = (
            self.create_dictionary(
                {
                    "مطن": "متن",
                }
            )
        )

        try:
            engine = DictionaryEngine(
                dictionary_path=str(dictionary_path)
            )

            result = engine.correct(
                "نامطن نباید تغییر کند."
            )

            self.assertEqual(
                result,
                "نامطن نباید تغییر کند.",
            )
        finally:
            temporary_directory.cleanup()

    def test_real_whisper_dictionary_corrections(self):
        with FIXTURE_PATH.open(
            "r",
            encoding="utf-8",
        ) as fixture_file:
            fixture_data = json.load(fixture_file)

        engine = DictionaryEngine(
            dictionary_path=str(PROJECT_DICTIONARY_PATH)
        )

        checked_corrections = 0

        for sample in fixture_data["samples"]:
            for correction in sample["confirmed_corrections"]:
                if correction["category"] != "dictionary":
                    continue

                result = engine.correct(
                    correction["input"]
                )

                self.assertEqual(
                    result,
                    correction["expected"],
                    msg=(
                        "Dictionary fixture correction failed: "
                        f"{sample['id']} / "
                        f"{correction['input']}"
                    ),
                )

                checked_corrections += 1

        self.assertGreater(
            checked_corrections,
            0,
            msg="No dictionary corrections found in fixture",
        )


if __name__ == "__main__":
    unittest.main()
