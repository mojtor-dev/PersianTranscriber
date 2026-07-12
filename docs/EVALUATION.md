# Evaluation Framework

معیارها: WER، CER، امتیاز ترکیبی کیفیت و زمان اجرا.

## ساخت متن مرجع

```bash
bash scripts/create_reference.sh test_fa
```

سپس `data/references/test_fa_reference.txt` را با متن دقیق و دستی صوت جایگزین کنید.

## اجرای Benchmark

```bash
python scripts/benchmark_prompts.py test_fa.mp3 data/references/test_fa_reference.txt --prompt-dir data/prompts --output-dir output/benchmarks/test_fa
```

گزارش‌ها در `report.json` و `report.html` ساخته می‌شوند. Baseline بدون Prompt همیشه اجرا می‌شود.
