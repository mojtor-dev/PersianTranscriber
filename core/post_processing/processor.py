from dataclasses import asdict, dataclass, field

from core.cleaner import TextCleaner
from core.dictionary_engine import DictionaryEngine
from core.persian_normalizer import PersianNormalizer
from core.post_processing.rule_engine import PostProcessingRuleEngine


@dataclass
class PostProcessingReport:
    cleaner_changed: bool = False
    normalizer_changed: bool = False
    dictionary_replacements: int = 0
    dictionary_rules: int = 0
    rule_replacements: int = 0
    rule_matches: int = 0
    dictionary_details: list = field(default_factory=list)
    rule_details: list = field(default_factory=list)

    @property
    def total_replacements(self):
        return self.dictionary_replacements + self.rule_replacements

    def to_dict(self):
        data = asdict(self)
        data["total_replacements"] = self.total_replacements
        return data


class PersianPostProcessor:
    def __init__(self, cleaner=None, normalizer=None, dictionary=None, rule_engine=None):
        self.cleaner = cleaner or TextCleaner()
        self.normalizer = normalizer or PersianNormalizer()
        self.dictionary = dictionary or DictionaryEngine()
        self.rule_engine = rule_engine or PostProcessingRuleEngine()

    def process(self, text):
        if not isinstance(text, str):
            raise TypeError("text must be a string")

        cleaned = self.cleaner.clean(text)
        normalized = self.normalizer.normalize(cleaned)
        corrected, dictionary_report = self.dictionary.correct_with_report(normalized)
        final_text, rule_report = self.rule_engine.apply(corrected)

        report = PostProcessingReport(
            cleaner_changed=cleaned != text,
            normalizer_changed=normalized != cleaned,
            dictionary_replacements=dictionary_report["replacement_count"],
            dictionary_rules=dictionary_report["matched_rules"],
            rule_replacements=rule_report["replacement_count"],
            rule_matches=rule_report["matched_rules"],
            dictionary_details=dictionary_report["details"],
            rule_details=rule_report["details"],
        )
        return final_text, report
