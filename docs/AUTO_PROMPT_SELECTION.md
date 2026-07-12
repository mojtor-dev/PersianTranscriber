# Automatic Prompt Profile Selection

این قابلیت به‌صورت محافظه‌کارانه از metadata فایل صوتی، نام فایل و hint اختیاری استفاده می‌کند.

## استفاده

```bash
python app.py audio.mp3 --auto-prompt-profile
```

## همراه با Content Hint

```bash
python app.py audio.mp3 \
  --auto-prompt-profile \
  --content-hint technical
```

اولویت انتخاب:

1. `--content-hint`
2. واژگان نام فایل
3. مدت و تعداد کانال
4. fallback بدون Prompt

در وضعیت کم‌اطمینان، سیستم `none` را انتخاب می‌کند تا Prompt اشتباه کیفیت را کاهش ندهد.
