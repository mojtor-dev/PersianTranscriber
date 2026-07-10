"""
PersianTranscriber Text Cleaner
Version: 0.2.0
"""

import re


class TextCleaner:

    def clean(self, text):

        if not text:
            return ""

        # حذف timestamp های Whisper
        text = re.sub(
            r"\[\d{2}:\d{2}:\d{2}\.\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}\.\d{3}\]",
            "",
            text
        )

        # حذف خطوط خالی اضافی
        lines = []

        for line in text.splitlines():

            line = line.strip()

            if line:
                lines.append(line)

        text = " ".join(lines)

        # فاصله‌های اضافی
        text = " ".join(text.split())

        # اصلاح فاصله قبل علائم
        replacements = {
            " .": ".",
            " ،": "،",
            " ؟": "؟",
            " !": "!"
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        return text.strip()
