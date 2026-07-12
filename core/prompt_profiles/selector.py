# Conservative automatic prompt-profile selection.

from dataclasses import asdict, dataclass

from core.audio_analysis import AudioAnalysis


@dataclass(frozen=True)
class PromptSelection:
    profile_name: str
    confidence: float
    reason: str
    automatic: bool = True

    def to_dict(self):
        return asdict(self)


class PromptProfileSelector:

    PROFILE_KEYWORDS = {
        "technical": {
            "tech",
            "technical",
            "software",
            "python",
            "termux",
            "whisper",
            "gpt",
            "ai",
            "فنی",
        },
        "meeting": {
            "meeting",
            "جلسه",
            "minutes",
            "team",
            "standup",
            "sync",
        },
        "lecture": {
            "lecture",
            "class",
            "course",
            "lesson",
            "سخنرانی",
            "کلاس",
            "درس",
            "آموزش",
        },
        "general": {
            "general",
            "conversation",
            "chat",
            "voice",
            "گفتگو",
            "مکالمه",
        },
    }

    VALID_CONTENT_HINTS = {
        "general",
        "technical",
        "meeting",
        "lecture",
    }

    def select(self, analysis, content_hint=None):
        if not isinstance(analysis, AudioAnalysis):
            raise TypeError(
                "analysis must be an AudioAnalysis"
            )

        if content_hint is not None:
            normalized_hint = str(content_hint).strip().lower()

            if normalized_hint not in self.VALID_CONTENT_HINTS:
                available = ", ".join(
                    sorted(self.VALID_CONTENT_HINTS)
                )
                raise ValueError(
                    f"Invalid content hint: {content_hint}. "
                    f"Available: {available}"
                )

            return PromptSelection(
                profile_name=normalized_hint,
                confidence=1.0,
                reason="explicit content hint",
            )

        keyword_selection = self._select_by_filename(
            analysis.filename_tokens
        )

        if keyword_selection is not None:
            return keyword_selection

        duration = analysis.duration_seconds
        channels = analysis.channels

        if duration >= 1800:
            return PromptSelection(
                profile_name="lecture",
                confidence=0.62,
                reason=(
                    "long continuous audio "
                    "(duration >= 30 minutes)"
                ),
            )

        if channels >= 2 and 300 <= duration <= 7200:
            return PromptSelection(
                profile_name="meeting",
                confidence=0.58,
                reason="multi-channel medium/long audio",
            )

        if 0 < duration <= 180:
            return PromptSelection(
                profile_name="general",
                confidence=0.52,
                reason="short audio with no strong content signal",
            )

        return PromptSelection(
            profile_name="none",
            confidence=0.35,
            reason=(
                "insufficient evidence; "
                "conservative no-prompt fallback"
            ),
        )

    def _select_by_filename(self, filename_tokens):
        token_set = set(filename_tokens)
        matches = []

        for profile_name, keywords in self.PROFILE_KEYWORDS.items():
            overlap = token_set & keywords

            if overlap:
                matches.append(
                    (
                        len(overlap),
                        profile_name,
                        sorted(overlap),
                    )
                )

        if not matches:
            return None

        matches.sort(
            key=lambda item: (
                -item[0],
                item[1],
            )
        )

        match_count, profile_name, matched = matches[0]
        confidence = min(
            0.95,
            0.72 + (0.08 * (match_count - 1)),
        )

        return PromptSelection(
            profile_name=profile_name,
            confidence=confidence,
            reason=(
                "filename keywords: "
                + ", ".join(matched)
            ),
        )
