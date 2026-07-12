import re
from typing import Sequence, TypeVar

T = TypeVar("T")


def normalize_evaluation_text(text: str) -> str:
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    for source, target in {"ي": "ی", "ى": "ی", "ك": "ک", "\u200c": " "}.items():
        text = text.replace(source, target)
    text = text.lower()
    text = re.sub(r"[،؛:؟!,.٪()\[\]{}«»\"']", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def levenshtein_distance(reference: Sequence[T], hypothesis: Sequence[T]) -> int:
    if len(reference) < len(hypothesis):
        reference, hypothesis = hypothesis, reference
    previous = list(range(len(hypothesis) + 1))
    for row, ref_item in enumerate(reference, start=1):
        current = [row]
        for col, hyp_item in enumerate(hypothesis, start=1):
            current.append(min(
                current[col - 1] + 1,
                previous[col] + 1,
                previous[col - 1] + (ref_item != hyp_item),
            ))
        previous = current
    return previous[-1]


def word_error_rate(reference: str, hypothesis: str) -> float:
    ref = normalize_evaluation_text(reference).split()
    hyp = normalize_evaluation_text(hypothesis).split()
    if not ref:
        return 0.0 if not hyp else 1.0
    return levenshtein_distance(ref, hyp) / len(ref)


def character_error_rate(reference: str, hypothesis: str) -> float:
    ref = list(normalize_evaluation_text(reference).replace(" ", ""))
    hyp = list(normalize_evaluation_text(hypothesis).replace(" ", ""))
    if not ref:
        return 0.0 if not hyp else 1.0
    return levenshtein_distance(ref, hyp) / len(ref)
