import re


class PersianNormalizer:
    """
    نرمال‌سازی پایه و کم‌خطر متن فارسی.

    این کلاس قواعد عمومی و قطعی نرمال‌سازی فارسی را اعمال می‌کند
    و پیش از DictionaryEngine در Pipeline اجرا می‌شود.
    """

    ZWNJ = "\u200c"

    CHARACTER_REPLACEMENTS = {
        "ي": "ی",
        "ى": "ی",
        "ك": "ک",
        "ة": "ه",
        "ۀ": "هٔ",
    }

    DIGIT_REPLACEMENTS = {
        "٠": "۰",
        "١": "۱",
        "٢": "۲",
        "٣": "۳",
        "٤": "۴",
        "٥": "۵",
        "٦": "۶",
        "٧": "۷",
        "٨": "۸",
        "٩": "۹",
    }

    PREFIXES = (
        "می",
        "نمی",
    )

    SUFFIXES = (
        "ها",
        "های",
        "هایی",
        "تر",
        "ترین",
    )

    PRONOUN_SUFFIXES_AFTER_HEH = (
        "ام",
        "ات",
        "اش",
        "مان",
        "تان",
        "شان",
    )

    def normalize(self, text: str) -> str:
        """
        متن فارسی را با قواعد پایه نرمال می‌کند.
        """
        if not isinstance(text, str):
            raise TypeError("text must be a string")

        if not text:
            return ""

        text = self._normalize_characters(text)
        text = self._normalize_digits(text)
        text = self._remove_tatweel(text)
        text = self._normalize_whitespace(text)
        text = self._normalize_punctuation_spacing(text)
        text = self._normalize_prefixes(text)
        text = self._normalize_suffixes(text)
        text = self._normalize_pronoun_suffixes_after_heh(text)
        text = self._normalize_whitespace(text)

        return text.strip()

    def _normalize_characters(self, text: str) -> str:
        for source, target in self.CHARACTER_REPLACEMENTS.items():
            text = text.replace(source, target)

        return text

    def _normalize_digits(self, text: str) -> str:
        for source, target in self.DIGIT_REPLACEMENTS.items():
            text = text.replace(source, target)

        return text

    @staticmethod
    def _remove_tatweel(text: str) -> str:
        return text.replace("ـ", "")

    @staticmethod
    def _normalize_whitespace(text: str) -> str:
        text = text.replace("\t", " ")
        text = re.sub(r"[ ]{2,}", " ", text)
        text = re.sub(r" *\n *", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text

    @staticmethod
    def _normalize_punctuation_spacing(text: str) -> str:
        punctuation = "،؛:؟!,.٪"

        text = re.sub(
            rf"\s+([{re.escape(punctuation)}])",
            r"\1",
            text,
        )

        text = re.sub(
            rf"([{re.escape(punctuation)}])"
            rf"(?=[^\s\n{re.escape(punctuation)}])",
            r"\1 ",
            text,
        )

        return text

    def _normalize_prefixes(self, text: str) -> str:
        prefixes_pattern = "|".join(
            re.escape(prefix)
            for prefix in self.PREFIXES
        )

        return re.sub(
            rf"(?<!\S)({prefixes_pattern})\s+([آ-ی]+)",
            rf"\1{self.ZWNJ}\2",
            text,
        )

    def _normalize_suffixes(self, text: str) -> str:
        suffixes_pattern = "|".join(
            re.escape(suffix)
            for suffix in self.SUFFIXES
        )

        return re.sub(
            rf"([آ-ی]+)\s+({suffixes_pattern})(?!\S)",
            rf"\1{self.ZWNJ}\2",
            text,
        )

    def _normalize_pronoun_suffixes_after_heh(
        self,
        text: str,
    ) -> str:
        pronoun_suffixes_pattern = "|".join(
            re.escape(suffix)
            for suffix in self.PRONOUN_SUFFIXES_AFTER_HEH
        )

        return re.sub(
            rf"([آ-ی]*ه)\s+({pronoun_suffixes_pattern})(?!\S)",
            rf"\1{self.ZWNJ}\2",
            text,
        )
