import json
from pathlib import Path


class PromptProfileManager:
    DEFAULT_PROFILE_DIR = (
        Path(__file__).resolve().parents[2]
        / "data"
        / "prompt_profiles"
    )

    def __init__(self, profile_dir=None):
        self.profile_dir = (
            Path(profile_dir).expanduser().resolve()
            if profile_dir is not None
            else self.DEFAULT_PROFILE_DIR
        )
        self._profiles = None

    def load(self):
        profiles = {}

        if not self.profile_dir.exists():
            self._profiles = profiles
            return profiles

        for path in sorted(self.profile_dir.glob("*.json")):
            payload = json.loads(
                path.read_text(encoding="utf-8")
            )
            self._validate(payload, path)

            name = payload["name"]

            if name in profiles:
                raise ValueError(
                    f"Duplicate prompt profile: {name}"
                )

            profiles[name] = {
                **payload,
                "source_path": str(path),
            }

        self._profiles = profiles
        return profiles

    @property
    def profiles(self):
        if self._profiles is None:
            return self.load()

        return self._profiles

    def list_names(self):
        return sorted(self.profiles)

    def get(self, name):
        if name in {None, "", "none"}:
            return None

        if name not in self.profiles:
            available = ", ".join(self.list_names()) or "none"
            raise ValueError(
                f"Unknown prompt profile: {name}. "
                f"Available profiles: {available}"
            )

        return self.profiles[name]

    def resolve_prompt(self, name):
        profile = self.get(name)

        if profile is None:
            return None

        return profile["prompt"].strip()

    @staticmethod
    def _validate(payload, path):
        required = {
            "name",
            "description",
            "prompt",
            "content_types",
        }

        if not isinstance(payload, dict):
            raise ValueError(
                f"Profile must be an object: {path}"
            )

        missing = required - payload.keys()

        if missing:
            raise ValueError(
                f"Missing fields in {path}: "
                + ", ".join(sorted(missing))
            )

        for field in ("name", "description", "prompt"):
            if (
                not isinstance(payload[field], str)
                or not payload[field].strip()
            ):
                raise ValueError(
                    f"Invalid {field} in {path}"
                )

        if (
            not isinstance(payload["content_types"], list)
            or not all(
                isinstance(item, str) and item.strip()
                for item in payload["content_types"]
            )
        ):
            raise ValueError(
                f"Invalid content_types in {path}"
            )
