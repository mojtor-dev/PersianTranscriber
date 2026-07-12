#!/usr/bin/env python
import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from core.evaluation.metrics import character_error_rate, word_error_rate
from core.evaluation.report import write_html_report, write_json_report
from core.evaluation.benchmark import BenchmarkResult

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class SafeResult:
    name: str
    hypothesis: str
    duration_seconds: float
    wer: float
    cer: float
    quality_score: float
    prompt_enabled: bool
    output_path: str | None = None
    error: str | None = None
    completed_at: str | None = None

    def to_dict(self):
        return asdict(self)


def parser():
    p = argparse.ArgumentParser(description="Safe resumable prompt benchmark")
    p.add_argument("audio")
    p.add_argument("reference")
    p.add_argument("--prompt-dir", default="data/prompts")
    p.add_argument("--output-dir", default="output/benchmarks/test_fa_safe")
    p.add_argument("--threads", type=int, default=3)
    p.add_argument("--cooldown", type=int, default=10)
    p.add_argument("--model", default=None)
    p.add_argument("--force", action="store_true")
    p.add_argument("--only", action="append", default=[])
    return p


def safe_name(name):
    value = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in name)
    return value.strip("_") or "variant"


def variants(prompt_dir):
    items = [{"name": "baseline-no-prompt", "prompt_file": None}]
    if prompt_dir.exists():
        for path in sorted(prompt_dir.glob("*.txt")):
            items.append({"name": path.stem, "prompt_file": str(path.resolve())})
    return items


def save_result(result, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(result.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def load_result(path):
    return SafeResult(**json.loads(path.read_text(encoding="utf-8")))


def memory_line():
    info = {}
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                parts = value.strip().split()
                if parts and parts[0].isdigit():
                    info[key] = int(parts[0])
    except OSError:
        return "memory=unknown"
    avail = info.get("MemAvailable")
    swap = info.get("SwapFree")
    return f"available={avail/1024:.0f}MiB swap_free={swap/1024:.0f}MiB" if avail and swap else "memory=unknown"


def run_one(variant, audio, reference, output_dir, threads, model):
    run_dir = output_dir / "runs" / safe_name(variant["name"])
    run_dir.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, str(PROJECT_ROOT / "app.py"), str(audio), "--txt-only", "--threads", str(threads), "--output-dir", str(run_dir)]
    if model:
        cmd += ["--model", model]
    if variant["prompt_file"]:
        cmd += ["--prompt-file", variant["prompt_file"]]

    started = time.perf_counter()
    proc = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True, check=False, env={**os.environ, "PYTHONUNBUFFERED": "1"})
    elapsed = time.perf_counter() - started

    if proc.returncode != 0:
        error = proc.stderr.strip() or proc.stdout.strip() or "transcription failed"
        return SafeResult(variant["name"], "", elapsed, 1.0, 1.0, 1.0, bool(variant["prompt_file"]), error=error, completed_at=datetime.now(timezone.utc).isoformat())

    transcript = run_dir / "transcription.txt"
    if not transcript.is_file():
        return SafeResult(variant["name"], "", elapsed, 1.0, 1.0, 1.0, bool(variant["prompt_file"]), error="output missing", completed_at=datetime.now(timezone.utc).isoformat())

    text = transcript.read_text(encoding="utf-8").strip()
    wer = word_error_rate(reference, text)
    cer = character_error_rate(reference, text)
    score = wer * 0.65 + cer * 0.35
    return SafeResult(variant["name"], text, elapsed, wer, cer, score, bool(variant["prompt_file"]), str(transcript), completed_at=datetime.now(timezone.utc).isoformat())


def report(output_dir, results, metadata):
    ranked = sorted(results, key=lambda r: (r.error is not None, r.quality_score, r.duration_seconds, r.name))
    converted = [BenchmarkResult(name=r.name, hypothesis=r.hypothesis, duration_seconds=r.duration_seconds, wer=r.wer, cer=r.cer, prompt_enabled=r.prompt_enabled, output_path=r.output_path, error=r.error) for r in ranked]
    write_json_report(converted, output_dir / "report.json", metadata=metadata)
    write_html_report(converted, output_dir / "report.html", metadata=metadata)
    print("\n===== Ranking =====")
    for i, r in enumerate(ranked, 1):
        status = f"ERROR: {r.error}" if r.error else "OK"
        print(f"{i}. {r.name} | WER={r.wer:.4f} | CER={r.cer:.4f} | Score={r.quality_score:.4f} | Time={r.duration_seconds:.2f}s | {status}")


def main(argv=None):
    args = parser().parse_args(argv)
    if args.threads <= 0 or args.cooldown < 0:
        raise SystemExit("invalid threads/cooldown")

    audio = Path(args.audio).expanduser().resolve()
    reference_path = Path(args.reference).expanduser().resolve()
    prompt_dir = Path(args.prompt_dir).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()

    if not audio.is_file():
        raise SystemExit(f"Audio file not found: {audio}")
    if not reference_path.is_file():
        raise SystemExit(f"Reference file not found: {reference_path}")

    reference = reference_path.read_text(encoding="utf-8").strip()
    if not reference:
        raise SystemExit("Reference transcript is empty")

    all_variants = variants(prompt_dir)
    if args.only:
        selected = set(args.only)
        all_variants = [v for v in all_variants if v["name"] in selected]
        missing = selected - {v["name"] for v in all_variants}
        if missing:
            raise SystemExit("Unknown variants: " + ", ".join(sorted(missing)))

    output_dir.mkdir(parents=True, exist_ok=True)
    results_dir = output_dir / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    metadata = {"audio": str(audio), "reference": str(reference_path), "threads": args.threads, "model": args.model or "default", "mode": "safe-resumable"}
    results = []

    for index, variant in enumerate(all_variants, 1):
        result_path = results_dir / f"{safe_name(variant['name'])}.json"
        if result_path.exists() and not args.force:
            print(f"\n[{index}/{len(all_variants)}] resume: {variant['name']}")
            result = load_result(result_path)
        else:
            print(f"\n[{index}/{len(all_variants)}] run: {variant['name']}")
            print("Before:", memory_line())
            result = run_one(variant, audio, reference, output_dir, args.threads, args.model)
            save_result(result, result_path)
            print("After:", memory_line())
        results.append(result)
        report(output_dir, results, metadata)
        if index < len(all_variants) and args.cooldown:
            print(f"Cooldown: {args.cooldown}s")
            time.sleep(args.cooldown)

    print("\nBenchmark complete")
    print("JSON:", output_dir / "report.json")
    print("HTML:", output_dir / "report.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
