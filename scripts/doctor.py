#!/usr/bin/env python

import json
import sys

from core.release import ReleaseDiagnostics


def main(argv=None):
    json_mode = "--json" in (argv or sys.argv[1:])

    diagnostics = ReleaseDiagnostics()
    results = diagnostics.run()

    if json_mode:
        print(
            json.dumps(
                [
                    result.to_dict()
                    for result in results
                ],
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(
            "PersianTranscriber Release Diagnostics"
        )
        print(
            "=" * 40
        )

        for result in results:
            status = (
                "OK"
                if result.ok
                else "FAIL"
            )

            print(
                f"[{status}] {result.name}: "
                f"{result.message}"
            )

    failed = [
        result
        for result in results
        if result.required and not result.ok
    ]

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
