import unittest

from core.persian_normalizer import PersianNormalizer


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


if __name__ == "__main__":
    unittest.main()
