import tempfile
import unittest
from pathlib import Path

from scripts.benchmark_prompts_safe import SafeResult, load_result, save_result, safe_name, variants


class TestSafeBenchmark(unittest.TestCase):
    def test_safe_name(self):
        self.assertEqual(safe_name("technical sentence"), "technical_sentence")

    def test_variants_include_baseline(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            (path / "a.txt").write_text("x", encoding="utf-8")
            result = variants(path)
        self.assertEqual(result[0]["name"], "baseline-no-prompt")
        self.assertEqual(result[1]["name"], "a")

    def test_result_round_trip(self):
        item = SafeResult("x", "سلام", 1.0, 0.0, 0.0, 0.0, False)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "result.json"
            save_result(item, path)
            loaded = load_result(path)
        self.assertEqual(item, loaded)


if __name__ == "__main__":
    unittest.main()
