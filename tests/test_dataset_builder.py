import json
import tempfile
import unittest
from pathlib import Path

from core.dataset import DatasetBuilder


class TestDatasetBuilder(unittest.TestCase):

    def setUp(self):
        self.temporary_directory = (
            tempfile.TemporaryDirectory()
        )

        self.project_root = Path(
            self.temporary_directory.name
        )

        self.dataset_path = (
            self.project_root
            / "data"
            / "evaluation_dataset"
            / "dataset.json"
        )

        self.audio_path = (
            self.project_root
            / "sample.wav"
        )

        self.audio_path.write_bytes(
            b"audio"
        )

        self.builder = DatasetBuilder(
            project_root=self.project_root,
            dataset_path=self.dataset_path,
        )

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_normalize_sample_id(self):
        self.assertEqual(
            self.builder.normalize_sample_id(
                " Test Sample "
            ),
            "test-sample",
        )

    def test_add_sample(self):
        sample = self.builder.add_sample(
            sample_id="test-one",
            audio_path=self.audio_path,
            reference_text="سلام دنیا",
            content_type="general",
        )

        self.assertEqual(
            sample["id"],
            "test-one",
        )

        dataset = json.loads(
            self.dataset_path.read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(
            dataset["samples"][0]["id"],
            "test-one",
        )

        reference_path = (
            self.project_root
            / sample["reference"]
        )

        self.assertEqual(
            reference_path.read_text(
                encoding="utf-8"
            ).strip(),
            "سلام دنیا",
        )

    def test_rejects_duplicate_sample(self):
        self.builder.add_sample(
            sample_id="duplicate",
            audio_path=self.audio_path,
            reference_text="سلام",
            content_type="general",
        )

        with self.assertRaisesRegex(
            ValueError,
            "already exists",
        ):
            self.builder.add_sample(
                sample_id="duplicate",
                audio_path=self.audio_path,
                reference_text="سلام",
                content_type="general",
            )

    def test_copy_audio(self):
        external_directory = (
            self.project_root.parent
            / "external-audio"
        )

        external_directory.mkdir(
            exist_ok=True,
        )

        external_audio = (
            external_directory
            / "external.mp3"
        )

        external_audio.write_bytes(
            b"external"
        )

        sample = self.builder.add_sample(
            sample_id="copied",
            audio_path=external_audio,
            reference_text="متن",
            content_type="mobile",
            copy_audio=True,
        )

        copied_path = (
            self.project_root
            / sample["audio"]
        )

        self.assertTrue(
            copied_path.is_file()
        )

    def test_remove_sample(self):
        self.builder.add_sample(
            sample_id="remove-me",
            audio_path=self.audio_path,
            reference_text="متن",
            content_type="general",
        )

        self.builder.remove_sample(
            "remove-me",
            delete_reference=True,
        )

        self.assertEqual(
            self.builder.load()["samples"],
            [],
        )

    def test_validate_paths(self):
        sample = self.builder.add_sample(
            sample_id="valid",
            audio_path=self.audio_path,
            reference_text="متن",
            content_type="general",
        )

        self.assertEqual(
            self.builder.validate_paths(),
            [],
        )

        (
            self.project_root
            / sample["reference"]
        ).unlink()

        errors = self.builder.validate_paths()

        self.assertEqual(
            len(errors),
            1,
        )

        self.assertIn(
            "missing reference",
            errors[0],
        )


if __name__ == "__main__":
    unittest.main()
