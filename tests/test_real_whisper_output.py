import json
import unittest
from pathlib import Path

from core.dictionary_engine import DictionaryEngine
from core.persian_normalizer import PersianNormalizer


PROJECT_ROOT = Path(__file__).parent.parent

FIXTURE_PATH = (
    PROJECT_ROOT
    / "tests"
    / "fixtures"
    / "whisper_fa_samples.json"
)

DICTIONARY_PATH = (
    PROJECT_ROOT
    / "data"
    / "persian_dictionary.json"
)


class TestRealWhisperOutput(unittest.TestCase):
    def setUp(self):
        self.normalizer = PersianNormalizer()

        self.dictionary = DictionaryEngine(
            dictionary_path=str(DICTIONARY_PATH)
        )

        with FIXTURE_PATH.open(
            "r",
            encoding="utf-8",
        ) as fixture_file:
            self.fixture_data = json.load(
                fixture_file
            )

    def process_text(self, text):
        normalized_text = self.normalizer.normalize(
            text
        )

        return self.dictionary.correct(
            normalized_text
        )

    def test_all_confirmed_corrections(self):
        checked_corrections = 0

        for sample in self.fixture_data["samples"]:
            for correction in sample[
                "confirmed_corrections"
            ]:
                source_text = correction["input"]

                if correction["category"] == "normalizer":
                    result = self.normalizer.normalize(
                        source_text
                    )
                elif correction["category"] == "dictionary":
                    result = self.process_text(
                        source_text
                    )
                else:
                    self.fail(
                        "Unknown correction category: "
                        f"{correction['category']}"
                    )

                self.assertEqual(
                    result,
                    correction["expected"],
                    msg=(
                        f"Correction failed in {sample['id']}: "
                        f"{source_text!r}"
                    ),
                )

                checked_corrections += 1

        self.assertGreaterEqual(
            checked_corrections,
            12,
        )

    def test_latest_real_output_is_corrected(self):
        latest_sample = next(
            sample
            for sample in self.fixture_data["samples"]
            if sample["id"] == "real-whisper-002"
        )

        corrected_text = self.process_text(
            latest_sample["raw_text"]
        )

        expected_phrases = [
            "صبح بخیر",
            "نرم‌افزاری",
            "کمک می‌کنه",
            "فایل‌های صوتی",
            "به متن",
            "امیدوارم",
            "خصوصاً",
            "دقت",
        ]

        for expected_phrase in expected_phrases:
            with self.subTest(
                phrase=expected_phrase
            ):
                self.assertIn(
                    expected_phrase,
                    corrected_text,
                )

        rejected_phrases = [
            "سب پخیر",
            "نرمفزری",
            "کومک",
            "سوطی",
            "بمتن",
            "اومید ورم",
            "اخصوصا",
            "دیقات",
        ]

        for rejected_phrase in rejected_phrases:
            with self.subTest(
                phrase=rejected_phrase
            ):
                self.assertNotIn(
                    rejected_phrase,
                    corrected_text,
                )

    def test_correction_pipeline_is_idempotent(self):
        latest_sample = next(
            sample
            for sample in self.fixture_data["samples"]
            if sample["id"] == "real-whisper-002"
        )

        first_result = self.process_text(
            latest_sample["raw_text"]
        )

        second_result = self.process_text(
            first_result
        )

        self.assertEqual(
            first_result,
            second_result,
        )


if __name__ == "__main__":
    unittest.main()
