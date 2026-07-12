#!/usr/bin/env python
"""
Command-line dataset builder.
"""

import argparse
import sys
from pathlib import Path

from core.dataset import DatasetBuilder


def build_parser():
    parser = argparse.ArgumentParser(
        description=(
            "Add, remove, list and validate PersianTranscriber "
            "evaluation samples"
        )
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    add_parser = subparsers.add_parser(
        "add",
        help="add a sample",
    )

    add_parser.add_argument(
        "sample_id",
    )

    add_parser.add_argument(
        "audio",
    )

    reference_group = (
        add_parser.add_mutually_exclusive_group(
            required=True
        )
    )

    reference_group.add_argument(
        "--reference-file",
    )

    reference_group.add_argument(
        "--reference-text",
    )

    add_parser.add_argument(
        "--content-type",
        required=True,
        choices=sorted(
            DatasetBuilder.VALID_CONTENT_TYPES
        ),
    )

    add_parser.add_argument(
        "--copy-audio",
        action="store_true",
    )

    add_parser.add_argument(
        "--overwrite",
        action="store_true",
    )

    remove_parser = subparsers.add_parser(
        "remove",
        help="remove a sample",
    )

    remove_parser.add_argument(
        "sample_id",
    )

    remove_parser.add_argument(
        "--delete-reference",
        action="store_true",
    )

    remove_parser.add_argument(
        "--delete-copied-audio",
        action="store_true",
    )

    subparsers.add_parser(
        "list",
        help="list samples",
    )

    subparsers.add_parser(
        "validate",
        help="validate all paths",
    )

    return parser


def read_reference(args):
    if args.reference_text is not None:
        return args.reference_text

    reference_path = Path(
        args.reference_file
    ).expanduser()

    if not reference_path.is_file():
        raise FileNotFoundError(
            f"Reference file not found: {reference_path}"
        )

    return reference_path.read_text(
        encoding="utf-8"
    )


def main(argv=None):
    args = build_parser().parse_args(argv)

    builder = DatasetBuilder()

    try:
        if args.command == "add":
            sample = builder.add_sample(
                sample_id=args.sample_id,
                audio_path=args.audio,
                reference_text=read_reference(args),
                content_type=args.content_type,
                copy_audio=args.copy_audio,
                overwrite=args.overwrite,
            )

            print(
                "Added sample:"
            )

            print(
                f"  id: {sample['id']}"
            )

            print(
                f"  audio: {sample['audio']}"
            )

            print(
                f"  reference: {sample['reference']}"
            )

            print(
                f"  content_type: {sample['content_type']}"
            )

            return 0

        if args.command == "remove":
            sample = builder.remove_sample(
                sample_id=args.sample_id,
                delete_reference=args.delete_reference,
                delete_copied_audio=(
                    args.delete_copied_audio
                ),
            )

            print(
                f"Removed sample: {sample['id']}"
            )

            return 0

        if args.command == "list":
            dataset = builder.load()

            if not dataset["samples"]:
                print(
                    "Dataset is empty."
                )

                return 0

            for sample in dataset["samples"]:
                print(
                    f"{sample['id']} | "
                    f"{sample['content_type']} | "
                    f"{sample['audio']} | "
                    f"{sample['reference']}"
                )

            return 0

        if args.command == "validate":
            errors = builder.validate_paths()

            if errors:
                for error in errors:
                    print(
                        f"ERROR: {error}",
                        file=sys.stderr,
                    )

                return 1

            print(
                "Dataset validation: OK"
            )

            return 0

    except Exception as error:
        print(
            f"ERROR: {error}",
            file=sys.stderr,
        )

        return 1

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
