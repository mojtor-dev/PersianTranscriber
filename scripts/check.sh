#!/data/data/com.termux/files/usr/bin/bash

set -euo pipefail

cd "$(dirname "$0")/.."

echo
echo "========================================"
echo " PersianTranscriber Development Check"
echo "========================================"

echo
echo "[1/6] Git branch"
branch_name="$(git branch --show-current)"
echo "Branch: $branch_name"

if [ "$branch_name" != "feature/core-architecture" ]; then
    echo "ERROR: Expected branch feature/core-architecture"
    exit 1
fi

echo
echo "[2/6] Environment"
echo "Python: $(python --version 2>&1)"

if command -v ffmpeg >/dev/null 2>&1; then
    echo "ffmpeg: available"
else
    echo "ERROR: ffmpeg is not available in PATH"
    exit 1
fi

if command -v ffprobe >/dev/null 2>&1; then
    echo "ffprobe: available"
else
    echo "ERROR: ffprobe is not available in PATH"
    exit 1
fi

echo
echo "[3/6] JSON validation"

json_files=(
    "data/persian_dictionary.json"
    "tests/fixtures/whisper_fa_samples.json"
)

for json_file in "${json_files[@]}"; do
    if [ -f "$json_file" ]; then
        python -m json.tool "$json_file" >/dev/null
        echo "OK: $json_file"
    else
        echo "ERROR: Missing JSON file: $json_file"
        exit 1
    fi
done

echo
echo "[4/6] Python syntax"

mapfile -t python_files < <(
    find core tests \
        -type f \
        -name '*.py' \
        ! -path '*/__pycache__/*' \
        | sort
)

if [ "${#python_files[@]}" -eq 0 ]; then
    echo "ERROR: No Python files found"
    exit 1
fi

python -m py_compile "${python_files[@]}"
echo "OK: ${#python_files[@]} Python files"

echo
echo "[5/6] Unit tests"

python -m unittest discover \
    -s tests \
    -p 'test_*.py' \
    -v

echo
echo "[6/6] Git status"

git status --short

echo
echo "========================================"
echo " ALL CHECKS PASSED"
echo "========================================"
