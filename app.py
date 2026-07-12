"""
PersianTranscriber Command Line Interface
Version: 0.2.0
"""

import argparse
import sys
from pathlib import Path

import config
from core.pipeline import TranscriptionPipeline


def positive_integer(value):
    try:
        number = int(value)
    except (TypeError, ValueError) as error:
        raise argparse.ArgumentTypeError(
            "must be an integer"
        ) from error

    if number <= 0:
        raise argparse.ArgumentTypeError(
            "must be greater than zero"
        )

    return number


def build_parser():
    parser = argparse.ArgumentParser(
        prog="persiantranscriber",
        description=(
            "Professional Persian speech-to-text "
            "using Whisper.cpp"
        ),
    )

    parser.add_argument(
        "audio",
        nargs="?",
        help="path to MP3, WAV or M4A audio file",
    )

    parser.add_argument(
        "--engine",
        choices=[
            "whisper_cpp",
            "whisper",
        ],
        default=None,
        help="transcription engine",
    )

    parser.add_argument(
        "--model",
        default=None,
        help="Whisper model name, such as small or medium",
    )

    parser.add_argument(
        "--language",
        default=None,
        help="language code; default comes from config.ini",
    )

    parser.add_argument(
        "--threads",
        type=positive_integer,
        default=None,
        help="number of CPU threads",
    )

    parser.add_argument(
        "--timeout",
        type=positive_integer,
        default=None,
        help="maximum transcription time in seconds",
    )

    parser.add_argument(
        "--chunk-duration",
        type=positive_integer,
        default=300,
        metavar="SECONDS",
        help="long-audio chunk duration; default: 300",
    )

    parser.add_argument(
        "--output-dir",
        default=config.DEFAULT_OUTPUT_FOLDER,
        help=(
            "output directory; default: "
            f"{config.DEFAULT_OUTPUT_FOLDER}"
        ),
    )

    output_group = (
        parser.add_mutually_exclusive_group()
    )

    output_group.add_argument(
        "--txt-only",
        action="store_true",
        help="create only TXT output",
    )

    output_group.add_argument(
        "--docx-only",
        action="store_true",
        help="create only DOCX output",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=(
            f"{config.APP_NAME} "
            f"{config.VERSION}"
        ),
    )

    return parser


def resolve_output_format(args):
    if args.txt_only:
        return "txt"

    if args.docx_only:
        return "docx"

    return "both"


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.audio:
        parser.print_help()
        return 0

    audio_path = Path(
        args.audio
    ).expanduser()

    if not audio_path.exists():
        print(
            f"ERROR: Audio file not found: {audio_path}",
            file=sys.stderr,
        )

        return 2

    if not audio_path.is_file():
        print(
            f"ERROR: Audio path is not a file: {audio_path}",
            file=sys.stderr,
        )

        return 2

    try:
        pipeline = TranscriptionPipeline(
            engine_name=args.engine,
            model=args.model,
            language=args.language,
            threads=args.threads,
            timeout_seconds=args.timeout,
            chunk_duration_seconds=(
                args.chunk_duration
            ),
            output_dir=args.output_dir,
            output_format=(
                resolve_output_format(args)
            ),
        )

        outputs = pipeline.run(
            str(audio_path)
        )

    except KeyboardInterrupt:
        print(
            "\nCancelled by user.",
            file=sys.stderr,
        )

        return 130

    except Exception as error:
        print(
            f"ERROR: {error}",
            file=sys.stderr,
        )

        return 1

    print()
    print("Completed successfully.")

    if "txt" in outputs:
        print(
            f"TXT: {outputs['txt']}"
        )

    if "docx" in outputs:
        print(
            f"DOCX: {outputs['docx']}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
