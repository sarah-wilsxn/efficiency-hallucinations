from __future__ import annotations

from pilot_study_analysis_utils import (
    ANALYSIS_DIR,
    format_markdown_table,
    group_and_summarize,
    load_records,
    percentage_columns,
    rate_columns,
    write_csv,
)


def main() -> None:
    records = load_records()
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

    per_model = group_and_summarize(records, ["requested_model", "model_family"])

    write_csv(
        ANALYSIS_DIR / "per_model_scorecard.csv",
        per_model,
        ["requested_model", "model_family", "n", *rate_columns()],
    )

    print("Per-model scorecard:\n")
    print(
        format_markdown_table(
            per_model,
            [
                ("model", "requested_model"),
                ("family", "model_family"),
                *percentage_columns(),
            ],
        )
    )
    print(f"Saved per-model scorecard to {ANALYSIS_DIR / 'per_model_scorecard.csv'}")


if __name__ == "__main__":
    main()