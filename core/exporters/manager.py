import json
import re
from datetime import datetime, timezone
from pathlib import Path

from core.docx_exporter import DocxExporter
from core.text_exporter import TextExporter


class ExportManager:

    VALID_FORMATS = {
        "txt",
        "docx",
        "md",
        "json",
        "srt",
        "vtt",
        "pdf",
    }

    def __init__(
        self,
        output_dir="output",
        subtitle_seconds=5,
    ):
        if subtitle_seconds <= 0:
            raise ValueError(
                "subtitle_seconds must be positive"
            )

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.subtitle_seconds = subtitle_seconds
        self.text_exporter = TextExporter(
            output_dir=output_dir
        )
        self.docx_exporter = DocxExporter(
            output_dir=output_dir
        )

    def normalize_formats(self, formats):
        if isinstance(formats, str):
            formats = [
                value.strip().lower()
                for value in formats.split(",")
                if value.strip()
            ]

        normalized = []

        for value in formats:
            name = value.strip().lower()

            if name == "both":
                for default_name in (
                    "txt",
                    "docx",
                ):
                    if default_name not in normalized:
                        normalized.append(default_name)
                continue

            if name not in self.VALID_FORMATS:
                available = ", ".join(
                    sorted(self.VALID_FORMATS)
                )
                raise ValueError(
                    f"Unknown output format: {name}. "
                    f"Available formats: {available}"
                )

            if name not in normalized:
                normalized.append(name)

        if not normalized:
            raise ValueError(
                "At least one output format is required"
            )

        return normalized

    def export(
        self,
        text,
        formats,
        stem="transcription",
        metadata=None,
    ):
        outputs = {}

        for name in self.normalize_formats(
            formats
        ):
            if name == "txt":
                outputs[name] = (
                    self.text_exporter.save_text(
                        text,
                        filename=f"{stem}.txt",
                    )
                )
            elif name == "docx":
                outputs[name] = (
                    self.docx_exporter.save_docx(
                        text,
                        filename=f"{stem}.docx",
                    )
                )
            elif name == "md":
                outputs[name] = self._export_markdown(
                    text,
                    stem,
                )
            elif name == "json":
                outputs[name] = self._export_json(
                    text,
                    stem,
                    metadata,
                )
            elif name == "srt":
                outputs[name] = self._export_srt(
                    text,
                    stem,
                )
            elif name == "vtt":
                outputs[name] = self._export_vtt(
                    text,
                    stem,
                )
            elif name == "pdf":
                outputs[name] = self._export_pdf(
                    text,
                    stem,
                )

        return outputs

    def _path(self, stem, suffix):
        return self.output_dir / f"{stem}.{suffix}"

    def _export_markdown(self, text, stem):
        path = self._path(stem, "md")
        path.write_text(
            "# رونویسی\n\n"
            + text.strip()
            + "\n",
            encoding="utf-8",
        )
        return str(path)

    def _export_json(
        self,
        text,
        stem,
        metadata,
    ):
        path = self._path(stem, "json")
        path.write_text(
            json.dumps(
                {
                    "text": text,
                    "metadata": metadata or {},
                    "generated_at": datetime.now(
                        timezone.utc
                    ).isoformat(),
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        return str(path)

    def _sentences(self, text):
        parts = re.split(
            r"(?<=[.!؟])\s+|\n+",
            text.strip(),
        )
        return [
            part.strip()
            for part in parts
            if part.strip()
        ]

    @staticmethod
    def _timestamp(seconds, separator):
        total_ms = int(round(seconds * 1000))
        hours, remainder = divmod(
            total_ms,
            3_600_000,
        )
        minutes, remainder = divmod(
            remainder,
            60_000,
        )
        seconds_value, milliseconds = divmod(
            remainder,
            1000,
        )
        return (
            f"{hours:02d}:{minutes:02d}:"
            f"{seconds_value:02d}"
            f"{separator}{milliseconds:03d}"
        )

    def _export_srt(self, text, stem):
        path = self._path(stem, "srt")
        lines = []

        for index, sentence in enumerate(
            self._sentences(text),
            start=1,
        ):
            start = (
                (index - 1)
                * self.subtitle_seconds
            )
            end = (
                index
                * self.subtitle_seconds
            )

            lines.extend(
                [
                    str(index),
                    (
                        f"{self._timestamp(start, ',')} --> "
                        f"{self._timestamp(end, ',')}"
                    ),
                    sentence,
                    "",
                ]
            )

        path.write_text(
            "\n".join(lines),
            encoding="utf-8",
        )
        return str(path)

    def _export_vtt(self, text, stem):
        path = self._path(stem, "vtt")
        lines = [
            "WEBVTT",
            "",
        ]

        for index, sentence in enumerate(
            self._sentences(text),
            start=1,
        ):
            start = (
                (index - 1)
                * self.subtitle_seconds
            )
            end = (
                index
                * self.subtitle_seconds
            )

            lines.extend(
                [
                    (
                        f"{self._timestamp(start, '.')} --> "
                        f"{self._timestamp(end, '.')}"
                    ),
                    sentence,
                    "",
                ]
            )

        path.write_text(
            "\n".join(lines),
            encoding="utf-8",
        )
        return str(path)

    def _export_pdf(self, text, stem):
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
        except ImportError as error:
            raise RuntimeError(
                "PDF export requires reportlab. "
                "Install it with: pip install reportlab"
            ) from error

        path = self._path(stem, "pdf")
        pdf = canvas.Canvas(
            str(path),
            pagesize=A4,
        )
        _, height = A4
        y = height - 50

        for line in text.splitlines() or [""]:
            chunks = [
                line[index:index + 85]
                for index in range(
                    0,
                    len(line),
                    85,
                )
            ] or [""]

            for chunk in chunks:
                if y < 50:
                    pdf.showPage()
                    y = height - 50

                pdf.drawString(
                    50,
                    y,
                    chunk,
                )
                y -= 18

        pdf.save()
        return str(path)
