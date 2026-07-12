#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."

MAIN="android/app/src/main/java/com/litongjava/whisper/android/java/MainActivity.java"
LAYOUT="android/app/src/main/res/layout/activity_main.xml"

grep -q "OpenDocument" "$MAIN"
grep -q "CreateDocument" "$MAIN"
grep -q "TranscriptionTask" "$MAIN"
grep -q "shareText" "$MAIN"
grep -q "selectAudioBtn" "$LAYOUT"
grep -q "saveBtn" "$LAYOUT"
grep -q "progressBar" "$LAYOUT"

echo "Android usable WAV MVP validation: OK"
