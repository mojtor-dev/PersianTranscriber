import json
import tempfile
import unittest
from pathlib import Path

from core.prompt_profiles import PromptProfileManager


class TestPromptProfiles(unittest.TestCase):

    def test_loads_default_profiles(self):
        names = PromptProfileManager().list_names()

        self.assertIn("technical", names)
        self.assertIn("general", names)

    def test_none_profile(self):
        self.assertIsNone(
            PromptProfileManager().resolve_prompt(
                "none"
            )
        )

    def test_technical_profile(self):
        prompt = (
            PromptProfileManager()
            .resolve_prompt("technical")
        )

        self.assertIn("جی‌پی‌تی", prompt)

    def test_unknown_profile(self):
        with self.assertRaisesRegex(
            ValueError,
            "Unknown prompt profile",
        ):
            PromptProfileManager().resolve_prompt(
                "missing"
            )

    def test_invalid_profile(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"

            path.write_text(
                json.dumps({"name": "bad"}),
                encoding="utf-8",
            )

            with self.assertRaises(ValueError):
                PromptProfileManager(
                    profile_dir=directory
                ).load()


if __name__ == "__main__":
    unittest.main()
