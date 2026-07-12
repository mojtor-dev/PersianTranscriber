# PersianTranscriber Android

این پوشه از نمونه رسمی Android پروژه `whisper.cpp` برای ساخت سریع نخستین APK استفاده می‌کند.

## هدف Bundle 18

- ایجاد شاخه مستقل Android
- تولید APK نصب‌پذیر آزمایشی
- استفاده از backend بومی `whisper.cpp`
- آماده‌سازی GitHub Actions

این نسخه Foundation است. در Bundle بعدی رابط فارسی، انتخاب فایل، مدل فارسی و ذخیره خروجی تکمیل می‌شود.

## ساخت محلی

```bash
cd android
chmod +x gradlew
./gradlew assembleDebug
```

## Usable WAV MVP

- رابط فارسی
- انتخاب فایل WAV
- بارگذاری مدل داخلی
- رونویسی فایل واقعی
- نمایش وضعیت
- ویرایش خروجی
- ذخیره TXT
- اشتراک متن

در مرحله بعد MP3 و M4A با decoder بومی Android اضافه می‌شوند.
