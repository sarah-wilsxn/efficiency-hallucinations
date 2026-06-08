from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


RESULTS_DIR = Path("results/pilot_study")
ANALYSIS_DIR = RESULTS_DIR / "analysis"

RATE_CATEGORIES = [
    "edit",
    "abstention",
    "over-edit",
    "false abstention",
    "unknown",
]

CLASS_TO_CATEGORY = {
    "Edit suggested (control)": "edit",
    "Action on improvable code": "edit",
    "Calibrated abstention": "abstention",
    "Unexpected abstention (control)": "abstention",
    "Potential over-edit": "over-edit",
    "Potential false abstention": "false abstention",
}


def load_records(results_dir: Path = RESULTS_DIR) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted(results_dir.glob("*.json")):
        if path.name == "pilot_study_all_models.json":
            continue
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if not isinstance(payload, list):
            continue
        for record in payload:
            if isinstance(record, dict):
                enriched = dict(record)
                enriched["source_file"] = path.name
                enriched["requested_model"] = path.stem
                enriched["model_family"] = infer_family(enriched.get("model", ""))
                enriched["rate_category"] = classify_rate_category(
                    enriched.get("behavioral_classification", "")
                )
                records.append(enriched)
    return records


def infer_family(model_id: str) -> str:
    lowered = model_id.lower()
    if "claude" in lowered:
        return "Claude"
    if "gemini" in lowered:
        return "Gemini"
    if "qwen" in lowered:
        return "Qwen"
    if "gpt" in lowered:
        return "GPT"
    if "/" in model_id:
        prefix = model_id.split("/", 1)[0].lower()
        if prefix in {"openai", "anthropic", "google", "qwen"}:
            return prefix.title()
        return "Gateway"
    return "Other"


def classify_rate_category(behavioral_classification: str) -> str:
    return CLASS_TO_CATEGORY.get(behavioral_classification, "unknown")


def group_and_summarize(records: list[dict[str, Any]], group_fields: list[str]) -> list[dict[str, Any]]:
    grouped: dict[tuple[Any, ...], Counter[str]] = defaultdict(Counter)
    totals: dict[tuple[Any, ...], int] = defaultdict(int)

    for record in records:
        key = tuple(record.get(field, "") for field in group_fields)
        category = record.get("rate_category", "unknown")
        grouped[key][category] += 1
        totals[key] += 1

    rows: list[dict[str, Any]] = []
    for key in sorted(grouped.keys()):
        total = totals[key]
        counts = grouped[key]
        row = {field: value for field, value in zip(group_fields, key)}
        row["n"] = total
        for category in RATE_CATEGORIES:
            row[f"{category}_count"] = counts.get(category, 0)
            row[f"{category}_rate"] = counts.get(category, 0) / total if total else 0.0
        rows.append(row)
    return rows


def overall_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    counts = Counter(record.get("rate_category", "unknown") for record in records)
    total = len(records)
    summary = {"n": total}
    for category in RATE_CATEGORIES:
        summary[f"{category}_count"] = counts.get(category, 0)
        summary[f"{category}_rate"] = counts.get(category, 0) / total if total else 0.0
    return summary


def write_csv(path: Path, rows: list[dict[str, Any]], field_order: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=field_order)
        writer.writeheader()
        writer.writerows(rows)


def format_markdown_table(rows: list[dict[str, Any]], columns: list[tuple[str, str]]) -> str:
    if not rows:
        return "No rows.\n"

    header = "| " + " | ".join(label for label, _ in columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"
    lines = [header, separator]
    for row in rows:
        cells = []
        for _, key in columns:
            value = row.get(key, "")
            if isinstance(value, float):
                cells.append(f"{value:.3f}")
            else:
                cells.append(str(value))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def rate_columns() -> list[str]:
    columns = ["n"]
    for category in RATE_CATEGORIES:
        columns.append(f"{category}_count")
        columns.append(f"{category}_rate")
    return columns


def percentage_columns() -> list[tuple[str, str]]:
    return [
        ("n", "n"),
        ("edit %", "edit_rate"),
        ("abstention %", "abstention_rate"),
        ("over-edit %", "over-edit_rate"),
        ("false abstention %", "false abstention_rate"),
        ("unknown %", "unknown_rate"),
    ]


def write_markdown(path: Path, title: str, sections: Iterable[tuple[str, list[dict[str, Any]], list[tuple[str, str]]]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# {title}", ""]
    for heading, rows, columns in sections:
        lines.append(f"## {heading}")
        lines.append("")
        lines.append(format_markdown_table(rows, columns))
    path.write_text("\n".join(lines), encoding="utf-8")