import json
import unittest
from pathlib import Path

from core.persian_normalizer import PersianNormalizer


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "whisper_fa_samples.json"
)


class TestPersianNormalizer(unittest.TestCase):
    def setUp(self):
        self.normalizer = PersianNormalizer()

    def test_empty_text(self):
        self.assertEqual(self.normalizer.normalize(""), "")

    def test_rejects_non_string_input(self):
        with self.assertRaises(TypeError):
            self.normalizer.normalize(None)

    def test_normalizes_arabic_characters(self):
        text = "كتاب يكي از بهترين منابع است."

        result = self.normalizer.normalize(text)

        self.assertEqual(
            result,
            "کتاب یکی از بهترین منابع است.",
        )

    def test_normalizes_arabic_digits(self):
        text = "سال ٢٠٢٦ و شماره ١٢٣"

        result = self.normalizer.normalize(text)

        self.assertEqual(
            result,
            "سال ۲۰۲۶ و شماره ۱۲۳",
        )

    def test_preserves_english_digits(self):
        text = "Version 123"

        result = self.normalizer.normalize(text)

        self.assertEqual(result, "Version 123")

    def test_removes_tatweel(self):
        text = "متــــن آزمایشی"

        result = self.normalizer.normalize(text)

        self.assertEqual(result, "متن آزمایشی")

    def test_normalizes_repeated_spaces(self):
        text = "این   یک    متن است."

        result = self.normalizer.normalize(text)

        self.assertEqual(result, "این یک متن است.")

    def test_normalizes_prefixes(self):
        text = "من مي روم و او نمي آيد."

        result = self.normalizer.normalize(text)

        self.assertEqual(
            result,
            "من می‌روم و او نمی‌آید.",
        )

    def test_normalizes_suffixes(self):
        text = "کتاب ها بهترين منبع ها هستند."

        result = self.normalizer.normalize(text)

        self.assertEqual(
            result,
            "کتاب‌ها بهترین منبع‌ها هستند.",
        )

    def test_normalizes_pronoun_suffixes_after_heh(self):
        text = "خانه ام بزرگ است و نامه اش را خواندم."

        result = self.normalizer.normalize(text)

        self.assertEqual(
            result,
            "خانه‌ام بزرگ است و نامه‌اش را خواندم.",
        )

    def test_normalizes_multiple_pronoun_suffixes_after_heh(self):
        text = "درباره ات گفتم و برنامه مان آماده است."

        result = self.normalizer.normalize(text)

        self.assertEqual(
            result,
            "درباره‌ات گفتم و برنامه‌مان آماده است.",
        )

    def test_normalizes_punctuation_spacing(self):
        text = "سلام ،حالت چطور است ؟"

        result = self.normalizer.normalize(text)

        self.assertEqual(
            result,
            "سلام، حالت چطور است؟",
        )

    def test_preserves_line_breaks(self):
        text = "خط اول\nخط دوم"

        result = self.normalizer.normalize(text)

        self.assertEqual(
            result,
            "خط اول\nخط دوم",
        )

    def test_limits_multiple_empty_lines(self):
        text = "خط اول\n\n\n\nخط دوم"

        result = self.normalizer.normalize(text)

        self.assertEqual(
            result,
            "خط اول\n\nخط دوم",
        )

    def test_normalization_is_idempotent(self):
        text = "من  مي روم ،اما او نمي آيد."

        first_result = self.normalizer.normalize(text)
        second_result = self.normalizer.normalize(first_result)

        self.assertEqual(first_result, second_result)

    def test_real_whisper_normalizer_corrections(self):
        with FIXTURE_PATH.open(
            "r",
            encoding="utf-8",
        ) as fixture_file:
            fixture_data = json.load(fixture_file)

        checked_corrections = 0

        for sample in fixture_data["samples"]:
            for correction in sample["confirmed_corrections"]:
                if correction["category"] != "normalizer":
                    continue

                result = self.normalizer.normalize(
                    correction["input"]
                )

                self.assertEqual(
                    result,
                    correction["expected"],
                    msg=(
                        "Fixture correction failed: "
                        f"{sample['id']}"
                    ),
                )

                checked_corrections += 1

        self.assertGreater(
            checked_corrections,
            0,
            msg="No normalizer corrections found in fixture",
        )


if __name__ == "__main__":
    unittest.main()
