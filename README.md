# PersianTranscriber

PersianTranscriber یک ابزار خط فرمان برای تبدیل فایل صوتی فارسی به متن است. پروژه از `whisper.cpp` استفاده می‌کند و برای فارسی دارای نرمال‌سازی، دیکشنری اصلاحات، پردازش متن، فایل‌های طولانی، Prompt Profile و خروجی‌های چندفرمتی است.

## قابلیت‌های نسخه 1.0

- اجرای محلی `whisper.cpp`
- پشتیبانی از فایل‌های صوتی کوتاه و بلند
- تقسیم خودکار فایل‌های طولانی
- نرمال‌سازی فارسی
- دیکشنری اصلاحات قابل توسعه
- Smart Persian Post Processor
- Prompt Profile دستی و خودکار
- خروجی TXT و DOCX
- خروجی Markdown، JSON، SRT، VTT و PDF
- Benchmark و Dataset Builder
- ابزار Diagnostics و Smoke Test

## نصب سریع روی Termux

ابتدا مخزن را دریافت کنید و سپس:

```bash
cd ~/PersianTranscriber
bash scripts/install_termux.sh
```

مدل Whisper باید در مسیر زیر قرار بگیرد:

```text
tools/whisper.cpp/models/ggml-small.bin
```

فایل اجرایی مورد انتظار:

```text
tools/whisper.cpp/build/bin/whisper-cli
```

## استفاده پایه

```bash
python app.py audio.mp3
```

فقط TXT:

```bash
python app.py audio.mp3 --txt-only
```

چند خروجی:

```bash
python app.py audio.mp3 \
  --formats txt,docx,md,json,srt,vtt
```

Prompt Profile:

```bash
python app.py audio.mp3 \
  --prompt-profile technical
```

انتخاب خودکار محافظه‌کارانه:

```bash
python app.py audio.mp3 \
  --auto-prompt-profile
```

همراه با Content Hint:

```bash
python app.py audio.mp3 \
  --auto-prompt-profile \
  --content-hint meeting
```

## فایل‌های طولانی

فایل‌های طولانی به chunkهای موقت تقسیم می‌شوند. chunkها پس از موفقیت یا خطا پاک‌سازی می‌شوند.

## بررسی محیط

```bash
PYTHONPATH="$PWD" python scripts/doctor.py
```

## اجرای تست‌ها

```bash
bash scripts/check.sh
```

## Smoke Test

```bash
PYTHONPATH="$PWD" python scripts/smoke_test.py test_fa.mp3
```

## Release Check کامل

```bash
bash scripts/release_check.sh
```

## نکته درباره SRT و VTT

در نسخه 1.0 زمان‌بندی SRT و VTT مصنوعی و ثابت است. timestamp واقعی Whisper برای نسخه‌های بعدی برنامه‌ریزی شده است.

## ساختار مهم

```text
app.py
core/
data/
docs/
scripts/
tests/
output/
temp/
logs/
```

## مجوز

MIT
