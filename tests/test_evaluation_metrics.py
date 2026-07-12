import unittest
from core.evaluation.metrics import character_error_rate, levenshtein_distance, normalize_evaluation_text, word_error_rate

class TestEvaluationMetrics(unittest.TestCase):
    def test_levenshtein(self):
        self.assertEqual(levenshtein_distance(list("kitten"), list("sitting")), 3)
    def test_normalization(self):
        self.assertEqual(normalize_evaluation_text("  كتاب، يكي!  "), "کتاب یکی")
    def test_wer_exact(self):
        self.assertEqual(word_error_rate("سلام دنیا", "سلام دنیا"), 0.0)
    def test_wer_substitution(self):
        self.assertEqual(word_error_rate("سلام دنیا", "سلام ایران"), 0.5)
    def test_cer_exact(self):
        self.assertEqual(character_error_rate("سلام", "سلام"), 0.0)
    def test_empty_reference(self):
        self.assertEqual(word_error_rate("", ""), 0.0)
        self.assertEqual(word_error_rate("", "متن"), 1.0)

if __name__ == "__main__":
    unittest.main()
