import unittest

from core.post_processing import PersianPostProcessor
from core.post_processing.rule_engine import PostProcessingRuleEngine


class TestSmartPostProcessor(unittest.TestCase):
    def test_safe_rules_are_idempotent(self):
        engine = PostProcessingRuleEngine()
        text = "سلام  ،،دنیا!!!\n\n\nپایان"
        first, _ = engine.apply(text)
        second, _ = engine.apply(first)
        self.assertEqual(first, second)

    def test_real_processor_reports_changes(self):
        processor = PersianPostProcessor()
        result, report = processor.process("  اين  مطن ،، آزمایشی است؟؟  ")
        self.assertIn("این متن، آزمایشی است؟", result)
        self.assertGreaterEqual(report.total_replacements, 1)

    def test_rejects_non_string_input(self):
        processor = PersianPostProcessor()
        with self.assertRaises(TypeError):
            processor.process(None)


if __name__ == "__main__":
    unittest.main()
