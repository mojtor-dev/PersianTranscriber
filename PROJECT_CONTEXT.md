# PersianTranscriber Project Context

## هدف پروژه

PersianTranscriber یک نرم‌افزار حرفه‌ای برای تبدیل فایل صوتی فارسی به متن است.

هدف:
ساخت یک ابزار قابل توسعه با دقت بالا برای تبدیل گفتار فارسی، اصلاح متن و خروجی حرفه‌ای DOCX و TXT.

---

## محیط توسعه

سیستم:
- Android
- Termux
- Python
- Git

موتور تبدیل:
Whisper.cpp

مسیر موتور:

tools/whisper.cpp/

فایل اجرایی:

tools/whisper.cpp/build/bin/whisper-cli


---

## مدل‌های Whisper

مدل‌های تست شده:

- base
- small
- medium

مدل فعال فعلی:

small

زبان:

fa

مدل medium تست شده و دقت بالاتری دارد ولی مصرف منابع بیشتری دارد.


---

## معماری فعلی

ساختار اصلی:

PersianTranscriber/

core/
- pipeline.py
- transcriber.py
- cleaner.py
- dictionary_engine.py
- text_merger.py
- audio_preprocessor.py
- text_exporter.py
- docx_exporter.py

core/engines/
- whisper_cpp.py

core/utils/
- timer.py

data/
- persian_dictionary.json

tools/
- whisper.cpp


---

## قابلیت‌های ساخته شده

### Whisper Engine

- اتصال Whisper.cpp
- بارگذاری مدل
- تبدیل صوت فارسی به متن


### Pipeline

مسیر پردازش:

Audio
↓
Audio Loader
↓
Whisper Engine
↓
Text Cleaner
↓
Dictionary Engine
↓
TXT Export
↓
DOCX Export


### خروجی

تولید می‌شود:

- transcription.txt
- transcription.docx


---

## Dictionary Engine

هدف:

اصلاح خطاهای رایج Whisper فارسی.

نمونه اصلاح‌ها:

تیر موکس → ترمکس

جیپی تی → جی‌پی‌تی

سوتی → صوتی

مطن → متن

نرم افزار → نرم‌افزار

فایلهای → فایل‌های


فایل فرهنگ لغت:

data/persian_dictionary.json


---

## Text Merger

برای ترکیب متن بخش‌های مختلف صوت ساخته شده است.


---

## Audio Preprocessor

ماژول اولیه آماده‌سازی صوت ساخته شده است.

هدف آینده:

- تبدیل فرمت صوت
- استانداردسازی فایل
- آماده‌سازی فایل‌های طولانی


---

## سیستم Progress

نمایش مراحل:

0% Starting

20% Loading audio

40% Loading model

70% Transcribing

85% Cleaning text

95% Saving output

100% Completed


---

## Logging

ثبت رویدادها در:

logs/


نمونه:

START file=test_fa.mp3

COMPLETE output=transcription.docx


---

## تست موفق

دستور:

python -c "from core.pipeline import TranscriptionPipeline; p=TranscriptionPipeline(); print(p.run('test_fa.mp3'))"


خروجی:

Whisper.cpp ready (model=small, language=fa)

output/transcription.docx


---

## وضعیت Git

Repository:

github.com/mojtor-dev/PersianTranscriber


Branch:

feature/core-architecture


آخرین commit:

d2e50e0

Message:

prepare project handover with dictionary and pipeline improvements


---

## مشکلات فعلی

Whisper در فارسی هنوز برخی کلمات را اشتباه تشخیص می‌دهد.

نمونه:

صبح بخیر → سو پخیر

جمع → جوم

کمک می‌کنه → کومک مکنه

بتونم → بطنم


راه حل‌های آینده:

- Persian Text Normalizer
- Dictionary گسترده‌تر
- مدل‌های بهتر


---

## برنامه ادامه توسعه

مرحله بعد:

1. Persian Text Normalizer

وظایف:

- اصلاح نیم‌فاصله
- اصلاح افعال فارسی
- اصلاح فاصله‌ها
- اصلاح خطاهای رایج گفتاری


مرحله بعد:

2. Audio Splitter

هدف:

پشتیبانی فایل‌های:

- 45 دقیقه
- 90 دقیقه
- چند ساعت


بعد از آن:

3. مدیریت صف فایل‌ها

4. رابط گرافیکی حرفه‌ای

5. تنظیمات انتخاب مدل

6. افزایش سرعت و دقت


---

## دستور مهم برای ادامه پروژه

قبل از تغییرات بزرگ:

- ساختار فعلی بررسی شود.
- معماری موجود حفظ شود.
- پروژه بازنویسی نشود.
- توسعه مرحله‌ای انجام شود.

این پروژه ادامه یک معماری موجود است، نه شروع از صفر.
