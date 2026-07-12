from dataclasses import asdict, dataclass
from time import perf_counter
from typing import Callable, Iterable, Optional

from core.evaluation.metrics import character_error_rate, word_error_rate


@dataclass(frozen=True)
class PromptVariant:
    name: str
    prompt: Optional[str] = None
    prompt_file: Optional[str] = None

    def __post_init__(self):
        if self.prompt is not None and self.prompt_file is not None:
            raise ValueError("cannot define both prompt and prompt_file")
        if not self.name.strip():
            raise ValueError("name cannot be empty")


@dataclass
class BenchmarkResult:
    name: str
    hypothesis: str
    duration_seconds: float
    wer: float
    cer: float
    prompt_enabled: bool
    output_path: Optional[str] = None
    error: Optional[str] = None

    @property
    def quality_score(self) -> float:
        return (self.wer * 0.65) + (self.cer * 0.35)

    def to_dict(self) -> dict:
        data = asdict(self)
        data["quality_score"] = self.quality_score
        return data


class PromptBenchmark:
    def __init__(self, reference_text: str, runner: Callable[[PromptVariant], object]):
        if not isinstance(reference_text, str) or not reference_text.strip():
            raise ValueError("reference_text cannot be empty")
        if not callable(runner):
            raise TypeError("runner must be callable")
        self.reference_text = reference_text
        self.runner = runner

    def run(self, variants: Iterable[PromptVariant]) -> list[BenchmarkResult]:
        results = []
        for variant in variants:
            started = perf_counter()
            try:
                runner_result = self.runner(variant)
                if isinstance(runner_result, tuple):
                    hypothesis, output_path = runner_result
                else:
                    hypothesis, output_path = runner_result, None
                if not isinstance(hypothesis, str):
                    raise TypeError("runner must return text")
                result = BenchmarkResult(
                    name=variant.name,
                    hypothesis=hypothesis,
                    duration_seconds=perf_counter() - started,
                    wer=word_error_rate(self.reference_text, hypothesis),
                    cer=character_error_rate(self.reference_text, hypothesis),
                    prompt_enabled=bool(variant.prompt or variant.prompt_file),
                    output_path=str(output_path) if output_path else None,
                )
            except Exception as error:
                result = BenchmarkResult(
                    name=variant.name,
                    hypothesis="",
                    duration_seconds=perf_counter() - started,
                    wer=1.0,
                    cer=1.0,
                    prompt_enabled=bool(variant.prompt or variant.prompt_file),
                    error=str(error),
                )
            results.append(result)
        return sorted(results, key=lambda item: (item.error is not None, item.quality_score, item.duration_seconds, item.name))
