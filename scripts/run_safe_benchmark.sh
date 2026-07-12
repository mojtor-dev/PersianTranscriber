#!/data/data/com.termux/files/usr/bin/bash

set -euo pipefail

cd "$(dirname "$0")/.."

export PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}"

audio_file="${1:-test_fa.mp3}"
reference_file="${2:-data/references/test_fa_reference.txt}"
output_dir="${3:-output/benchmarks/test_fa_safe}"

termux-wake-lock 2>/dev/null || true

cleanup() {
    termux-wake-unlock 2>/dev/null || true
}

trap cleanup EXIT INT TERM

python scripts/benchmark_prompts_safe.py \
    "$audio_file" \
    "$reference_file" \
    --prompt-dir data/prompts \
    --output-dir "$output_dir" \
    --threads 3 \
    --cooldown 10
