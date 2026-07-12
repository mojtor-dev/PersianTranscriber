import unittest

from core.pipeline import TranscriptionPipeline


class FakePostProcessor:
    def process(self, text):
        class Report:
            dictionary_replacements = 2
            dictionary_rules = 1
            rule_replacements = 3
            rule_matches = 2
        return "متن نهایی", Report()


class FakeLogger:
    def __init__(self):
        self.messages = []
    def write(self, message):
        self.messages.append(message)


class TestPipelineSmartPostProcessor(unittest.TestCase):
    def test_logs_dictionary_and_rule_reports(self):
        pipeline = TranscriptionPipeline.__new__(TranscriptionPipeline)
        pipeline.post_processor = FakePostProcessor()
        pipeline.logger = FakeLogger()
        result = pipeline._post_process_text("متن خام")
        self.assertEqual(result, "متن نهایی")
        self.assertEqual(pipeline.logger.messages, [
            "DICTIONARY replacements=2 rules=1",
            "POST_PROCESSOR replacements=3 rules=2",
        ])


if __name__ == "__main__":
    unittest.main()
