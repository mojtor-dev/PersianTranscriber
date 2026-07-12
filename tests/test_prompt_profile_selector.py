import unittest

from core.audio_analysis import AudioAnalysis
from core.prompt_profiles.selector import PromptProfileSelector


class TestPromptProfileSelector(unittest.TestCase):

    def create_analysis(
        self,
        duration=600,
        channels=1,
        filename_tokens=(),
    ):
        return AudioAnalysis(
            file_path="/tmp/audio.wav",
            duration_seconds=duration,
            channels=channels,
            sample_rate=16000,
            bit_rate=128000,
            format_name="wav",
            file_size_bytes=1000,
            filename_tokens=tuple(filename_tokens),
        )

    def test_explicit_content_hint_wins(self):
        selection = PromptProfileSelector().select(
            self.create_analysis(),
            content_hint="technical",
        )

        self.assertEqual(selection.profile_name, "technical")
        self.assertEqual(selection.confidence, 1.0)

    def test_filename_keyword_selects_profile(self):
        selection = PromptProfileSelector().select(
            self.create_analysis(
                filename_tokens=("python", "lesson")
            )
        )

        self.assertIn(
            selection.profile_name,
            {"technical", "lecture"},
        )

    def test_long_audio_selects_lecture(self):
        selection = PromptProfileSelector().select(
            self.create_analysis(duration=2400)
        )

        self.assertEqual(selection.profile_name, "lecture")

    def test_stereo_medium_audio_selects_meeting(self):
        selection = PromptProfileSelector().select(
            self.create_analysis(
                duration=900,
                channels=2,
            )
        )

        self.assertEqual(selection.profile_name, "meeting")

    def test_uncertain_case_falls_back_to_none(self):
        selection = PromptProfileSelector().select(
            self.create_analysis(
                duration=600,
                channels=1,
            )
        )

        self.assertEqual(selection.profile_name, "none")
        self.assertLess(selection.confidence, 0.5)


if __name__ == "__main__":
    unittest.main()
