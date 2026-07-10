#!/data/data/com.termux/files/usr/bin/bash

echo "=============================="
echo " PersianTranscriber Check"
echo "=============================="

echo
echo "[1/5] Python Syntax Check..."

python -m py_compile core/*.py core/engines/*.py

if [ $? -ne 0 ]; then
    echo "❌ Syntax Error Found"
    exit 1
fi

echo "✅ Syntax OK"


echo
echo "[2/5] Pipeline Test..."

python -c "from core.pipeline import TranscriptionPipeline; p=TranscriptionPipeline(); print(p.run('test_fa.mp3'))"

if [ $? -ne 0 ]; then
    echo "❌ Pipeline Failed"
    exit 1
fi

echo "✅ Pipeline OK"


echo
echo "[3/5] Git Add..."

git add .


echo
echo "[4/5] Commit"

read -p "Commit message: " message

if [ -z "$message" ]; then
    echo "❌ Empty commit message"
    exit 1
fi

git commit -m "$message"


if [ $? -ne 0 ]; then
    echo "❌ Commit Failed"
    exit 1
fi


echo
echo "[5/5] Push..."

git push origin feature/core-architecture


if [ $? -ne 0 ]; then
    echo "❌ Push Failed"
    exit 1
fi


echo
echo "=============================="
echo "✅ Commit & Push Completed"
echo "=============================="
