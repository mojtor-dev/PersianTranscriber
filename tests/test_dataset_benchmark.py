import json
import tempfile
import unittest
from pathlib import Path

from scripts.benchmark_dataset_safe import (
    aggregate_results,
    load_dataset,
    result_path_for,
)


class TestDatasetBenchmark(unittest.TestCase):

    def test_load_dataset(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "dataset.json"

            path.write_text(
                json.dumps(
                    {
                        "samples": [
                            {
                                "id": "one",
                                "audio": "a.wav",
                                "reference": "a.txt",
                                "content_type": "general",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            data = load_dataset(path)

        self.assertEqual(
            data["samples"][0]["id"],
            "one",
        )

    def test_result_path(self):
        self.assertEqual(
            result_path_for(
                Path("/tmp/out"),
                "sample",
                "technical",
            ),
            Path(
                "/tmp/out/results/sample/technical.json"
            ),
        )

    def test_aggregate_ranking(self):
        rows = aggregate_results(
            [
                {
                    "profile": "none",
                    "wer": 0.4,
                    "cer": 0.2,
                    "quality_score": 0.33,
                    "duration_seconds": 10,
                    "error": None,
                },
                {
                    "profile": "technical",
                    "wer": 0.3,
                    "cer": 0.1,
                    "quality_score": 0.23,
                    "duration_seconds": 11,
                    "error": None,
                },
            ]
        )

        self.assertEqual(
            rows[0]["profile"],
            "technical",
        )


if __name__ == "__main__":
    unittest.main()
