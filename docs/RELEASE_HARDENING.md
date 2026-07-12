# Release Hardening

## بررسی محیط

```bash
PYTHONPATH="$PWD" python scripts/doctor.py
```

خروجی JSON:

```bash
PYTHONPATH="$PWD" python scripts/doctor.py --json
```

## Smoke Test

```bash
PYTHONPATH="$PWD" python scripts/smoke_test.py test_fa.mp3
```

Smoke Test خروجی را در پوشهٔ موقت می‌سازد و چیزی را در `output/` بازنویسی نمی‌کند.

## الزامات ضروری نسخه ۱

- Python
- ffmpeg
- ffprobe
- whisper-cli قابل اجرا
- حداقل یک مدل `ggml-*.bin`
- پوشه‌های `output/` و `temp/` قابل نوشتن
