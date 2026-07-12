#!/usr/bin/env python

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def build_parser():
    parser = argparse.ArgumentParser(
        description="Run a production CLI smoke test"
    )

    parser.add_argument(
        "audio",
        nargs="?",
        default="test_fa.mp3",
    )

    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)

    audio_path = Path(
        args.audio
    ).expanduser().resolve()

    if not audio_path.is_file():
        print(
            f"SKIP: audio file not found: {audio_path}"
        )
        return 0

    with tempfile.TemporaryDirectory() as directory:
        output_dir = Path(directory)

        command = [
            sys.executable,
            str(PROJECT_ROOT / "app.py"),
            str(audio_path),
            "--txt-only",
            "--threads",
            "3",
            "--output-dir",
            str(output_dir),
        ]

        completed = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        if completed.returncode != 0:
            print(
                completed.stdout
            )
            print(
                completed.stderr,
                file=sys.stderr,
            )
            return completed.returncode

        transcript = (
            output_dir
            / "transcription.txt"
        )

        if not transcript.is_file():
            print(
                "ERROR: transcription.txt was not created",
                file=sys.stderr,
            )
            return 1

        if not transcript.read_text(
            encoding="utf-8"
        ).strip():
            print(
                "ERROR: transcription output is empty",
                file=sys.stderr,
            )
            return 1

        print(
            "Smoke test: OK"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
