#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "========================================"
echo " PersianTranscriber Release Check"
echo "========================================"

bash scripts/check.sh
PYTHONPATH="$PWD" python scripts/doctor.py
PYTHONPATH="$PWD" python scripts/smoke_test.py test_fa.mp3

echo
echo "Git status:"
git status -sb

echo
echo "Release check completed successfully."
