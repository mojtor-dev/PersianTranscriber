#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "========================================"
echo " PersianTranscriber Termux Installer"
echo "========================================"

pkg update -y
pkg install -y \
  python \
  git \
  ffmpeg \
  cmake \
  clang \
  make \
  pkg-config

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

mkdir -p \
  output \
  temp \
  logs \
  data/references \
  data/evaluation_dataset

echo
echo "Checking environment..."
PYTHONPATH="$PWD" python scripts/doctor.py

echo
echo "Installation completed."
echo "Run:"
echo "  python app.py --help"
