"""
PersianTranscriber Command Line Interface
Version: 0.2.0
"""

import argparse
import sys
from pathlib import Path

import config
from core.pipeline import TranscriptionPipeline
from core.audio_analysis import AudioAnalyzer
from core.prompt_profiles.selector import PromptProfileSelector
from core.prompt_profiles import PromptProfileManager


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

    parser.add_argument(
        "--formats",
        help=(
            "comma-separated formats: "
            "txt,docx,md,json,srt,vtt,pdf"
        ),
    )

    parser.add_argument(
        "--subtitle-seconds",
        type=positive_integer,
        default=5,
        help=(
            "synthetic subtitle duration per segment"
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

    prompt_group = (
        parser.add_mutually_exclusive_group()
    )

    prompt_group.add_argument(
        "--prompt",
        help=(
            "initial Whisper prompt text; "
            "use it as vocabulary and writing-style context"
        ),
    )

    prompt_group.add_argument(
        "--prompt-file",
        help="UTF-8 file containing the initial Whisper prompt",
    )

    prompt_group.add_argument(
        "--prompt-profile",
        help=(
            "named prompt profile: general, technical, "
            "meeting or lecture"
        ),
    )

    parser.add_argument(
        "--auto-prompt-profile",
        action="store_true",
        help=(
            "conservatively select a prompt profile from audio metadata; "
            "low-confidence cases use no prompt"
        ),
    )

    parser.add_argument(
        "--content-hint",
        choices=[
            "general",
            "technical",
            "meeting",
            "lecture",
        ],
        help=(
            "optional content hint used by automatic profile selection"
        ),
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



def resolve_output_formats(args):
    if args.formats:
        if args.txt_only or args.docx_only:
            raise ValueError(
                "--formats cannot be combined with "
                "--txt-only or --docx-only"
            )

        values = [
            item.strip().lower()
            for item in args.formats.split(",")
            if item.strip()
        ]

        if not values:
            raise ValueError(
                "--formats cannot be empty"
            )

        return values

    if args.txt_only:
        return ["txt"]

    if args.docx_only:
        return ["docx"]

    return [
        "txt",
        "docx",
    ]


def resolve_initial_prompt(
    args,
    audio_path=None,
):
    selected_sources = sum(
        value is not None
        for value in (
            args.prompt,
            args.prompt_file,
            args.prompt_profile,
        )
    )

    if selected_sources > 1:
        raise ValueError(
            "Use only one of --prompt, "
            "--prompt-file or --prompt-profile"
        )

    if args.auto_prompt_profile and selected_sources > 0:
        raise ValueError(
            "--auto-prompt-profile cannot be combined with "
            "--prompt, --prompt-file or --prompt-profile"
        )

    if (
        args.content_hint is not None
        and not args.auto_prompt_profile
    ):
        raise ValueError(
            "--content-hint requires --auto-prompt-profile"
        )

    if args.prompt is not None:
        prompt = args.prompt.strip()

        if not prompt:
            raise ValueError(
                "Prompt cannot be empty"
            )

        return prompt

    if args.prompt_file is not None:
        prompt_path = Path(
            args.prompt_file
        ).expanduser()

        if not prompt_path.exists():
            raise FileNotFoundError(
                f"Prompt file not found: {prompt_path}"
            )

        if not prompt_path.is_file():
            raise ValueError(
                f"Prompt path is not a file: {prompt_path}"
            )

        prompt = prompt_path.read_text(
            encoding="utf-8"
        ).strip()

        if not prompt:
            raise ValueError(
                f"Prompt file is empty: {prompt_path}"
            )

        return prompt

    manager = PromptProfileManager()

    if args.prompt_profile is not None:
        return manager.resolve_prompt(
            args.prompt_profile
        )

    if args.auto_prompt_profile:
        if audio_path is None:
            raise ValueError(
                "audio_path is required for automatic profile selection"
            )

        analysis = AudioAnalyzer().analyze(
            audio_path
        )

        selection = PromptProfileSelector().select(
            analysis,
            content_hint=args.content_hint,
        )

        print(
            "Automatic prompt profile: "
            f"{selection.profile_name} "
            f"(confidence={selection.confidence:.2f}; "
            f"reason={selection.reason})"
        )

        return manager.resolve_prompt(
            selection.profile_name
        )

    return None

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
        pipeline_options = {
            "engine_name": args.engine,
            "model": args.model,
            "language": args.language,
            "threads": args.threads,
            "timeout_seconds": args.timeout,
            "chunk_duration_seconds": (
                args.chunk_duration
            ),
            "output_dir": args.output_dir,
            "output_format": (
                resolve_output_format(args)
            ),
            "output_formats": (
                resolve_output_formats(args)
            ),
            "subtitle_seconds": (
                args.subtitle_seconds
            ),
        }

        initial_prompt = resolve_initial_prompt(
            args,
            audio_path=audio_path,
        )

        if initial_prompt is not None:
            pipeline_options[
                "initial_prompt"
            ] = initial_prompt

        pipeline = TranscriptionPipeline(
            **pipeline_options
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
