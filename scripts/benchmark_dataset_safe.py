#!/usr/bin/env python

import argparse
import json
import subprocess
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from core.evaluation.metrics import (
    character_error_rate,
    word_error_rate,
)
from core.prompt_profiles import PromptProfileManager


ROOT = Path(__file__).resolve().parent.parent


def load_dataset(path):
    payload = json.loads(
        Path(path).read_text(encoding="utf-8")
    )

    samples = payload.get("samples")

    if not isinstance(samples, list):
        raise ValueError(
            "Dataset must contain a samples list"
        )

    required = {
        "id",
        "audio",
        "reference",
        "content_type",
    }

    for sample in samples:
        missing = required - sample.keys()

        if missing:
            raise ValueError(
                f"Missing sample fields: {sorted(missing)}"
            )

    return payload


def result_path_for(output_dir, sample_id, profile):
    return (
        Path(output_dir)
        / "results"
        / sample_id
        / f"{profile}.json"
    )


def atomic_write_json(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    temporary = path.with_suffix(
        path.suffix + ".tmp"
    )

    temporary.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    temporary.replace(path)


def aggregate_results(results):
    groups = defaultdict(list)

    for result in results:
        groups[result["profile"]].append(result)

    summary = []

    for profile, rows in groups.items():
        successful = [
            row
            for row in rows
            if row.get("error") is None
        ]

        if not successful:
            summary.append(
                {
                    "profile": profile,
                    "sample_count": len(rows),
                    "successful_count": 0,
                    "mean_wer": 1.0,
                    "mean_cer": 1.0,
                    "mean_quality_score": 1.0,
                    "mean_duration_seconds": 0.0,
                }
            )
            continue

        count = len(successful)

        summary.append(
            {
                "profile": profile,
                "sample_count": len(rows),
                "successful_count": count,
                "mean_wer": sum(
                    row["wer"]
                    for row in successful
                ) / count,
                "mean_cer": sum(
                    row["cer"]
                    for row in successful
                ) / count,
                "mean_quality_score": sum(
                    row["quality_score"]
                    for row in successful
                ) / count,
                "mean_duration_seconds": sum(
                    row["duration_seconds"]
                    for row in successful
                ) / count,
            }
        )

    return sorted(
        summary,
        key=lambda row: (
            row["mean_quality_score"],
            row["mean_duration_seconds"],
            row["profile"],
        ),
    )


def run_one(sample, profile, prompt, output_dir, threads):
    audio = (ROOT / sample["audio"]).resolve()
    reference_path = (
        ROOT / sample["reference"]
    ).resolve()

    if not audio.is_file():
        raise FileNotFoundError(
            f"Audio not found: {audio}"
        )

    if not reference_path.is_file():
        raise FileNotFoundError(
            f"Reference not found: {reference_path}"
        )

    reference = reference_path.read_text(
        encoding="utf-8"
    ).strip()

    run_dir = (
        Path(output_dir)
        / "runs"
        / sample["id"]
        / profile
    )

    command = [
        sys.executable,
        str(ROOT / "app.py"),
        str(audio),
        "--txt-only",
        "--threads",
        str(threads),
        "--output-dir",
        str(run_dir),
    ]

    if prompt is not None:
        command.extend(["--prompt", prompt])

    started = time.perf_counter()

    completed = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    duration = time.perf_counter() - started

    base = {
        "sample_id": sample["id"],
        "profile": profile,
        "content_type": sample["content_type"],
        "duration_seconds": duration,
        "completed_at": datetime.now(
            timezone.utc
        ).isoformat(),
    }

    if completed.returncode != 0:
        return {
            **base,
            "wer": 1.0,
            "cer": 1.0,
            "quality_score": 1.0,
            "error": (
                completed.stderr.strip()
                or completed.stdout.strip()
                or "transcription failed"
            ),
        }

    transcript_path = run_dir / "transcription.txt"
    hypothesis = transcript_path.read_text(
        encoding="utf-8"
    ).strip()

    wer = word_error_rate(reference, hypothesis)
    cer = character_error_rate(reference, hypothesis)

    return {
        **base,
        "wer": wer,
        "cer": cer,
        "quality_score": wer * 0.65 + cer * 0.35,
        "error": None,
        "hypothesis": hypothesis,
        "output_path": str(transcript_path),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset")
    parser.add_argument(
        "--output-dir",
        default="output/benchmarks/dataset_safe",
    )
    parser.add_argument("--threads", type=int, default=3)
    parser.add_argument("--cooldown", type=int, default=10)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if args.threads <= 0:
        raise SystemExit(
            "--threads must be greater than zero"
        )

    dataset = load_dataset(args.dataset)
    output_dir = Path(args.output_dir)
    manager = PromptProfileManager()
    profiles = ["none", *manager.list_names()]
    all_results = []

    for sample in dataset["samples"]:
        for profile in profiles:
            result_path = result_path_for(
                output_dir,
                sample["id"],
                profile,
            )

            if result_path.exists() and not args.force:
                print(
                    f"[resume] {sample['id']} / {profile}"
                )
                all_results.append(
                    json.loads(
                        result_path.read_text(
                            encoding="utf-8"
                        )
                    )
                )
                continue

            print(
                f"[run] {sample['id']} / {profile}"
            )

            prompt = (
                None
                if profile == "none"
                else manager.resolve_prompt(profile)
            )

            result = run_one(
                sample,
                profile,
                prompt,
                output_dir,
                args.threads,
            )

            atomic_write_json(result_path, result)
            all_results.append(result)

            atomic_write_json(
                output_dir / "summary.json",
                {
                    "generated_at": datetime.now(
                        timezone.utc
                    ).isoformat(),
                    "dataset": str(
                        Path(args.dataset).resolve()
                    ),
                    "results": all_results,
                    "aggregate": aggregate_results(
                        all_results
                    ),
                },
            )

            if args.cooldown:
                time.sleep(args.cooldown)

    ranking = aggregate_results(all_results)

    print()
    print("===== Dataset Profile Ranking =====")

    for index, row in enumerate(ranking, start=1):
        print(
            f"{index}. {row['profile']} | "
            f"WER={row['mean_wer']:.4f} | "
            f"CER={row['mean_cer']:.4f} | "
            f"Score={row['mean_quality_score']:.4f} | "
            f"Time={row['mean_duration_seconds']:.1f}s | "
            f"Samples={row['successful_count']}"
        )

    print(
        f"Summary: {output_dir / 'summary.json'}"
    )


if __name__ == "__main__":
    main()
