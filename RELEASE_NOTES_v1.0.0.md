# PersianTranscriber v1.0.0

اولین نسخهٔ پایدار PersianTranscriber.

## امکانات اصلی

- تبدیل گفتار فارسی به متن با `whisper.cpp`
- پشتیبانی از فایل‌های صوتی کوتاه و بلند
- تقسیم خودکار فایل‌های طولانی
- نرمال‌سازی فارسی
- دیکشنری اصلاحات
- Smart Persian Post Processor
- Prompt Profileهای دستی و انتخاب خودکار محافظه‌کارانه
- Benchmark و Dataset Builder
- خروجی TXT، DOCX، Markdown، JSON، SRT، VTT و PDF
- Diagnostics، Smoke Test و Release Check
- بیش از ۱۱۰ تست خودکار

## محدودیت‌های نسخه ۱

- SRT و VTT از زمان‌بندی مصنوعی استفاده می‌کنند.
- diarization و timestamp واقعی Whisper در نسخه‌های بعدی اضافه می‌شوند.
- GUI و مدیریت خودکار مدل‌ها جزو برنامهٔ نسخه‌های بعدی هستند.

## بررسی نصب

```bash
PYTHONPATH="$PWD" python scripts/doctor.py
```

## اجرای سریع

```bash
python app.py audio.mp3
```
