import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestPackagingFiles(unittest.TestCase):

    def test_required_release_files_exist(self):
        required_paths = [
            "README.md",
            "CHANGELOG.md",
            "LICENSE",
            "requirements.txt",
            "requirements-dev.txt",
            "scripts/install_termux.sh",
            "scripts/release_check.sh",
            "docs/QUICKSTART.md",
            "docs/TROUBLESHOOTING.md",
        ]

        for relative_path in required_paths:
            with self.subTest(path=relative_path):
                self.assertTrue(
                    (
                        PROJECT_ROOT
                        / relative_path
                    ).is_file()
                )

    def test_readme_mentions_core_commands(self):
        text = (
            PROJECT_ROOT
            / "README.md"
        ).read_text(
            encoding="utf-8"
        )

        self.assertIn(
            "python app.py audio.mp3",
            text,
        )

        self.assertIn(
            "scripts/doctor.py",
            text,
        )

        self.assertIn(
            "scripts/release_check.sh",
            text,
        )


if __name__ == "__main__":
    unittest.main()
