# Safe Resumable Benchmark

اجرای کم‌حافظه و Resume‌پذیر برای Termux:

```bash
bash scripts/run_safe_benchmark.sh
```

اگر Termux بسته شد، همان دستور را دوباره اجرا کنید. Variantهای تکمیل‌شده دوباره اجرا نمی‌شوند.

اجرای فقط baseline:

```bash
python scripts/benchmark_prompts_safe.py test_fa.mp3 data/references/test_fa_reference.txt --only baseline-no-prompt --threads 3
```
