#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

cd "$(dirname "$0")/.."

test -d android
test -f .github/workflows/android-apk.yml

if [ ! -f android/gradlew ]; then
    echo "ERROR: android/gradlew is missing" >&2
    exit 1
fi

if [ ! -d android/app ]; then
    echo "ERROR: Android app module is missing" >&2
    exit 1
fi

if ! find android/app/src -type f \
    \( -name '*.kt' -o -name '*.java' \) \
    -print -quit | grep -q .; then
    echo "ERROR: no Android Kotlin/Java source found" >&2
    exit 1
fi

if ! find android -type f -name 'build.gradle*' \
    -print -quit | grep -q .; then
    echo "ERROR: no Gradle build file found" >&2
    exit 1
fi

echo "Android foundation validation: OK"
