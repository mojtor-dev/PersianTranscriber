import json
import tempfile
import unittest
from pathlib import Path

from core.dictionary_engine import DictionaryEngine
from core.pipeline import TranscriptionPipeline


PROJECT_ROOT = Path(__file__).parent.parent

DATASET_PATH = (
    PROJECT_ROOT
    / "tests"
    / "fixtures"
    / "whisper_common_errors.json"
)

DICTIONARY_PATH = (
    PROJECT_ROOT
    / "data"
    / "persian_dictionary.json"
)


class FakeCleaner:
    def clean(self, text):
        return text.strip()


class FakeNormalizer:
    def normalize(self, text):
        return text


class FakeDictionary:
    def correct_with_report(self, text):
        return "متن نهایی", {
            "replacement_count": 3,
            "matched_rules": 2,
            "details": [],
        }


class FakeLogger:
    def __init__(self):
        self.messages = []

    def write(self, message):
        self.messages.append(message)


class TestDictionaryReporting(unittest.TestCase):

    def create_engine(self, entries):
        temporary_directory = (
            tempfile.TemporaryDirectory()
        )

        dictionary_path = (
            Path(temporary_directory.name)
            / "dictionary.json"
        )

        dictionary_path.write_text(
            json.dumps(
                entries,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        engine = DictionaryEngine(
            dictionary_path=str(dictionary_path)
        )

        return temporary_directory, engine

    def test_empty_text_returns_empty_report(self):
        temporary_directory, engine = (
            self.create_engine({})
        )

        try:
            corrected, report = (
                engine.correct_with_report("")
            )

            self.assertEqual(corrected, "")
            self.assertEqual(
                report["replacement_count"],
                0,
            )
            self.assertEqual(
                report["matched_rules"],
                0,
            )
            self.assertEqual(
                report["details"],
                [],
            )
        finally:
            temporary_directory.cleanup()

    def test_report_counts_repeated_replacements(self):
        temporary_directory, engine = (
            self.create_engine(
                {
                    "کومک": "کمک",
                }
            )
        )

        try:
            corrected, report = (
                engine.correct_with_report(
                    "کومک کن و دوباره کومک کن."
                )
            )

            self.assertEqual(
                corrected,
                "کمک کن و دوباره کمک کن.",
            )

            self.assertEqual(
                report["replacement_count"],
                2,
            )

            self.assertEqual(
                report["matched_rules"],
                1,
            )

            self.assertEqual(
                report["details"][0]["count"],
                2,
            )
        finally:
            temporary_directory.cleanup()

    def test_longer_phrase_has_priority(self):
        temporary_directory, engine = (
            self.create_engine(
                {
                    "کومک": "کمک",
                    "کومک مکنه": "کمک می‌کنه",
                }
            )
        )

        try:
            corrected, report = (
                engine.correct_with_report(
                    "کومک مکنه"
                )
            )

            self.assertEqual(
                corrected,
                "کمک می‌کنه",
            )

            self.assertEqual(
                report["replacement_count"],
                1,
            )
        finally:
            temporary_directory.cleanup()

    def test_patterns_are_compiled_once(self):
        temporary_directory, engine = (
            self.create_engine(
                {
                    "مطن": "متن",
                    "کومک": "کمک",
                }
            )
        )

        try:
            pattern_ids_before = [
                id(entry["pattern"])
                for entry in engine._compiled_entries
            ]

            engine.correct("مطن")
            engine.correct("کومک")

            pattern_ids_after = [
                id(entry["pattern"])
                for entry in engine._compiled_entries
            ]

            self.assertEqual(
                pattern_ids_before,
                pattern_ids_after,
            )
        finally:
            temporary_directory.cleanup()

    def test_verified_dataset(self):
        engine = DictionaryEngine(
            dictionary_path=str(
                DICTIONARY_PATH
            )
        )

        with DATASET_PATH.open(
            "r",
            encoding="utf-8",
        ) as dataset_file:
            dataset = json.load(
                dataset_file
            )

        checked_entries = 0

        for entry in dataset["entries"]:
            with self.subTest(
                source=entry["input"]
            ):
                corrected = engine.correct(
                    entry["input"]
                )

                self.assertEqual(
                    corrected,
                    entry["expected"],
                )

                checked_entries += 1

        self.assertGreaterEqual(
            checked_entries,
            12,
        )

    def test_pipeline_logs_dictionary_report(self):
        pipeline = (
            TranscriptionPipeline.__new__(
                TranscriptionPipeline
            )
        )

        pipeline.cleaner = FakeCleaner()
        pipeline.normalizer = FakeNormalizer()
        pipeline.dictionary = FakeDictionary()
        pipeline.logger = FakeLogger()

        result = pipeline._post_process_text(
            " متن خام "
        )

        self.assertEqual(
            result,
            "متن نهایی",
        )

        self.assertEqual(
            pipeline.logger.messages,
            [
                "DICTIONARY replacements=3 rules=2"
            ],
        )


if __name__ == "__main__":
    unittest.main()
