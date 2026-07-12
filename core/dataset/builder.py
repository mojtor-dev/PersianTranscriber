"""
Evaluation dataset builder.
"""

import json
import re
import shutil
from pathlib import Path


class DatasetBuilder:

    VALID_CONTENT_TYPES = {
        "general",
        "technical",
        "meeting",
        "lecture",
        "noisy",
        "mobile",
        "other",
    }

    def __init__(
        self,
        project_root=None,
        dataset_path=None,
    ):
        self.project_root = (
            Path(project_root).expanduser().resolve()
            if project_root is not None
            else Path(__file__).resolve().parents[2]
        )

        self.dataset_path = (
            Path(dataset_path).expanduser().resolve()
            if dataset_path is not None
            else (
                self.project_root
                / "data"
                / "evaluation_dataset"
                / "dataset.json"
            )
        )

    def load(self):
        if not self.dataset_path.exists():
            return {
                "name": "persiantranscriber-evaluation",
                "version": 1,
                "samples": [],
            }

        payload = json.loads(
            self.dataset_path.read_text(
                encoding="utf-8"
            )
        )

        self._validate_dataset(payload)

        return payload

    def save(self, payload):
        self._validate_dataset(payload)

        self.dataset_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temporary_path = self.dataset_path.with_suffix(
            self.dataset_path.suffix + ".tmp"
        )

        temporary_path.write_text(
            json.dumps(
                payload,
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        temporary_path.replace(
            self.dataset_path
        )

    def add_sample(
        self,
        sample_id,
        audio_path,
        reference_text,
        content_type,
        copy_audio=False,
        overwrite=False,
    ):
        normalized_id = self.normalize_sample_id(
            sample_id
        )

        if content_type not in self.VALID_CONTENT_TYPES:
            available = ", ".join(
                sorted(self.VALID_CONTENT_TYPES)
            )

            raise ValueError(
                f"Invalid content type: {content_type}. "
                f"Available: {available}"
            )

        source_audio_path = Path(
            audio_path
        ).expanduser().resolve()

        if not source_audio_path.is_file():
            raise FileNotFoundError(
                f"Audio file not found: {source_audio_path}"
            )

        if not isinstance(reference_text, str):
            raise TypeError(
                "reference_text must be a string"
            )

        reference_text = reference_text.strip()

        if not reference_text:
            raise ValueError(
                "reference_text cannot be empty"
            )

        dataset = self.load()
        samples = dataset["samples"]

        existing_sample = next(
            (
                sample
                for sample in samples
                if sample["id"] == normalized_id
            ),
            None,
        )

        if existing_sample is not None and not overwrite:
            raise ValueError(
                f"Dataset sample already exists: {normalized_id}"
            )

        if copy_audio:
            audio_relative_path = (
                Path("data")
                / "evaluation_dataset"
                / "audio"
                / (
                    normalized_id
                    + source_audio_path.suffix.lower()
                )
            )

            target_audio_path = (
                self.project_root
                / audio_relative_path
            )

            target_audio_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            shutil.copy2(
                source_audio_path,
                target_audio_path,
            )

        else:
            try:
                audio_relative_path = source_audio_path.relative_to(
                    self.project_root
                )
            except ValueError as error:
                raise ValueError(
                    "Audio file must be inside the project "
                    "unless copy_audio=True"
                ) from error

        reference_relative_path = (
            Path("data")
            / "references"
            / f"{normalized_id}_reference.txt"
        )

        reference_path = (
            self.project_root
            / reference_relative_path
        )

        reference_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        reference_path.write_text(
            reference_text + "\n",
            encoding="utf-8",
        )

        sample = {
            "id": normalized_id,
            "audio": audio_relative_path.as_posix(),
            "reference": reference_relative_path.as_posix(),
            "content_type": content_type,
        }

        if existing_sample is not None:
            samples[
                samples.index(existing_sample)
            ] = sample
        else:
            samples.append(sample)

        samples.sort(
            key=lambda item: item["id"]
        )

        self.save(dataset)

        return sample

    def remove_sample(
        self,
        sample_id,
        delete_reference=False,
        delete_copied_audio=False,
    ):
        normalized_id = self.normalize_sample_id(
            sample_id
        )

        dataset = self.load()

        sample = next(
            (
                item
                for item in dataset["samples"]
                if item["id"] == normalized_id
            ),
            None,
        )

        if sample is None:
            raise ValueError(
                f"Dataset sample not found: {normalized_id}"
            )

        dataset["samples"].remove(
            sample
        )

        self.save(dataset)

        if delete_reference:
            reference_path = (
                self.project_root
                / sample["reference"]
            )

            if reference_path.is_file():
                reference_path.unlink()

        if delete_copied_audio:
            audio_path = (
                self.project_root
                / sample["audio"]
            )

            copied_audio_dir = (
                self.project_root
                / "data"
                / "evaluation_dataset"
                / "audio"
            )

            try:
                audio_path.resolve().relative_to(
                    copied_audio_dir.resolve()
                )
            except ValueError:
                pass
            else:
                if audio_path.is_file():
                    audio_path.unlink()

        return sample

    def validate_paths(self):
        dataset = self.load()
        errors = []

        for sample in dataset["samples"]:
            audio_path = (
                self.project_root
                / sample["audio"]
            )

            reference_path = (
                self.project_root
                / sample["reference"]
            )

            if not audio_path.is_file():
                errors.append(
                    f"{sample['id']}: missing audio {sample['audio']}"
                )

            if not reference_path.is_file():
                errors.append(
                    f"{sample['id']}: missing reference "
                    f"{sample['reference']}"
                )

            elif not reference_path.read_text(
                encoding="utf-8"
            ).strip():
                errors.append(
                    f"{sample['id']}: empty reference "
                    f"{sample['reference']}"
                )

        return errors

    @staticmethod
    def normalize_sample_id(sample_id):
        if not isinstance(sample_id, str):
            raise TypeError(
                "sample_id must be a string"
            )

        normalized = sample_id.strip().lower()
        normalized = re.sub(
            r"[^a-z0-9_-]+",
            "-",
            normalized,
        )

        normalized = re.sub(
            r"-{2,}",
            "-",
            normalized,
        ).strip("-_")

        if not normalized:
            raise ValueError(
                "sample_id cannot be empty"
            )

        return normalized

    @staticmethod
    def _validate_dataset(payload):
        if not isinstance(payload, dict):
            raise ValueError(
                "Dataset must be a JSON object"
            )

        samples = payload.get("samples")

        if not isinstance(samples, list):
            raise ValueError(
                "Dataset must contain a samples list"
            )

        seen_ids = set()

        for sample in samples:
            if not isinstance(sample, dict):
                raise ValueError(
                    "Each dataset sample must be an object"
                )

            required = {
                "id",
                "audio",
                "reference",
                "content_type",
            }

            missing = required - sample.keys()

            if missing:
                raise ValueError(
                    "Dataset sample missing fields: "
                    + ", ".join(
                        sorted(missing)
                    )
                )

            if sample["id"] in seen_ids:
                raise ValueError(
                    f"Duplicate dataset sample id: {sample['id']}"
                )

            seen_ids.add(
                sample["id"]
            )
