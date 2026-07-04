# Efficiency Hallucinations Pilot Study

This repository contains the pilot study code, saved results, and analysis scripts for the paper *Efficiency Hallucination: Formalizing and Measuring Behavioral Calibration in LLM-Based Code Optimization*. The study sends 10 Python snippets to a model gateway under two prompt conditions and records how each model responds.

## Repository Layout

| File | Purpose |
|---|---|
| `pilot_study.py` | Experiment runner — calls the model gateway and writes per-model JSON files. Does **not** classify responses. |
| `classify.py` | Reclassification script — reads existing result JSONs, applies deterministic behavioral labels, and regenerates the combined results file. Run this after `pilot_study.py`, or whenever the classification logic changes, without making any new API calls. |
| `analyze_pilot_study.py` | Builds aggregate summary tables (by family, condition, snippet type) and writes CSV/Markdown outputs. |
| `analyze_pilot_study_by_model.py` | Generates a compact per-model scorecard from the saved JSON files. |
| `pilot_study_analysis_utils.py` | Shared helpers used by both analysis scripts. |
| `generate_figure.py` | Generates `calibration_figure.pdf` — the per-model abstention rate bar chart included in the paper. |
| `Pilot_Study_Empirical_Validation.pdf` | Case-by-case analysis validating that each Gemini-3.5-Flash-generated sub-optimal snippet is genuinely sub-optimal and suitable as study data. Provides empirical grounding for the optimal/sub-optimal snippet pairs used in the experiment. |

## Requirements

```
pip install aiohttp
```

## Configuration

Create a `.env` file in this directory:

```
MODEL_GATEWAY_BASE_URL=https://your-gateway.example.com
MODEL_GATEWAY_API_KEY=your_api_key_here
MODEL_GATEWAY_MODELS=claude-opus-4.8,gpt-5.4-mini,gemini-3.5-flash,...
MODEL_GATEWAY_CHAT_PATH=/v1/chat/completions
```

The script auto-loads `.env` on startup. Optional env vars: `MODEL_GATEWAY_TIMEOUT`, `MODEL_GATEWAY_MAX_CONCURRENCY`, `MODEL_GATEWAY_REQUEST_STAGGER_SECONDS`, `MODEL_GATEWAY_MODEL_STAGGER_SECONDS`, `MODEL_GATEWAY_SLOW_TIMEOUT`, `MODEL_GATEWAY_SLOW_MODELS`, `MODEL_GATEWAY_RESULTS_DIR`.

## Reproducing the Results

**Step 1 — Collect responses** (skips any model that already has a saved JSON):

```
python pilot_study.py
```

**Step 2 — Classify responses** (no API calls; reads existing JSONs and writes `behavioral_classification` to each record):

```
python classify.py
```

**Step 3 — Run analysis**:

```
python analyze_pilot_study.py
python analyze_pilot_study_by_model.py
```

Analysis outputs are written to `results/pilot_study/analysis/`.

## Output Files

Per-model JSON files land in `results/pilot_study/` named after the requested model label (e.g. `claude-opus-4_8.json`). The combined file is `results/pilot_study/pilot_study_all_models.json`.

Each record in a per-model JSON contains:

| Field | Description |
|---|---|
| `id` | Snippet id (1–10) |
| `model` | Resolved model id used for the request |
| `code_type` | `optimal` or `sub-optimal` |
| `prompt_condition` | `control` or `iiv_penalty` |
| `response` | Raw model output |
| `response_preview` | Truncated single-line version of the response |
| `behavioral_classification` | Deterministic label assigned by `classify.py` |

## Behavioral Classification Rules

`classify.py` applies the following deterministic rules (substring match on `Already Optimal`):

| Condition | Snippet type | Contains "Already Optimal" | Label |
|---|---|---|---|
| `iiv_penalty` | `optimal` | Yes | `Calibrated abstention` |
| `iiv_penalty` | `sub-optimal` | Yes | `Potential false abstention` |
| `iiv_penalty` | `optimal` | No | `Potential over-edit` |
| `iiv_penalty` | `sub-optimal` | No | `Action on improvable code` |
| `control` | either | Yes | `Unexpected abstention (control)` |
| `control` | either | No | `Edit suggested (control)` |

The match is a substring check, not an exact match. Responses that begin with or conclude with "Already Optimal" after extended chain-of-thought reasoning are counted as abstentions. Pilot study classifications have been manually verified by humans. If scaling to a complex codebase, LLM-as-a-judge may be better.
