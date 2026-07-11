"""
PersianTranscriber Text Merger
Version: 0.1.0
"""


class TextMerger:

    def merge(self, texts):

        if not texts:
            return ""

        output = []

        for text in texts:

            text = text.strip()

            if text:

                output.append(text)

        return "\n\n".join(output)
