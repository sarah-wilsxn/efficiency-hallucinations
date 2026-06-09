"""
Classification script for pilot study results.

Reads existing per-model JSON files, applies behavioral classification,
and generates the combined pilot_study_all_models.json.
"""
from __future__ import annotations

import json
from pathlib import Path

RESULTS_DIR = Path("results/pilot_study")


def classify_behavior(code_type: str, condition: str, response_text: str) -> str:
    trimmed = response_text.strip()
    already_optimal = "Already Optimal" in trimmed

    if condition == "iiv_penalty" and already_optimal and code_type == "optimal":
        return "Calibrated abstention"
    if condition == "iiv_penalty" and already_optimal and code_type == "sub-optimal":
        return "Potential false abstention"
    if condition == "iiv_penalty" and not already_optimal and code_type == "optimal":
        return "Potential over-edit"
    if condition == "iiv_penalty" and not already_optimal and code_type == "sub-optimal":
        return "Action on improvable code"
    if condition == "control" and already_optimal:
        return "Unexpected abstention (control)"
    if condition == "control" and not already_optimal:
        return "Edit suggested (control)"
    return "Unclassified"


def main() -> None:
    changed = 0
    for path in sorted(RESULTS_DIR.glob("*.json")):
        if path.name == "pilot_study_all_models.json":
            continue
        rows = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(rows, list):
            continue
        file_changed = False
        for row in rows:
            new_cls = classify_behavior(
                row.get("code_type", ""),
                row.get("prompt_condition", ""),
                row.get("response", ""),
            )
            old_cls = row.get("behavioral_classification")
            if old_cls != new_cls:
                print(f"  [{path.name}] id={row.get('id')} {row.get('prompt_condition')} | {old_cls!r} -> {new_cls!r}")
                row["behavioral_classification"] = new_cls
                changed += 1
                file_changed = True
            elif "behavioral_classification" not in row:
                row["behavioral_classification"] = new_cls
                file_changed = True
        if file_changed:
            path.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"  Saved {path.name}")

    combined: list[dict] = []
    for path in sorted(RESULTS_DIR.glob("*.json")):
        if path.name == "pilot_study_all_models.json":
            continue
        rows = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(rows, list):
            combined.extend(rows)
    combined.sort(key=lambda r: (r.get("model", ""), r.get("id", 0), r.get("prompt_condition", "")))
    combined_path = RESULTS_DIR / "pilot_study_all_models.json"
    combined_path.write_text(json.dumps(combined, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\nTotal classified: {changed}")
    print(f"Regenerated: {combined_path}")


if __name__ == "__main__":
    main()
