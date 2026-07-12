#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

cd "$(dirname "$0")/.."
export PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}"

dataset="${1:-data/evaluation_dataset/dataset.json}"
output="${2:-output/benchmarks/dataset_safe}"

termux-wake-lock 2>/dev/null || true
trap 'termux-wake-unlock 2>/dev/null || true' EXIT INT TERM

python scripts/benchmark_dataset_safe.py   "$dataset"   --output-dir "$output"   --threads 3   --cooldown 10
