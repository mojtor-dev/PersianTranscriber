# Quick Start

## 1. بررسی محیط

```bash
PYTHONPATH="$PWD" python scripts/doctor.py
```

## 2. تبدیل فایل صوتی

```bash
python app.py test_fa.mp3
```

## 3. فقط متن

```bash
python app.py test_fa.mp3 --txt-only
```

## 4. چند خروجی

```bash
python app.py test_fa.mp3 \
  --formats txt,docx,md,json
```

## 5. Prompt Profile

```bash
python app.py test_fa.mp3 \
  --prompt-profile meeting
```

## 6. بررسی نهایی نسخه

```bash
bash scripts/release_check.sh
```
