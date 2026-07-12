import json
import tempfile
import unittest
from pathlib import Path
from core.evaluation import PromptBenchmark, PromptVariant, write_html_report, write_json_report

class TestPromptBenchmark(unittest.TestCase):
    def test_ranking(self):
        hypotheses = {"baseline": "سلام ایران", "prompted": "سلام دنیا"}
        results = PromptBenchmark("سلام دنیا", lambda variant: hypotheses[variant.name]).run([
            PromptVariant(name="baseline"),
            PromptVariant(name="prompted", prompt="سلام دنیا"),
        ])
        self.assertEqual(results[0].name, "prompted")
        self.assertEqual(results[0].wer, 0.0)
    def test_runner_error(self):
        def runner(_):
            raise RuntimeError("failed")
        result = PromptBenchmark("سلام", runner).run([PromptVariant(name="broken")])[0]
        self.assertEqual(result.error, "failed")
        self.assertEqual(result.wer, 1.0)
    def test_conflicting_sources(self):
        with self.assertRaises(ValueError):
            PromptVariant(name="invalid", prompt="x", prompt_file="y")
    def test_reports(self):
        results = PromptBenchmark("سلام", lambda _: "سلام").run([PromptVariant(name="baseline")])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            json_path = write_json_report(results, root / "report.json", {"audio": "sample.wav"})
            html_path = write_html_report(results, root / "report.html", {"audio": "sample.wav"})
            payload = json.loads(Path(json_path).read_text(encoding="utf-8"))
            html_text = Path(html_path).read_text(encoding="utf-8")
        self.assertEqual(payload["results"][0]["name"], "baseline")
        self.assertIn("PersianTranscriber Prompt Benchmark", html_text)

if __name__ == "__main__":
    unittest.main()
