# Troubleshooting

## Termux بسته می‌شود

- Battery را برای Termux روی Unrestricted قرار دهید.
- قبل از پردازش طولانی اجرا کنید:

```bash
termux-wake-lock
```

- پس از پایان:

```bash
termux-wake-unlock
```

- تعداد thread را کاهش دهید:

```bash
python app.py audio.mp3 --threads 3
```

## ffmpeg یا ffprobe پیدا نمی‌شود

```bash
pkg install ffmpeg
```

## whisper-cli پیدا نمی‌شود

فایل اجرایی باید در این مسیر باشد:

```text
tools/whisper.cpp/build/bin/whisper-cli
```

## مدل پیدا نمی‌شود

حداقل یک مدل با الگوی زیر لازم است:

```text
tools/whisper.cpp/models/ggml-*.bin
```

## PDF کار نمی‌کند

```bash
pip install reportlab
```

## Benchmark نیمه‌کاره مانده

همان دستور Resume‌پذیر را دوباره اجرا کنید:

```bash
bash scripts/run_safe_benchmark.sh
```

یا:

```bash
bash scripts/run_dataset_benchmark.sh
```
