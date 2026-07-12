# Dataset Builder

## افزودن سریع نمونه

```bash
bash scripts/add_dataset_sample.sh \
  sample-id \
  path/to/audio.mp3 \
  technical
```

اسکریپت `nano` را برای واردکردن متن مرجع باز می‌کند.

## افزودن با فایل مرجع آماده

```bash
python scripts/dataset_builder.py add \
  sample-id \
  path/to/audio.mp3 \
  --reference-file path/to/reference.txt \
  --content-type technical
```

## کپی فایل صوتی به داخل Dataset

```bash
python scripts/dataset_builder.py add \
  sample-id \
  /sdcard/Download/audio.mp3 \
  --reference-file reference.txt \
  --content-type mobile \
  --copy-audio
```

## فهرست نمونه‌ها

```bash
python scripts/dataset_builder.py list
```

## اعتبارسنجی Dataset

```bash
python scripts/dataset_builder.py validate
```

## حذف نمونه

```bash
python scripts/dataset_builder.py remove sample-id
```

برای حذف فایل مرجع و فایل صوتی کپی‌شده نیز:

```bash
python scripts/dataset_builder.py remove sample-id \
  --delete-reference \
  --delete-copied-audio
```
