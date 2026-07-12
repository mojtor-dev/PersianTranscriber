#!/data/data/com.termux/files/usr/bin/bash

set -euo pipefail

cd "$(dirname "$0")/.."

audio_file="${1:-test_fa.mp3}"
prompt_file="${2:-data/whisper_prompt_fa.txt}"

if [ ! -f "$audio_file" ]; then
    echo "ERROR: Audio file not found: $audio_file" >&2
    exit 2
fi

if [ ! -f "$prompt_file" ]; then
    echo "ERROR: Prompt file not found: $prompt_file" >&2
    exit 2
fi

no_prompt_dir="output/comparison/no_prompt"
with_prompt_dir="output/comparison/with_prompt"

rm -rf "$no_prompt_dir" "$with_prompt_dir"

mkdir -p "$no_prompt_dir" "$with_prompt_dir"

echo
echo "===== Run without prompt ====="

python app.py "$audio_file" \
    --txt-only \
    --output-dir "$no_prompt_dir"

echo
echo "===== Run with prompt ====="

python app.py "$audio_file" \
    --txt-only \
    --output-dir "$with_prompt_dir" \
    --prompt-file "$prompt_file"

no_prompt_file="$no_prompt_dir/transcription.txt"
with_prompt_file="$with_prompt_dir/transcription.txt"

echo
echo "===== WITHOUT PROMPT ====="
cat "$no_prompt_file"

echo
echo
echo "===== WITH PROMPT ====="
cat "$with_prompt_file"

echo
echo
echo "===== DIFF ====="

diff -u \
    "$no_prompt_file" \
    "$with_prompt_file" \
    || true

echo
echo "===== Output paths ====="
echo "Without prompt: $no_prompt_file"
echo "With prompt:    $with_prompt_file"
