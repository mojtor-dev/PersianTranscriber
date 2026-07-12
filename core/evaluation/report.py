import html
import json
from datetime import datetime, timezone
from pathlib import Path


def write_json_report(results, output_path, metadata=None) -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "metadata": metadata or {},
        "results": [item.to_dict() for item in results],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path)


def write_html_report(results, output_path, metadata=None) -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for rank, item in enumerate(results, start=1):
        status = f"ERROR: {item.error}" if item.error else "OK"
        rows.append(
            "<tr>"
            f"<td>{rank}</td><td>{html.escape(item.name)}</td>"
            f"<td>{item.wer:.4f}</td><td>{item.cer:.4f}</td>"
            f"<td>{item.quality_score:.4f}</td><td>{item.duration_seconds:.2f}</td>"
            f"<td>{'Yes' if item.prompt_enabled else 'No'}</td><td>{html.escape(status)}</td>"
            "</tr>"
        )
    meta = "".join(
        f"<li><b>{html.escape(str(key))}:</b> {html.escape(str(value))}</li>"
        for key, value in (metadata or {}).items()
    )
    document = f'''<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8">
<title>PersianTranscriber Prompt Benchmark</title>
<style>body{{font-family:sans-serif;max-width:1200px;margin:2rem auto;padding:0 1rem}}table{{width:100%;border-collapse:collapse;direction:ltr}}th,td{{border:1px solid #ccc;padding:.6rem;text-align:center}}th{{background:#eee}}</style>
</head><body><h1>گزارش ارزیابی Prompt</h1><ul>{meta}</ul>
<p>مقادیر کمتر برای WER، CER و Quality Score بهتر هستند.</p>
<table><thead><tr><th>Rank</th><th>Name</th><th>WER</th><th>CER</th><th>Quality</th><th>Seconds</th><th>Prompt</th><th>Status</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></body></html>'''
    path.write_text(document, encoding="utf-8")
    return str(path)
