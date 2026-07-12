#!/usr/bin/env python
import argparse
import subprocess
import sys
from pathlib import Path

from core.evaluation import PromptBenchmark, PromptVariant, write_html_report, write_json_report

ROOT = Path(__file__).resolve().parent.parent


def main(argv=None):
    parser = argparse.ArgumentParser(description="Benchmark prompts with WER and CER")
    parser.add_argument("audio")
    parser.add_argument("reference")
    parser.add_argument("--prompt-dir", default="data/prompts")
    parser.add_argument("--output-dir", default="output/benchmarks/latest")
    parser.add_argument("--model", default=None)
    parser.add_argument("--threads", type=int, default=None)
    args = parser.parse_args(argv)

    audio = Path(args.audio).expanduser().resolve()
    reference = Path(args.reference).expanduser().resolve()
    prompt_dir = Path(args.prompt_dir).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()

    if not audio.is_file():
        raise SystemExit(f"Audio file not found: {audio}")
    if not reference.is_file():
        raise SystemExit(f"Reference file not found: {reference}")

    variants = [PromptVariant(name="baseline-no-prompt")]
    if prompt_dir.exists():
        variants.extend(
            PromptVariant(name=path.stem, prompt_file=str(path))
            for path in sorted(prompt_dir.glob("*.txt"))
        )

    output_dir.mkdir(parents=True, exist_ok=True)

    def runner(variant):
        run_dir = output_dir / "runs" / variant.name
        command = [sys.executable, str(ROOT / "app.py"), str(audio), "--txt-only", "--output-dir", str(run_dir)]
        if args.model:
            command.extend(["--model", args.model])
        if args.threads:
            command.extend(["--threads", str(args.threads)])
        if variant.prompt_file:
            command.extend(["--prompt-file", variant.prompt_file])
        completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
        if completed.returncode != 0:
            raise RuntimeError(completed.stderr.strip() or completed.stdout.strip() or "transcription failed")
        transcript = run_dir / "transcription.txt"
        return transcript.read_text(encoding="utf-8"), transcript

    benchmark = PromptBenchmark(reference.read_text(encoding="utf-8"), runner)
    results = benchmark.run(variants)
    metadata = {"audio": str(audio), "reference": str(reference), "model": args.model or "config default", "threads": args.threads or "auto"}
    json_path = write_json_report(results, output_dir / "report.json", metadata)
    html_path = write_html_report(results, output_dir / "report.html", metadata)

    print("\n===== Ranking =====")
    for rank, item in enumerate(results, start=1):
        print(f"{rank}. {item.name} | WER={item.wer:.4f} | CER={item.cer:.4f} | Score={item.quality_score:.4f} | Time={item.duration_seconds:.2f}s")
        if item.error:
            print(f"   ERROR: {item.error}")
    print(f"\nJSON report: {json_path}")
    print(f"HTML report: {html_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
