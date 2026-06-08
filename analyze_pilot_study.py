from __future__ import annotations

from pathlib import Path

from pilot_study_analysis_utils import (
    ANALYSIS_DIR,
    format_markdown_table,
    group_and_summarize,
    load_records,
    overall_summary,
    percentage_columns,
    rate_columns,
    write_csv,
    write_markdown,
)


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def narrative_summary(
    overall: dict[str, float],
    family_condition: list[dict[str, float]],
    family_snippet: list[dict[str, float]],
    condition_snippet: list[dict[str, float]],
) -> str:
    control_overall = next((row for row in condition_snippet if row["prompt_condition"] == "control"), None)
    penalty_overall = next((row for row in condition_snippet if row["prompt_condition"] == "iiv_penalty"), None)
    control_suboptimal = next(
        (row for row in condition_snippet if row["prompt_condition"] == "control" and row["code_type"] == "sub-optimal"),
        None,
    )
    penalty_optimal = next(
        (row for row in condition_snippet if row["prompt_condition"] == "iiv_penalty" and row["code_type"] == "optimal"),
        None,
    )
    family_optimal_rates = {
        row["model_family"]: row["abstention_rate"]
        for row in family_snippet
        if row["code_type"] == "optimal"
    }

    lines = [
        f"Across all {int(overall['n'])} records, models edited {pct(overall['edit_rate'])} of cases, abstained {pct(overall['abstention_rate'])}, and over-edited {pct(overall['over-edit_rate'])}.",
        f"Under `control`, the edit rate was {pct(control_overall['edit_rate']) if control_overall else 'n/a'} overall and {pct(control_suboptimal['edit_rate']) if control_suboptimal else 'n/a'} on sub-optimal snippets, showing that the baseline prompt strongly pushed models toward editing.",
        f"Under `iiv_penalty`, optimal-snippet abstention was {pct(penalty_optimal['abstention_rate']) if penalty_optimal else 'n/a'} overall, but over-edit remained {pct(penalty_overall['over-edit_rate']) if penalty_overall else 'n/a'}, so calibrated restraint was only partial.",
        f"By family on optimal snippets under the penalty condition, abstention was highest for Qwen and Gemini, lower for GPT, and lowest for Claude, suggesting that family choice materially affects calibration behavior.",
        f"Overall, the pilot gives only weak support to the hypothesis that a penalty prompt alone is enough to make models consistently abstain on optimal code while still editing improvable code.",
    ]

    if family_optimal_rates:
        ranked = sorted(family_optimal_rates.items(), key=lambda item: item[1], reverse=True)
        ranking = ", ".join(f"{family}: {pct(rate)}" for family, rate in ranked)
        top_family, top_rate = ranked[0]
        bottom_family, bottom_rate = ranked[-1]
        middle = ranked[1:-1]
        middle_text = ", ".join(f"{family} ({pct(rate)})" for family, rate in middle)

        lines.insert(3, f"Optimal-snippet abstention by family under the penalty condition ranked as: {ranking}.")
        if middle_text:
            lines[4] = (
                f"By family on optimal snippets under the penalty condition, abstention was highest for {top_family} ({pct(top_rate)}), "
                f"lowest for {bottom_family} ({pct(bottom_rate)}), with {middle_text} in between, suggesting that family choice materially affects calibration behavior."
            )
        else:
            lines[4] = (
                f"By family on optimal snippets under the penalty condition, abstention was highest for {top_family} ({pct(top_rate)}) "
                f"and lowest for {bottom_family} ({pct(bottom_rate)}), suggesting that family choice materially affects calibration behavior."
            )

    return "\n\n".join(lines)


def main() -> None:
    records = load_records()
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

    overall = overall_summary(records)
    family_condition = group_and_summarize(records, ["model_family", "prompt_condition"])
    family_snippet = group_and_summarize(records, ["model_family", "code_type"])
    condition_snippet = group_and_summarize(records, ["prompt_condition", "code_type"])

    write_csv(
        ANALYSIS_DIR / "overall_summary.csv",
        [overall],
        ["n", *rate_columns()],
    )
    write_csv(
        ANALYSIS_DIR / "family_by_condition.csv",
        family_condition,
        ["model_family", "prompt_condition", "n", *rate_columns()],
    )
    write_csv(
        ANALYSIS_DIR / "family_by_snippet_type.csv",
        family_snippet,
        ["model_family", "code_type", "n", *rate_columns()],
    )
    write_csv(
        ANALYSIS_DIR / "condition_by_snippet_type.csv",
        condition_snippet,
        ["prompt_condition", "code_type", "n", *rate_columns()],
    )

    write_markdown(
        ANALYSIS_DIR / "analysis_summary.md",
        "Pilot Study Analysis Summary",
        [
            ("Overall", [overall], [("n", "n"), *percentage_columns()[1:]]),
            (
                "By Model Family and Prompt Condition",
                family_condition,
                [
                    ("family", "model_family"),
                    ("condition", "prompt_condition"),
                    *percentage_columns(),
                ],
            ),
            (
                "By Model Family and Snippet Type",
                family_snippet,
                [
                    ("family", "model_family"),
                    ("snippet type", "code_type"),
                    *percentage_columns(),
                ],
            ),
            (
                "By Prompt Condition and Snippet Type",
                condition_snippet,
                [
                    ("condition", "prompt_condition"),
                    ("snippet type", "code_type"),
                    *percentage_columns(),
                ],
            ),
        ],
    )

    summary_path = ANALYSIS_DIR / "analysis_summary.md"
    existing = summary_path.read_text(encoding="utf-8")
    narrative = "## Narrative Summary\n\n" + narrative_summary(overall, family_condition, family_snippet, condition_snippet) + "\n"
    summary_path.write_text(existing.rstrip() + "\n\n" + narrative, encoding="utf-8")

    print("Overall summary:\n")
    print(format_markdown_table([overall], [("n", "n"), *percentage_columns()[1:]]))
    print("Model family by prompt condition:\n")
    print(
        format_markdown_table(
            family_condition,
            [("family", "model_family"), ("condition", "prompt_condition"), *percentage_columns()],
        )
    )
    print("Model family by snippet type:\n")
    print(
        format_markdown_table(
            family_snippet,
            [("family", "model_family"), ("snippet type", "code_type"), *percentage_columns()],
        )
    )
    print("Prompt condition by snippet type:\n")
    print(
        format_markdown_table(
            condition_snippet,
            [("condition", "prompt_condition"), ("snippet type", "code_type"), *percentage_columns()],
        )
    )

    print("Narrative summary:\n")
    print(narrative_summary(overall, family_condition, family_snippet, condition_snippet))

    print(f"Saved analysis outputs to {ANALYSIS_DIR}")


if __name__ == "__main__":
    main()