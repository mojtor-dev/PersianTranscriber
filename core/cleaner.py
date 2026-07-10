"""
PersianTranscriber Text Cleaner
Version: 0.1.0
"""


class TextCleaner:

    def clean(self, text):

        if not text:
            return ""

        # حذف فاصله‌های اضافی
        text = " ".join(text.split())

        # اصلاح فاصله قبل از علائم
        replacements = {
            " .": ".",
            " ،": "،",
            " ؟": "؟",
            " !": "!"
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        return text.strip()
