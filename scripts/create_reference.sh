#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
name="${1:-test_fa}"
path="${2:-data/references/${name}_reference.txt}"
mkdir -p "$(dirname "$path")"
[ ! -e "$path" ] || { echo "Reference already exists: $path" >&2; exit 1; }
printf '%s\n' 'این فایل را با متن دقیق و دستی فایل صوتی جایگزین کنید.' 'برای WER و CER معتبر، متن باید دقیقاً مطابق گفتار باشد.' > "$path"
echo "Created: $path"
