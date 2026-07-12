#!/data/data/com.termux/files/usr/bin/bash

set -euo pipefail

cd "$(dirname "$0")/.."

if [ "$#" -lt 3 ]; then
    echo "Usage:"
    echo "  bash scripts/add_dataset_sample.sh SAMPLE_ID AUDIO CONTENT_TYPE"
    echo
    echo "The script opens nano for the reference transcript."
    exit 2
fi

sample_id="$1"
audio_file="$2"
content_type="$3"

reference_file="/tmp/${sample_id}_reference.txt"

cat > "$reference_file" <<'TXT'
متن دقیق و کامل فایل صوتی را اینجا وارد کنید.
TXT

nano "$reference_file"

python scripts/dataset_builder.py add \
    "$sample_id" \
    "$audio_file" \
    --reference-file "$reference_file" \
    --content-type "$content_type"

rm -f "$reference_file"

python scripts/dataset_builder.py validate

echo
echo "Dataset sample added successfully."
echo "Run benchmark with:"
echo "  bash scripts/run_dataset_benchmark.sh"
