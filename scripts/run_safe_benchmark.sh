#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
AUDIO="${1:-test_fa.mp3}"
REFERENCE="${2:-data/references/test_fa_reference.txt}"
OUTPUT="${3:-output/benchmarks/test_fa_safe}"
termux-wake-lock 2>/dev/null || true
trap 'termux-wake-unlock 2>/dev/null || true' EXIT INT TERM
python scripts/benchmark_prompts_safe.py "$AUDIO" "$REFERENCE" --prompt-dir data/prompts --output-dir "$OUTPUT" --threads 3 --cooldown 10
