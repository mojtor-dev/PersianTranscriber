# Export Suite

فرمت‌ها:

- TXT
- DOCX
- Markdown
- JSON
- SRT
- VTT
- PDF

## نمونه

```bash
python app.py audio.mp3 \
  --formats txt,docx,md,json,srt,vtt
```

PDF به کتابخانهٔ `reportlab` نیاز دارد:

```bash
pip install reportlab
python app.py audio.mp3 --formats pdf
```

SRT و VTT فعلاً از بازه‌های زمانی مصنوعی ثابت استفاده می‌کنند، چون Pipeline هنوز timestamp واقعی segmentهای Whisper را نگه نمی‌دارد:

```bash
python app.py audio.mp3 \
  --formats srt,vtt \
  --subtitle-seconds 4
```
